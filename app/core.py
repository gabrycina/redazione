import openai
import requests
import json
import logging
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

from app.prompts import (
    DRAFTER_SYSTEM_PROMPT,
    SUMMARIZER_SYSTEM_PROMPT,
    REPORTER_SYSTEM_PROMPT,
)

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class Worker:
    def __init__(self):
        pass

    def do(self, input, context):
        pass


class Agent(Worker):
    def __init__(
        self,
        api_key,
        system_prompt,
        agent_role: str,
        model="gpt-3.5-turbo",
        response_format=None,
    ):
        super().__init__()
        self.system_prompt = system_prompt
        self.agent_role = agent_role
        self.model = model
        self.response_format = response_format
        self.client = openai.OpenAI(api_key=api_key)

    def do(self, input: str, context):
        logger.info(f"Agent:{self.agent_role} starting...")
        data = self.client.chat.completions.create(
            model=self.model,
            response_format=self.response_format,
            messages=[
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": context[self.agent_role].format(input)},
            ],
        )
        res = data.choices[0].message.content

        logger.info(f"Agent:{self.agent_role} ending...")
        return res if res else ""


class Crawler2(Worker):
    def __init__(self):
        super().__init__()
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36"
        }

    def normalize_link(self, base_url, relative_or_absolute_url):
        parsed_url = urlparse(relative_or_absolute_url)
        if parsed_url.netloc:
            return relative_or_absolute_url
        else:
            return urljoin(base_url, relative_or_absolute_url)

    def do(self, input, context):
        logger.info("Crawler starting...")
        res = []
        for source in input:
            logger.info(f"Crawler requesting {source}")
            try:
                response = requests.get(source, headers=self.headers)
                response.raise_for_status()
            except Exception as e:
                logger.error(f"crawler: {e}")
                continue

            soup = BeautifulSoup(response.content, "html.parser")
            links = soup.find_all("a")
            res.append(
                {
                    "source": source,
                    "data": {
                        link.get_text(strip=True): self.normalize_link(source, link.get("href"))
                        for link in links
                        if len(link.get_text(strip=True)) > 10
                    },
                }
            )

        if len(res) == 0:
            raise Exception("crawler didn't produce any results")
        logger.info("Crawler ending...")
        return res


class Drafter(Worker):
    def __init__(self, api_key):
        super().__init__()
        self.api_key = api_key

    def relative_url_handling(self, base_url, relative_url):
        if "http://" in relative_url or "https://" in relative_url:
            return relative_url
        base_url = base_url[:-1] if base_url[-1] == "/" else base_url
        relative_url = relative_url[1:] if relative_url[0] == "/" else relative_url
        complete_url = base_url + "/" + relative_url
        return complete_url.replace("https://", "")

    def do(self, input, context):
        logger.info("Drafter starting...")
        agent = Agent(
            api_key=self.api_key,
            system_prompt=DRAFTER_SYSTEM_PROMPT,
            agent_role="drafter",
            response_format={"type": "json_object"},
        )

        for source_data in input:
            logger.info(
                f"Drafter working on {source_data['source']} with data len {len(source_data['data'])}"
            )
            ranked_data = agent.do(source_data["data"], context=context)

            try:
                ranked_data = json.loads(ranked_data)["ranked_data"]
            except Exception as e:
                logger.error(f"drafter: {e}")
                continue

            try:
                source_data["data"] = [
                    {"title": article_title, "url": source_data["data"][article_title]}
                    for article_title in ranked_data
                ]
            except Exception as e:
                logger.error(f"drafter: {e}")
                continue

        logger.info(f"Drafter ending...")
        return input


class BatchSummarizer(Worker):
    def __init__(self, api_key):
        super().__init__()
        self.api_key = api_key

    def do(self, input, context):
        logger.info(f"Summarizer starting...")
        summarizer = Agent(
            api_key=self.api_key,
            system_prompt=SUMMARIZER_SYSTEM_PROMPT,
            agent_role="summarizer",
        )

        for source in input:
            for article in source["data"]:
                logger.info(f"Summarizer working on {article}")
                try:
                    response = requests.get(
                        "https://r.jina.ai/" + article["url"].replace("https://", "")
                    )
                    response.raise_for_status()
                except Exception as e:
                    logger.error(f"summarizer: {e}")
                    continue

                try:
                    data = response.text
                    article["summary"] = summarizer.do(data, context)
                except Exception as e:
                    logger.error(f"summarizer: {e}")
                    continue

        logger.info(f"Summarizer ending...")
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
