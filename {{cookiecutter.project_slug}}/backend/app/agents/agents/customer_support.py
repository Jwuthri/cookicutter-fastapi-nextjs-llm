"""Customer support agent using LangChain's create_agent."""
from typing import Optional

from langchain.agents import create_agent
from langchain_core.messages import HumanMessage

from app.agents.prompt.customer_support import SYSTEM_PROMPT
from app.agents.structured_output.customer_support import CustomerSupportResponse
from app.agents.tool.customer_support import CUSTOMER_SUPPORT_TOOLS
from app.infrastructure.langfuse_handler import get_langfuse_config
from app.infrastructure.llm_provider import OpenRouterProvider
from app.utils.logging import get_logger

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
