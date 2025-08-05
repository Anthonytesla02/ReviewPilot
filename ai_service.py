import os
import json
import logging
import requests
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)

class MistralAIService:
    """Service class for Mistral AI API interactions"""
    
    def __init__(self):
        self.api_key = os.environ.get('MISTRAL_API_KEY')
        self.base_url = "https://api.mistral.ai/v1"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    def _make_request(self, endpoint: str, data: dict) -> Optional[dict]:
        """Make API request to Mistral"""
        try:
            response = requests.post(
                f"{self.base_url}/{endpoint}",
                headers=self.headers,
                json=data,
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error(f"Mistral API error: {e}")
            return None
    
    def analyze_sentiment(self, text: str) -> Tuple[str, float]:
        """
        Analyze sentiment of review text
        Returns: (sentiment, confidence_score)
        """
        prompt = f"""Analyze the sentiment of this customer review and categorize it as one of: satisfied, confused, frustrated, angry, neutral.

Review: "{text}"

Respond with only the sentiment category and a confidence score (0-1) in this exact format:
SENTIMENT: [category]
CONFIDENCE: [score]"""

        data = {
            "model": "mistral-small-latest",
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "max_tokens": 100,
            "temperature": 0.1
        }
        
        response = self._make_request("chat/completions", data)
        
        if response and 'choices' in response:
            content = response['choices'][0]['message']['content'].strip()
            
            # Parse response
            sentiment = "neutral"
            confidence = 0.5
            
            lines = content.split('\n')
            for line in lines:
                if line.startswith('SENTIMENT:'):
                    sentiment = line.split(':', 1)[1].strip().lower()
                elif line.startswith('CONFIDENCE:'):
                    try:
                        confidence = float(line.split(':', 1)[1].strip())
                    except:
                        confidence = 0.5
            
            return sentiment, confidence
        
        return "neutral", 0.5
    
    def generate_response_suggestion(self, review_text: str, rating: int, business_name: str, tone: str = "professional") -> str:
        """
        Generate AI response suggestion for a review
        """
        tone_instructions = {
            "professional": "professional and courteous",
            "friendly": "warm and friendly", 
            "casual": "casual and conversational"
        }
        
        tone_style = tone_instructions.get(tone, "professional and courteous")
        
        prompt = f"""You are a customer service representative for {business_name}. Generate a {tone_style} response to this customer review.

Rating: {rating}/5 stars
Review: "{review_text}"

Guidelines:
- Be empathetic and understanding
- Thank the customer for their feedback
- Address specific concerns if rating is low
- For high ratings, express gratitude and encourage future visits
- Keep response under 150 words
- Be genuine and avoid overly scripted language

Response:"""

        data = {
            "model": "mistral-small-latest",
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "max_tokens": 200,
            "temperature": 0.7
        }
        
        response = self._make_request("chat/completions", data)
        
        if response and 'choices' in response:
            return response['choices'][0]['message']['content'].strip()
        
        return f"Thank you for your {rating}-star review. We appreciate your feedback and look forward to serving you again."
    
    def categorize_feedback(self, text: str) -> str:
        """
        Categorize feedback as complaint, praise, or suggestion
        """
        prompt = f"""Categorize this customer feedback as one of: complaint, praise, suggestion

Feedback: "{text}"

Respond with only the category:"""

        data = {
            "model": "mistral-small-latest",
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "max_tokens": 20,
            "temperature": 0.1
        }
        
        response = self._make_request("chat/completions", data)
        
        if response and 'choices' in response:
            category = response['choices'][0]['message']['content'].strip().lower()
            if category in ['complaint', 'praise', 'suggestion']:
                return category
        
        return "feedback"
    
    def generate_follow_up_email(self, customer_name: str, business_name: str, step: int, incentive: str = None) -> Dict[str, str]:
        """
        Generate follow-up email content for sequence steps
        """
        step_prompts = {
            1: f"Write a friendly reminder email asking {customer_name} to leave a review for {business_name}. Keep it brief and polite.",
            2: f"Write a second follow-up email to {customer_name} emphasizing the importance of customer feedback for {business_name}. Mention how reviews help improve service.",
            3: f"Write a final follow-up email to {customer_name} offering a small incentive: {incentive or '10% off next service'} in exchange for an honest review of {business_name}."
        }
        
        prompt = step_prompts.get(step, step_prompts[1])
        prompt += "\n\nProvide both a subject line and email body. Format as:\nSUBJECT: [subject]\nBODY: [body]"
        
        data = {
            "model": "mistral-small-latest", 
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "max_tokens": 300,
            "temperature": 0.7
        }
        
        response = self._make_request("chat/completions", data)
        
        if response and 'choices' in response:
            content = response['choices'][0]['message']['content'].strip()
            
            # Parse subject and body
            lines = content.split('\n')
            subject = ""
            body = ""
            
            for i, line in enumerate(lines):
                if line.startswith('SUBJECT:'):
                    subject = line.split(':', 1)[1].strip()
                elif line.startswith('BODY:'):
                    body = '\n'.join(lines[i:]).replace('BODY:', '').strip()
                    break
            
            return {
                "subject": subject or f"Quick reminder - Share your experience with {business_name}",
                "body": body or f"Hi {customer_name},\n\nWe hope you enjoyed your recent experience with {business_name}. Could you take a moment to share your feedback? It would mean a lot to us.\n\nThank you!"
            }
        
        return {
            "subject": f"Share your experience with {business_name}",
            "body": f"Hi {customer_name},\n\nWe'd love to hear about your experience with {business_name}. Your feedback helps us improve our service.\n\nThank you!"
        }

# Initialize global service instance
mistral_service = MistralAIService()