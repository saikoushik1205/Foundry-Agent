import os
import asyncio

from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain.agents import create_agent
from langchain_mcp_adapters.client import MultiServerMCPClient


load_dotenv()

google_api_key = os.getenv("GOOGLE_API_KEY")


model = init_chat_model(
    "google_genai:gemini-2.5-flash",
    api_key=google_api_key
)

# ------------------------------------
# System Prompt
# ------------------------------------
SYSTEM_PROMPT = """
You are an intelligent Email Inbox Summarizer Agent.

Responsibilities:
- Read unread Gmail emails.
- Summarize emails.
- Categorize emails into:
    • High Priority
    • Medium Priority
    • Low Priority
- Identify urgent emails.
- Draft professional replies if requested.
- Never fabricate information.
- Be concise and accurate.
"""


client = MultiServerMCPClient(
    {
        "gmail": {
            "transport": "streamable_http",
            "url": "YOUR_MCP_HTTP_ENDPOINT"
        }
    }
)


async def main():

    # Get Gmail tools
    tools = await client.get_tools()

    # Create Agent
    agent = create_agent(
        model=model,
        tools=tools,
        system_prompt=SYSTEM_PROMPT
    )

    # User Query
    response = await agent.ainvoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": "Summarize my unread Gmail emails."
                }
            ]
        }
    )

    print(response)



asyncio.run(main())