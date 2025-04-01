# ScrapTrade - Metal Waste Management System

A Flask-based web application for managing metal waste trading and processing.

## Features

- User authentication
- Scrap material management
- Cart system
- Razorpay payment integration
- Admin dashboard
- Processor dashboard
- Buyer dashboard

## Deployment Instructions

### Local Development

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
python other/app.py
```

### Heroku Deployment

1. Install Heroku CLI and login:
```bash
heroku login
```

2. Create a new Heroku app:
```bash
heroku create your-app-name
```

3. Set environment variables:
```bash
heroku config:set FLASK_ENV=production
heroku config:set RAZORPAY_KEY_ID=your_razorpay_key_id
heroku config:set RAZORPAY_KEY_SECRET=your_razorpay_key_secret
```

4. Deploy to Heroku:
```bash
git push heroku main
```

### Important Notes

- The application uses in-memory storage, so data will reset when the server restarts
- Make sure to set up your Razorpay API credentials in the environment variables
- The application is configured to run with Gunicorn in production

## Default Login Credentials

- Admin: admin/admin123
- User: user/user123
- Processor: processor/processor123
- Buyer: buyer/buyer123 