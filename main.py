from openai.types.chat.chat_completion import Choice
import requests
from typing import List
from dotenv import load_dotenv
import openai
import os

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

def main():
    sources = [
        'https://news.ycombinator.com/from?site=arxiv.org'
    ]
    
    sources_data = crawler(sources)
    drafted_data = drafter(sources_data)
    report = reporter(drafted_data)
    print(report)

if __name__ == '__main__':
    main()
