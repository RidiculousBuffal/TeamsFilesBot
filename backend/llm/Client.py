import os
from typing import Optional

import dotenv
from llama_index.embeddings.openai import OpenAIEmbedding, OpenAIEmbeddingModelType
from openai import OpenAI

dotenv.load_dotenv()


class LLM:
    def __init__(self, model: Optional[str] = None):
        self.model = model if model else 'gpt-4o-mini-2024-07-18'
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"), base_url=os.getenv("OPENAI_BASE_URL"))
        self.embeddingClient = OpenAIEmbedding(api_key=os.getenv('OPENAI_API_KEY'),
                                               api_base=os.getenv('OPENAI_BASE_URL'),
                                               model=OpenAIEmbeddingModelType.TEXT_EMBED_3_SMALL)

    def getClient(self):
        return self.client

    def getCompletion(self, systemPrompt, messages, tools, stream):
        client = self.getClient()
        completion = client.chat.completions.create(
            model=self.model,
            stream=stream,
            messages=[{"role": "system", "content": systemPrompt}] + messages,
            tools=tools,
            parallel_tool_calls=True if tools else None,
        )
        return completion

    def getCompletionAnswerWithNoSysPrompt(self, message):
        client = self.getClient()
        completion = client.chat.completions.create(
            model=self.model,
            stream=False,
            messages=[message],
        )
        return completion.choices[0].message.content

    def getEmbeddingClient(self):
        return self.embeddingClient
