import time
import os
from dotenv import load_dotenv
from .orchestrator import Orchestrator
from .state_manager import StateManager
from .shared.logger import log

def main():
    load_dotenv()

    # Verify environment variables
    required_vars = ["OPENAI_API_KEY", "STRIPE_API_KEY", "VERCEL_API_TOKEN"]
    if not all(os.getenv(var) for var in required_vars):
        log.error("Missing required environment variables. Please check your .env file.")
        return

    # Ensure required directories exist
    os.makedirs("db", exist_ok=True)
    os.makedirs("ventures", exist_ok=True)

    state_manager = StateManager()
    orchestrator = Orchestrator()

    log.info("AuraFlow System Started")

    # Check for existing ventures to process or create a new one
    conn = state_manager.conn
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM ventures WHERE state != 'LIVE' AND state NOT LIKE 'FAILED_%'")
    active_ventures = cursor.fetchone()[0]

    if active_ventures == 0:
        log.info("No active ventures found. Creating a new one.")
        state_manager.create_venture()

    # Main loop
    while True:
        log.info("Starting orchestration cycle...")
        orchestrator.process_all_ventures()
        log.info("Orchestration cycle complete. Sleeping for 1 hour.")
        time.sleep(3600) # Run once per hour

if __name__ == "__main__":
    main()
