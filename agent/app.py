import asyncio
import json
import os

from mcp import Resource
from mcp.types import Prompt

from mcp_client import MCPClient
from dial_client import DialClient
from models.message import Message, Role
from prompts import SYSTEM_PROMPT


# https://remote.mcpservers.org/fetch/mcp
# Pay attention that `fetch` doesn't have resources and prompts

async def main():
    async with MCPClient(mcp_server_url="http://localhost:8005/mcp") as mcp_client:
        # Get available MCP resources and print them
        resources = await mcp_client.get_resources()
        print(f"\n📦 Available MCP Resources: {resources}\n")

        # Get available MCP tools and print them
        tools = await mcp_client.get_tools()
        print(f"🔧 Available MCP Tools:")
        for tool in tools:
            print(f"  - {tool['function']['name']}: {tool['function']['description']}")
        print()

        # Create DialClient
        api_key = os.getenv("DIAL_API_KEY", "")
        endpoint = os.getenv("DIAL_ENDPOINT", "")
        dial_client = DialClient(api_key=api_key, endpoint=endpoint, tools=tools, mcp_client=mcp_client)

        # Create message list with system prompt
        messages: list[Message] = [
            Message(role=Role.SYSTEM, content=SYSTEM_PROMPT)
        ]

        # Add MCP prompts as User messages
        prompts = await mcp_client.get_prompts()
        for prompt in prompts:
            prompt_content = await mcp_client.get_prompt(prompt.name)
            if prompt_content.strip():
                messages.append(Message(role=Role.USER, content=prompt_content))

        # Console chat loop
        print("💬 User Management Agent is ready! Type 'exit' or 'quit' to leave.\n")
        while True:
            user_input = input("👤: ").strip()
            if user_input.lower() in ("exit", "quit"):
                print("Goodbye!")
                break
            if not user_input:
                continue

            messages.append(Message(role=Role.USER, content=user_input))
            ai_message = await dial_client.get_completion(messages)
            messages.append(ai_message)


if __name__ == "__main__":
    asyncio.run(main())
