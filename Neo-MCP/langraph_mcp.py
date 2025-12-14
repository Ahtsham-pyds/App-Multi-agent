import asyncio
import os
from typing import Any

from dotenv import load_dotenv
from langchain_core.messages import AnyMessage
from langchain_core.messages.utils import count_tokens_approximately, trim_messages
from langchain_core.tools import StructuredTool
from langchain_mcp_adapters.tools import load_mcp_tools
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.prebuilt import create_react_agent
from langchain.agents import create_agent
from langgraph.prebuilt.chat_agent_executor import AgentState

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from neo4j import GraphDatabase, RoutingControl
from pydantic import BaseModel, Field

if load_dotenv():
    print("Loaded .env file")
else:
    print("No .env file found")