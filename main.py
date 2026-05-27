"""
Main entry point for running the customer order agent.

Responsibilities:
- Configure application logging
- Accept a natural language order query from the user
- Run the LangGraph customer order workflow
- Print final filtered order results as clean JSON
"""

import json
import logging

from agent.graph import run_order_agent


def configure_logging():
    """
    Configure logging for the application.

    This makes it easier to trace the workflow during live demo:
    API retrieval -> LLM extraction -> validation -> filtering
    """

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s"
    )


def main():
    """
    Run the customer order agent from the command line.
    """

    configure_logging()

    print("Customer Order Agent")
    print("--------------------")
    print("Example query: Show me all orders where the buyer was located in Ohio and total value was over 500.")
    print()

    user_query = input("Enter your order query: ").strip()

    if not user_query:
        print("No query provided. Please enter a natural language order request.")
        return

    result = run_order_agent(user_query)

    print("\nFinal JSON Response:")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()