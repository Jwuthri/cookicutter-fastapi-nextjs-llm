"""
Complete LLM Team Example with Agno Framework
==============================================

A production-ready chat application featuring:
- Multi-agent team collaboration
- Persistent Pinecone memory
- Multiple specialized tools
- Human-in-the-loop capabilities
- Real-time chat interface

This example shows how to build a sophisticated AI team that can:
- Research topics (Research Agent)
- Write code (Developer Agent) 
- Review and improve content (QA Agent)
- Coordinate the whole process (Orchestrator Agent)
- Ask humans for help when needed
"""

import asyncio
from typing import Dict, List, Any, Optional, Callable
from datetime import datetime
from enum import Enum

try:
    from agno import Agent, Team
    from agno.memory import HybridMemory, ChatMemory, VectorMemory
    from agno.vector_db import Pinecone
    from agno.storage import RedisStorage
    from agno.tools import (
        WebSearchTool, CodeGeneratorTool, FileOperationsTool, 
        EmailTool, SlackTool, GitHubTool
    )
    from agno.models.openrouter import OpenRouter
    AGNO_AVAILABLE = True
except ImportError:
    AGNO_AVAILABLE = False

from app.models.chat import ChatRequest, ChatResponse, Message
from app.exceptions import ConfigurationError, ExternalServiceError
from app.utils.logging import get_logger

logger = get_logger("llm_team_example")


class AgentRole(str, Enum):
    """Agent roles in the team."""
    ORCHESTRATOR = "orchestrator"
    RESEARCHER = "researcher" 
    DEVELOPER = "developer"
    QA_REVIEWER = "qa_reviewer"
    HUMAN_LIAISON = "human_liaison"


