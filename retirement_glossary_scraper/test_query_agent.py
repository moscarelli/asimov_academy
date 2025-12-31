"""
Test script for Query Agent - Q&A and Tag Extraction
"""
from src.query_agent_core import RetirementQueryAgent

print("="*80)
print("TESTING QUERY AGENT")
print("="*80)

# Test 1: Q&A Mode
print("\n" + "="*80)
print("TEST 1: Q&A MODE")
print("="*80 + "\n")

qa_agent = RetirementQueryAgent(mode="qa")

test_questions = [
    "What are the 401k contribution limits?",
    "What is a Roth IRA?",
    "When do I need to take required minimum distributions?"
]

for question in test_questions:
    print(f"\n{'='*80}")
    print(f"Question: {question}")
    print('='*80)
    answer = qa_agent.answer_question(question)
    print(f"\nAnswer:\n{answer}")
    print("\n")

# Test 2: Tag Extraction Mode
print("\n" + "="*80)
print("TEST 2: TAG EXTRACTION MODE")
print("="*80 + "\n")

tag_agent = RetirementQueryAgent(mode="tags")

test_texts = [
    "I want to maximize my retirement savings. Should I contribute to a 401k or open a Roth IRA? I'm also concerned about early withdrawal penalties and required minimum distributions.",
    "Our company offers a SIMPLE IRA and profit-sharing plan. Employees are wondering about contribution limits and catch-up contributions for those over 50.",
]

for i, text in enumerate(test_texts, 1):
    print(f"\n{'='*80}")
    print(f"Test Text #{i}:")
    print(f"{'='*80}")
    print(f"{text}\n")
    print(f"{'='*80}")
    print("Extracted Tags:")
    print('='*80)
    tags = tag_agent.extract_tags(text, max_tags=5)
    print(f"\n{tags}\n")

print("="*80)
print("ALL TESTS COMPLETED")
print("="*80)
