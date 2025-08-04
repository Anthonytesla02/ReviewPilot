import uuid
import logging
from datetime import datetime
from flask import render_template, redirect, url_for, flash, request, abort
from flask_login import login_user, logout_user, login_required, current_user
from app import app, db
from models import User, ReviewTemplate, Customer, Review, ReviewRequest
from forms import (LoginForm, RegistrationForm, ReviewTemplateForm, CustomerForm, 
                  ReviewForm, AdminResponseForm, SettingsForm, SendReviewRequestForm, DetailedFeedbackForm)
from gmail_service import send_review_request_email, send_admin_notification
from utils import generate_review_link

logger = logging.getLogger(__name__)

@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            flash('Login successful!', 'success')
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('dashboard'))
        flash('Invalid username or password', 'danger')
    
    return render_template('login.html', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        # Check if username or email already exists
        if User.query.filter_by(username=form.username.data).first():
            flash('Username already exists', 'danger')
            return render_template('register.html', form=form)
        
        if User.query.filter_by(email=form.email.data).first():
            flash('Email already registered', 'danger')
            return render_template('register.html', form=form)
        
        user = User(
            username=form.username.data,
            email=form.email.data,
            business_name=form.business_name.data,
            google_business_url=form.google_business_url.data
        )
        user.set_password(form.password.data)
        
        db.session.add(user)
        db.session.commit()
        
        # Create multiple email template designs
        templates = [
            {
                'name': 'Professional Classic',
                'subject': 'We\'d love your feedback on your recent visit!',
                'message': '''Dear {customer_name},

Thank you for choosing {business_name} for your recent service. We hope you had a great experience!

We would really appreciate if you could take a moment to share your feedback about our service. Your review helps us improve and helps other customers make informed decisions.

Please click the link below to leave your review:
{review_link}

Thank you for your time and support!

Best regards,
{business_name} Team''',
                'is_default': True
            },
            {
                'name': 'Friendly & Personal',
                'subject': 'How was your experience with us? 😊',
                'message': '''Hi {customer_name}!

We hope you loved your recent visit to {business_name}! 

Your opinion means the world to us, and we'd be so grateful if you could share your experience. It only takes a minute and helps other customers discover what makes us special.

Ready to share your thoughts?
{review_link}

Thanks a bunch!
The {business_name} family 💙''',
                'is_default': False
            },
            {
                'name': 'Concise & Direct',
                'subject': 'Quick feedback request',
                'message': '''Hello {customer_name},

Thank you for visiting {business_name}. 

We'd appreciate your quick feedback: {review_link}

Your review helps us serve you better.

Thanks,
{business_name}''',
                'is_default': False
            },
            {
                'name': 'Gratitude-Focused',
                'subject': 'Thank you - we\'d love to hear from you!',
                'message': '''Dear {customer_name},

We're truly grateful you chose {business_name} and wanted to reach out personally.

Your experience matters deeply to us. Whether everything went perfectly or there's something we could improve, we'd love to hear your honest thoughts.

Share your experience here: {review_link}

With sincere appreciation,
{business_name}

P.S. Your feedback helps us create better experiences for everyone!''',
                'is_default': False
            },
            {
                'name': 'Value-Driven',
                'subject': 'Help others discover {business_name}!',
                'message': '''Hi {customer_name},

Thank you for being a valued customer of {business_name}!

Would you help other customers by sharing your experience? Your honest review helps people make confident decisions and supports local businesses like ours.

Leave your review: {review_link}

As a small token of our appreciation, customers who leave reviews are always welcomed with a smile and our best service!

Warmly,
{business_name} Team''',
                'is_default': False
            }
        ]
        
        for template_data in templates:
            template = ReviewTemplate(
                user_id=user.id,
                name=template_data['name'],
                subject=template_data['subject'],
                message=template_data['message'],
                is_default=template_data['is_default']
            )
            db.session.add(template)
        
        # Templates are added in the loop above
        db.session.commit()
        
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    # Get statistics
    total_customers = Customer.query.filter_by(user_id=current_user.id).count()
    total_reviews = Review.query.filter_by(user_id=current_user.id).count()
    pending_reviews = Review.query.filter_by(user_id=current_user.id, status='pending').count()
    
    # Recent reviews
    recent_reviews = Review.query.filter_by(user_id=current_user.id)\
        .order_by(Review.created_at.desc()).limit(5).all()
    
    # Recent customers
    recent_customers = Customer.query.filter_by(user_id=current_user.id)\
        .order_by(Customer.created_at.desc()).limit(5).all()
    
    return render_template('dashboard.html', 
                         total_customers=total_customers,
                         total_reviews=total_reviews,
                         pending_reviews=pending_reviews,
                         recent_reviews=recent_reviews,
                         recent_customers=recent_customers)

@app.route('/templates')
@login_required
def templates():
    templates = ReviewTemplate.query.filter_by(user_id=current_user.id).all()
    return render_template('templates.html', templates=templates)

@app.route('/templates/new', methods=['GET', 'POST'])
@login_required
def new_template():
    form = ReviewTemplateForm()
    if form.validate_on_submit():
        # If setting as default, unset other defaults
        if form.is_default.data:
            ReviewTemplate.query.filter_by(user_id=current_user.id, is_default=True)\
                .update({'is_default': False})
        
        template = ReviewTemplate(
            user_id=current_user.id,
            name=form.name.data,
            subject=form.subject.data,
            message=form.message.data,
            is_default=form.is_default.data
        )
        
        db.session.add(template)
        db.session.commit()
        
        flash('Template created successfully!', 'success')
        return redirect(url_for('templates'))
    
    return render_template('template_form.html', form=form, title='New Template')

@app.route('/templates/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_template(id):
    template = ReviewTemplate.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    
    form = ReviewTemplateForm(obj=template)
    if form.validate_on_submit():
        # If setting as default, unset other defaults
        if form.is_default.data and not template.is_default:
            ReviewTemplate.query.filter_by(user_id=current_user.id, is_default=True)\
                .update({'is_default': False})
        
        template.name = form.name.data
        template.subject = form.subject.data
        template.message = form.message.data
        template.is_default = form.is_default.data
        template.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        flash('Template updated successfully!', 'success')
        return redirect(url_for('templates'))
    
    return render_template('template_form.html', form=form, template=template, title='Edit Template')

@app.route('/templates/<int:id>/delete', methods=['POST'])
@login_required
def delete_template(id):
    template = ReviewTemplate.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    
    # Don't delete if it's the only template
    template_count = ReviewTemplate.query.filter_by(user_id=current_user.id).count()
    if template_count <= 1:
        flash('Cannot delete the last template. Create another template first.', 'danger')
        return redirect(url_for('templates'))
    
    db.session.delete(template)
    db.session.commit()
    
    flash('Template deleted successfully!', 'success')
    return redirect(url_for('templates'))


@app.route('/templates/preset', methods=['POST'])
@login_required
def add_preset_templates():
    """Add preset email templates for existing users"""
    # Check if user already has multiple templates
    existing_count = ReviewTemplate.query.filter_by(user_id=current_user.id).count()
    if existing_count >= 5:
        flash('You already have plenty of templates!', 'info')
        return redirect(url_for('templates'))
    
    # Add the new preset templates
    templates = [
        {
            'name': 'Friendly & Personal',
            'subject': 'How was your experience with us? 😊',
            'message': '''Hi {customer_name}!

We hope you loved your recent visit to {business_name}! 

Your opinion means the world to us, and we'd be so grateful if you could share your experience. It only takes a minute and helps other customers discover what makes us special.

Ready to share your thoughts?
{review_link}

Thanks a bunch!
The {business_name} family 💙''',
            'is_default': False
        },
        {
            'name': 'Concise & Direct',
            'subject': 'Quick feedback request',
            'message': '''Hello {customer_name},

Thank you for visiting {business_name}. 

We'd appreciate your quick feedback: {review_link}

Your review helps us serve you better.

Thanks,
{business_name}''',
            'is_default': False
        },
        {
            'name': 'Gratitude-Focused',
            'subject': 'Thank you - we\'d love to hear from you!',
            'message': '''Dear {customer_name},

We're truly grateful you chose {business_name} and wanted to reach out personally.

Your experience matters deeply to us. Whether everything went perfectly or there's something we could improve, we'd love to hear your honest thoughts.

Share your experience here: {review_link}

With sincere appreciation,
{business_name}

P.S. Your feedback helps us create better experiences for everyone!''',
            'is_default': False
        },
        {
            'name': 'Value-Driven',
            'subject': 'Help others discover {business_name}!',
            'message': '''Hi {customer_name},

Thank you for being a valued customer of {business_name}!

Would you help other customers by sharing your experience? Your honest review helps people make confident decisions and supports local businesses like ours.

Leave your review: {review_link}

As a small token of our appreciation, customers who leave reviews are always welcomed with a smile and our best service!

Warmly,
{business_name} Team''',
            'is_default': False
        }
    ]
    
    added_count = 0
    for template_data in templates:
        # Check if template with similar name already exists
        existing = ReviewTemplate.query.filter_by(
            user_id=current_user.id, 
            name=template_data['name']
        ).first()
        
        if not existing:
            template = ReviewTemplate(
                user_id=current_user.id,
                name=template_data['name'],
                subject=template_data['subject'],
                message=template_data['message'],
                is_default=template_data['is_default']
            )
            db.session.add(template)
            added_count += 1
    
    db.session.commit()
    
    if added_count > 0:
        flash(f'Added {added_count} new email template designs!', 'success')
    else:
        flash('All preset templates already exist in your account.', 'info')
    
    return redirect(url_for('templates'))


@app.route('/test-db')
def test_database():
    """Test route to check database connectivity"""
    try:
        from app import db
        from models import User, ReviewTemplate
        
        # Test database connection
        user_count = User.query.count()
        template_count = ReviewTemplate.query.count()
        
        return f"Database OK! Users: {user_count}, Templates: {template_count}"
    except Exception as e:
        return f"Database Error: {str(e)}"


@app.route('/customers')
@login_required
def customers():
    page = request.args.get('page', 1, type=int)
    customers = Customer.query.filter_by(user_id=current_user.id)\
        .order_by(Customer.created_at.desc())\
        .paginate(page=page, per_page=20, error_out=False)
    
    return render_template('customers.html', customers=customers)

@app.route('/customers/new', methods=['GET', 'POST'])
@login_required
def new_customer():
    form = CustomerForm()
    if form.validate_on_submit():
        customer = Customer(
            user_id=current_user.id,
            name=form.name.data,
            email=form.email.data,
            phone=form.phone.data,
            appointment_date=form.appointment_date.data,
            service_type=form.service_type.data,
            notes=form.notes.data
        )
        
        db.session.add(customer)
        db.session.commit()
        
        flash('Customer added successfully!', 'success')
        return redirect(url_for('customers'))
    
    return render_template('customer_form.html', form=form, title='New Customer')

@app.route('/customers/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_customer(id):
    customer = Customer.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    
    form = CustomerForm(obj=customer)
    if form.validate_on_submit():
        customer.name = form.name.data
        customer.email = form.email.data
        customer.phone = form.phone.data
        customer.appointment_date = form.appointment_date.data
        customer.service_type = form.service_type.data
        customer.notes = form.notes.data
        
        db.session.commit()
        
        flash('Customer updated successfully!', 'success')
        return redirect(url_for('customers'))
    
    return render_template('customer_form.html', form=form, customer=customer, title='Edit Customer')

@app.route('/customers/<int:id>/send-review-request', methods=['GET', 'POST'])
@login_required
def send_review_request(id):
    customer = Customer.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    
    form = SendReviewRequestForm()
    templates = ReviewTemplate.query.filter_by(user_id=current_user.id, is_active=True).all()
    form.template_id.choices = [(t.id, t.name) for t in templates]
    
    # Set default template if available
    default_template = ReviewTemplate.query.filter_by(user_id=current_user.id, is_default=True).first()
    if default_template and not form.template_id.data:
        form.template_id.data = default_template.id
    
    form.customer_id.data = customer.id
    
    if form.validate_on_submit():
        template = ReviewTemplate.query.get(form.template_id.data)
        
        # Generate unique token for this review request
        unique_token = str(uuid.uuid4())
        
        # Create review request record
        review_request = ReviewRequest(
            user_id=current_user.id,
            customer_id=customer.id,
            template_id=template.id,
            unique_token=unique_token
        )
        
        db.session.add(review_request)
        
        # Update customer record
        customer.review_requested = True
        customer.review_request_date = datetime.utcnow()
        
        db.session.commit()
        
        # Generate review link
        review_link = generate_review_link(unique_token)
        
        # Send email
        try:
            send_review_request_email(
                customer.email,
                template.subject,
                template.message,
                customer.name,
                current_user.business_name,
                review_link
            )
            
            flash('Review request sent successfully!', 'success')
        except Exception as e:
            flash(f'Error sending email: {str(e)}', 'danger')
            # Rollback the database changes if email fails
            review_request.status = 'failed'
            db.session.commit()
        
        return redirect(url_for('customers'))
    
    return render_template('review_request_form.html', form=form, customer=customer, 
                         title=f'Send Review Request to {customer.name}')

@app.route('/reviews')
@login_required
def reviews():
    page = request.args.get('page', 1, type=int)
    status_filter = request.args.get('status', 'all')
    
    query = Review.query.filter_by(user_id=current_user.id)
    
    if status_filter != 'all':
        query = query.filter_by(status=status_filter)
    
    reviews = query.order_by(Review.created_at.desc())\
        .paginate(page=page, per_page=20, error_out=False)
    
    return render_template('reviews.html', reviews=reviews, status_filter=status_filter)

@app.route('/reviews/<int:id>')
@login_required
def review_detail(id):
    review = Review.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    
    form = AdminResponseForm()
    if review.admin_response:
        form.admin_response.data = review.admin_response
    
    return render_template('review_detail.html', review=review, form=form)

@app.route('/reviews/<int:id>/respond', methods=['POST'])
@login_required
def respond_to_review(id):
    review = Review.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    
    form = AdminResponseForm()
    if form.validate_on_submit():
        review.admin_response = form.admin_response.data
        review.response_date = datetime.utcnow()
        review.status = 'responded'
        
        db.session.commit()
        
        # Here you could send the response via email to the customer
        flash('Response saved successfully!', 'success')
    
    return redirect(url_for('review_detail', id=id))

@app.route('/review/<token>', methods=['GET', 'POST'])
def public_review(token):
    # This is the public review form that customers will access
    review_request = ReviewRequest.query.filter_by(unique_token=token).first_or_404()
    
    # Mark as opened if not already
    if not review_request.opened_at:
        review_request.opened_at = datetime.utcnow()
        review_request.status = 'opened'
        db.session.commit()
    
    form = ReviewForm()
    if form.validate_on_submit():
        # Create review record
        review = Review(
            user_id=review_request.user_id,
            customer_id=review_request.customer_id,
            rating=form.rating.data,
            comment=form.comment.data
        )
        
        db.session.add(review)
        
        # Update review request
        review_request.completed_at = datetime.utcnow()
        review_request.status = 'completed'
        
        db.session.commit()
        
        # Smart routing based on rating
        if form.rating.data <= 3:
            # Low rating (1-3 stars) - redirect to detailed feedback form
            comment_text = form.comment.data or ''
            return redirect(url_for('detailed_feedback', token=token, rating=form.rating.data, comment=comment_text))
        elif form.rating.data >= 4:
            # High rating (4-5 stars) - redirect to Google Business page
            user = User.query.get(review_request.user_id)
            if user and user.google_business_url:
                return render_template('review_submitted.html',
                                     message='Thank you for your excellent feedback! Please consider sharing your experience on Google as well.',
                                     google_url=user.google_business_url,
                                     is_low_rating=False,
                                     auto_redirect=True)
            else:
                # Fallback if no Google URL is set
                return render_template('review_submitted.html',
                                     message='Thank you for your excellent feedback!',
                                     is_low_rating=False)
    
    customer = Customer.query.get(review_request.customer_id)
    business = User.query.get(review_request.user_id)
    
    return render_template('review_form.html', form=form, 
                         review_request=review_request,
                         customer=customer,
                         business=business)

@app.route('/feedback/<token>', methods=['GET', 'POST'])
def detailed_feedback(token):
    # Handle detailed feedback for low ratings
    review_request = ReviewRequest.query.filter_by(unique_token=token).first_or_404()
    
    rating = request.args.get('rating', type=int)
    comment = request.args.get('comment', '')
    
    form = DetailedFeedbackForm()
    if form.validate_on_submit():
        # Find the most recent review for this customer and rating
        review = Review.query.filter_by(customer_id=review_request.customer_id, rating=rating).order_by(Review.created_at.desc()).first()
        if review:
            # Update the review with detailed feedback
            issues = []
            if form.service_quality.data: issues.append('Service Quality')
            if form.staff_behavior.data: issues.append('Staff Behavior')
            if form.cleanliness.data: issues.append('Cleanliness')
            if form.wait_time.data: issues.append('Wait Time')
            if form.pricing.data: issues.append('Pricing')
            if form.communication.data: issues.append('Communication')
            if form.other.data: issues.append('Other')
            
            detailed_comment = f"""
Original Comment: {comment}

Issues Identified: {', '.join(issues) if issues else 'None specified'}

What went wrong: {form.what_went_wrong.data or 'Not specified'}

Suggestions for improvement: {form.suggestions.data or 'Not specified'}

Contact requested: {'Yes' if form.contact_me.data else 'No'}
            """
            
            review.comment = detailed_comment.strip()
            review.status = 'needs_response' if form.contact_me.data else 'pending'
            
            db.session.commit()
            
            # Send detailed admin notification
            try:
                user = User.query.get(review_request.user_id)
                customer = Customer.query.get(review_request.customer_id)
                if user and customer:
                    send_admin_notification(
                        user.email,
                        customer.name,
                        rating,
                        detailed_comment
                    )
            except Exception as e:
                logger.error(f"Failed to send detailed admin notification: {str(e)}")
        
        return render_template('review_submitted.html',
                             message='Thank you for the detailed feedback. We take your concerns seriously and will work to address them.',
                             is_low_rating=True,
                             contact_requested=form.contact_me.data)
    
    customer = Customer.query.get(review_request.customer_id)
    business = User.query.get(review_request.user_id)
    
    return render_template('detailed_feedback.html', 
                         form=form, 
                         rating=rating,
                         comment=comment,
                         customer=customer,
                         business=business)

@app.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    form = SettingsForm(obj=current_user)
    if form.validate_on_submit():
        current_user.business_name = form.business_name.data
        current_user.google_business_url = form.google_business_url.data
        current_user.email = form.email.data
        
        db.session.commit()
        
        flash('Settings updated successfully!', 'success')
        return redirect(url_for('settings'))
    
    return render_template('settings.html', form=form)

@app.route('/analytics')
@login_required
def analytics():
    # Calculate analytics data
    total_customers = Customer.query.filter_by(user_id=current_user.id).count()
    total_reviews = Review.query.filter_by(user_id=current_user.id).count()
    
    # Review distribution by rating
    rating_counts = {}
    for i in range(1, 6):
        rating_counts[i] = Review.query.filter_by(user_id=current_user.id, rating=i).count()
    
    # Reviews by month (last 6 months)
    from sqlalchemy import extract, func
    monthly_reviews = db.session.query(
        extract('month', Review.created_at).label('month'),
        func.count(Review.id).label('count')
    ).filter_by(user_id=current_user.id).group_by(extract('month', Review.created_at)).all()
    
    # Average rating
    avg_rating = db.session.query(func.avg(Review.rating)).filter_by(user_id=current_user.id).scalar()
    avg_rating = round(avg_rating, 1) if avg_rating else 0
    
    return render_template('analytics.html',
                         total_customers=total_customers,
                         total_reviews=total_reviews,
                         rating_counts=rating_counts,
                         monthly_reviews=monthly_reviews,
                         avg_rating=avg_rating)

@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500
