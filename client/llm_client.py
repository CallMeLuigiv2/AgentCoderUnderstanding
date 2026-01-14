from openai import AsyncOpenAI
from typing import List, Dict, Any

class LLMClient:
    def __init__(self,)-> None:
        self.client : AsyncOpenAI | None = None

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
    ):
        kwargs = {
            "model":"ministral-3:8b-instruct-2512-q4_K_M",
            "messages":messages,
            "stream":stream,
        }
        client = self.get_client()
        
        if stream:
           await self.stream_response()
        else:
           await self.non_stream_response(client, kwargs)

    #this is loading the response
    async def stream_response(self):
        pass
    #this is giving the response
    async def non_stream_response(
        self,
        client: AsyncOpenAI, 
        kwargs: Dict[str, Any],
    ):

        response = await client.chat.completions.create(**kwargs)
        print(response)
        choice = response.choices[0]
        message = choice.message

        text = None
        if message.content:
            text = message.cont

    