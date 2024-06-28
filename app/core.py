import openai
import requests
import json
import logging
from bs4 import BeautifulSoup

from app.prompts import (
    DRAFTER_SYSTEM_PROMPT,
    SUMMARIZER_SYSTEM_PROMPT,
    REPORTER_SYSTEM_PROMPT,
)

logger = logging.getLogger(__name__)

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


class Crawler2(Worker):
    def __init__(self):
        super().__init__()

    def do(self, input, context):
        res = []
        for source in input:
            response = requests.get(source)
            if response.status_code != 200:
                logging.error(f"Crawler: failed to fetch the URL: {source}")
                continue

            soup = BeautifulSoup(response.content, "html.parser")
            links = soup.find_all("a")
            res.append(
                {
                    "source": source,
                    "data": {
                        link.get_text(strip=True): link.get("href")
                        for link in links
                        if len(link.get_text(strip=True)) > 10
                    },
                }
            )
        return res


class Drafter(Worker):
    def __init__(self, api_key):
        super().__init__()
        self.api_key = api_key

    def do(self, input, context):
        agent = Agent(
            api_key=self.api_key,
            system_prompt=DRAFTER_SYSTEM_PROMPT,
            agent_role="drafter",
        )

        for source_data in input:
            # TODO provare a fare ricostruire il link relativo all LLM
            # passare tutto source_data e non solo "data"
            ranked_data = agent.do(source_data["data"], context=context)

            try:
                ranked_data = json.loads(ranked_data)
            except Exception as e:
                logging.error(f"Drafter: {e} -- data that caused error {ranked_data}")
                continue

            try:
                source_data["data"] = [
                    {"title": article_title, "url": source_data["data"][article_title]}
                    for article_title in ranked_data
                ]
            except Exception as e:
                logging.error(f"Drafter: {e} -- context {source_data} ")
                continue

        return input


class BatchSummarizer(Worker):
    def __init__(self, api_key):
        super().__init__()
        self.api_key = api_key

    def do(self, input, context):
        summarizer = Agent(
            api_key=self.api_key,
            system_prompt=SUMMARIZER_SYSTEM_PROMPT,
            agent_role="summarizer",
        )

        for source in input:
            for article in source["data"]:
                try:
                    response = requests.get("https://r.jina.ai/" + article["url"])
                    response.raise_for_status()
                except Exception as e:
                    logging.error(f"Summarizer: {e} -- data that caused error {article['url']}")
                    continue

                try:
                    data = response.text
                    article["summary"] = summarizer.do(data, context)
                except Exception as e:
                    logging.error(f"Summarizer: {e} -- len of data that caused error {len(data)}")
                    continue

        return input


class Pipeline:
    def __init__(self, workers):
        self.workers = workers

    def run(self, input=None, context=None):
        data = input
        for worker in self.workers:
            data = worker.do(data, context)
        return data


def get_basic_pipeline(api_key):
    crawler = Crawler2()
    drafter = Drafter(api_key=api_key)
    batch_summarizer = BatchSummarizer(api_key=api_key)
    reporter = Agent(
        api_key=api_key,
        system_prompt=REPORTER_SYSTEM_PROMPT,
        agent_role="reporter",
    )
    return Pipeline([crawler, drafter, batch_summarizer, reporter])
