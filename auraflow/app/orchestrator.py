import time
import json
from .state_manager import StateManager
from .agents.market_research import MarketResearchAgent
from .agents.product_generation import ProductGenerationAgent
from .agents.sales_fulfillment import SalesFulfillmentAgent
from .shared.api_clients import OpenAIClient, StripeClient, VercelClient, RedditClient
from .shared.logger import log

class Orchestrator:
    def __init__(self):
        self.state_manager = StateManager()

        # Create shared API clients
        openai_client = OpenAIClient()
        stripe_client = StripeClient()
        vercel_client = VercelClient()
        reddit_client = RedditClient()

        # Inject clients into agents
        self.mra = MarketResearchAgent(
            openai_client=openai_client,
            reddit_client=reddit_client
        )
        self.pga = ProductGenerationAgent(openai_client=openai_client)
        self.sfa = SalesFulfillmentAgent(
            openai_client=openai_client,
            stripe_client=stripe_client,
            vercel_client=vercel_client
        )

    def run_venture(self, venture_id):
        log.info(f"--- Starting orchestration for venture: {venture_id} ---")
        venture = self.state_manager.get_venture(venture_id)
        if not venture:
            log.error(f"Venture {venture_id} not found.")
            return

        current_state = venture['state']
        log.info(f"Current state: {current_state}")

        try:
            if current_state == "DISCOVERY":
                niche_idea = self.mra.find_niche()
                if niche_idea:
                    self.state_manager.update_venture_details(venture_id, 'niche_idea', niche_idea)
                    self.state_manager.update_venture_state(venture_id, "PRODUCT_GENERATION")
                else:
                    raise Exception("Failed to discover a niche.")
                # After state change, fetch the next state to process immediately
                self.run_venture(venture_id)

            elif current_state == "PRODUCT_GENERATION":
                niche_idea_str = venture.get('niche_idea')
                if not niche_idea_str:
                     raise Exception("Niche idea is missing for product generation.")
                niche_idea = json.loads(niche_idea_str)

                product_details = self.pga.generate_ebook(venture_id, niche_idea['chosen_topic'])
                if product_details:
                    self.state_manager.update_venture_details(venture_id, 'product_details', product_details)
                    self.state_manager.update_venture_state(venture_id, "DEPLOYMENT")
                else:
                    raise Exception("Failed to generate product.")
                # After state change, fetch the next state to process immediately
                self.run_venture(venture_id)

            elif current_state == "DEPLOYMENT":
                venture_data = self.state_manager.get_venture(venture_id)
                niche_idea_str = venture_data.get('niche_idea')
                if not niche_idea_str:
                     raise Exception("Niche idea is missing for deployment.")

                product_details = {
                    'niche_idea': json.loads(niche_idea_str)
                }
                sales_details = self.sfa.create_and_deploy_storefront(venture_id, product_details)
                if sales_details:
                    self.state_manager.update_venture_details(venture_id, 'sales_details', sales_details)
                    self.state_manager.update_venture_state(venture_id, "LIVE")
                else:
                    raise Exception("Failed to deploy storefront.")
                # After state change, fetch the next state to process immediately
                self.run_venture(venture_id)

            elif current_state == "LIVE":
                log.info(f"Venture {venture_id} is LIVE. Monitoring phase would start here.")
                venture_details = self.state_manager.get_venture(venture_id)
                sales_details = json.loads(venture_details['sales_details'])
                log.info(f"Landing Page URL: {sales_details['landing_page_url']}")
                log.info("Orchestration for this venture is complete.")

        except Exception as e:
            log.error(f"Error in state {current_state} for venture {venture_id}: {e}", exc_info=True)
            self.state_manager.update_venture_state(venture_id, f"FAILED_{current_state}")

    def process_all_ventures(self):
        # A simple sequential processor. In a larger system, this could be parallelized.
        conn = self.state_manager.conn
        cursor = conn.cursor()
        # Process ventures that are not in a terminal state
        cursor.execute("SELECT id FROM ventures WHERE state NOT LIKE 'FAILED_%' AND state != 'LIVE'")
        ventures_to_process = [row[0] for row in cursor.fetchall()]

        if not ventures_to_process:
            log.info("No active ventures to process.")
            return

        log.info(f"Found {len(ventures_to_process)} ventures to process.")
        for venture_id in ventures_to_process:
            self.run_venture(venture_id)
            time.sleep(5) # Rate limit to avoid overwhelming APIs
