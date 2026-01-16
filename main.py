from client.llm_client import LLMClient
import asyncio
import pprint
import click
from typing import List, Dict, Any
from agent.agent import Agent
from agent.events import AgentStreamEventType
from ui.tui import TUI
from ui.tui import get_console
import sys


console = get_console()
class CLI:
    def __init__(self):
      self.agent: Agent | None = None
      self.tui = TUI(console)

    async def run_single(self,message:str)->str | None:
        async with Agent() as agent:
            self.agent = agent
            return await self.process_messages(message)

    async def process_messages(self,message:str)->str | None:
        if not self.agent:
            return None
        
        assistant_streaming = False
        async for event in self.agent.run(message):
            if event.type == AgentStreamEventType.TEXT_DELTA:
                content = event.data.get("content","")
                if not assistant_streaming:
                    self.tui.begin_assistant()
                    assistant_streaming = True
                self.tui.stream_assistant_delta(content)
            elif event.type == AgentStreamEventType.TEXT_COMPLETE:
                final_response = event.data.get("content")
                if assistant_streaming:
                    self.tui.end_assistant()
                    assistant_streaming = False
        return final_response

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
        result = asyncio.run(cli.run_single(prompt))
        if result is None:
            sys.exit(1)


  

main()