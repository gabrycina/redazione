import openai
import requests


class Worker:
    def __init__(self):
        pass

    def do(self, input, context):
        pass


class Agent(Worker):
    def __init__(self, api_key, system_prompt, agent_role: str, model="gpt-3.5-turbo"):
        super().__init__()
        self.system_prompt = system_prompt
        self.agent_role = agent_role
        self.model = model
        self.client = openai.OpenAI(api_key=api_key)

    def do(self, input: str, context):
        data = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": context[self.agent_role].format(input)},
            ],
        )
        res = data.choices[0].message.content
        return res if res else ""


class Crawler(Worker):
    def __init__(self):
        super().__init__()

    def do(self, input, context):
        res = []
        for source in input:
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

    def run(self, input=None, context=None):
        data = input
        for worker in self.workers:
            data = worker.do(data, context)
        return data


def get_basic_pipeline(api_key):
    crawler = Crawler()
    drafter = Agent(
        api_key=api_key,
        system_prompt="Your role is to select and rank articles based on user preferences. Output them in format: title - link.",
        agent_role="drafter"
    )
    reporter = Agent(
        api_key=api_key,
        system_prompt="Your role is to report 5 top articles each day. Write an email, the format is: 1 line intro - papers (title + link and no more!) - Sign as 'La Redazione' ",
        agent_role="reporter"
    )
    return Pipeline([crawler, drafter, reporter])
