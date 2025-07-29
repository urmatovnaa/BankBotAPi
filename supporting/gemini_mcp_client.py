import os
from dotenv import load_dotenv
load_dotenv()

import asyncio
from google import genai
from google.genai import types
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

async def main():
    # Configure MCP server parameters
    server_params = StdioServerParameters(
        command="python",
        args=["banking_mcp_server.py"],
        env={}
    )
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            
            # Get tools from MCP server
            mcp_tools = await session.list_tools()
            print(f"Available tools: {[tool.name for tool in mcp_tools.tools]}")
            
            # Convert MCP tools to Gemini format
            tools = [
                types.Tool(
                    function_declarations=[
                        {
                            "name": tool.name,
                            "description": tool.description,
                            "parameters": {
                                k: v
                                for k, v in tool.inputSchema.items()
                                if k not in ["additionalProperties", "$schema"]
                            },
                        }
                    ]
                )
                for tool in mcp_tools.tools
            ]
            
            # Test with a user query
            prompt = "Покажи мой баланс и последние 3 транзакции"
            
            response = client.models.generate_content(
                model="gemini-2.0-flash",
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0,
                    tools=tools,
                ),
            )
            
            print(f"Gemini response: {response}")
            
            # Handle function calls
            for candidate in response.candidates:
                content = candidate.content
                for part in content.parts:
                    if hasattr(part, 'function_call') and part.function_call:
                        print(f"Function call: {part.function_call}")
                        
                        # Call MCP tool
                        result = await session.call_tool(
                            part.function_call.name,
                            arguments=dict(part.function_call.args)
                        )
                        print(f"MCP result: {result}")
                        
                        # You can send the result back to Gemini for further processing
                        # or return it directly to the user
                        return result.content[0].text if result.content else "No result"
                    
                    elif hasattr(part, 'text') and part.text:
                        print(f"Text response: {part.text}")
                        return part.text.strip()
            
            return "No valid response from Gemini"

if __name__ == "__main__":
    result = asyncio.run(main())
    print(f"Final result: {result}") 