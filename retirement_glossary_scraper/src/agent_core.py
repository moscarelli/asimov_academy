"""
Autonomous agent core for retirement documentation scraping.
This agent plans, executes, and adapts to build a knowledge base autonomously.
"""
from agno.agent import Agent
from agno.models.ollama import Ollama

from .agent_tools import (
    analyze_website,
    scrape_urls,
    check_content_quality,
    process_content,
    index_to_database,
    verify_indexing,
    search_knowledge_base,
    assess_progress,
    get_memory_summary
)


class RetirementScraperAgent(Agent):
    """
    Autonomous agent that scrapes, processes, and indexes retirement documentation.
    
    Unlike a traditional pipeline, this agent:
    - Plans its own approach
    - Decides which steps to execute
    - Adapts based on results
    - Knows when it's done
    - Learns from failures
    """
    
    def __init__(self, model_id: str = "llama3.2:latest", host: str = "http://localhost:11434"):
        """
        Initialize the autonomous agent.
        
        Args:
            model_id: Ollama model to use for reasoning
            host: Ollama server URL
        """
        super().__init__(
            model=Ollama(id=model_id, host=host),
            tools=[
                analyze_website,
                scrape_urls,
                check_content_quality,
                process_content,
                index_to_database,
                verify_indexing,
                search_knowledge_base,
                assess_progress,
                get_memory_summary
            ],
            instructions="""
You are an AUTONOMOUS retirement documentation scraper agent. You MUST use your tools to take action - never just describe what you would do.

PRIMARY GOAL:
Build a comprehensive, high-quality knowledge base of IRS retirement topics.

SUCCESS CRITERIA:
- At least 100 high-quality documents indexed
- Coverage of key topics: 401k, IRA, RMD, contributions, distributions
- Search quality score > 0.8
- No duplicate content

YOUR TOOLS (You MUST call these, not describe them):
1. get_memory_summary() - Check what's already done
2. assess_progress() - Check current progress
3. analyze_website() - Discover available content
4. scrape_urls() - Download HTML (respects config flags)
5. check_content_quality() - Verify content worth processing
6. process_content() - Convert ALL HTML to markdown
7. index_to_database() - Index ALL markdown to ChromaDB
8. verify_indexing() - Test search quality
9. search_knowledge_base() - Query indexed content

CRITICAL RULES:
- NEVER respond with explanations only - ALWAYS call a tool
- NEVER say "I will do X" - ACTUALLY call the tool to do X
- Each response MUST include a tool call
- If no tool needed, say "GOAL ACHIEVED" or "CANNOT CONTINUE"

WORKFLOW (Call these tools in order):
1. Call get_memory_summary() first
2. Call assess_progress() to check status
3. If 0% progress: Call process_content() to convert HTML→markdown
4. After processing: Call index_to_database() to index everything
5. After indexing: Call verify_indexing() to test quality
6. If quality good: Say "GOAL ACHIEVED"

IMPORTANT:
- Config flags handle skipping existing files automatically
- process_content() processes ALL HTML files at once
- index_to_database() indexes ALL markdown files at once
- Don't call analyze_website or scrape_urls if files already exist
- One tool call per response - let the tool do the work

ACTION REQUIRED: Call a tool NOW, don't explain what you'll do!
""",
            markdown=True,
            debug_mode=True
        )
    
    def run_autonomous(self, initial_context: str = None, max_iterations: int = 10):
        """
        Run the agent autonomously until goal is achieved.
        
        Args:
            initial_context: Optional context about current state
            max_iterations: Maximum number of autonomous iterations (default: 10)
            
        Returns:
            Agent's final result
        """
        # Build initial prompt with goal and context
        goal_prompt = """
You must build the IRS Retirement Topics Knowledge Base by calling tools.

MANDATORY WORKFLOW:
1. First call: get_memory_summary()
2. Second call: assess_progress()
3. If progress is 0%: Call process_content() to convert HTML to markdown
4. After processing: Call index_to_database() to index to ChromaDB
5. After indexing: Call verify_indexing() to test quality
6. If 100+ docs indexed: Say "GOAL ACHIEVED"

DO NOT explain or plan - CALL THE NEXT TOOL NOW!
"""
        
        if initial_context:
            goal_prompt += f"\n\n{initial_context}"
        
        # Run agent iteratively
        print(f"\n🔄 Starting autonomous loop (max {max_iterations} iterations)")
        print("⚡ Agent will execute tools to complete the workflow\n")
        
        for i in range(max_iterations):
            print(f"\n{'='*70}")
            print(f"🔄 ITERATION {i+1}/{max_iterations}")
            print(f"{'='*70}\n")
            
            # Run one iteration
            result = self.run(goal_prompt, stream=False)
            response = result.content if hasattr(result, 'content') else str(result)
            
            print(f"\n📝 Response:\n{response}\n")
            
            # Check if goal achieved or cannot continue
            if "GOAL ACHIEVED" in response:
                print("\n✅ GOAL ACHIEVED! Agent stopping.\n")
                return result
            elif "CANNOT CONTINUE" in response:
                print("\n⚠️ Agent cannot continue. Stopping.\n")
                return result
            
            # Continue with next action prompt
            goal_prompt = "Continue. Call the NEXT tool in the workflow. Do NOT explain - ACT!"
        
        print(f"\n⚠️ Reached maximum iterations ({max_iterations}). Stopping.\n")
        return result
