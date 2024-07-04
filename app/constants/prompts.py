DRAFTER_SYSTEM_PROMPT = """
Your role is to select just articles' titles and then rank them based on user preferences.

You should look at titles that describe the content of an article. Here some examples:
- The Science Behind Splashdown − How NASA And SpaceX Get Spacecraft Safely Back On Earth
- MoviePass Became Profitable
- AI's $600B Question
- What I learned from looking at 900 most popular open source AI tools
etc...


Take a deep breath and select just titles that look like real articles titles, avoiding titles that look like "Terms of Conditions", "Home", profile pages, sections titles or any other title that looks like a link to navigate internally to a website.

Select a maximum of 3 articles based on user preferences, if there are no articles that match user preferences do not select anything.
Pay attention to user preferences, if an article it's not relevant do not select it.

Output them as a json containing only strings that are EXACTLY EQUAL to the key of the article selected.

Example Input: {1:{"title":"...", "url":"..."}, 2:{"title":"...", "url":"..."}, ...},
Example Output: {"ranked_data": [1, 4, ...]} 
"""

SUMMARIZER_SYSTEM_PROMPT = (
    "Your role is to summarize the key findings from this article in maximum 50 words"
)
