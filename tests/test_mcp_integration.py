#!/usr/bin/env python3
"""
Test script to verify MCP integration with the banking chatbot
"""

import asyncio
import os
from dotenv import load_dotenv
load_dotenv()

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def test_mcp_server():
    """Test the MCP server connection and tool calls"""
    print("Testing MCP server connection...")
    
    # Configure MCP server parameters
    server_params = StdioServerParameters(
        command="python",
        args=["banking_mcp_server.py"],
        env={}
    )
    
    try:
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                
                # Get tools from MCP server
                mcp_tools = await session.list_tools()
                print(f"Available tools: {[tool.name for tool in mcp_tools.tools]}")
                
                # Test get_balance tool
                print("\nTesting get_balance tool...")
                result = await session.call_tool("get_balance", arguments={})
                print(f"get_balance result: {result.content[0].text if result.content else 'No result'}")
                
                # Test get_transactions tool
                print("\nTesting get_transactions tool...")
                result = await session.call_tool("get_transactions", arguments={"limit": 3})
                print(f"get_transactions result: {result.content[0].text if result.content else 'No result'}")
                
                # Test get_last_incoming_transaction tool
                print("\nTesting get_last_incoming_transaction tool...")
                result = await session.call_tool("get_last_incoming_transaction", arguments={})
                print(f"get_last_incoming_transaction result: {result.content[0].text if result.content else 'No result'}")
                
                print("\nMCP server test completed successfully!")
                
    except Exception as e:
        print(f"Error testing MCP server: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_mcp_server()) 