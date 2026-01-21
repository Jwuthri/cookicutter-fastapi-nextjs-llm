"""Customer support agent using LangChain's create_agent."""
import json
from typing import AsyncGenerator, Callable, Optional

from langchain.agents import create_agent
from langchain_core.messages import AIMessage, HumanMessage

from app.agents.prompt.customer_support import SYSTEM_PROMPT
from app.agents.structured_output.customer_support import CustomerSupportResponse
from app.agents.tool.customer_support import CUSTOMER_SUPPORT_TOOLS
from app.infrastructure.langfuse_handler import get_langfuse_config
from app.infrastructure.llm_provider import OpenRouterProvider
from app.utils.logging import get_logger
from app.utils.structured_streaming import StructuredStreamingHandler

logger = get_logger("customer_support_agent")


class CustomerSupportAgent:
    """
    Customer support agent using LangChain's create_agent.
    
    This agent handles customer inquiries, provides helpful responses,
    and can escalate issues when necessary.
    """

    def __init__(
        self,
        llm_provider: OpenRouterProvider,
        model_name: str = "openai/gpt-4o-mini",
        temperature: float = 0.7,
    ):
        """
        Initialize customer support agent.

        Args:
            llm_provider: OpenRouter provider instance
            model_name: Model name for the agent
            temperature: Model temperature (default: 0.7)
        """
        self.llm_provider = llm_provider
        self.model_name = model_name
        self.temperature = temperature

        # Get LLM instance (Langfuse automatically enabled if configured)
        self.llm = llm_provider.get_llm(
            model_name=model_name,
            temperature=temperature
        )

        # Create agent with structured output and tools
        self.agent = create_agent(
            model=self.llm,
            system_prompt=SYSTEM_PROMPT,
            tools=CUSTOMER_SUPPORT_TOOLS,
            response_format=CustomerSupportResponse,
        )

        logger.info(f"[CustomerSupportAgent] Initialized with model: {model_name}")

    async def handle_inquiry(
        self,
        customer_message: str,
        customer_id: Optional[str] = None,
        session_id: Optional[str] = None,
        tags: Optional[list[str]] = None,
        metadata: Optional[dict] = None,
    ) -> CustomerSupportResponse:
        """
        Handle a customer inquiry.

        Args:
            customer_message: The customer's message or question
            customer_id: Optional customer ID for tracking
            session_id: Optional session ID for grouping related conversations
            tags: Optional tags for filtering in Langfuse
            metadata: Optional metadata for additional context

        Returns:
            CustomerSupportResponse with structured response
        """
        # Build Langfuse config with filtering attributes
        langfuse_config = get_langfuse_config(
            session_id=session_id,
            user_id=customer_id,
            tags=tags or ["customer-support"],
            metadata={
                "agent_type": "customer_support",
                "model": self.model_name,
                **(metadata or {})
            },
            run_name="customer-support-inquiry"
        )

        # Invoke agent with Langfuse config
        result = await self.agent.ainvoke(
            {"messages": [HumanMessage(content=customer_message)]},
            config=langfuse_config
        )

        # Extract structured response with error handling
        try:
            if isinstance(result, dict) and "structured_response" in result:
                response = result["structured_response"]
                
                # If it's already a CustomerSupportResponse instance, return as is
                if isinstance(response, CustomerSupportResponse):
                    support_response = response
                elif isinstance(response, dict):
                    # Convert dict to Pydantic model
                    support_response = CustomerSupportResponse(**response)
                else:
                    # Fallback for unexpected types
                    logger.warning(f"[CustomerSupportAgent] Unexpected response type: {type(response)}")
                    raise ValueError(f"Unexpected response type: {type(response)}")
                
                logger.info(
                    f"[CustomerSupportAgent] Response generated - "
                    f"Escalation: {support_response.requires_escalation}, "
                    f"Confidence: {support_response.confidence:.2f}"
                )
                
                return support_response
            else:
                # Fallback if structured response not available
                raise ValueError("Structured response not found in result")
        except Exception as e:
            # Fallback on any error
            logger.warning(f"[CustomerSupportAgent] Error processing response: {e}")
            return CustomerSupportResponse(
                response=str(result),
                sentiment="neutral",
                requires_escalation=False,
                confidence=0.5
            )

    async def handle_inquiry_stream(
        self,
        customer_message: str,
        customer_id: Optional[str] = None,
        session_id: Optional[str] = None,
        tags: Optional[list[str]] = None,
        metadata: Optional[dict] = None,
    ) -> AsyncGenerator[CustomerSupportResponse, None]:
        """
        Handle a customer inquiry with streaming structured output.
        
        Yields incremental CustomerSupportResponse updates as fields arrive.
        Fields update incrementally:
        - response: grows character by character
        - suggested_actions: list extends as items arrive
        - confidence, sentiment, requires_escalation: update when determined
        
        Args:
            customer_message: The customer's message or question
            customer_id: Optional customer ID for tracking
            session_id: Optional session ID for grouping related conversations
            tags: Optional tags for filtering in Langfuse
            metadata: Optional metadata for additional context
            
        Yields:
            CustomerSupportResponse instances with incremental updates
        """
        # Build Langfuse config
        langfuse_config = get_langfuse_config(
            session_id=session_id,
            user_id=customer_id,
            tags=tags or ["customer-support", "streaming"],
            metadata={
                "agent_type": "customer_support",
                "model": self.model_name,
                "streaming": True,
                **(metadata or {})
            },
            run_name="customer-support-inquiry-stream"
        )
        
        # Initialize streaming handler (tracks changes internally, Agno-style)
        handler = StructuredStreamingHandler(CustomerSupportResponse)
        last_yielded: Optional[CustomerSupportResponse] = None
        
        try:
            # Stream agent response
            async for chunk in self.agent.astream(
                {"messages": [HumanMessage(content=customer_message)]},
                config=langfuse_config
            ):
                # Extract content from chunk
                content_chunk = self._extract_content_from_chunk(chunk)
                
                if content_chunk:
                    # Add chunk and get incremental update
                    # handler.add_chunk() only returns a value if data changed (Agno's approach)
                    incremental_update = handler.add_chunk(content_chunk)
                    
                    if incremental_update is not None:
                        # Yield the update (handler already ensures it's different from its last return)
                        last_yielded = incremental_update
                        yield incremental_update
            
            # Yield final response if we have one and haven't yielded it yet
            final_response = handler.get_last_valid()
            if final_response is not None:
                # Only yield if different from what we last yielded
                # (handler tracks internally, but we track what we actually yielded)
                if (
                    last_yielded is None
                    or final_response.model_dump() != last_yielded.model_dump()
                ):
                    yield final_response
            elif last_yielded is None:
                # Fallback: yield a basic response if nothing was parsed
                logger.warning(
                    "[CustomerSupportAgent] No valid structured response parsed from stream"
                )
                yield CustomerSupportResponse(
                    response="",
                    sentiment="neutral",
                    requires_escalation=False,
                    confidence=0.5
                )
        except Exception as e:
            logger.error(f"[CustomerSupportAgent] Error in streaming: {e}")
            # Yield fallback response
            yield CustomerSupportResponse(
                response="",
                sentiment="neutral",
                requires_escalation=False,
                confidence=0.5
            )

    async def handle_inquiry_stream_with_callback(
        self,
        customer_message: str,
        callback: Callable[[CustomerSupportResponse], None],
        customer_id: Optional[str] = None,
        session_id: Optional[str] = None,
        tags: Optional[list[str]] = None,
        metadata: Optional[dict] = None,
    ) -> CustomerSupportResponse:
        """
        Handle a customer inquiry with streaming structured output using callback.
        
        Calls the callback function with incremental CustomerSupportResponse updates
        as fields arrive. Returns the final complete response.
        
        Args:
            customer_message: The customer's message or question
            callback: Function to call with each incremental update
            customer_id: Optional customer ID for tracking
            session_id: Optional session ID for grouping related conversations
            tags: Optional tags for filtering in Langfuse
            metadata: Optional metadata for additional context
            
        Returns:
            Final complete CustomerSupportResponse
        """
        final_response: Optional[CustomerSupportResponse] = None
        
        async for partial_response in self.handle_inquiry_stream(
            customer_message=customer_message,
            customer_id=customer_id,
            session_id=session_id,
            tags=tags,
            metadata=metadata,
        ):
            callback(partial_response)
            final_response = partial_response
        
        # Return final response or fallback
        if final_response is None:
            logger.warning(
                "[CustomerSupportAgent] No response received from stream"
            )
            final_response = CustomerSupportResponse(
                response="",
                sentiment="neutral",
                requires_escalation=False,
                confidence=0.5
            )
        
        return final_response

    def _extract_content_from_chunk(self, chunk: dict) -> str:
        """
        Extract content string from LangChain streaming chunk.
        
        Prioritizes raw JSON content for incremental parsing (Agno-style).
        Handles different chunk formats:
        - Raw content from AIMessage (preferred for streaming)
        - Chunks with "structured_response" key (fallback)
        - Direct string content
        
        Args:
            chunk: Streaming chunk from LangChain agent
            
        Returns:
            Extracted content string (raw JSON preferred)
        """
        # Priority 1: Try messages for raw content (best for streaming)
        if isinstance(chunk, dict):
            if "messages" in chunk:
                messages = chunk["messages"]
                if isinstance(messages, list) and len(messages) > 0:
                    last_message = messages[-1]
                    if isinstance(last_message, AIMessage):
                        content = last_message.content
                        if isinstance(content, str):
                            # Raw string content (preferred for incremental parsing)
                            return content
                        elif isinstance(content, list):
                            # Handle content blocks (e.g., from OpenAI)
                            text_parts = []
                            for block in content:
                                if isinstance(block, dict) and "text" in block:
                                    text_parts.append(block["text"])
                                elif isinstance(block, str):
                                    text_parts.append(block)
                            return "".join(text_parts)
            
            # Priority 2: Try direct content keys (raw content)
            for key in ["content", "text", "response"]:
                if key in chunk:
                    value = chunk[key]
                    if isinstance(value, str):
                        return value
            
            # Priority 3: Try structured_response (fallback - already parsed)
            if "structured_response" in chunk:
                structured = chunk["structured_response"]
                if isinstance(structured, CustomerSupportResponse):
                    # Convert BaseModel to JSON string for parsing
                    return structured.model_dump_json()
                elif isinstance(structured, dict):
                    return json.dumps(structured)
                elif isinstance(structured, str):
                    return structured
        
        # Fallback: convert to string
        if isinstance(chunk, str):
            return chunk
        
        return ""

    def handle_inquiry_sync(
        self,
        customer_message: str,
        customer_id: Optional[str] = None,
        session_id: Optional[str] = None,
        tags: Optional[list[str]] = None,
        metadata: Optional[dict] = None,
    ) -> CustomerSupportResponse:
        """
        Handle a customer inquiry synchronously.

        Args:
            customer_message: The customer's message or question
            customer_id: Optional customer ID for tracking
            session_id: Optional session ID for grouping related conversations
            tags: Optional tags for filtering in Langfuse
            metadata: Optional metadata for additional context

        Returns:
            CustomerSupportResponse with structured response
        """
        # Build Langfuse config
        langfuse_config = get_langfuse_config(
            session_id=session_id,
            user_id=customer_id,
            tags=tags or ["customer-support"],
            metadata={
                "agent_type": "customer_support",
                "model": self.model_name,
                **(metadata or {})
            },
            run_name="customer-support-inquiry"
        )

        # Invoke agent synchronously
        result = self.agent.invoke(
            {"messages": [HumanMessage(content=customer_message)]},
            config=langfuse_config
        )

        # Extract structured response with error handling
        try:
            if isinstance(result, dict) and "structured_response" in result:
                response = result["structured_response"]
                
                # If it's already a CustomerSupportResponse instance, return as is
                if isinstance(response, CustomerSupportResponse):
                    return response
                elif isinstance(response, dict):
                    # Convert dict to Pydantic model
                    return CustomerSupportResponse(**response)
                else:
                    # Fallback for unexpected types
                    raise ValueError(f"Unexpected response type: {type(response)}")
            else:
                # Fallback if structured response not available
                raise ValueError("Structured response not found in result")
        except Exception as e:
            # Fallback on any error
            logger.warning(f"[CustomerSupportAgent] Error processing response: {e}")
            return CustomerSupportResponse(
                response=str(result),
                sentiment="neutral",
                requires_escalation=False,
                confidence=0.5
            )
