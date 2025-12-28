import os
import time
import requests
import markdown

OLLAMA_MODEL = "tinyllama:1.1b"
LANGUAGES = [
    ("python", "discount_rule.py"),
    ("java", "DiscountRule.java"),
    ("csharp", "DiscountRule.cs"),
    ("javascript", "discountRule.js")
]
CODE_EXAMPLES_DIR = os.path.join(os.path.dirname(__file__), "../code-examples")
BUSINESS_RULE_FILE = os.path.join(CODE_EXAMPLES_DIR, "business_rule.md")
RESULTS_MD = os.path.join(os.path.dirname(__file__), "ollama_eval_results_tiny.md")
OLLAMA_API = "http://localhost:11434/api"

def read_file(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

def copilot_semantic_eval(response, business_rule):
    if not response:
        return False
    resp = response.lower()
    rule = business_rule.lower()
    keywords = ["10%", "discount", "order", "100", "loyalty"]
    if all(k in resp for k in keywords):
        return True
    if "discount" in resp and ("loyalty" in resp or "member" in resp) and ("100" in resp or "hundred" in resp):
        return True
    return False

def ollama_chat(model, prompt, step=None, lang=None):
    print(f"[CALL] Model: {model} | Step: {step or ''} | Lang: {lang or ''}")
    print(f"[PROMPT]\n{prompt[:120]}{'...' if len(prompt) > 120 else ''}")
    try:
        start = time.time()
        resp = requests.post(f"{OLLAMA_API}/chat", json={"model": model, "messages": [{"role": "user", "content": prompt}], "stream": False}, timeout=60)
        elapsed = time.time() - start
        resp.raise_for_status()
        lines = resp.text.strip().splitlines()
        last_json = None
        import json
        for line in lines:
            try:
                last_json = json.loads(line)
            except Exception:
                continue
        if last_json and 'message' in last_json:
            answer = last_json['message'].get('content', '')
        else:
            answer = ''
        print(f"[RESPONSE] ({elapsed:.2f}s)\n{answer[:120]}{'...' if len(answer) > 120 else ''}")
        return answer, elapsed, None
    except Exception as e:
        print(f"[ERROR] Model: {model} | Step: {step or ''} | Lang: {lang or ''} | {e}")
        return None, None, str(e)

def main():
    # Load business rule
    with open(BUSINESS_RULE_FILE, encoding='utf-8') as f:
        business_rule_text = f.read().strip().split('\n', 1)[-1].strip()
    # Load code examples
    CODE_EXAMPLES = {}
    for lang, fname in LANGUAGES:
        with open(os.path.join(CODE_EXAMPLES_DIR, fname), encoding='utf-8') as f:
            CODE_EXAMPLES[lang] = f.read()

    # Step 1: Health check
    health_results = []
    answer, elapsed, err = ollama_chat(OLLAMA_MODEL, "hello", step="health")
    health_results.append({'model': OLLAMA_MODEL, 'step': 'health', 'response': answer, 'time': elapsed, 'error': err})
    passing_health = [OLLAMA_MODEL] if answer and not err else []

    # Step 2: Code analysis
    code_results = []
    passing_code = []
    for model in passing_health:
        model_passed_all = True
        for lang, code in CODE_EXAMPLES.items():
            prompt = (
                f"You are a senior software engineer. Carefully read the following {lang} code and explain in detail what it does, step by step. Focus on the business logic and any rules implemented.\n\n{code}"
            )
            answer, elapsed, err = ollama_chat(model, prompt, step="understand", lang=lang)
            is_accurate = copilot_semantic_eval(answer, business_rule_text)
            code_results.append({'model': model, 'lang': lang, 'step': 'understand', 'response': answer, 'time': elapsed, 'error': err, 'accurate': is_accurate})
            if not answer or err:
                model_passed_all = False
        if model_passed_all:
            passing_code.append(model)

    # Step 3: Business rule extraction
    business_results = []
    passing_business = []
    for model in passing_code:
        model_passed_all = True
        for lang, code in CODE_EXAMPLES.items():
            prompt = (
                f"You are a business analyst. Read the following {lang} code and extract the business rule it implements. State the rule clearly and concisely in plain English.\n\n{code}"
            )
            answer, elapsed, err = ollama_chat(model, prompt, step="business", lang=lang)
            copilot_acc = copilot_semantic_eval(answer, business_rule_text)
            business_results.append({'model': model, 'lang': lang, 'step': 'business', 'response': answer, 'time': elapsed, 'error': err, 'accurate': copilot_acc})
            if not answer or err:
                model_passed_all = False
        if model_passed_all:
            passing_business.append(model)

    # Step 4: Final comprehensive test
    final_results = []
    for model in passing_business:
        # Health check
        answer, elapsed, err = ollama_chat(model, "hello", step="final-health")
        final_results.append({'model': model, 'step': 'final-health', 'response': answer, 'time': elapsed, 'error': err})
        # Code understanding
        for lang, code in CODE_EXAMPLES.items():
            prompt = (
                f"You are a senior software engineer. Carefully read the following {lang} code and explain in detail what it does, step by step. Focus on the business logic and any rules implemented.\n\n{code}"
            )
            answer, elapsed, err = ollama_chat(model, prompt, step="final-understand", lang=lang)
            is_accurate = copilot_semantic_eval(answer, business_rule_text)
            final_results.append({'model': model, 'lang': lang, 'step': 'final-understand', 'response': answer, 'time': elapsed, 'error': err, 'accurate': is_accurate})
        # Business rule extraction
        for lang, code in CODE_EXAMPLES.items():
            prompt = (
                f"You are a business analyst. Read the following {lang} code and extract the business rule it implements. State the rule clearly and concisely in plain English.\n\n{code}"
            )
            answer, elapsed, err = ollama_chat(model, prompt, step="final-business", lang=lang)
            is_accurate = copilot_semantic_eval(answer, business_rule_text)
            final_results.append({'model': model, 'lang': lang, 'step': 'final-business', 'response': answer, 'time': elapsed, 'error': err, 'accurate': is_accurate})

    # Write results to markdown
    md_lines = ["# Ollama Model Evaluation Results (Tiny Model Only)", ""]
    md_lines.append("## Health Check Results\n| Model | Step | Time (s) | Error | Response |\n|-------|------|----------|-------|----------|")
    for r in health_results:
        full_response = str(r.get('response','')).replace('|','\\|').replace('\n', ' ')
        md_lines.append(f"| {r.get('model','')} | {r.get('step','')} | {r.get('time','')} | {r.get('error','')} | {full_response} |")

    md_lines.append("\n## Code Understanding Results\n| Model | Language | Step | Time (s) | Accurate (Copilot) | Error | Response |\n|-------|----------|------|----------|--------------------|-------|----------|")
    for r in code_results:
        full_response = str(r.get('response','')).replace('|','\\|').replace('\n', ' ')
        md_lines.append(f"| {r.get('model','')} | {r.get('lang','')} | {r.get('step','')} | {r.get('time','')} | {r.get('accurate','')} | {r.get('error','')} | {full_response} |")

    md_lines.append("\n## Business Rule Extraction Results\n| Model | Language | Step | Time (s) | Accurate (Copilot) | Error | Full Response |\n|-------|----------|------|----------|--------------------|-------|--------------|")
    for r in business_results:
        full_response = str(r.get('response','')).replace('|','\\|').replace('\n', ' ')
        md_lines.append(f"| {r.get('model','')} | {r.get('lang','')} | {r.get('step','')} | {r.get('time','')} | {r.get('accurate','')} | {r.get('error','')} | {full_response} |")

    md_lines.append("\n## Final Comprehensive Test Results\n| Model | Language | Step | Time (s) | Accurate (Copilot) | Error | Response |\n|-------|----------|------|----------|--------------------|-------|----------|")
    for r in final_results:
        full_response = str(r.get('response','')).replace('|','\\|').replace('\n', ' ')
        md_lines.append(f"| {r.get('model','')} | {r.get('lang','')} | {r.get('step','')} | {r.get('time','')} | {r.get('accurate','')} | {r.get('error','')} | {full_response} |")

    with open(RESULTS_MD, "w", encoding="utf-8") as f:
        f.write('\n'.join(md_lines))

    print("Evaluation complete. Results saved to ollama_eval_results_tiny.md.")

if __name__ == "__main__":
    main()