class TaskStatus(str, Enum):
    """Task execution status."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    WAITING_FOR_HUMAN = "waiting_for_human"
    COMPLETED = "completed"
    FAILED = "failed"


class LLMTeamChat:
    """
    Complete LLM Team Chat Application with Agno Framework.
    
    Features:
    - Multi-agent collaboration
    - Persistent memory (Pinecone + Redis)
    - Specialized tools for each agent
    - Human-in-the-loop workflows
    - Real-time chat interface
    - Task coordination and handoffs
    """
    
    def __init__(self, settings: Any):
        if not AGNO_AVAILABLE:
            raise ConfigurationError("Agno package required for LLM team")
        
        self.settings = settings
        self.team: Optional[Team] = None
        self.agents: Dict[str, Agent] = {}
        self.human_callbacks: Dict[str, Callable] = {}
        self.task_history: List[Dict] = []
        self._initialized = False
    
    async def initialize(self):
        """Initialize the complete LLM team with agents, memory, and tools."""
        if self._initialized:
            return
        
        try:
            # Create shared persistent memory
            shared_memory = await self._create_shared_memory()
            
            # Create specialized agents
            self.agents = {
                AgentRole.ORCHESTRATOR: await self._create_orchestrator_agent(shared_memory),
                AgentRole.RESEARCHER: await self._create_researcher_agent(shared_memory),
                AgentRole.DEVELOPER: await self._create_developer_agent(shared_memory),
                AgentRole.QA_REVIEWER: await self._create_qa_agent(shared_memory),
                AgentRole.HUMAN_LIAISON: await self._create_human_liaison_agent(shared_memory)
            }
            
            # Create the team
            self.team = Team(
                agents=list(self.agents.values()),
                
                # Team coordination settings
                leader=self.agents[AgentRole.ORCHESTRATOR],
                collaboration_mode="hierarchical",  # Orchestrator leads
                shared_memory=shared_memory,
                
                # Human-in-the-loop settings
                human_in_loop=True,
                approval_required_for=["code_deployment", "external_api_calls"],
                escalation_triggers=["agent_conflict", "task_timeout", "error_threshold"],
                
                # Performance settings
                max_iterations=10,
                timeout_seconds=300,
                parallel_execution=True
            )
            
            self._initialized = True
            logger.info("LLM Team initialized successfully with 5 agents")
            
        except Exception as e:
            logger.error(f"Failed to initialize LLM team: {e}")
            raise ConfigurationError(f"Team initialization failed: {e}")
    
    async def _create_shared_memory(self) -> HybridMemory:
        """Create shared persistent memory for the team."""
        
        # Pinecone for long-term team knowledge
        pinecone_db = Pinecone(
            api_key=self.settings.get_secret("pinecone_api_key"),
            environment=self.settings.pinecone_environment,
            index_name=self.settings.pinecone_index_name,
            namespace=f"{self.settings.app_name}_team_memory"
        )
        
        # Redis for recent team conversations
        redis_storage = RedisStorage(
            url=self.settings.redis_url,
            key_prefix="team_memory:",
            ttl=60 * 60 * 24 * 7,  # 7 days for team chat
            persistence_config={
                "save": "900 1 300 10 60 10000",
                "appendonly": "yes"
            }
        )
        
        return HybridMemory(
            chat_memory=ChatMemory(
                storage=redis_storage,
                max_messages=1000,
                compress_when_full=True
            ),
            vector_memory=VectorMemory(
                vector_db=pinecone_db,
                max_items=50000,  # Large team knowledge base
                retrieve_count=20,
                auto_save_interval=30
            ),
            
            # Team collaboration settings
            cross_agent_sharing=True,      # Agents can access each other's memory
            context_synthesis=True,        # Combine insights from multiple agents
            knowledge_distillation=True    # Extract key learnings automatically
        )
    
    async def _create_orchestrator_agent(self, memory: HybridMemory) -> Agent:
        """Create the orchestrator agent that coordinates the team."""
        
        # Tools for coordination
        orchestrator_tools = [
            # Team management tools
            await self._create_task_delegation_tool(),
            await self._create_progress_tracking_tool(),
            await self._create_human_escalation_tool(),
            
            # Communication tools  
            SlackTool(webhook_url=self.settings.get_secret("slack_webhook")),
            EmailTool(smtp_config=self._get_email_config()),
        ]
        
        return Agent(
            name="Orchestrator",
            role="Team Leader & Task Coordinator",
            model=OpenRouter(id=self.settings.default_model),
            memory=memory,
            tools=orchestrator_tools,
            
            instructions="""
            You are the Orchestrator Agent, the leader of a specialized AI team.
            
            Your responsibilities:
            1. Understand user requests and break them into tasks
            2. Delegate tasks to appropriate team members
            3. Coordinate between agents and ensure smooth handoffs
            4. Track progress and resolve conflicts
            5. Escalate to humans when needed
            6. Synthesize final results for users
            
            Team members and their specialties:
            - Researcher: Information gathering, analysis, fact-checking
            - Developer: Code generation, architecture, technical solutions
            - QA Reviewer: Quality assurance, testing, improvements
            - Human Liaison: Human communication, approvals, feedback
            
            Always start by understanding the request, then create a plan
            and delegate appropriately. Keep humans informed of progress.
            """,
            
            # Orchestrator-specific settings
            decision_making_authority=True,
            can_delegate_tasks=True,
            escalation_threshold=0.7,
            max_delegation_depth=3
        )
    
    async def _create_researcher_agent(self, memory: HybridMemory) -> Agent:
        """Create the research specialist agent."""
        
        research_tools = [
            WebSearchTool(
                search_engine="google",
                api_key=self.settings.get_secret("google_search_api_key"),
                max_results=10
            ),
            await self._create_fact_checking_tool(),
            await self._create_web_scraping_tool(),
            await self._create_data_analysis_tool(),
        ]
        
        return Agent(
            name="Researcher",
            role="Information Specialist & Analyst",
            model=OpenRouter(id="anthropic/claude-3.5-sonnet"),  # Good for research
            memory=memory,
            tools=research_tools,
            
            instructions="""
            You are the Research Agent, the team's information specialist.
            
            Your expertise includes:
            1. Comprehensive web research and fact-checking
            2. Data analysis and pattern recognition
            3. Market research and competitive analysis
            4. Academic paper analysis and citation
            5. Trend identification and forecasting
            
            Always provide:
            - Well-sourced, factual information
            - Multiple perspectives on topics
            - Confidence levels for your findings
            - Recommendations for further investigation
            
            When uncertain, clearly state limitations and suggest verification.
            Collaborate with other agents by sharing your findings proactively.
            """,
            
            # Research-specific settings
            fact_checking_enabled=True,
            citation_required=True,
            confidence_threshold=0.8,
            source_diversity_requirement=3
        )
    
    async def _create_developer_agent(self, memory: HybridMemory) -> Agent:
        """Create the developer/engineer agent."""
        
        developer_tools = [
            CodeGeneratorTool(
                supported_languages=["python", "javascript", "typescript", "sql"],
                include_tests=True,
                code_review=True
            ),
            GitHubTool(
                token=self.settings.get_secret("github_token"),
                auto_commit=False  # Require human approval
            ),
            FileOperationsTool(
                allowed_paths=["/workspace", "/tmp"],
                read_only=False
            ),
            await self._create_architecture_design_tool(),
            await self._create_code_review_tool(),
        ]
        
        return Agent(
            name="Developer",
            role="Software Engineer & Architect",
            model=OpenRouter(id="openai/gpt-4o"),  # Excellent for coding
            memory=memory,
            tools=developer_tools,
            
            instructions="""
            You are the Developer Agent, the team's technical specialist.
            
            Your capabilities include:
            1. Full-stack software development
            2. System architecture and design
            3. Code review and optimization
            4. Database design and queries
            5. API development and integration
            6. Testing and debugging
            
            Code quality standards:
            - Write clean, documented, testable code
            - Follow best practices and design patterns
            - Include comprehensive error handling
            - Provide clear documentation
            - Consider security and performance
            
            Always collaborate with QA for code review and with
            Researcher for technical requirements gathering.
            """,
            
            # Developer-specific settings
            code_review_required=True,
            test_coverage_minimum=80,
            security_scan_enabled=True,
            documentation_required=True
        )
    
    async def _create_qa_agent(self, memory: HybridMemory) -> Agent:
        """Create the quality assurance agent."""
        
        qa_tools = [
            await self._create_testing_framework_tool(),
            await self._create_code_analysis_tool(),
            await self._create_performance_testing_tool(),
            await self._create_security_audit_tool(),
        ]
        
        return Agent(
            name="QA_Reviewer", 
            role="Quality Assurance & Testing Specialist",
            model=OpenRouter(id="anthropic/claude-3.5-sonnet"),  # Good for analysis
            memory=memory,
            tools=qa_tools,
            
            instructions="""
            You are the QA Agent, ensuring quality and reliability.
            
            Your responsibilities:
            1. Code review and quality assessment
            2. Test design and execution
            3. Performance and security testing
            4. Documentation review
            5. Process improvement recommendations
            
            Quality criteria:
            - Functionality: Does it work as intended?
            - Reliability: Can it handle edge cases?
            - Performance: Is it efficient and scalable?
            - Security: Are there vulnerabilities?
            - Maintainability: Is it clean and documented?
            
            Always provide constructive feedback with specific
            recommendations for improvement.
            """,
            
            # QA-specific settings
            approval_authority=True,
            quality_gates_enabled=True,
            automated_testing=True,
            regression_testing=True
        )
    
    async def _create_human_liaison_agent(self, memory: HybridMemory) -> Agent:
        """Create the human communication agent."""
        
        liaison_tools = [
            await self._create_human_approval_tool(),
            await self._create_feedback_collection_tool(),
            await self._create_status_reporting_tool(),
        ]
        
        return Agent(
            name="Human_Liaison",
            role="Human Communication & Approval Coordinator",
            model=OpenRouter(id="openai/gpt-4o-mini"),  # Fast for communication
            memory=memory,
            tools=liaison_tools,
            
            instructions="""
            You are the Human Liaison Agent, the bridge between AI and humans.
            
            Your role includes:
            1. Translating technical concepts for humans
            2. Collecting human feedback and approvals
            3. Escalating complex decisions to humans
            4. Providing clear status updates
            5. Managing expectations and timelines
            
            Communication principles:
            - Be clear, concise, and jargon-free
            - Provide context and options
            - Respect human time and priorities
            - Follow up appropriately
            - Document decisions and feedback
            
            Always ensure humans are informed and comfortable
            with AI recommendations before proceeding.
            """,
            
            # Human liaison settings
            human_approval_required=True,
            escalation_protocols=True,
            feedback_tracking=True,
            status_reporting_frequency="hourly"
        )
    
    async def process_chat_request(self, request: ChatRequest, user_id: str = None) -> ChatResponse:
        """
        Process a chat request through the LLM team.
        
        This is the main entry point for chat interactions.
        """
        if not self._initialized:
            await self.initialize()
        
        try:
            # Log the request
            task = {
                "id": f"task_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "request": request.message,
                "user_id": user_id,
                "session_id": request.session_id,
                "timestamp": datetime.utcnow().isoformat(),
                "status": TaskStatus.PENDING
            }
            self.task_history.append(task)
            
            # Process through the team
            team_response = await self.team.run(
                message=request.message,
                session_id=request.session_id,
                user_id=user_id,
                
                # Team coordination settings
                require_consensus=False,  # Orchestrator makes decisions
                human_approval_required=self._requires_human_approval(request.message),
                max_agents_involved=5,
                timeout_seconds=300
            )
            
            # Extract the final response
            if hasattr(team_response, 'content'):
                response_content = team_response.content
            elif isinstance(team_response, dict):
                response_content = team_response.get('final_response', str(team_response))
            else:
                response_content = str(team_response)
            
            # Update task status
            task["status"] = TaskStatus.COMPLETED
            task["response"] = response_content
            task["agents_involved"] = [agent.name for agent in team_response.agents_used] if hasattr(team_response, 'agents_used') else []
            
            # Create chat response
            chat_response = ChatResponse(
                message=response_content,
                session_id=request.session_id,
                metadata={
                    "team_collaboration": True,
                    "agents_involved": task["agents_involved"],
                    "task_id": task["id"],
                    "processing_time": (datetime.utcnow() - datetime.fromisoformat(task["timestamp"])).total_seconds(),
                    "human_approval_required": self._requires_human_approval(request.message),
                    "confidence_score": getattr(team_response, 'confidence', 0.9)
                }
            )
            
            logger.info(f"Team processed request for session {request.session_id}")
            return chat_response
            
        except Exception as e:
            logger.error(f"Error processing team request: {e}")
            
            # Update task status
            if 'task' in locals():
                task["status"] = TaskStatus.FAILED
                task["error"] = str(e)
            
            # Return error response
            return ChatResponse(
                message=f"I apologize, but the team encountered an error: {str(e)}. Please try again or contact support.",
                session_id=request.session_id,
                metadata={"error": True, "team_collaboration": True}
            )
    
    def _requires_human_approval(self, message: str) -> bool:
        """Determine if a request requires human approval."""
        approval_keywords = [
            "deploy", "delete", "payment", "purchase", "send email",
            "external api", "database change", "production",
            "critical", "sensitive", "private", "confidential"
        ]
        return any(keyword in message.lower() for keyword in approval_keywords)
    
    async def get_team_status(self) -> Dict[str, Any]:
        """Get current team status and metrics."""
        status = {
            "team_initialized": self._initialized,
            "agents": {},
            "memory_status": {},
            "recent_tasks": self.task_history[-5:],  # Last 5 tasks
            "metrics": {
                "total_tasks": len(self.task_history),
                "completed_tasks": len([t for t in self.task_history if t["status"] == TaskStatus.COMPLETED]),
                "failed_tasks": len([t for t in self.task_history if t["status"] == TaskStatus.FAILED]),
                "average_processing_time": self._calculate_average_processing_time()
            }
        }
        
        # Agent status
        for role, agent in self.agents.items():
            status["agents"][role] = {
                "name": agent.name,
                "model": getattr(agent.model, 'id', 'unknown'),
                "tools_count": len(getattr(agent, 'tools', [])),
                "memory_size": await self._get_agent_memory_size(agent),
                "active": True
            }
        
        # Memory status
        if self.team and hasattr(self.team, 'shared_memory'):
            memory = self.team.shared_memory
            status["memory_status"] = {
                "type": "HybridMemory",
                "chat_messages": await self._get_chat_memory_count(memory),
                "vector_items": await self._get_vector_memory_count(memory),
                "persistent": True
            }
        
        return status
    
    async def request_human_input(self, request: str, context: Dict = None) -> str:
        """Request input from a human for complex decisions."""
        if "human_input" in self.human_callbacks:
            return await self.human_callbacks["human_input"](request, context)
        else:
            # Fallback - could integrate with UI, Slack, email, etc.
            logger.warning(f"Human input requested but no callback configured: {request}")
            return "Human input not available - proceeding with AI decision"
    
    def register_human_callback(self, callback_type: str, callback: Callable):
        """Register callbacks for human interaction."""
        self.human_callbacks[callback_type] = callback
    
    # Tool creation methods (placeholder implementations)
    async def _create_task_delegation_tool(self):
        """Create tool for task delegation between agents."""
        # Implementation would create an Agno tool for task management
        pass
    
    async def _create_progress_tracking_tool(self):
        """Create tool for tracking task progress."""
        pass
    
    async def _create_human_escalation_tool(self):
        """Create tool for escalating to humans."""
        pass
    
    async def _create_fact_checking_tool(self):
        """Create tool for fact-checking information."""
        pass
    
    async def _create_web_scraping_tool(self):
        """Create tool for web scraping."""
        pass
    
    async def _create_data_analysis_tool(self):
        """Create tool for data analysis."""
        pass
    
    async def _create_architecture_design_tool(self):
        """Create tool for software architecture design."""
        pass
    
    async def _create_code_review_tool(self):
        """Create tool for automated code review."""
        pass
    
    async def _create_testing_framework_tool(self):
        """Create tool for test generation and execution."""
        pass
    
    async def _create_code_analysis_tool(self):
        """Create tool for static code analysis."""
        pass
    
    async def _create_performance_testing_tool(self):
        """Create tool for performance testing."""
        pass
    
    async def _create_security_audit_tool(self):
        """Create tool for security auditing."""
        pass
    
    async def _create_human_approval_tool(self):
        """Create tool for requesting human approvals."""
        pass
    
    async def _create_feedback_collection_tool(self):
        """Create tool for collecting human feedback."""
        pass
    
    async def _create_status_reporting_tool(self):
        """Create tool for status reporting."""
        pass
    
    # Helper methods
    def _get_email_config(self) -> Dict:
        """Get email configuration for notifications."""
        return {
            "smtp_server": self.settings.smtp_server,
            "smtp_port": self.settings.smtp_port,
            "username": self.settings.smtp_username,
            "password": self.settings.get_secret("smtp_password")
        }
    
    def _calculate_average_processing_time(self) -> float:
        """Calculate average task processing time."""
        completed_tasks = [t for t in self.task_history if t["status"] == TaskStatus.COMPLETED and "processing_time" in t]
        if not completed_tasks:
            return 0.0
        return sum(t["processing_time"] for t in completed_tasks) / len(completed_tasks)
    
    async def _get_agent_memory_size(self, agent: Agent) -> int:
        """Get memory size for an agent."""
        try:
            if hasattr(agent, 'memory') and hasattr(agent.memory, 'get_size'):
                return await agent.memory.get_size()
            return 0
        except:
            return 0
    
    async def _get_chat_memory_count(self, memory) -> int:
        """Get chat memory message count."""
        try:
            if hasattr(memory, 'chat_memory') and hasattr(memory.chat_memory, 'get_message_count'):
                return await memory.chat_memory.get_message_count()
            return 0
        except:
            return 0
    
    async def _get_vector_memory_count(self, memory) -> int:
        """Get vector memory item count."""
        try:
            if hasattr(memory, 'vector_memory') and hasattr(memory.vector_memory, 'get_item_count'):
                return await memory.vector_memory.get_item_count()
            return 0
        except:
            return 0


# Example usage and integration
class LLMTeamChatService:
    """
    Service wrapper for integrating LLM Team with existing chat infrastructure.
    """
    
    def __init__(self, settings: Any):
        self.settings = settings
        self.team_chat = LLMTeamChat(settings)
    
    async def initialize(self):
        """Initialize the team chat service."""
        await self.team_chat.initialize()
        
        # Register human interaction callbacks
        self.team_chat.register_human_callback("human_input", self._handle_human_input)
        self.team_chat.register_human_callback("approval", self._handle_approval_request)
        
        logger.info("LLM Team Chat Service initialized")
    
    async def process_message(self, request: ChatRequest, user_id: str = None) -> ChatResponse:
        """Process a message through the LLM team."""
        return await self.team_chat.process_chat_request(request, user_id)
    
    async def get_team_status(self) -> Dict[str, Any]:
        """Get team status for monitoring."""
        return await self.team_chat.get_team_status()
    
    async def _handle_human_input(self, request: str, context: Dict = None) -> str:
        """Handle human input requests."""
        # This would integrate with your chat UI, Slack, etc.
        # For now, return a placeholder
        return "Human input received and processed"
    
    async def _handle_approval_request(self, request: str, context: Dict = None) -> bool:
        """Handle approval requests."""
        # This would integrate with your approval workflow
        # For now, auto-approve non-critical requests
        return not any(keyword in request.lower() for keyword in ["delete", "deploy", "payment"])


# Configuration example
def create_team_chat_config(settings) -> Dict[str, Any]:
    """Create configuration for the LLM team chat."""
    return {
        "team_settings": {
            "collaboration_mode": "hierarchical",
            "max_agents": 5,
            "timeout_seconds": 300,
            "human_in_loop": True
        },
        
        "memory_settings": {
            "provider": "hybrid",
            "chat_retention_days": 7,
            "vector_retention_days": 365,
            "auto_backup": True
        },
        
        "tools_settings": {
            "web_search_enabled": True,
            "code_generation_enabled": True,
            "file_operations_enabled": True,
            "external_apis_enabled": True
        },
        
        "human_interaction": {
            "approval_required_for": ["deployments", "external_api_calls", "data_modifications"],
            "escalation_triggers": ["agent_conflict", "task_timeout", "low_confidence"],
            "notification_channels": ["slack", "email", "in_app"]
        }
    }
