"""
LLM Team Chat Usage Examples
============================

Complete examples showing how to use the LLM team for various scenarios.
These examples demonstrate the power of multi-agent collaboration with
persistent memory, specialized tools, and human-in-the-loop workflows.
"""

import asyncio
from typing import Dict, Any
from datetime import datetime

from app.agents.llm_team_example import LLMTeamChatService
from app.models.chat import ChatRequest, ChatResponse
from app.config import get_settings
from app.utils.logging import get_logger

logger = get_logger("team_chat_examples")


class TeamChatExamples:
    """
    Comprehensive examples of using the LLM team for different scenarios.
    """
    
    def __init__(self):
        self.settings = get_settings()
        self.team_service = LLMTeamChatService(self.settings)
        self.session_id = f"example_session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    async def initialize(self):
        """Initialize the team service."""
        await self.team_service.initialize()
        logger.info("Team chat examples initialized")
    
    async def example_1_research_and_analysis(self):
        """
        Example 1: Research and Analysis
        
        Shows how the team handles research requests with the Researcher agent
        gathering information and the Orchestrator coordinating the response.
        """
        print("\n🔍 Example 1: Research and Analysis")
        print("=" * 50)
        
        request = ChatRequest(
            message="""
            Research the latest developments in AI agents and multi-agent systems. 
            I need a comprehensive overview of:
            1. Current state of the technology
            2. Key players and frameworks
            3. Business applications and use cases
            4. Future trends and predictions
            
            Please provide sources and confidence levels for your findings.
            """,
            session_id=self.session_id,
            metadata={"example": "research_analysis", "priority": "high"}
        )
        
        print(f"🤖 User Request: {request.message[:100]}...")
        
        # Process through team
        response = await self.team_service.process_message(request, "example_user_1")
        
        print(f"\n✅ Team Response:")
        print(f"Agents Involved: {response.metadata.get('agents_involved', [])}")
        print(f"Processing Time: {response.metadata.get('processing_time', 0):.2f}s")
        print(f"Confidence Score: {response.metadata.get('confidence_score', 0):.2f}")
        print(f"\nResponse: {response.message[:500]}...")
        
        return response
    
    async def example_2_software_development(self):
        """
        Example 2: Software Development
        
        Shows how the Developer and QA agents collaborate to create
        and review code with proper testing and documentation.
        """
        print("\n💻 Example 2: Software Development")
        print("=" * 50)
        
        request = ChatRequest(
            message="""
            Create a Python FastAPI endpoint for user authentication that:
            1. Accepts email and password
            2. Validates credentials against a database
            3. Returns a JWT token on success
            4. Includes proper error handling and security measures
            5. Has comprehensive tests
            
            Please follow best practices for security and code quality.
            """,
            session_id=self.session_id,
            metadata={"example": "software_development", "requires_review": True}
        )
        
        print(f"🤖 User Request: {request.message[:100]}...")
        
        response = await self.team_service.process_message(request, "example_user_2")
        
        print(f"\n✅ Team Response:")
        print(f"Agents Involved: {response.metadata.get('agents_involved', [])}")
        print(f"Human Approval Required: {response.metadata.get('human_approval_required', False)}")
        print(f"\nResponse: {response.message[:500]}...")
        
        return response
    
    async def example_3_multi_step_project(self):
        """
        Example 3: Multi-step Project
        
        Shows how the team handles complex projects requiring coordination
        between multiple agents and handoffs between different expertise areas.
        """
        print("\n🚀 Example 3: Multi-step Project")
        print("=" * 50)
        
        request = ChatRequest(
            message="""
            I want to build a recommendation system for an e-commerce platform.
            
            Please:
            1. Research different recommendation algorithms and approaches
            2. Design the system architecture
            3. Create the database schema
            4. Implement the core recommendation engine
            5. Add API endpoints for integration
            6. Include testing and performance optimization
            
            This needs to handle millions of products and users.
            """,
            session_id=self.session_id,
            metadata={"example": "multi_step_project", "complexity": "high"}
        )
        
        print(f"🤖 User Request: {request.message[:100]}...")
        
        response = await self.team_service.process_message(request, "example_user_3")
        
        print(f"\n✅ Team Response:")
        print(f"Agents Involved: {response.metadata.get('agents_involved', [])}")
        print(f"Task ID: {response.metadata.get('task_id')}")
        print(f"\nResponse: {response.message[:500]}...")
        
        return response
    
    async def example_4_human_in_loop(self):
        """
        Example 4: Human-in-the-Loop
        
        Shows how the team handles requests that require human approval
        or input, such as deployments, external API calls, or sensitive operations.
        """
        print("\n👥 Example 4: Human-in-the-Loop")
        print("=" * 50)
        
        request = ChatRequest(
            message="""
            Deploy the new user authentication system to production.
            
            Before deploying:
            1. Run all tests and security scans
            2. Create a deployment checklist
            3. Prepare rollback procedures
            4. Send notification to the team
            5. Get approval from the team lead
            
            Once approved, proceed with the deployment.
            """,
            session_id=self.session_id,
            metadata={"example": "human_in_loop", "requires_approval": True}
        )
        
        print(f"🤖 User Request: {request.message[:100]}...")
        
        # This will trigger human approval workflow
        response = await self.team_service.process_message(request, "example_user_4")
        
        print(f"\n✅ Team Response:")
        print(f"Human Approval Required: {response.metadata.get('human_approval_required', False)}")
        print(f"Agents Involved: {response.metadata.get('agents_involved', [])}")
        print(f"\nResponse: {response.message[:500]}...")
        
        return response
    
    async def example_5_memory_and_context(self):
        """
        Example 5: Memory and Context
        
        Shows how the team uses persistent memory to maintain context
        across conversations and build on previous interactions.
        """
        print("\n🧠 Example 5: Memory and Context")
        print("=" * 50)
        
        # First message - establish context
        request1 = ChatRequest(
            message="""
            I'm building a social media analytics platform. We need to track
            engagement metrics, sentiment analysis, and trend detection.
            Can you help me design the overall architecture?
            """,
            session_id=self.session_id,
            metadata={"example": "memory_context", "conversation_part": 1}
        )
        
        print(f"🤖 User Request 1: {request1.message[:100]}...")
        response1 = await self.team_service.process_message(request1, "example_user_5")
        print(f"✅ Response 1: {response1.message[:200]}...")
        
        # Wait a moment to simulate conversation flow
        await asyncio.sleep(1)
        
        # Second message - build on previous context
        request2 = ChatRequest(
            message="""
            Great! Now focusing on the sentiment analysis component you mentioned,
            can you implement the core sentiment analysis service with real-time
            processing capabilities? Remember our platform needs to handle
            high-volume social media data.
            """,
            session_id=self.session_id,  # Same session
            metadata={"example": "memory_context", "conversation_part": 2}
        )
        
        print(f"\n🤖 User Request 2: {request2.message[:100]}...")
        response2 = await self.team_service.process_message(request2, "example_user_5")
        
        print(f"\n✅ Team Response (with context):")
        print(f"Agents Involved: {response2.metadata.get('agents_involved', [])}")
        print(f"Context Maintained: The team remembers the social media analytics platform!")
        print(f"\nResponse: {response2.message[:500]}...")
        
        return response1, response2
    
    async def example_6_tool_usage(self):
        """
        Example 6: Specialized Tool Usage
        
        Shows how different agents use their specialized tools
        for web search, code generation, file operations, etc.
        """
        print("\n🛠️ Example 6: Specialized Tool Usage")
        print("=" * 50)
        
        request = ChatRequest(
            message="""
            I need to analyze the GitHub repository for FastAPI to understand
            its architecture and recent changes. Please:
            
            1. Search for recent FastAPI updates and releases
            2. Examine the repository structure and key files
            3. Analyze the code quality and testing practices
            4. Create a summary report with insights
            
            Use appropriate tools for web research and code analysis.
            """,
            session_id=self.session_id,
            metadata={"example": "tool_usage", "tools_required": ["web_search", "github", "code_analysis"]}
        )
        
        print(f"🤖 User Request: {request.message[:100]}...")
        
        response = await self.team_service.process_message(request, "example_user_6")
        
        print(f"\n✅ Team Response (with tools):")
        print(f"Agents Involved: {response.metadata.get('agents_involved', [])}")
        print(f"Tools Used: Web search, GitHub API, code analysis")
        print(f"\nResponse: {response.message[:500]}...")
        
        return response
    
    async def run_all_examples(self):
        """Run all examples in sequence."""
        print("🎯 Running All LLM Team Examples")
        print("=" * 60)
        
        await self.initialize()
        
        try:
            # Run examples
            await self.example_1_research_and_analysis()
            await self.example_2_software_development()
            await self.example_3_multi_step_project()
            await self.example_4_human_in_loop()
            await self.example_5_memory_and_context()
            await self.example_6_tool_usage()
            
            # Show final team status
            await self.show_team_status()
            
        except Exception as e:
            logger.error(f"Error running examples: {e}")
            print(f"\n❌ Error: {e}")
    
    async def show_team_status(self):
        """Show final team status and metrics."""
        print("\n📊 Final Team Status")
        print("=" * 30)
        
        status = await self.team_service.get_team_status()
        
        print(f"Team Initialized: {status['team_initialized']}")
        print(f"Total Tasks Processed: {status['metrics']['total_tasks']}")
        print(f"Completed Tasks: {status['metrics']['completed_tasks']}")
        print(f"Average Processing Time: {status['metrics']['average_processing_time']:.2f}s")
        
        print(f"\nAgent Status:")
        for role, agent in status['agents'].items():
            print(f"  {role}: {agent['name']} ({agent['tools_count']} tools)")
        
        print(f"\nMemory Status:")
        memory = status['memory_status']
        print(f"  Type: {memory.get('type', 'Unknown')}")
        print(f"  Chat Messages: {memory.get('chat_messages', 0)}")
        print(f"  Vector Items: {memory.get('vector_items', 0)}")
        print(f"  Persistent: {memory.get('persistent', False)}")


