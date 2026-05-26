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

# original natural language request from the user
user_query: str

# raw unstructured order strings fetched from the customer API
raw_orders: List[str]