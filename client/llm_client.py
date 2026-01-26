import asyncio
from openai import AsyncOpenAI, RateLimitError, APIConnectionError, APIError
from typing import List, Dict, Any
from client.response import TextDelta
from client.response import TokenUsage
from client.response import StreamEventType
from client.response import StreamEvent
from typing import AsyncGenerator

class LLMClient:
    def __init__(self,)-> None:
        self.client : AsyncOpenAI | None = None
        self.max_retries:int = 3

#this will return the client if it is not None, otherwise it will create a new client
#using ollama as the llm provider
    def get_client(self)-> AsyncOpenAI:
        if self.client is None:
            self.client = AsyncOpenAI(
                api_key = "olama_api_key",
                base_url = "http://localhost:11434/v1",
            )
        return self.client
    
#this will close the client if it is not None, otherwise it will do nothing
    async def close(self)-> None:
        if self.client is not None:
            await self.client.close()
            self.client = None
    
    async def chat_completion(
        self,
        messages: List[Dict[str, Any]],  #whose message assiatant or user is sending
        stream: bool = True,
    )-> AsyncGenerator[StreamEvent, None]:

    #get the kwargs and client
     client = self.get_client()
     kwargs = {
                "model":"ministral-3:8b-instruct-2512-q4_K_M",
                "messages":messages,
                "stream":stream,
                
            }
    #do this for 3 tries with exponential backof
     for attempt in range(self.max_retries +1):
        try:
            if stream:
                async for event in self.stream_response(client, kwargs):
                    yield event
            else:
                event = await self.non_stream_response(client, kwargs)
                yield event
                return
        except RateLimitError as e:
            if attempt < self.max_retries:
                wait_time = 2 ** attempt
                await asyncio.sleep(wait_time)
            else:
                yield StreamEvent(
                    type=StreamEventType.ERROR,
                    error=str(f"Max retries reached: {e}"),
                )
                return
        except APIConnectionError as e:
            if attempt < self.max_retries:
                wait_time = 2 ** attempt
                await asyncio.sleep(wait_time)
            else:
                yield StreamEvent(
                    type=StreamEventType.ERROR,
                    error=str(f"Connection error: {e}"),
                )
                return
        except APIError as e:

                yield StreamEvent(
                    type=StreamEventType.ERROR,
                    error=str(f"API error: {e}"),
                )
                return
                
                 
        


    #bit by bit showing the response
    async def stream_response(
        self,
        client: AsyncOpenAI, 
        kwargs: Dict[str, Any],
    )-> AsyncGenerator[StreamEvent, None]:


        response = await client.chat.completions.create(**kwargs)

        usage: TokenUsage | None = None
        finish_reason: str | None = None


        async for chunk in response:
            if chunk.usage:
                usage = TokenUsage(
                    prompt_tokens=chunk.usage.prompt_tokens,
                    completion_tokens=chunk.usage.completion_tokens,
                    total_tokens=chunk.usage.total_tokens,
                    cached_tokens=0,
                )
            if not chunk.choices:
                continue
            choice = chunk.choices[0]
            delta = choice.delta
            if choice.finish_reason:
                finish_reason = choice.finish_reason
            if delta.content:
                yield StreamEvent(
                    type=StreamEventType.TEXT_DELTA,
                    text_delta=TextDelta(delta.content),
                )

        yield StreamEvent(
            type=StreamEventType.MESSAGE_COMPLETE,
            finish_reason=finish_reason,
            usage=usage,
        )
    #showing the response all at once
    async def non_stream_response(
        self,
        client: AsyncOpenAI, 
        kwargs: Dict[str, Any],
    )-> StreamEvent:

        response = await client.chat.completions.create(**kwargs)
        print(response)
        choice = response.choices[0]
        message = choice.message

        text_delta = None
        if message.content:
            text_delta = TextDelta(content=message.content)
        
        usage = None
        if response.usage:
            cached = 0
            if response.usage.prompt_tokens_details:
                cached = response.usage.prompt_tokens_details.cached_tokens
            usage = TokenUsage(
                prompt_tokens=response.usage.prompt_tokens,
                completion_tokens=response.usage.completion_tokens,
                total_tokens=response.usage.total_tokens,
                cached_tokens=cached,
            )
      
        
        return StreamEvent(
            type=StreamEventType.MESSAGE_COMPLETE,
            text_delta=text_delta,
            finish_reason=choice.finish_reason,
            usage=usage,
        )