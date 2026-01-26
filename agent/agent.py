from __future__ import annotations
from agent.events import AgentEvent
from typing import AsyncGenerator
import pprint
from client import response
from client.llm_client import LLMClient
from client.response import StreamEventType
from agent.events import AgentStreamEventType
from context.manager import ContextManager



class Agent:
    def __init__(self,prompt:str | None = None):
        self.client = LLMClient()
        self.context_manager = ContextManager()

        if prompt:
            self.context_manager.add_system_message(prompt)

    async def run(self, prompt: str)->AsyncGenerator[AgentEvent, None]:
        yield AgentEvent.agent_start(prompt)
        self.context_manager.add_user_message(prompt)
  

        final_response:str | None = None
        async for event in self.agentic_loop():
            yield event
            if event.type == AgentStreamEventType.TEXT_COMPLETE:
                final_response = event.data.get("content")
        if final_response:
             self.context_manager.add_assistant_message(final_response)
        yield AgentEvent.agent_end(final_response)

    async def agentic_loop(self)->AsyncGenerator[AgentEvent, None]:

        response_text = "" 


        
        async for event in self.client.chat_completion(
            self.context_manager.get_messages(),
            True
            ):

           if event.type == StreamEventType.TEXT_DELTA:
                if event.text_delta:
                    content = event.text_delta.content
                    response_text += content
                    yield AgentEvent.text_delta(content)

           elif event.type == StreamEventType.ERROR:
             yield AgentEvent.agent_error(
                event.error or "Unknown error occurred",
                )
             return
        self.context_manager.add_assistant_message(
            response_text or None,
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
        
