# Daily Positive Thoughts Email System

An automated system that sends personalized encouraging emails using Google Forms/Sheets, Mistral AI, and Gmail. The goal is to brighten people's day with AI-generated positive messages tailored to their current situation.

## Want to Receive Daily Positive Thoughts?

Fill out this form to subscribe: [Daily Positive Thoughts Signup](https://forms.gle/SzCf7zVF5KtvndNh6)

**Note:** This is a demo project running for fun - no guarantee on how long the service will continue. Feel free to unsubscribe anytime by responding "UNSUBSCRIBE" to any email.

## How It Works

1. You share what's on your mind through the Google Form
2. The system uses Mistral AI to generate a personalized encouraging message
3. You receive a daily email with positive thoughts related to your situation
4. You can unsubscribe anytime

## Technical Components

- `sheets.py`: Main script that handles recipient management and email sending
- `send_email.py`: Email sending functionality


## Run It Yourself

1. Install required packages:

```bash
pip install mistralai gspread google-auth python-dotenv
```

2. Set up credentials in `.env` file:
- Gmail account and app password
- Mistral AI API key
- Google service account JSON

3. Run the script:

```bash
python sheets.py
```

    