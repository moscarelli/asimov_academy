"""
Query Agent Core - RAG Agent for Q&A and Tag Extraction
"""
from agno.agent import Agent
from agno.models.ollama import Ollama
from typing import Optional
from . import query_agent_tools


class RetirementQueryAgent(Agent):
    """
    Autonomous agent for querying the IRS Retirement Glossary knowledge base.
    
    Two main capabilities:
    1. Direct Q&A: Answer user questions about retirement terms
    2. Tag Extraction: Extract relevant terms from external text
    """
    
    def __init__(self, mode: str = "qa"):
        """
        Initialize the query agent.
        
        Args:
            mode: Operation mode - "qa" for questions, "tags" for tag extraction
        """
        self.mode = mode
        
        # Define agent instructions based on mode
        if mode == "qa":
            instructions = self._get_qa_instructions()
        elif mode == "tags":
            instructions = self._get_tag_extraction_instructions()
        else:
            raise ValueError(f"Invalid mode: {mode}. Must be 'qa' or 'tags'")
        
        super().__init__(
            name="RetirementQueryAgent",
            model=Ollama(
                id="llama3.2:latest",
                host="http://localhost:11434",
                timeout=60
            ),
            tools=[
                query_agent_tools.search_glossary,
                query_agent_tools.extract_tags_from_text,
                query_agent_tools.get_document_references,
                query_agent_tools.analyze_text_for_concepts
            ],
            instructions=instructions,
            markdown=True,
            debug_mode=True,
            # No knowledge in context - we use tool-based retrieval (RAG pattern)
            # No culture - this is a task-focused agent, not conversational
            tool_choice="auto",     # Let agent decide which tools to use
        )
    
    def _get_qa_instructions(self) -> list[str]:
        """Instructions for Q&A mode."""
        return [
            "You are an expert on IRS retirement topics and regulations.",
            "Your role is to answer user questions using the knowledge base.",
            "",
            "CRITICAL RULES:",
            "- ONLY use information from search_glossary() tool results",
            "- NEVER make up or invent information not in the search results",
            "- NEVER provide external links or sources not from the knowledge base",
            "- If search results don't contain the answer, say 'I could not find information about [topic] in the IRS retirement glossary'",
            "",
            "HOW TO ANSWER QUESTIONS:",
            "1. ALWAYS use search_glossary() to find relevant information",
            "2. Read the returned content carefully",
            "3. Answer ONLY based on what's in the search results",
            "4. Include exact quotes or paraphrases from the documents",
            "5. Cite the source URL from the metadata",
            "6. If nothing relevant is found, admit it clearly",
            "",
            "RESPONSE FORMAT:",
            "- Start with a direct answer based on search results",
            "- Provide supporting details from the documents",
            "- End with source citations from metadata",
            "",
            "EXAMPLE:",
            "Question: What are the 2024 401k contribution limits?",
            "",
            "Answer: The 2024 401k contribution limit is $23,000 for individuals under 50...",
            "",
            "Sources:",
            "- Retirement Topics (https://www.irs.gov/retirement-plans/...)",
            "",
            "Remember: NEVER hallucinate or provide information not found in search_glossary() results!"
        ]
    
    def _get_tag_extraction_instructions(self) -> list[str]:
        """Instructions for tag extraction mode."""
        return [
            "You are a retirement terminology extraction specialist.",
            "Your role is to identify retirement-related terms in text from external APIs.",
            "",
            "HOW TO EXTRACT TAGS:",
            "1. Receive text from external API",
            "2. Use extract_tags_from_text() to find matching retirement terms",
            "3. For each tag, get document references using get_document_references()",
            "4. Return structured list with term, relevance, filename, and URL",
            "",
            "TAG EXTRACTION CRITERIA:",
            "- Only extract terms that exist in the knowledge base",
            "- Prioritize high-relevance matches",
            "- Include document references for linking",
            "- Maximum 10 tags per text",
            "",
            "OUTPUT FORMAT:",
            "Return a structured list:",
            "1. Term: [Term Name]",
            "   - Relevance: high/medium",
            "   - Filename: [file.md]",
            "   - URL: [IRS URL]",
            "",
            "EXAMPLE INPUT:",
            "Text: 'I want to maximize my retirement savings. Should I contribute to a 401k or Roth IRA?'",
            "",
            "EXAMPLE OUTPUT:",
            "Extracted Tags:",
            "1. Term: 401(k) Plans",
            "   - Relevance: high",
            "   - Filename: 401k-plans.md",
            "   - URL: https://www.irs.gov/...",
            "",
            "2. Term: Roth IRA",
            "   - Relevance: high",
            "   - Filename: roth-ira.md",
            "   - URL: https://www.irs.gov/...",
            "",
            "Be precise and only extract terms that are actually in the knowledge base!"
        ]
    
    def answer_question(self, question: str) -> str:
        """
        Answer a user question using the knowledge base.
        
        Args:
            question: User's question about retirement topics
        
        Returns:
            Agent's answer with citations
        """
        if self.mode != "qa":
            return "Error: Agent not in Q&A mode. Create agent with mode='qa'"
        
        print(f"\n{'='*80}")
        print(f"QUESTION: {question}")
        print(f"{'='*80}\n")
        
        response = self.run(question)
        
        return response.content if response else "Error: No response from agent"
    
    def extract_tags(self, text: str, max_tags: int = 10) -> str:
        """
        Extract retirement-related tags from text.
        
        Args:
            text: Large text to analyze (from external API)
            max_tags: Maximum number of tags to extract
        
        Returns:
            Structured list of tags with document references
        """
        if self.mode != "tags":
            return "Error: Agent not in tag extraction mode. Create agent with mode='tags'"
        
        print(f"\n{'='*80}")
        print(f"EXTRACTING TAGS FROM TEXT ({len(text)} characters)")
        print(f"{'='*80}\n")
        
        prompt = f"Extract retirement-related tags from this text (max {max_tags} tags):\n\n{text}"
        
        response = self.run(prompt)
        
        return response.content if response else "Error: No response from agent"
    
    def interactive_qa(self):
        """
        Run interactive Q&A session with the agent.
        """
        if self.mode != "qa":
            print("Error: Agent not in Q&A mode")
            return
        
        print("\n" + "="*80)
        print("IRS Retirement Topics - Interactive Q&A")
        print("="*80)
        print("Ask questions about retirement topics (type 'quit' to exit)\n")
        
        while True:
            try:
                question = input("Question: ").strip()
                
                if question.lower() in ['quit', 'exit', 'q']:
                    print("\nGoodbye!")
                    break
                
                if not question:
                    continue
                
                answer = self.answer_question(question)
                print(f"\n{answer}\n")
                print("-" * 80 + "\n")
                
            except KeyboardInterrupt:
                print("\n\nSession interrupted. Goodbye!")
                break
            except Exception as e:
                print(f"Error: {str(e)}")
                continue
