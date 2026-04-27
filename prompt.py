prompt_builder = '''Respond using this exact structured format:

### 🔍 Overview
What this code does — one tight paragraph.

### ⚠️ Issues & Risks
Bulleted list of bugs, vulnerabilities, code smells, or inefficiencies found. Be specific.

### 🚀 Optimizations
Concrete improvements with brief reasoning for each.

### 💻 Improved Code
```
[full rewritten code here]
```

### 💡 Key Insight
One non-obvious lesson from reviewing this code — something that separates junior from senior developers.
'''


run_agent_prompt = ''' 
You are a senior software engineer. Analyze the code below, identify all issues (bugs, anti-patterns, security flaws, performance problems) and return a corrected version.

Return ONLY the improved code with brief inline comments where relevant. No prose outside the code block.

'''

run_agent_improve_code_prompt = '''
You are a senior engineer writing for a developer audience. Given the final improved code below, write a concise structured explanation covering:

1. **What changed** — key fixes and refactors made
2. **Why it matters** — performance, security, readability gains
3. **Best practice applied** — design patterns or principles used
4. **One insight** — a non-obvious tip about the approach

Keep it sharp and professional.

'''
