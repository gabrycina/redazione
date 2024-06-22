import os
import openai
import requests
import json

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
            ]
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

class BatchSummarizer(Worker):
    def __init__(self):
        super().__init__()

    def do(self, input, context):
        articles = json.loads(input)
        summarizer = Agent(
            api_key=os.getenv("OPENAI_API_KEY"),
            system_prompt="Your role is to summarize the key findings from this article in maximum 50 words",
            agent_role="summarizer"
        )

        for article in articles:
            try:
                response = requests.get("https://r.jina.ai/" + article['link'])
                response.raise_for_status()  # Raise an error for bad status codes
                data = response.text
                article['summary'] = summarizer.do(data, context)

            except requests.exceptions.RequestException as e:
                print(f"An error occurred while crawling {article['link']}: {e}")

        return articles

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
        system_prompt="Your role is to select and do your own ranking for articles based on user preferences. Output them as a json array containing objects leaving summary as empty string. Example: [{\"title\": \"example title\", \"link\": \"example link\", \"summary\": \"\"}, ...]. DONT ANSWER IN MARKDOWN. JUST WRITE THE JSON.",
        agent_role="drafter"
    )
    batch_summarizer = BatchSummarizer()
    reporter = Agent(
        api_key=api_key,
        system_prompt="Your role is to report 5 top articles each day. Write an email in HTML. The format is: [1 line intro] - for each article: title ALWAYS WITH CLICKABLE link, summary. Make it readable and beautiful. DONT WRITE IN MARKDOWN. Sign as 'Redact 🚀'.",
        agent_role="reporter"
    )
    return Pipeline([crawler, drafter, batch_summarizer, reporter])
