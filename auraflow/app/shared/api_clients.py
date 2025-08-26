import os
import time
import openai
import stripe
import requests
import praw
from .logger import log

class RedditClient:
    def __init__(self):
        try:
            self.reddit = praw.Reddit(
                client_id=os.getenv("PRAW_CLIENT_ID"),
                client_secret=os.getenv("PRAW_CLIENT_SECRET"),
                user_agent=os.getenv("PRAW_USER_AGENT"),
            )
            log.info("Reddit client initialized successfully.")
        except Exception as e:
            log.error(f"Failed to initialize Reddit client: {e}")
            self.reddit = None

    def get_hot_posts(self, subreddit_name: str, limit: int = 10):
        if not self.reddit:
            log.error("Reddit client not available.")
            return []
        try:
            log.info(f"Fetching {limit} hot posts from r/{subreddit_name}...")
            subreddit = self.reddit.subreddit(subreddit_name)
            hot_posts = subreddit.hot(limit=limit)
            return [post.title for post in hot_posts]
        except Exception as e:
            log.error(f"Failed to fetch posts from Reddit: {e}")
            return []

class OpenAIClient:
    def __init__(self):
        self.client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    def query(self, prompt, model="gpt-4o", max_retries=3):
        for attempt in range(max_retries):
            try:
                log.info(f"Querying OpenAI (model: {model})...")
                response = self.client.chat.completions.create(
                    model=model,
                    messages=[{"role": "user", "content": prompt}]
                )
                log.info("OpenAI query successful.")
                return response.choices[0].message.content.strip()
            except Exception as e:
                log.warning(f"OpenAI API error: {e}. Retrying in {2**attempt}s...")
                time.sleep(2**attempt)
        log.error("OpenAI API query failed after all retries.")
        return None

class StripeClient:
    def __init__(self):
        stripe.api_key = os.getenv("STRIPE_API_KEY")

    def create_product_and_payment_link(self, name, price_cents):
        try:
            log.info(f"Creating Stripe product: {name}")
            product = stripe.Product.create(name=name)
            price = stripe.Price.create(
                product=product.id,
                unit_amount=price_cents,
                currency="usd",
            )
            payment_link = stripe.PaymentLink.create(
                line_items=[{"price": price.id, "quantity": 1}]
            )
            log.info(f"Stripe product and payment link created: {payment_link.url}")
            return payment_link.url
        except Exception as e:
            log.error(f"Stripe API error: {e}")
            return None

class VercelClient:
    def __init__(self):
        self.token = os.getenv("VERCEL_API_TOKEN")
        self.team_id = os.getenv("VERCEL_TEAM_ID")
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
        self.api_base = "https://api.vercel.com"

    def deploy_static_site(self, project_name, files_content):
        # This is a simplified deployment process.
        # In a real app, you'd check if the project exists first.
        try:
            log.info(f"Deploying to Vercel project: {project_name}")

            # Step 1: Define deployment payload
            # The Vercel API (v13) can create the project implicitly.
            upload_url = f"{self.api_base}/v13/deployments"
            if self.team_id:
                upload_url += f"?teamId={self.team_id}"

            files_to_upload = []
            for file_path, content in files_content.items():
                files_to_upload.append({
                    "file": file_path,
                    "data": content
                })

            deployment_payload = {
                "name": project_name,
                "files": files_to_upload,
                "projectSettings": {
                    "framework": "other"
                },
                "target": "production"
            }

            # Step 2: Post deployment request
            response = requests.post(upload_url, headers=self.headers, json=deployment_payload)
            response.raise_for_status()

            deployment_url = response.json().get('url')
            log.info(f"Vercel deployment successful: https://{deployment_url}")
            return f"https://{deployment_url}"

        except requests.exceptions.HTTPError as e:
            log.error(f"Vercel API HTTP error: {e.response.status_code} - {e.response.text}")
            return None
        except Exception as e:
            log.error(f"Vercel API deployment error: {e}")
            return None
