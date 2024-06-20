import requests
from typing import List
from dotenv import load_dotenv
import openai
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib

load_dotenv()

def crawler(sources) -> List[str]:
    res = []

    for source in sources:
        try:
            response = requests.get(source)
            response.raise_for_status()  # Raise an error for bad status codes
            data = response.text
            res.append(data)
            
        except requests.exceptions.RequestException as e:
            print(f"An error occurred while crawling {source}: {e}")

    return res

def drafter(data) -> str:
    client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    messages = [
        {
            "role": "system", 
            "content": "Your role is to select and rank articles that mention research papers. Output them in format title, link. The link must be an arxiv link or any website for scientific papers"
        },
        {
            "role": "user", 
            "content": f"Tell me everything about this data: {data}"
        }
    ]

    data = client.chat.completions.create(model="gpt-3.5-turbo", messages=messages)
    res = data.choices[0].message.content

    return res if res else ""


def reporter(data):
    client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    messages = [
        {
            "role": "system", 
            "content": "Your role is to report 5 top research papers each day. Write an email for Gabriele and Caleb in the format is: 1 line intro - papers (title + link and no more!) - conclude by joking about the fact that caleb dates an under 18 girl. Sign as 'La Redazione' "
        },
        {
            "role": "user", 
            "content": f"Here's today papers, write the newsletter: {data}"
        }
    ]

    data = client.chat.completions.create(model="gpt-3.5-turbo", messages=messages)
    res = data.choices[0].message.content

    return res if res else ""

def send_email(subject, body, to_email, from_email, smtp_port):
    smtp_user = os.getenv('EMAIL_USER')
    smtp_password = os.getenv('EMAIL_PASSWORD')
    from_email = os.getenv('FROM_EMAIL')
    smtp_server = "smtp.gmail.com"
    
    if not smtp_user or not smtp_password or not from_email:
        raise ValueError("Environment variables for email credentials are not set")

    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = to_email
    msg['Subject'] = subject
    
    msg.attach(MIMEText(body, 'plain'))
    
    try:
        # Create a secure SSL context
        server = smtplib.SMTP_SSL(smtp_server, smtp_port)
        server.login(smtp_user, smtp_password)  # login with your email and password
        
        # Send the email
        server.sendmail(from_email, to_email, msg.as_string())
        server.quit()
        print("Email sent successfully!")
        
    except Exception as e:
        print(f"Failed to send email: {e}")

def main():
    sources = [
        'https://news.ycombinator.com/from?site=arxiv.org'
    ]
    
    sources_data = crawler(sources)
    drafted_data = drafter(sources_data)
    report = reporter(drafted_data)
    send_email(
        subject="Test Email",
        body=f"{report}",
        to_email="c.gabriele.info@gmail.com",
        from_email="blablagabriele@gmail.com",
        smtp_port=465
    )
    

if __name__ == '__main__':
    main()
