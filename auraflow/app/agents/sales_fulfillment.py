import os
import json
from ..shared.api_clients import OpenAIClient, StripeClient, VercelClient
from ..shared.logger import log

class SalesFulfillmentAgent:
    def __init__(self, openai_client: OpenAIClient, stripe_client: StripeClient, vercel_client: VercelClient):
        self.openai_client = openai_client
        self.stripe_client = stripe_client
        self.vercel_client = vercel_client
        self.base_domain = os.getenv("BASE_DOMAIN")

    def create_and_deploy_storefront(self, venture_id, product_details):
        log.info(f"Sales Agent: Creating storefront for venture {venture_id}")

        topic = product_details['niche_idea']['chosen_topic']

        # 1. Generate Landing Page Copy
        copy_prompt = f"""
        Generate compelling marketing copy for a landing page selling an e-book titled "{topic}".

        Respond with a JSON object with the following keys:
        - "headline": A catchy headline.
        - "subheader": A brief, compelling subheader.
        - "cta_button_text": Text for the call-to-action button (e.g., "Get It Now").
        - "features": A list of 3-4 key benefits or features of the e-book.
        """
        copy_response = self.openai_client.query(copy_prompt)
        try:
            copy = json.loads(copy_response)
        except (json.JSONDecodeError, TypeError):
            log.error("Failed to parse landing page copy from LLM.")
            # Provide a fallback copy to avoid complete failure
            copy = {
                "headline": f"Your Guide to {topic}",
                "subheader": "Discover the secrets to success.",
                "cta_button_text": "Buy Now",
                "features": ["In-depth chapters", "Actionable advice", "Expert insights"]
            }

        # 2. Create Stripe Payment Link
        price_cents = int(os.getenv("VENTURE_PRODUCT_PRICE_CENTS", 999))
        payment_link_url = self.stripe_client.create_product_and_payment_link(topic, price_cents)
        if not payment_link_url:
            log.error("Failed to create Stripe payment link.")
            return None

        # 3. Prepare landing page files
        try:
            # Construct path relative to this file's location
            script_dir = os.path.dirname(__file__)
            template_dir = os.path.abspath(os.path.join(script_dir, "..", "..", "templates", "landing_page"))

            with open(os.path.join(template_dir, "index.html"), "r", encoding="utf-8") as f:
                html_template = f.read()
            with open(os.path.join(template_dir, "style.css"), "r", encoding="utf-8") as f:
                css_content = f.read()
        except FileNotFoundError as e:
            log.error(f"Could not find landing page template: {e}")
            return None

        html_content = html_template.format(
            title=topic,
            headline=copy.get("headline", "New E-Book"),
            subheader=copy.get("subheader", "Unlock your potential."),
            features="\n".join([f"<li>{item}</li>" for item in copy.get("features", [])]),
            cta_button_text=copy.get("cta_button_text", "Buy Now"),
            payment_link=payment_link_url
        )

        project_name = f"auraflow-venture-{venture_id[:8]}"

        # 4. Deploy to Vercel
        deployment_url = self.vercel_client.deploy_static_site(
        project_name=project_name,
            files_content={
                "index.html": html_content,
                "style.css": css_content
            }
        )

        if not deployment_url:
            log.error("Failed to deploy landing page to Vercel.")
            return None

        sales_details = {
            "landing_page_url": deployment_url,
            "payment_link_url": payment_link_url,
            "project_name": project_name,
            "copy": copy
        }
        return sales_details
