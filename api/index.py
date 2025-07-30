from vercel_app import app

# Vercel expects the WSGI app to be in api/index.py
def handler(request):
    return app(request.environ, request.start_response)

# Alternative approach for Vercel
app = app