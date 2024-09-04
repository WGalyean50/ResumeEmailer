import os
import base64
import re
import smtplib
import requests
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import PyPDF2

# Define the scopes
SCOPES = ['https://www.googleapis.com/auth/gmail.send']

# Email configuration
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SENDER_EMAIL = os.getenv("SENDER_EMAIL")
SENDER_PASSWORD = os.getenv("SENDER_PASSWORD")
RECEIVER_EMAIL = os.getenv("RECEIVER_EMAIL")

# OpenAI API key
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

def extract_text_from_pdf(pdf_path):
    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        text = ""
        for page in reader.pages:
            text += page.extract_text()
    return text

def extract_email_from_text(text):
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    match = re.search(email_pattern, text)
    if match:
        return match.group(0)
    return None

def call_gpt4_api(prompt):
    headers = {
        'Authorization': f'Bearer {OPENAI_API_KEY}',
        'Content-Type': 'application/json'
    }
    data = {
        'model': 'gpt-4',
        'messages': [{'role': 'user', 'content': prompt}]
    }
    try:
        response = requests.post('https://api.openai.com/v1/chat/completions', headers=headers, json=data)
        response.raise_for_status()  # Raise an error for bad status codes
        response_data = response.json()
        print("API response:", response_data)  # Debugging output
        return response_data['choices'][0]['message']['content']
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return None
    except KeyError as e:
        print(f"Key error: {e}. Response data: {response_data}")
        return None

def send_email(to_address, subject, body):
    msg = MIMEMultipart()
    msg['From'] = SENDER_EMAIL
    msg['To'] = to_address
    msg['Subject'] = subject

    msg.attach(MIMEText(body, 'plain'))

    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        text = msg.as_string()
        server.sendmail(SENDER_EMAIL, to_address, text)
        server.quit()
        print(f"Email sent successfully to {to_address}")
    except Exception as e:
        print(f"Failed to send email. Error: {str(e)}")

def authenticate_gmail_api():
    creds = None
    if os.path.exists('token.json'):
        print("Loading credentials from token.json")
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            print("Refreshing expired credentials")
            creds.refresh(Request())
        else:
            print("Requesting new credentials via user login")
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
            print("Saved new credentials to token.json")
    return build('gmail', 'v1', credentials=creds)

def main():
    # Extract text from resume and job description
    resume_text = extract_text_from_pdf('WG_Resume_GPT_20240803.pdf')
    job_description_text = extract_text_from_pdf('JD_SRPM.pdf')

    # Extract email from resume
    candidate_email = extract_email_from_text(resume_text)
    if not candidate_email:
        print("Could not find an email address in the resume.")
        return

    # Analyze fit
    analysis_prompt = f"""
    Analyze the following resume and job description. Determine if the candidate is a good fit for the job. 
    Provide your analysis and a yes/no decision.

    Resume:
    {resume_text}

    Job Description:
    {job_description_text}
    """

    analysis_result = call_gpt4_api(analysis_prompt)
    if not analysis_result:
        print("Failed to get a response from the GPT-4 API.")
        return

    print("Analysis Result:")
    print(analysis_result)

    # Check if candidate is a good fit
    is_good_fit = "yes" in analysis_result.lower()

    if is_good_fit:
        # Generate email
        email_prompt = f"""
        Generate a personalized email to the candidate based on their resume and the job description. 
        The email should express interest in the candidate and invite them for an interview.
        
        Resume:
        {resume_text}
        
        Job Description:
        {job_description_text}
        """
        
        personalized_email = call_gpt4_api(email_prompt)
        if not personalized_email:
            print("Failed to get a personalized email from the GPT-4 API.")
            return

        print("\nPersonalized Email:")
        print(personalized_email)

        # Send the email
        send_email(candidate_email, "Interview Invitation", personalized_email)
    else:
        print("The candidate is not a good fit. No email will be sent.")

if __name__ == "__main__":
    main()
