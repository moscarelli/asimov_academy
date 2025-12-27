import requests
import time
import os
import markdown

# Load code examples
CODE_DIR = os.path.join(os.path.dirname(__file__), '../code-examples')
CODE_FILES = {
    'Python': 'discount_rule.py',
    'Java': 'DiscountRule.java',
    'C#': 'DiscountRule.cs',
    'JavaScript': 'discountRule.js',
}

with open(os.path.join(CODE_DIR, 'business_rule.md'), encoding='utf-8') as f:
    BUSINESS_RULE = f.read().split('\n', 2)[2].strip()

CODE_EXAMPLES = {}
for lang, fname in CODE_FILES.items():
    with open(os.path.join(CODE_DIR, fname), encoding='utf-8') as f:
        CODE_EXAMPLES[lang] = f.read()

OLLAMA_API = "http://localhost:11434/api"

# Get local models
def get_models():
    print("[INFO] Fetching local Ollama models...")
    try:
        resp = requests.get(f"{OLLAMA_API}/tags", timeout=30)
        resp.raise_for_status()
        models = [m['name'] for m in resp.json().get('models', [])]
        print(f"[INFO] Found models: {models}")
        return models, None
    except Exception as e:
        print(f"[ERROR] Could not fetch models: {e}")
        return [], str(e)

# Send prompt to model
def ollama_chat(model, prompt, step=None, lang=None):
    print(f"[CALL] Model: {model} | Step: {step or ''} | Lang: {lang or ''}")
    print(f"[PROMPT]\n{prompt[:120]}{'...' if len(prompt) > 120 else ''}")
    try:
        start = time.time()
        resp = requests.post(f"{OLLAMA_API}/chat", json={"model": model, "messages": [{"role": "user", "content": prompt}], "stream": False}, timeout=60)
        elapsed = time.time() - start
        resp.raise_for_status()
        # Handle multi-line JSON (streamed) responses
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


# Step 1: Health check for all models
health_results = []
models, error = get_models()
passing_health = []
if error:
    health_results.append({'model': 'ERROR', 'step': 'list', 'error': error})
else:
    for model in models:
        answer, elapsed, err = ollama_chat(model, "hello", step="health")
        health_results.append({'model': model, 'step': 'health', 'response': answer, 'time': elapsed, 'error': err})
        if answer and not err:
            passing_health.append(model)

# Step 2: Code analysis for models that passed health check
code_results = []
passing_code = []
for model in passing_health:
    model_passed_all = True
    for lang, code in CODE_EXAMPLES.items():
        prompt = (
            f"You are a senior software engineer. Carefully read the following {lang} code and explain in detail what it does, step by step. Focus on the business logic and any rules implemented.\n\n{code}"
        )
        answer, elapsed, err = ollama_chat(model, prompt, step="understand", lang=lang)
        is_accurate = BUSINESS_RULE.lower() in answer.lower() if answer else False
        code_results.append({'model': model, 'lang': lang, 'step': 'understand', 'response': answer, 'time': elapsed, 'error': err, 'accurate': is_accurate})
        if not answer or err:
            model_passed_all = False
    if model_passed_all:
        passing_code.append(model)

# Step 3: Business rule extraction for models that passed code analysis
business_results = []
passing_business = []
for model in passing_code:
    model_passed_all = True
    for lang, code in CODE_EXAMPLES.items():
        prompt = (
            f"You are a business analyst. Read the following {lang} code and extract the business rule it implements. State the rule clearly and concisely in plain English.\n\n{code}"
        )
        answer, elapsed, err = ollama_chat(model, prompt, step="business", lang=lang)
        is_accurate = BUSINESS_RULE.lower() in answer.lower() if answer else False
        business_results.append({'model': model, 'lang': lang, 'step': 'business', 'response': answer, 'time': elapsed, 'error': err, 'accurate': is_accurate})
        if not answer or err:
            model_passed_all = False
    if model_passed_all:
        passing_business.append(model)

# Step 4: Final comprehensive test for models that passed all previous steps
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
        is_accurate = BUSINESS_RULE.lower() in answer.lower() if answer else False
        final_results.append({'model': model, 'lang': lang, 'step': 'final-understand', 'response': answer, 'time': elapsed, 'error': err, 'accurate': is_accurate})
    # Business rule extraction
    for lang, code in CODE_EXAMPLES.items():
        prompt = (
            f"You are a business analyst. Read the following {lang} code and extract the business rule it implements. State the rule clearly and concisely in plain English.\n\n{code}"
        )
        answer, elapsed, err = ollama_chat(model, prompt, step="final-business", lang=lang)
        is_accurate = BUSINESS_RULE.lower() in answer.lower() if answer else False
        final_results.append({'model': model, 'lang': lang, 'step': 'final-business', 'response': answer, 'time': elapsed, 'error': err, 'accurate': is_accurate})

# Write results to markdown
md_lines = ["# Ollama Model Evaluation Results", ""]
md_lines.append("## Health Check Results\n| Model | Step | Time (s) | Error | Response |\n|-------|------|----------|-------|----------|")
for r in health_results:
    md_lines.append(f"| {r.get('model','')} | {r.get('step','')} | {r.get('time','')} | {r.get('error','')} | {str(r.get('response','')).replace('|','\\|')[:80]} ... |")

md_lines.append("\n## Code Understanding Results\n| Model | Language | Step | Time (s) | Accurate | Error | Response |\n|-------|----------|------|----------|---------|-------|----------|")
for r in code_results:
    md_lines.append(f"| {r.get('model','')} | {r.get('lang','')} | {r.get('step','')} | {r.get('time','')} | {r.get('accurate','')} | {r.get('error','')} | {str(r.get('response','')).replace('|','\\|')[:80]} ... |")

md_lines.append("\n## Business Rule Extraction Results\n| Model | Language | Step | Time (s) | Accurate | Error | Response |\n|-------|----------|------|----------|---------|-------|----------|")
for r in business_results:
    md_lines.append(f"| {r.get('model','')} | {r.get('lang','')} | {r.get('step','')} | {r.get('time','')} | {r.get('accurate','')} | {r.get('error','')} | {str(r.get('response','')).replace('|','\\|')[:80]} ... |")

md_lines.append("\n## Final Comprehensive Test Results\n| Model | Language | Step | Time (s) | Accurate | Error | Response |\n|-------|----------|------|----------|---------|-------|----------|")
for r in final_results:
    md_lines.append(f"| {r.get('model','')} | {r.get('lang','')} | {r.get('step','')} | {r.get('time','')} | {r.get('accurate','')} | {r.get('error','')} | {str(r.get('response','')).replace('|','\\|')[:80]} ... |")

with open(os.path.join(os.path.dirname(__file__), 'ollama_eval_results.md'), 'w', encoding='utf-8') as f:
    f.write('\n'.join(md_lines))

print("Evaluation complete. Results saved to ollama_eval_results.md.")