# Simple usage example
async def simple_team_chat_example():
    """
    Simple example showing basic team chat usage.
    Perfect for getting started quickly.
    """
    print("🚀 Simple Team Chat Example")
    print("=" * 40)
    
    # Initialize team
    settings = get_settings()
    team_service = LLMTeamChatService(settings)
    await team_service.initialize()
    
    # Send a simple request
    request = ChatRequest(
        message="Help me create a simple REST API for a todo app with authentication",
        session_id="simple_example",
        metadata={"priority": "normal"}
    )
    
    print(f"💬 Request: {request.message}")
    
    # Get team response
    response = await team_service.process_message(request, "simple_user")
    
    print(f"\n🤖 Team Response:")
    print(f"Agents: {response.metadata.get('agents_involved', [])}")
    print(f"Time: {response.metadata.get('processing_time', 0):.2f}s")
    print(f"\n{response.message}")
    
    return response


# WebSocket example for real-time interaction
async def websocket_simulation():
    """
    Simulate a WebSocket conversation with the team.
    Shows real-time interaction capabilities.
    """
    print("🌐 WebSocket Simulation Example")
    print("=" * 40)
    
    # This would typically be handled by your WebSocket endpoint
    # Here we simulate the interaction
    
    settings = get_settings()
    team_service = LLMTeamChatService(settings)
    await team_service.initialize()
    
    messages = [
        "Hello team! I need help with a project.",
        "I want to build a chat application with real-time features.",
        "What technology stack would you recommend?",
        "Can you help me implement WebSocket support?",
        "Great! Now let's add authentication to the chat."
    ]
    
    session_id = "websocket_simulation"
    
    for i, message in enumerate(messages, 1):
        print(f"\n📤 Message {i}: {message}")
        
        request = ChatRequest(
            message=message,
            session_id=session_id,
            metadata={"websocket": True, "message_number": i}
        )
        
        response = await team_service.process_message(request, "websocket_user")
        
        print(f"📥 Team Response: {response.message[:200]}...")
        print(f"   Agents: {response.metadata.get('agents_involved', [])}")
        
        # Simulate real-time delay
        await asyncio.sleep(0.5)


if __name__ == "__main__":
    # Run examples
    async def main():
        print("🎯 LLM Team Chat Examples")
        print("=" * 60)
        print()
        
        # Choose which example to run
        example_choice = input("""
Choose an example to run:
1. Simple team chat example
2. All comprehensive examples  
3. WebSocket simulation
4. All of the above

Enter choice (1-4): """).strip()
        
        if example_choice == "1":
            await simple_team_chat_example()
        elif example_choice == "2":
            examples = TeamChatExamples()
            await examples.run_all_examples()
        elif example_choice == "3":
            await websocket_simulation()
        elif example_choice == "4":
            await simple_team_chat_example()
            print("\n" + "="*60 + "\n")
            examples = TeamChatExamples()
            await examples.run_all_examples()
            print("\n" + "="*60 + "\n")
            await websocket_simulation()
        else:
            print("Invalid choice. Running simple example...")
            await simple_team_chat_example()
    
    asyncio.run(main())
