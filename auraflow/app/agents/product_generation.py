import os
import json
from ..shared.api_clients import OpenAIClient
from ..shared.logger import log

class ProductGenerationAgent:
    def __init__(self, openai_client: OpenAIClient):
        self.openai_client = openai_client

    def generate_ebook(self, venture_id, topic):
        log.info(f"Product Generation Agent: Generating e-book for topic: '{topic}'")

        # 1. Generate Outline
        outline_prompt = f"""
        Create a detailed chapter outline for an e-book titled '{topic}'. The e-book should be practical, actionable, and around 5,000 words in total.

        The outline should be a list of chapter titles. Respond with only the chapter titles, one per line.
        """
        outline = self.openai_client.query(outline_prompt)
        if not outline:
            log.error("Failed to generate e-book outline.")
            return None

        chapters = [ch.strip() for ch in outline.split('\n') if ch.strip()]
        log.info(f"Generated outline with {len(chapters)} chapters.")

        # 2. Generate Content for each chapter
        full_ebook_content = f"# {topic}\n\n"
        # Handle case where no chapters were generated
        if not chapters:
            log.error("Outline generation resulted in zero chapters.")
            return None

        for i, chapter_title in enumerate(chapters):
            log.info(f"Generating content for Chapter {i+1}: {chapter_title}")
            content_prompt = f"""
            Write the content for the chapter titled "{chapter_title}" of the e-book "{topic}".
            The content should be approximately {5000 // len(chapters)} words.
            Be comprehensive, clear, and provide practical advice. Use Markdown for formatting.
            Do not include the chapter title itself in the response; only provide the chapter body content.
            """
            chapter_content = self.openai_client.query(content_prompt, model="gpt-4o")
            if chapter_content:
                full_ebook_content += f"## {chapter_title}\n\n{chapter_content}\n\n"
            else:
                log.warning(f"Failed to generate content for chapter: {chapter_title}")

        # 3. Save the e-book
        venture_path = f"ventures/{venture_id}"
        os.makedirs(venture_path, exist_ok=True)
        ebook_file_path = os.path.join(venture_path, "product.md")
        with open(ebook_file_path, "w", encoding="utf-8") as f:
            f.write(full_ebook_content)

        log.info(f"E-book successfully generated and saved to {ebook_file_path}")
        return {"ebook_path": ebook_file_path}
