from fastmcp import Client
import asyncio

client = Client("./server.py")

async def main():
    async with client:
        tools = await client.list_tools()
        print(tools)

if __name__ == "__main__":
    asyncio.run(main())