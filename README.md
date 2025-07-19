# ScrapTrade - Metal Waste Management System

A web application for managing metal waste trading and processing, built with Flask and integrated with Razorpay for payments.

## Features

- User Authentication (Admin, Processor, Buyer roles)
- Scrap Material Management
- Cart System
- Razorpay Payment Integration
- Dashboards for different user roles

## Local Development

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
Create a `.env` file with:
```
RAZORPAY_KEY_ID=your_key_id
RAZORPAY_KEY_SECRET=your_key_secret
```

4. Run the application:
```bash
python other/app.py
```

## Heroku Deployment

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
heroku config:set RAZORPAY_KEY_ID=your_key_id
heroku config:set RAZORPAY_KEY_SECRET=your_key_secret
```

4. Deploy the app:
```bash
git push heroku main
```

## Important Notes

- The application uses in-memory storage (lists and dictionaries) for data management
- Data will reset on server restarts
- Users will need to log in again after server restarts

## Default Login Credentials

- Admin: admin/admin123
- User: user/user123
- Processor: processor/processor123
- Buyer: buyer/buyer123 