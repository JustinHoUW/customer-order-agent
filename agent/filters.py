"""
Filtering layer responsible for applying deterministic business rules to validated order records

Responsibilities:
- Receive schema-safe order objects from validator.py
- Interpret supported user filter conditions such as state and minimum total value
- Apply deterministic Python filtering instead of relying on the LLM for business logic
- Return only orders that match the user's request
- Keep filtering behavior predictable, repeatable, and easy to test
"""

import logging

# maps full state names to abbreviations
#
# helps normalize user queries like:
# "Ohio" into "OH"

STATE_MAPPING = {
    "ohio": "OH",
    "texas": "TX",
    "washington": "WA"
}

def extract_filters(user_query):
    """
    Extract supported filter conditions from the user's natural language query.

    Args:
        user_query (str):
            Natural language request from the user.

    Returns:
        dict:
            Dictionary containing extracted filter conditions.
    """

    query = user_query.lower()

    filters = {
        "state": None,
        "minimum_total": None
    }

    # detect supported state filters
    #
    # example: 
    # 'orders in ohio'
    for state_name, abbreviation in STATE_MAPPING.items():

        if state_name in query:
            filters["state"] = abbreviation
    
    words = query.split()

    for index, word in enumerate(words):

        # detect:
        # over 500
        # above 500
        if word in ["over", "above"]:

            # ensure next token exists
            if index + 1 < len(words):

                # extract number 
                try:
                    filters["minimum_total"] = float(words[index + 1])
                
                except ValueError:
                    logging.warning(
                        "Failed to parse minimum total value from query"
                    )
    logging.info("Extracted filters from user query: %s", filters)
    return filters

def filter_orders(orders, filters):
    """
    Apply deterministic filtering rules to validated order records.

    Args:
        orders (list):
            List of validated structured order dictionaries.

        filters (dict):
            Filter conditions extracted from user query.

    Returns:
        list:
            Orders matching all filter conditions.
    """

    filtered_orders = []

    # iterate through every validated order
    for order in orders:

        # assume order matches until proven otherwise
        matches = True

        # apply state filter
        # example:
        # state == "OH"
        if filters["state"] is not None:
            
            if order["state"] != filters["state"]:
                matches = False

        # apply minimum total filter
        #
        # example:
        # total > 500
        if filters["minimum_total"] is not None:

            if order["total"] <= filters["minimum_total"]:
                matches = False
        
        # append only matching records
        if matches:
            filtered_orders.append(order)
        
    logging.info(
        "Filtered %d out of %d validated orders",
        len(filtered_orders), 
        len(orders)
    )
    return filtered_orders