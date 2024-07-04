import openai
import requests
import json
import logging
import tiktoken
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

from app.db import SessionLocal
from app.models import User
from app.constants.prompts import (
    DRAFTER_SYSTEM_PROMPT,
    SUMMARIZER_SYSTEM_PROMPT,
)
from app.constants.emails import EMAIL_BODY, EMAIL_ARTICLE


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
        max_tokens=16000,
    ):
        super().__init__()
        self.system_prompt = system_prompt
        self.agent_role = agent_role
        self.model = model
        self.response_format = response_format
        self.client = openai.OpenAI(api_key=api_key)
        self.tokenizer = tiktoken.get_encoding("cl100k_base")
        self.max_tokens = max_tokens

    def limit_to_context_length(self, message):
        tokens = self.tokenizer.encode(message)
        if len(tokens) > self.max_tokens:
            tokens = tokens[: self.max_tokens]
            message = self.tokenizer.decode(tokens)
        return message

    def do(self, input: str, context):
        logger.info(f"Agent:{self.agent_role} starting...")
        data = self.client.chat.completions.create(
            model=self.model,
            response_format=self.response_format,
            messages=[
                {"role": "system", "content": self.system_prompt},
                {
                    "role": "user",
                    "content": self.limit_to_context_length(
                        context[self.agent_role].format(input)
                    ),
                },
            ],
        )
        res = data.choices[0].message.content

        logger.info(f"Agent:{self.agent_role} ending...")
        return res if res else ""


class Crawler2(Worker):
    def __init__(self):
        super().__init__()
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
            "DNT": "1",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
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
            collected_data = {"source": source, "data": {}}
            unique_urls = set()
            for i, link in enumerate(links):
                normalized_link = self.normalize_link(source, link.get("href"))
                title = link.get_text(strip=True)
                if normalized_link not in context["history"] and len(title) > 15 and normalized_link not in unique_urls:
                    collected_data["data"][i] = {
                        "title": title,
                        "url": normalized_link,
                    }
                    unique_urls.add(normalized_link)
                else:
                    logger.info(f"Removed {normalized_link} as it is a duplicate")

            res.append(collected_data)

        if len(res) == 0:
            raise Exception("crawler didn't produce any results")

        logger.info(res)
        logger.info("Crawler ending...")
        return res


class Drafter(Worker):
    def __init__(self, api_key):
        super().__init__()
        self.api_key = api_key

    def update_history(self, drafter_output, context):
        current_history = context["history"]
        add_to_history = []
        for source_data in drafter_output:
            for data in source_data["data"]:
                add_to_history.append(data["url"])

        merged_history = current_history + add_to_history

        try:
            db = SessionLocal()
            user_db = db.query(User).filter(User.id == context["user_id"]).one()
            user_db.history = json.dumps(merged_history)
            db.add(user_db)
            db.commit()
            db.refresh(user_db)
        except Exception as e:
            logger.error(f"Update History Failed: {e}")
        finally:
            db.close()

    def do(self, input, context):
        logger.info("Drafter starting...")
        agent = Agent(
            api_key=self.api_key,
            system_prompt=DRAFTER_SYSTEM_PROMPT,
            agent_role="drafter",
            response_format={"type": "json_object"},
        )

        result = []
        for source_data in input:
            logger.info(
                f"Drafter working on {source_data['source']} with data len {len(source_data['data'])}"
            )

            try:
                ranked_data = agent.do(source_data["data"], context=context)
            except Exception as e:
                logger.error(f"0.drafter: {e}")
                continue

            try:
                ranked_data = json.loads(ranked_data)["ranked_data"]
                logger.info(f"ranked_data: {ranked_data}")
            except Exception as e:
                logger.error(f"1.drafter: {e}")
                continue

            data = []
            for id_article in ranked_data:
                try:
                    data.append(
                        {
                            "title": source_data["data"][id_article]["title"],
                            "url": source_data["data"][id_article]["url"],
                        }
                    )
                except Exception as e:
                    logger.error(f"2.drafter: {e}")

            if len(data) != 0:
                result.append({"source": source_data["source"], "data": data})

        self.update_history(result, context)
        logger.info(f"Drafter ending...")
        return result


class BatchSummarizer(Worker):
    def __init__(self, api_key):
        super().__init__()
        self.api_key = api_key

    def strip_protocol(self, url: str):
        if url.startswith("https://"):
            return url.replace("https://", "", 1)
        if url.startswith("http://"):
            return url.replace("http://", "", 1)
        logger.warn(f"Url {url} does not contain protocol")
        return url

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
                        "https://r.jina.ai/" + self.strip_protocol(article["url"])
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


class Reporter(Worker):
    def __init__(self):
        super().__init__()

    def do(self, input, context):
        html_articles = []
        for source in input:
            for article in source["data"]:
                html_articles.append(
                    EMAIL_ARTICLE.format(
                        article["url"], article["title"], article["summary"]
                    )
                )

        return EMAIL_BODY.format("".join(html_articles))


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
    reporter = Reporter()
    return Pipeline([crawler, drafter, batch_summarizer, reporter])
