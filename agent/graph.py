"""
LangGraph orchestration layer responsible for coordinating the end-to-end customer order processing workflow

Responsibilities:
- Coordinate data flow between retrieval, extraction, validation, and filtering layers
"""

import logging
from typing import TypedDict, List, Dict, Any

from langgraph.graph import StateGraph, END

from services.customer_api import fetch_orders
from services.llm_service import parse_orders_with_llm
from agent.validator import validate_orders
from agent.filters import extract_filters, filter_orders


class OrderAgentState(TypedDict):
    """
    Shared state object passed between LangGraph nodes
    
    Each node reads from this state dictionary
    adds or updates one part of the workflow,
    then returns the updated state

    This makes the full pipeline easier to trace
    user_query -> raw_orders -> structured_orders -> validated_orders -> filters -> final_orders
    """

    # original natural language request from the user
    user_query: str

    # raw unstructured order strings fetched from the customer API
    raw_orders: List[str]

    # structured dictionaries returned by the LLM extraction layer
    structured_orders: List[Dict[str, Any]]

    # schema-safe orders that passed validator.py checks
    validated_orders: List[Dict[str, Any]]

    # deterministic filter conditions extracted from the user query
    filters: Dict[str, Any]

    # final orders matching the user's request
    final_orders: List[Dict[str, Any]]

def fetch_orders_node(state: OrderAgentState) -> OrderAgentState:
    """
    LangGraph node responsible for retrieving raw order data from the customer API.
    """

    logging.info("Graph node started: fetch_orders_node")

    # call customer_api.py service layer
    # this retrieves raw unstructured order strings from the dummy Flask API
    raw_orders = fetch_orders()

    # store raw API results in graph state for the next node
    state["raw_orders"] = raw_orders

    logging.info("Graph node completed: fetched %d raw orders", len(raw_orders))

    return state

def parse_orders_node(state: OrderAgentState) -> OrderAgentState:
    """
    LangGraph node responsible for converting raw order text into structured dictionaries.
    """

    logging.info("Graph node started: parse_orders_node")

    # get raw orders from previous graph step
    raw_orders = state.get("raw_orders", [])

    # call llm_service.py to perform controlled LLM extraction
    structured_orders = parse_orders_with_llm(raw_orders)

    # store structured LLM outputs in graph state
    state["structured_orders"] = structured_orders

    logging.info("Graph node completed: parsed %d structured orders", len(structured_orders))

    return state

def validate_orders_node(state: OrderAgentState) -> OrderAgentState:
    """
    LangGraph node responsible for validating structured LLM outputs.
    """

    logging.info("Graph node started: validate_orders_node")

    # get structured orders returned by the LLM
    structured_orders = state.get("structured_orders", [])

    # validate required fields, data types, state format, and total values
    validated_orders = validate_orders(structured_orders)

    # store safe validated records in graph state
    state["validated_orders"] = validated_orders

    logging.info("Graph node completed: validated %d orders", len(validated_orders))

    return state


def extract_filters_node(state: OrderAgentState) -> OrderAgentState:
    """
    LangGraph node responsible for extracting deterministic filter rules from user query.
    """

    logging.info("Graph node started: extract_filters_node")

    # get original user request
    user_query = state["user_query"]

    # convert supported natural language conditions into deterministic filter dictionary
    #
    # example:
    # "orders in Ohio over 500"
    #
    # becomes:
    # {"state": "OH", "minimum_total": 500.0}
    filters = extract_filters(user_query)

    # store extracted filters in graph state
    state["filters"] = filters

    logging.info("Graph node completed: extracted filters %s", filters)

    return state


def filter_orders_node(state: OrderAgentState) -> OrderAgentState:
    """
    LangGraph node responsible for applying deterministic filtering logic.
    """

    logging.info("Graph node started: filter_orders_node")

    # get validated orders from validator.py output
    validated_orders = state.get("validated_orders", [])

    # get filter dictionary extracted from user query
    filters = state.get("filters", {})

    # apply deterministic Python filtering
    # this keeps business logic predictable and repeatable
    final_orders = filter_orders(validated_orders, filters)

    # store final matched results in graph state
    state["final_orders"] = final_orders

    logging.info("Graph node completed: filtered down to %d final orders", len(final_orders))

    return state

def build_order_agent_graph():
    """
    Build and compile the LangGraph workflow.

    Returns:
        Compiled LangGraph application that can process a user query end-to-end.
    """

    # create a state graph using our shared state schema
    graph = StateGraph(OrderAgentState)

    # register each workflow step as a named graph node
    graph.add_node("fetch_orders", fetch_orders_node)
    graph.add_node("parse_orders", parse_orders_node)
    graph.add_node("validate_orders", validate_orders_node)
    graph.add_node("extract_filters", extract_filters_node)
    graph.add_node("filter_orders", filter_orders_node)

    # define where the graph starts
    graph.set_entry_point("fetch_orders")

    # connect nodes in a deterministic pipeline
    graph.add_edge("fetch_orders", "parse_orders")
    graph.add_edge("parse_orders", "validate_orders")
    graph.add_edge("validate_orders", "extract_filters")
    graph.add_edge("extract_filters", "filter_orders")

    # after filtering, workflow is complete
    graph.add_edge("filter_orders", END)

    # compile graph into executable app
    return graph.compile()

def run_order_agent(user_query):
    """
    Run the full order-processing agent workflow from a natural language request.

    Args:
        user_query (str):
            Natural language request from user.

    Returns:
        dict:
            Clean JSON-compatible response containing matching orders.
    """

    logging.info("Starting order agent workflow")

    # compile LangGraph app
    app = build_order_agent_graph()

    # initialize graph state
    #
    # each downstream node fills in its corresponding field
    initial_state = {
        "user_query": user_query,
        "raw_orders": [],
        "structured_orders": [],
        "validated_orders": [],
        "filters": {},
        "final_orders": []
    }

    # execute graph from entry point to END
    final_state = app.invoke(initial_state)

    logging.info("Order agent workflow completed")

    # return clean JSON-compatible output required by the assignment
    return {
        "orders": final_state.get("final_orders", [])
    }