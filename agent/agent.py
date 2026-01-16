from __future__ import annotations
from agent.events import AgentEvent
from typing import AsyncGenerator
import pprint
from client import response
from client.llm_client import LLMClient
from client.response import StreamEventType
from agent.events import AgentStreamEventType



class Agent:
    def __init__(self,prompt:str | None = None):
        self.client = LLMClient()
        self.messages = []

        if prompt:
            self.messages.append({"role":"system", "content":prompt})

    async def run(self, prompt: str)->AsyncGenerator[AgentEvent, None]:
        self.messages.append({"role": "user", "content": prompt})
        yield AgentEvent.agent_start(prompt)

        final_response = ""
        async for event in self.agentic_loop():
            yield event
            if event.type == AgentStreamEventType.TEXT_COMPLETE:
                final_response = event.data.get("content")
        if final_response:
             self.messages.append({"role": "assistant", "content": final_response})
        yield AgentEvent.agent_end(final_response)

    async def agentic_loop(self)->AsyncGenerator[AgentEvent, None]:

        #messages = [{"role":"user", "content":"sonic?"}] 
        response_text = "" 


        
        async for event in self.client.chat_completion(self.messages,True):

           if event.type == StreamEventType.TEXT_DELTA:
                if event.text_delta:
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

            await self.client.close()
        
