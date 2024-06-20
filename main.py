import requests
from typing import List
from dotenv import load_dotenv
import openai
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
from core import Agent, Crawler, Pipeline

load_dotenv()

def send_email(subject, body, to_email, smtp_port):
    smtp_user = os.getenv('EMAIL_USER')
    smtp_password = os.getenv('EMAIL_PASSWORD')
    smtp_server = "smtp.gmail.com"
    
    if not smtp_user or not smtp_password:
        raise ValueError("Environment variables for email credentials are not set")

    msg = MIMEMultipart()
    msg['From'] = smtp_user
    msg['To'] = to_email
    msg['Subject'] = subject
    
    msg.attach(MIMEText(body, 'plain'))
    
    try:
        # Create a secure SSL context
        server = smtplib.SMTP_SSL(smtp_server, smtp_port)
        server.login(smtp_user, smtp_password)  # login with your email and password
        
        # Send the email
        server.sendmail(smtp_user, to_email, msg.as_string())
        server.quit()
        print("Email sent successfully!")
        
    except Exception as e:
        print(f"Failed to send email: {e}")

def main():
    api_key = os.getenv("OPENAI_API_KEY")
    sources = [
        'https://news.ycombinator.com/from?site=arxiv.org'
    ]


    to_email = input("Email :: ")

    crawler = Crawler(sources=sources)
    drafter = Agent(
        api_key = api_key,
        system_prompt = "Your role is to select and rank articles that mention research papers. Output them in format title, link. The link must be an arxiv link or any website for scientific papers",
        user_prompt = "Here's today papers, write the newsletter: {}"
    )
    reporter = Agent(
        api_key = api_key,
        system_prompt =  "Your role is to report 5 top research papers each day. Write an email for Gabriele and Caleb in the format is: 1 line intro - papers (title + link and no more!) - Sign as 'La Redazione' ",
        user_prompt = "Here's today papers, write the newsletter: {}"
    )

    pipeline = Pipeline([crawler, drafter, reporter])
    report = pipeline.run()

    send_email(
        subject="Your daily report",
        body=f"{report}",
        to_email=to_email,
        smtp_port=465
    )
    

if __name__ == '__main__':
    main()
