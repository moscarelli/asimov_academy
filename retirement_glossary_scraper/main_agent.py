#!/usr/bin/env python3
"""
Autonomous Agent Entry Point for IRS Retirement Glossary Scraper

This is a TRUE AUTONOMOUS AGENT that:
- Plans its own approach
- Decides what to do next
- Adapts based on results
- Knows when it's done
- Learns from failures

Unlike main.py (fixed pipeline), this agent makes its own decisions.
"""

from src.agent_core import RetirementScraperAgent
from src.agent_memory import AgentMemory
from src.utils import print_header


def main():
    """Main execution function for autonomous agent."""
    
    print_header("AUTONOMOUS RETIREMENT SCRAPER AGENT", width=70)
    print("Starting autonomous agent session...")
    print("The agent will plan and execute its own approach to build the knowledge base.")
    print("=" * 70)
    
    # Initialize agent and memory
    agent = RetirementScraperAgent()
    memory = AgentMemory()
    
    # Show current state
    print("\n📊 Current State (from memory):")
    summary = memory.get_summary()
    print(f"  • Previous sessions: {summary['total_sessions']}")
    print(f"  • URLs scraped: {summary['scraped_urls_count']}")
    print(f"  • Documents indexed: {summary['indexed_documents']}")
    print(f"  • Failed attempts: {summary['failed_attempts']}")
    print(f"  • Knowledge gaps: {summary['knowledge_gaps']}")
    
    if summary['current_progress']:
        progress = summary['current_progress']
        print(f"\n📈 Last Progress Check:")
        print(f"  • Status: {progress.get('status', 'unknown')}")
        print(f"  • Progress: {progress.get('progress_percentage', 0):.1f}%")
        print(f"  • Recommendation: {progress.get('recommendation', 'N/A')}")
    
    print("\n" + "=" * 70)
    print("🤖 Agent is now running autonomously...")
    print("=" * 70 + "\n")
    
    # Build context for agent
    initial_context = f"""
Previous Work Summary:
- Sessions completed: {summary['total_sessions']}
- URLs already scraped: {summary['scraped_urls_count']}
- Documents indexed: {summary['indexed_documents']}
- Failed attempts: {summary['failed_attempts']}

Current Goal Progress:
{summary['current_progress']}

Use this information to decide what to do next.
"""
    
    # Run agent autonomously
    try:
        result = agent.run_autonomous(initial_context)
        
        print("\n" + "=" * 70)
        print("🎯 AGENT COMPLETED")
        print("=" * 70)
        print("\n📋 Agent's Final Report:")
        print(result.content)
        
        # Show final state
        print("\n" + "=" * 70)
        print("📊 Final State:")
        final_summary = memory.get_summary()
        print(f"  • Total sessions: {final_summary['total_sessions']}")
        print(f"  • Documents indexed: {final_summary['indexed_documents']}")
        print(f"  • Quality metrics: {final_summary.get('quality_metrics', {})}")
        
        final_progress = memory.get_goal_progress()
        if final_progress:
            print(f"\n✅ Final Status: {final_progress.get('status', 'unknown')}")
            print(f"📈 Progress: {final_progress.get('progress_percentage', 0):.1f}%")
            print(f"💡 Recommendation: {final_progress.get('recommendation', 'N/A')}")
        
        print("=" * 70)
        
    except KeyboardInterrupt:
        print("\n\n⚠️ Agent interrupted by user")
        print("Memory has been saved. Agent can resume from this point.")
    except Exception as e:
        print(f"\n\n❌ Agent encountered an error: {e}")
        memory.record_failure({"operation": "autonomous_run", "error": str(e)})
        raise


if __name__ == "__main__":
    main()
