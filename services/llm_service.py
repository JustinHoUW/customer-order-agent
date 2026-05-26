"""
Service layer responsible for interacting with the LLM through OpenRouter.

Responsibilities:
- Receive validated raw unstructured customer order text from customer_api.py
- Send raw order text to the language model for structured extraction
- Constrain the LLM to deterministic JSON formatting tasks
- Normalize messy customer order text into structured order objects
- Reduce hallucination risk through prompt constraints and controlled extraction
- Handle malformed model responses and API failures gracefully
- Return structured Python data for downstream schema validation and deterministic filtering
"""

import json
import logging
import os

from dotenv import load_dotenv
from openai import OpenAI

# load environment variables from .env file
# this allows us to keep API keys out of source control
load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1"
)

MODEL_NAME = "openai/gpt-oss-120b:exacto"

def build_extraction_prompt(raw_order_text):
    """
    Build a constrained prompt for extracting structured order data to pass into the LLM

    Args:
        raw_order_text (str):
            One raw messy customer order string
    
    Returns:
        str:
            Prompt send to the language model
    """
    return f"""
You are an information extraction system

Your job is to extract structured order fields from the raw customer order text

Rules:
- Only use values explicitly present in the raw text
- Do not guess or invent missing fields
- Return valid JSON only
- Do not include markdown
- Do not include explanations
- The toal field must be a number, not a string
- The items field must be a list of strings.

Required JSON schema:
{{
  "orderId": "string",
  "buyer": "string",
  "city": "string",
  "state": "string",
  "total": number,
  "items": ["string"]
}}

Raw order text:
{raw_order_text}
"""

def parse_order_with_llm(raw_order_text):
    """
    Convert one raw order string into a structured Python dictionary using the LLM

    Args:
        raw_order_text (str):
            Raw unstructured order text from the customer API
    
    Returns:
        dict | None:
            Structured order dictionary if parsing succeeds
            None if model/API/parsing fails
    """

    try:
        logging.info("Starting LLM extraction for raw order text")
        prompt = build_extraction_prompt(raw_order_text)
        response = client.chat.completions.create(
            model=MODEL_NAME,
            temperature=0,
            messages=[
                {
                    "role": "system",
                    "content": "You extract structured JSON from messy customer order text"
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        # get text content from model response
        model_output = response.choices[0].message.content

        logging.info("Received LLM extraction response")

        # convert JSON string returned by model into Python dictionary
        structured_order = json.loads(model_output)

        return structured_order
    
    # protects against malformed LLM responses
    except json.JSONDecodeError as error:
        logging.error("LLM returned invalid JSON: %s", error)
        return None

    except Exception as error:
        logging.error("LLM extraction failed: %s", error)
        return None

def parse_orders_with_llm(raw_orders):
    """
    Parse multiple raw order strings into structured dictionaries

    Args:
        raw_orders (list): 
            List of raw unstructured order strings
    
    Returns:
        list:
            List of structured order dictionaries
            Invalid or failed parses are skipped
    """

    structured_orders = []

    for raw_order in raw_orders:
        parsed_order = parse_order_with_llm(raw_order)

        if parsed_order is None:
            logging.warning("Skipping order because LLM parsing failed")
            continue

        structured_orders.append(parsed_order)
    
    logging.info("Parsed %d orders with LLM", len(structured_orders))
    return structured_orders
