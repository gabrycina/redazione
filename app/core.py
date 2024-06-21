import openai
import os
import requests
from dotenv import load_dotenv
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib

class Worker:
    def __init__(self):
        pass

    def do(self, input):
        pass

class Agent(Worker):
    def __init__(self, api_key, system_prompt, user_prompt, model = "gpt-3.5-turbo"):
        super().__init__()
        self.system_prompt = system_prompt
        self.user_prompt = user_prompt
        self.model = model
        self.client = openai.OpenAI(api_key=api_key)
    
    def do(self, input: str):
        data = self.client.chat.completions.create(
            model = self.model,
            messages = [
                {
                    "role": "system",
                    "content": self.system_prompt
                },
                {
                    "role": "user",
                    "content": self.user_prompt.format(input)
                }
            ]
        ) 

        res = data.choices[0].message.content
        return res if res else ""


class Crawler(Worker):
    def __init__(self, sources):
        self.sources = sources
    
    def do(self, input):
        res = []
        for source in self.sources:
            try:
                response = requests.get(source)
                response.raise_for_status()  # Raise an error for bad status codes
                data = response.text
                res.append(data)
                
            except requests.exceptions.RequestException as e:
                print(f"An error occurred while crawling {source}: {e}")

        return res

class Pipeline:
    def __init__(self, workers):
        self.workers = workers

    def run(self, initial_input = None):
        input = initial_input
        for worker in self.workers:
            input = worker.do(input)
        return input 
 

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
crawler = Crawler(sources=[
    'https://news.ycombinator.com/from?site=arxiv.org'
])
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


def redact(email: str):
    report = pipeline.run()
    send_email(
        subject="Your daily report",
        body=f"{report}",
        to_email=email,
        smtp_port=465
    )
