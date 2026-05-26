"""
Service layer responsible for interacting with the dummy customer Flask API

Responsibility:
- Connect to customer order API endpoints
- Retrieve raw unstructured customer order data
- Handle API/network failures gracefully
- Log request and response activity
- Return normalized Python data structures for downstream processing
"""

# python library used for debugging; helps trace failures during API call
import logging

# requests library allows my application to make HTTP requests to external Flask customer API
import requests

API_BASE_URL = "http://localhost:5001"

def fetch_orders(limit=None):
    """
    Fetch raw unstructured orders from the dummy customer API

    Args:
        limit (int | None):
            Optional limit for how many orders to retrieve

    Returns:
        list:
            List of raw unstructured order strings.
            Returns empty list if request fails or response is invalid
    """

    try:

        # dictionary that'll hold optional query parameters
        # example:
        # /api/orders?limit=2
        params = {}

        # only include limit parameter if user provided one
        # avoids sending unnecessary query parameters
        if limit is not None:
            params["limit"] = limit
        
        # send GET request to Flask API endpoint
        # params=param automatically converts:
        # {"limit": 2}
        #
        # into:
        # ?limit=2
        response = requests.get(
            f"{API_BASE_URL}/api/orders",
            params=params,
            timeout=10
        )

        # if HTTP status code is not successful
        response.raise_for_status()

        # convert JSON HTTP response into Python dict
        # example:
        # {
        #   "status": "ok",
        #   "raw_orders": [...]
        # }
        # python dict
        data = response.json()


        # defensive validation:
        # verify API returned successful status
        if data.get("status") != "ok":
            logging.error(
                "Customer API returned non-ok status: %s",
                data
            )

            # return empty list instead of crashing application
            return []

        # safely retrieve raw_orders field
        raw_orders = data.get("raw_orders", [])

        # we expect raw_orders to ALWAYS be a list
        # validate expected schema structure
        if not isinstance(raw_orders, list):

            logging.error(
                "Unexpected API schema. raw_orders is not a list: %s",
                data
            )
            return []
        
        # observability logging to monitor request success and number of orders retrieved
        logging.info(
            "Fetched %d raw orders from customer API",
            len(raw_orders)
        )

        return raw_orders
    
    # catches network/API-related failures
    #
    # examples
    # - API server offline
    # - connection timeout
    # - DNS issues
    # - refused connection
    except requests.exceptions.RequestException as error:

        logging.error(
            "Failed to fetch orders from customer API: %s",
            error
        )
        return []
    
    # catches JSON parsing failures
    except ValueError as error:
        logging.error(
            "Failed to parse customer API JSON response: %s",
            error
        )
        return []
    
if __name__ == "__main__":

    # fetch all orders from dummy API
    orders = fetch_orders()

    # print raw results to terminal for debugging
    print(orders)
