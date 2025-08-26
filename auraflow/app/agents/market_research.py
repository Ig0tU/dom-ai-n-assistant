import json
from ..shared.api_clients import OpenAIClient, RedditClient
from ..shared.logger import log

class MarketResearchAgent:
    def __init__(self, openai_client: OpenAIClient, reddit_client: RedditClient):
        self.openai_client = openai_client
        self.reddit_client = reddit_client

    def find_niche(self, subreddit: str = "SideProject"):
        log.info(f"Market Research Agent: Starting niche discovery from r/{subreddit}...")

        # Step 1: Get hot topics from Reddit
        potential_topics = self.reddit_client.get_hot_posts(subreddit, limit=15)
        if not potential_topics:
            log.error(f"Could not fetch topics from r/{subreddit}. Aborting niche discovery.")
            return None

        topics_list_str = "\n- ".join(potential_topics)

        # Step 2: Use LLM to analyze the topics
        prompt = f"""
        Analyze the following list of raw ideas scraped from r/{subreddit}. Identify the most promising idea for a short, practical e-book.
        The ideal idea should target a clear audience, solve a specific problem, and be something people would pay for.

        Idea List:
        - {topics_list_str}

        Filter out vague, overly technical, or non-monetizable ideas.
        Your analysis must be brief. Respond with only a JSON object containing the following keys:
        - "chosen_topic": The topic you selected.
        - "target_audience": A brief description of the target audience.
        - "reasoning": A one-sentence explanation for your choice.

        Example JSON format:
        {{
          "chosen_topic": "Topic Name",
          "target_audience": "Description",
          "reasoning": "Reason."
        }}
        """

        response = self.openai_client.query(prompt)
        if response:
            try:
                niche_data = json.loads(response)
                log.info(f"Niche selected: {niche_data.get('chosen_topic')}")
                return niche_data
            except json.JSONDecodeError:
                log.error("Failed to parse JSON response from LLM for niche discovery.")
                return None
        return None
