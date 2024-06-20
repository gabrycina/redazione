import openai
import requests

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
        
