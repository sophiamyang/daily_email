import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


def send_email(recipient_email, subject, body):
    """
    Send an email using Gmail SMTP server
    
    Parameters:
        recipient_email (str): Recipient's email address
        subject (str): Email subject
        body (str): Email body content
    """
    # Get credentials from environment variables
    sender_email = os.getenv('EMAIL_SENDER')
    sender_password = os.getenv('EMAIL_PASSWORD')

    if not sender_email or not sender_password:
        raise ValueError("Email credentials not found in environment variables")

    # Create message container
    message = MIMEMultipart()
    message['From'] = sender_email
    message['To'] = recipient_email
    message['Subject'] = subject

    # Add body to email
    message.attach(MIMEText(body, 'plain'))

    try:
        # Create SMTP session
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            # Enable security
            server.starttls()
            
            # Login to the server
            server.login(sender_email, sender_password)
            
            # Send email
            text = message.as_string()
            server.sendmail(sender_email, recipient_email, text)
            return True
            
    except Exception as e:
        print(f"An error occurred while sending email to {recipient_email}: {e}")
        return False


if __name__ == "__main__":
    recipient_email = "sophiayang1211@gmail.com"
    subject = "Test Email"
    body = "This is a test email sent from Python!"
    
    send_email(recipient_email, subject, body) 