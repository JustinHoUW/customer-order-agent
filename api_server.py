"""
Flask API server responsible for connecting the React frontend
to the LangGraph customer order agent backend.

Responsibilities:
- Expose HTTP API endpoints for the frontend
- Receive natural language customer order queries from React
- Execute the LangGraph workflow pipeline
- Return final structured JSON responses back to frontend clients
- Act as the communication layer between frontend UI and backend agent system
"""

# Flask web framework used for creating backend HTTP API routes
from flask import Flask, request, jsonify

# enables cross-origin requests between React frontend and Flask backend
#
# without CORS:
# browser blocks frontend requests because frontend and backend
# run on different ports
#
# example:
# React frontend:
# localhost:5173
#
# Flask backend:
# localhost:8000
from flask_cors import CORS

# import main LangGraph workflow execution entry point
#
# this function runs:
# API retrieval -> LLM extraction -> validation -> filtering
from agent.graph import run_order_agent


# initialize Flask application server
app = Flask(__name__)

# enable frontend/backend communication across different ports
CORS(app)


@app.route("/agent", methods=["POST"])
def run_agent():
    """
    API endpoint responsible for executing the customer order agent.

    Frontend sends:
    {
        "query": "Show me all Ohio orders over 500"
    }

    Backend returns:
    {
        "orders": [...]
    }
    """

    # retrieve JSON request body sent from React frontend
    #
    # example:
    # {
    #     "query": "orders in ohio over 500"
    # }
    data = request.get_json()

    # safely retrieve query field from request body
    #
    # .get() prevents KeyError crashes if query field is missing
    #
    # .strip() removes extra whitespace from user input
    user_query = data.get("query", "").strip()

    # defensive validation:
    # reject empty queries before running expensive workflow pipeline
    if not user_query:

        return jsonify({
            "error": "Query is required"
        }), 400

    # execute full LangGraph workflow pipeline
    #
    # internally executes:
    # - fetch_orders_node
    # - parse_orders_node
    # - validate_orders_node
    # - extract_filters_node
    # - filter_orders_node
    result = run_order_agent(user_query)

    return jsonify(result)


# only run Flask server if file is directly executed
#
# prevents accidental server startup during imports
if __name__ == "__main__":

    # start backend API server
    #
    # host="0.0.0.0"
    # allows external/frontend access
    #
    # port=8000
    # backend server port
    #
    # debug=True
    # auto-restarts server when code changes during development
    app.run(host="0.0.0.0", port=8000, debug=True)