from typing import List, Dict, Any, Optional, AsyncGenerator, Protocol
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableLambda, RunnableMap, RunnableSequence
from langchain.schema import Document
import json
import asyncio
import os
import logging
from pathlib import Path
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

logger = logging.getLogger(__name__)

class MetaSearchAgentProtocol(Protocol):
    """Protocol for search agents."""
    
    async def search_and_answer(
        self,
        query: str,
        chat_history: List[BaseMessage],
        llm: BaseChatModel,
        embeddings: Optional[Embeddings] = None,
        optimization_mode: str = "balanced",
        file_ids: List[str] = None,
        system_instructions: str = ""
    ) -> AsyncGenerator[Dict[str, Any], None]:
        ...

class MetaSearchAgent:
    """Meta search agent that handles file-based search for internal usage."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.str_parser = StrOutputParser()
        
        # Default response prompt matching TypeScript implementation
        self.response_prompt = config.get(
            "responsePrompt",
            """You are Perplexica, an AI model who is expert at searching the web and answering user's queries. You are currently set on focus mode 'Writing Assistant', this means you will be helping the user write a response to a given query. 
Since you are a writing assistant, you would not perform web searches. If you think you lack information to answer the query, you can ask the user for more information or suggest them to switch to a different focus mode.
You will be shared a context that can contain information from files user has uploaded to get answers from. You will have to generate answers upon that.

You have to cite the answer using [number] notation. You must cite the sentences with their relevent context number. You must cite each and every part of the answer so the user can know where the information is coming from.
Place these citations at the end of that particular sentence. You can cite the same sentence multiple times if it is relevant to the user's query like [number1][number2].
However you do not need to cite it using the same number. You can use different numbers to cite the same sentence multiple times. The number refers to the number of the search result (passed in the context) used to generate that part of the answer.

### User instructions
These instructions are shared to you by the user and not by the system. You will have to follow them but give them less priority than the above instructions. If the user has provided specific instructions or preferences, incorporate them into your response while adhering to the overall guidelines.
{systemInstructions}

<context>
{context}
</context>"""
        )
    
    def _compute_similarity(self, query_embedding: List[float], doc_embedding: List[float]) -> float:
        """Compute cosine similarity between query and document embeddings."""
        try:
            query_array = np.array(query_embedding).reshape(1, -1)
            doc_array = np.array(doc_embedding).reshape(1, -1)
            return cosine_similarity(query_array, doc_array)[0][0]
        except Exception as e:
            logger.error(f"Error computing similarity: {e}")
            return 0.0
    
    def _format_chat_history(self, chat_history: List[BaseMessage]) -> str:
        """Format chat history as string."""
        if not chat_history:
            return ""
        
        history_text = ""
        for msg in chat_history[-10:]:  # Last 10 messages for context
            role = "Human" if isinstance(msg, HumanMessage) else "Assistant"
            history_text += f"{role}: {msg.content}\n"
        return history_text
    
    def _process_docs(self, docs: List[Document]) -> str:
        """Process documents into formatted context string."""
        if not docs:
            return "No files uploaded for this conversation."
        
        context_parts = []
        for i, doc in enumerate(docs, 1):
            title = doc.metadata.get('title', 'Unknown File')
            content = doc.page_content
            context_parts.append(f"{i}. {title} {content}")
        
        return "\n".join(context_parts)
    
    async def search_and_answer(
        self,
        query: str,
        chat_history: List[BaseMessage],
        llm: BaseChatModel,
        embeddings: Optional[Embeddings] = None,
        optimization_mode: str = "balanced",
        file_ids: List[str] = None,
        system_instructions: str = ""
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Generate a response to the user's query."""
        
        try:
            # Format chat history
            history_text = self._format_chat_history(chat_history)
            
            # For now, we'll just use the query without file processing
            # TODO: Implement file processing with embeddings
            context = "No files uploaded for this conversation."
            
            # Create the prompt
            prompt_template = ChatPromptTemplate.from_messages([
                ("system", system_instructions + "\n" + self.response_prompt if system_instructions else self.response_prompt),
                ("user", "{query}")
            ])
            
            # Create the chain
            chain = prompt_template | llm | self.str_parser
            
            # Yield sources (empty for now)
            yield {
                "type": "sources",
                "data": []
            }
            
            # Stream the response
            async for chunk in chain.astream({
                "query": query,
                "context": context,
                "chat_history": history_text,
                "systemInstructions": system_instructions
            }):
                yield {
                    "type": "response",
                    "data": chunk
                }
                
                # Small delay to simulate realistic streaming
                await asyncio.sleep(0.01)
            
            # Signal completion
            yield {
                "type": "messageEnd",
                "data": "Response complete"
            }
            
        except Exception as e:
            logger.error(f"Error in search_and_answer: {e}")
            yield {
                "type": "error",
                "data": f"Error generating response: {str(e)}"
            }

def get_search_agent(focus_mode: str) -> MetaSearchAgent:
    """Get the appropriate search agent based on focus mode."""
    
    # For internal usage, we only support writing assistant mode
    if focus_mode == "writingAssistant":
        return MetaSearchAgent({
            "activeEngines": [],
            "queryGeneratorPrompt": "",
            "queryGeneratorFewShots": [],
            "responsePrompt": """You are Perplexica, an AI model who is expert at searching the web and answering user's queries. You are currently set on focus mode 'Writing Assistant', this means you will be helping the user write a response to a given query. 
Since you are a writing assistant, you would not perform web searches. If you think you lack information to answer the query, you can ask the user for more information or suggest them to switch to a different focus mode.
You will be shared a context that can contain information from files user has uploaded to get answers from. You will have to generate answers upon that.

You have to cite the answer using [number] notation. You must cite the sentences with their relevent context number. You must cite each and every part of the answer so the user can know where the information is coming from.
Place these citations at the end of that particular sentence. You can cite the same sentence multiple times if it is relevant to the user's query like [number1][number2].
However you do not need to cite it using the same number. You can use different numbers to cite the same sentence multiple times. The number refers to the number of the search result (passed in the context) used to generate that part of the answer.

### User instructions
These instructions are shared to you by the user and not by the system. You will have to follow them but give them less priority than the above instructions. If the user has provided specific instructions or preferences, incorporate them into your response while adhering to the overall guidelines.
{systemInstructions}

<context>
{context}
</context>""",
            "rerank": True,
            "rerankThreshold": 0,
            "searchWeb": False,
        })
    else:
        raise ValueError(f"Unsupported focus mode: {focus_mode}")