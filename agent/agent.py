from __future__ import annotations
from agent.events import AgentEvent
from typing import AsyncGenerator
import pprint
from client import response
from client.llm_client import LLMClient
from client.response import StreamEventType
from agent.events import AgentEventType



class Agent:
    def __init__(self):
        self.client = LLMClient()

    async def run(self, messages: str)->AsyncGenerator[AgentEvent, None]:
        yield AgentEvent.agent_start(messages)

        async for event in self.agentic_loop():
            yield event
            if event.type == AgentEventType.TEXT_COMPLETE:
                final_response = event.data.get("content")

        yield AgentEvent.agent_end(final_response)

    async def agentic_loop(self)->AsyncGenerator[AgentEvent, None]:

        response_text = "" 

        messages = [{"role":"user", "content":"Hello, how are you?"}] 

        client = LLMClient()
        async for event in client.chat_completion(self.messages,stream=True):

           if event.type == StreamEventType.TEXT_DELTA:
             content = event.text_delta.content
             response_text += content
             yield AgentEvent.text_delta(content)
           elif event.type == StreamEventType.ERROR:
             yield AgentEvent.agent_error(
                event.error or "Unknown error occurred",
                )
        if response_text:
            yield AgentEvent.text_complete(response_text)

        async def __aenter__(self)->Agent:
            return self

        async def __aexit__(
            self, 
            exc_type, 
            exc_value, 
            exc_traceback,
         )->None:


            if self.client:
                await self.client.close()
                self.client = None

