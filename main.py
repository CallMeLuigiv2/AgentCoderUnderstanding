from client.llm_client import LLMClient
import asyncio
import pprint
import click
from typing import List, Dict, Any
from agent.agent import Agent
from agent.events import AgentEventType

class CLI:
    def __init__(self):
      self.agent = Agent | None = None

    async def run_single(self,message:str):
        async with Agent() as agent:
            self.agent = agent
            self.process_messages(message)

    async def process_messages(self,message:str)->str | None:
        if not self.agent:
            return None
        async for event in self.agent.run(message):
            if event.type == AgentEventType.TEXT_DELTA:
                content = event.data.get("content","")
                


@click.command()
@click.argument("prompt",required=False)

def main(
    prompt: str | None = None,

):
    cli = CLI()
   # messages=[{
   #     "role":"user",
   #     "content":prompt
   # }]
    if prompt:
        asyncio.run(cli.run_single(prompt))

  
if __name__ == "__main__":
    main()