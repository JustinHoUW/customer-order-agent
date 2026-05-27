# Customer Order AI Agent

A full-stack customer order processing system that takes natural language order requests, retrieves messy unstructured order records from a dummy customer API, converts them into structured JSON using an LLM extraction pipeline, validates the output, and applies deterministic filtering logic to return clean customer order results.

## Demo

![Customer Order AI Agent Demo](assets/customer_agent_demo.gif)

## What It Does

This project solves a realistic data integration problem: customer systems often return messy or inconsistent order data. Instead of assuming clean structured input, this agent retrieves raw order text, extracts structured fields, validates the output, and filter customer orders based on a natural language request.

Example query:

```text
Show me all orders where the buyer was located in Ohio and total value was over 500.