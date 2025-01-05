import gspread
import os
from google.oauth2.service_account import Credentials
from send_email import send_email
from mistralai import Mistral
import requests


def open_spreadsheet(spreadsheet_name):
    """
    Open a Google Spreadsheet by name
    
    Parameters:
        spreadsheet_name (str): Name of the spreadsheet to open
    
    Returns:
        gspread.Spreadsheet: The opened spreadsheet
    """
    # Define the scope
    scopes = [
        'https://www.googleapis.com/auth/spreadsheets',
        'https://www.googleapis.com/auth/drive'
    ]

    try:
        # Get absolute path to credentials file
        creds_path = os.path.join(os.path.dirname(__file__), 
                                'sinuous-canto-427508-k5-8fe207f9654f.json')
        
        # Load credentials from service account file
        credentials = Credentials.from_service_account_file(
            creds_path,
            scopes=scopes
        )

        # Create gspread client
        gc = gspread.authorize(credentials)
        
        spreadsheet = gc.open(spreadsheet_name)
        print(f"Successfully opened: {spreadsheet_name}")
        return spreadsheet

    except FileNotFoundError:
        print(f"Credentials file not found at: {creds_path}")
        return None
    except Exception as e:
        print(f"Error opening spreadsheet: {str(e)}")
        return None


def get_recipients(worksheet):
    """
    Extract names, emails, and preferences from the worksheet
    
    Parameters:
        worksheet: gspread worksheet object
    
    Returns:
        list: List of dictionaries containing recipient information
    """
    try:
        records = worksheet.get_all_records()
        recipients = []
        for record in records:
            name = record.get('What would you like to be called in the email? ', '').strip()
            email = record.get("What's your email address? ", '').strip()
            content = record.get("Would you like to tell me a little bit about yourself? ", '').strip()
            unsubscribed_value = record.get("Unsubscribe", "").strip()
            unsubscribed = unsubscribed_value.lower() == "yes"
            
            # Only include if they have name, email and haven't unsubscribed
            if name and email and not unsubscribed:
                recipients.append({
                    'name': name,
                    'email': email,
                    'content': content
                })
        return recipients
    
    except Exception as e:
        print(f"Error extracting recipients: {str(e)}")
        return []


def get_mistral_response(user_content):
    """
    Generate an uplifting response using Mistral API
    
    Parameters:
        user_content (str): User's input about their situation
    
    Returns:
        str: Generated response from Mistral
    """
    api_key = os.getenv('MISTRAL_API_KEY')
    if not api_key:
        print("Error: MISTRAL_API_KEY not found in environment variables")
        return None
        
    client = Mistral(api_key=api_key)
    
    if not user_content:
        messages = [
            {"role": "system", "content": """You are generating uplifting message content. 
            Create a brief, encouraging message without any greeting or direct addressing. 
            Keep it warm and universal (1-2 paragraphs)."""},
            
            {"role": "user", "content": """
            Generate a positive message that:
            1. Offers encouragement for the day ahead
            2. Includes a positive perspective on life
            3. Ends with an uplifting note
            
            Important: Do NOT include any greetings (like "Hello" or "Hi") or direct addressing.
            Just start with the encouraging content directly.
            Keep it brief and warm.
            """}
        ]
    else:
        messages = [
            {"role": "system", "content": """You are generating personalized encouraging content. 
            Create a response that acknowledges feelings and offers support, without any greeting 
            or direct addressing. Keep responses warm, personal, and concise (2-3 paragraphs)."""},
            
            {"role": "user", "content": f"""
            Based on this sharing: "{user_content}"
            
            Generate a supportive response that:
            1. Acknowledges the shared feelings
            2. Offers a positive perspective
            3. Provides gentle encouragement
            4. Ends with a hopeful note
            
            Important: Do NOT include any greetings or direct addressing.
            The message will be part of an email that already has "Dear [Name]" at the start.
            Just focus on the supportive content.
            """}
        ]

    try:
        response = client.chat.complete(
            model="mistral-small-latest",
            messages=messages,
            temperature=0.7,
            max_tokens=500
        )
        
        return response.choices[0].message.content
    except Exception as e:
        print(f"Error generating Mistral response: {str(e)}")
        return None


def get_random_cat_image():
    """
    Get a random cat image as bytes
    
    Returns:
        tuple: (image_bytes, content_type) or (None, None) if failed
    """
    try:
        response = requests.get('https://api.thecatapi.com/v1/images/search')
        if response.status_code == 200:
            image_url = response.json()[0]['url']
            image_response = requests.get(image_url)
            if image_response.status_code == 200:
                content_type = image_response.headers['Content-Type']
                return image_response.content, content_type
    except Exception as e:
        print(f"Error fetching cat image: {str(e)}")
    return None, None


def send_emails_to_recipients(recipients):
    """
    Send personalized emails to all recipients
    """
    successful = 0
    failed = 0

    for recipient in recipients:
        name = recipient['name']
        email = recipient['email']
        user_content = recipient['content']
        
        # Get a random cat picture
        image_data, content_type = get_random_cat_image()
        cat_message = "\nHere's a cute cat to brighten your day!" if image_data else ""
        
        # Add unsubscribe note to the email
        unsubscribe_note = "\nP.S. If you'd like to unsubscribe from these emails, please reply with 'UNSUBSCRIBE'."
        
        # Generate personalized message using Mistral
        ai_response = get_mistral_response(user_content)
        if not ai_response:
            ai_response = "I appreciate you sharing your thoughts with me. Stay positive!"

        subject = f"Your Daily Encouragement, {name}"
        body = f"""Dear {name},

{ai_response}

Wishing you a wonderful day ahead,
Sophia

{unsubscribe_note}
{cat_message}
"""
        
        if send_email(email, subject, body, image_data, content_type):
            successful += 1
        else:
            failed += 1
    
    print(f"\nSummary: {successful} emails sent successfully, {failed} failed")


if __name__ == "__main__":
    sheet = open_spreadsheet("daily_email (Responses)")
    if sheet:
        try:
            worksheet = sheet.worksheet("Form Responses 1")
            recipients = get_recipients(worksheet)
            
            if recipients:
                send_emails_to_recipients(recipients)
            else:
                print("No recipients found in the worksheet")
                
        except Exception as e:
            print(f"Error processing worksheet: {str(e)}") 