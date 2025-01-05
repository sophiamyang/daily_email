import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


def send_email(recipient_email, subject, body, image_data=None, content_type=None):
    """
    Send an email using Gmail SMTP server
    
    Parameters:
        recipient_email (str): Recipient's email address
        subject (str): Email subject
        body (str): Email body content
        image_data (bytes, optional): Image data to embed
        content_type (str, optional): Image content type
    """
    # Get credentials from environment variables
    sender_email = os.getenv('EMAIL_SENDER')
    sender_password = os.getenv('EMAIL_PASSWORD')

    if not sender_email or not sender_password:
        raise ValueError("Email credentials not found in environment variables")

    # Create message container
    message = MIMEMultipart('related')
    message['From'] = sender_email
    message['To'] = recipient_email
    message['Subject'] = subject

    # Create HTML version of the body with embedded image
    html_body = f"""
    <html>
        <body>
            <p>{body.replace('\n', '<br>')}</p>
            {f'<img src="cid:cat_image" style="max-width:500px;">' if image_data else ''}
        </body>
    </html>
    """

    # Attach HTML body
    message.attach(MIMEText(html_body, 'html'))

    # Attach image if provided
    if image_data and content_type:
        image = MIMEImage(image_data)
        image.add_header('Content-ID', '<cat_image>')
        message.attach(image)

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
    recipient_email = "test@test.com" #change to real email
    subject = "Test Email"
    body = "This is a test email sent from Python!"
    
    # Test without image
    send_email(recipient_email, subject, body, None, None) 