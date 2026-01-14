from client.llm_client import LLMClient
import asyncio
import pprint
import click
from typing import List, Dict, Any



async def run(messages: List[Dict[str, Any]]):
    client = LLMClient()
    async for event in client.chat_completion(messages,stream=True):
        pprint.pprint(event)



@click.command()
@click.argument("prompt",required=False)

def main(
    prompt: str | None = None,

):
    print(prompt)
    messages=[{
        "role":"user",
        "content":prompt
    }]
    asyncio.run(run(messages))
    print("done")


if __name__ == "__main__":
    main()