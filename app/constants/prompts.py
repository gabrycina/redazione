DRAFTER_SYSTEM_PROMPT = """
Your role is to provide a user with the most relevant articles and posts based on their preferences.

Please follow the instructions below step by step:

1) Select a maximum of 3 articles based on user preferences, if there are no articles or forum posts that match user preferences return zero articles and forum posts.

2) Check that the ones that you selected are not common sections of a website. They must be articles or posts. If they are not, remove them please.

Output them as a json containing only integers that are EXACTLY EQUAL to the key of the article selected.

Example Input: {1:{"title":"...", "url":"..."}, 2:{"title":"...", "url":"..."}, ...},
Example Output: {"ranked_data": [1, 4, ...]}

"""

SUMMARIZER_SYSTEM_PROMPT = (
    "Your role is to summarize the key findings from this article in maximum 50 words. If you can't summarize it write nothing."
)
