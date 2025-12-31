"""
Query Agent - Entry Point for RAG Q&A and Tag Extraction

Two modes of operation:
1. Q&A Mode: Answer user questions about retirement topics
2. Tag Extraction Mode: Extract retirement terms from external text

Usage:
    # Q&A Mode (interactive)
    uv run query_agent.py
    
    # Q&A Mode (single question)
    uv run query_agent.py --question "What are 401k contribution limits?"
    
    # Tag Extraction Mode
    uv run query_agent.py --mode tags --text "Your text here..."
"""
import sys
import argparse
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.query_agent_core import RetirementQueryAgent
from src.utils import print_header


def main():
    """Main entry point for query agent."""
    parser = argparse.ArgumentParser(description="IRS Retirement Topics Query Agent")
    parser.add_argument(
        "--mode",
        choices=["qa", "tags"],
        default="qa",
        help="Operation mode: 'qa' for questions, 'tags' for tag extraction"
    )
    parser.add_argument(
        "--question",
        "-q",
        type=str,
        help="Single question to answer (Q&A mode only)"
    )
    parser.add_argument(
        "--text",
        "-t",
        type=str,
        help="Text to analyze for tag extraction (tags mode only)"
    )
    parser.add_argument(
        "--max-tags",
        type=int,
        default=10,
        help="Maximum number of tags to extract (default: 10)"
    )
    parser.add_argument(
        "--interactive",
        "-i",
        action="store_true",
        help="Run in interactive mode (Q&A mode only)"
    )
    
    args = parser.parse_args()
    
    # Initialize agent with selected mode
    print_header(f"IRS Retirement Topics Query Agent - {args.mode.upper()} Mode")
    print("Initializing agent...")
    
    agent = RetirementQueryAgent(mode=args.mode)
    print("✓ Agent ready\n")
    
    # Q&A Mode
    if args.mode == "qa":
        if args.question:
            # Single question
            answer = agent.answer_question(args.question)
            print(f"\n{answer}\n")
        else:
            # Interactive mode
            agent.interactive_qa()
    
    # Tag Extraction Mode
    elif args.mode == "tags":
        if not args.text:
            print("Error: --text argument required for tag extraction mode")
            print("Example: uv run query_agent.py --mode tags --text 'Your text here'")
            sys.exit(1)
        
        tags = agent.extract_tags(args.text, max_tags=args.max_tags)
        print(f"\n{tags}\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nAgent stopped by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\nError: {str(e)}")
        sys.exit(1)
