from client.llm_client import LLMClient
import asyncio

async def main():

    client = LLMClient()
    messages=[{
        "role":"user",
        "content":"Are you a thinking model?"
    }]
    await client.chat_completion(messages,stream=False)
    print("done")

if __name__ == "__main__":
    asyncio.run(main())