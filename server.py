from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.gzip import GZipMiddleware
import os
import json
import base64
import logging
from pydantic import BaseModel
from dotenv import load_dotenv
from google import genai
from google.genai import types
import prompt as pr

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()
try:
    client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))
    logger.info("Gemini client initialized.")
except Exception as e:
    client = None
    logger.error(f"Failed to init Gemini client: {e}")
gemini_model = "gemini-3.1-flash-lite-preview"

app = FastAPI()
app.add_middleware(GZipMiddleware, minimum_size=1000)

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", response_class=FileResponse)
async def read_index():
    return FileResponse("static/index.html")

class AnalyzeRequest(BaseModel):
    code: str
    action: str
    level: str
    language: str
    agent_mode: bool

async def call_llm(prompt: str) -> str:
    if not client: return "Error: API key missing. Set GOOGLE_API_KEY in .env"
    try:
        response = await client.aio.models.generate_content(
            model=gemini_model,
            contents=prompt,
        )
        return response.text
    except Exception as e:
        logger.error(f"LLM call failed: {e}")
        return f"Error: {str(e)}"

async def run_agent(code: str):
    improved = await call_llm(f"{pr.run_agent_prompt}\n```\n{code}\n```")
    final_code = await call_llm(f"{pr.run_agent_prompt}\n```\n{improved}\n```")
    explanation = await call_llm(f"{pr.run_agent_improve_code_prompt}\nCode:\n```\n{final_code}\n```")
    return final_code, explanation

@app.post("/api/analyze")
async def analyze(req: AnalyzeRequest):
    if not req.code.strip():
        return {"result": "Paste some code first."}
    
    if req.action == "Visualize Architecture":
        # Generate visual prompt from code
        prompt_text = (
            "Analyze the architecture and data flow of this code to generate a highly detailed prompt for an image generation model. "
            f"The user wants a diagram suitable for a '{req.level}' audience. Make sure the visual complexity and details match this level. "
            "CRITICAL INSTRUCTIONS FOR THE VISUAL PROMPT: "
            "1. Request a high-quality, meticulously hand-drawn ink style pen and paper architecture flowchart on textured paper. "
            "2. COLOR PALETTE: Monochrome ink or subtle sepia tones with a warm, clean paper background. "
            "3. FLOW DIRECTION: Use a strict TOP-TO-BOTTOM or LEFT-TO-RIGHT flow. All arrows must follow a single consistent direction. Do NOT scatter nodes randomly. "
            "4. Show INNER STRUCTURE: For each major component, draw it as a large open container with clearly separated sub-steps inside (e.g., validation → processing → response). Sub-nodes inside containers must also be properly sized and spaced. "
            "5. Label all nodes and arrows with precise technical terms (e.g., 'Input Validation', 'LLM API Call', 'JSON Response', 'Error Handling'). Do not use generic labels like 'Step 1', 'Step 2'. "
            "6. Use thick, clear hand-drawn arrows between nodes. Arrows must not cross or overlap each other. "
            "7. SPACING: Leave generous whitespace between all elements. No overlapping text or nodes. Every label must be fully readable. "
            f"\nCode:\n```\n{req.code}\n```"
        )
        visual_prompt = await call_llm(prompt_text)
        
        try:
            image_result = await client.aio.models.generate_content(
                model='gemini-2.5-flash-image',
                contents=visual_prompt[:4000],
                config=types.GenerateContentConfig(
                    response_modalities=["IMAGE"],
                    image_config=types.ImageConfig(aspect_ratio="16:9")
                )
            )
            
            b64_img = None
            for part in image_result.parts:
                if getattr(part, 'inline_data', None):
                    b64_img = base64.b64encode(part.inline_data.data).decode('utf-8')
                    break
            
            if b64_img:
                # Generate a proper explanation of the diagram
                explain_prompt = f"Based on the following code, provide a clear, concise explanation of the architecture flow shown in the diagram. Describe what each component does and how data flows between them. Do NOT mention image generation prompts.\n\nCode:\n```\n{req.code}\n```"
                explanation = await call_llm(explain_prompt)
                result = f"### Architecture Diagram\n\n![Generated Architecture](data:image/jpeg;base64,{b64_img})\n\n### Diagram Explanation\n{explanation}"
            else:
                result = f"### Error Generating Image\nNo image returned by the model."
        except Exception as e:
            logger.error(f"Image generation failed: {e}")
            result = f"### Error Generating Image\n{str(e)}"
    elif req.agent_mode:
        final_code, explanation = await run_agent(req.code)
        clean_code = final_code.replace("```python", "").replace("```javascript", "").replace("```", "").strip()
        result = f"### Improved Code\n```\n{clean_code}\n```\n\n### Analysis\n{explanation}"
    else:
        lang_hint = f"\nLang: {req.language}" if req.language != "Auto-detect" else ""
        prompt_text = f"Task: {req.action}\nLevel: {req.level} (CRITICAL: You MUST tailor your response depth, tone, and terminology specifically for a {req.level} developer).\n{pr.prompt_builder}\nCode:\n```\n{req.code}\n```\n{lang_hint}"
        result = await call_llm(prompt_text)
    
    return {"result": result}

@app.post("/api/analyze/stream")
async def analyze_stream(req: AnalyzeRequest):
    """Streaming endpoint for text analysis (non-diagram)."""
    if not req.code.strip():
        return {"result": "Paste some code first."}
    if not client:
        return {"result": "Error: API missing."}
    
    lang_hint = f"\nLang: {req.language}" if req.language != "Auto-detect" else ""
    prompt_text = f"Task: {req.action}\nLevel: {req.level} (CRITICAL: You MUST tailor your response depth, tone, and terminology specifically for a {req.level} developer).\n{pr.prompt_builder}\nCode:\n```\n{req.code}\n```\n{lang_hint}"
    
    async def generate():
        try:
            response = await client.aio.models.generate_content_stream(
                model=gemini_model,
                contents=prompt_text,
            )
            async for chunk in response:
                if chunk.text:
                    yield f"data: {json.dumps({'chunk': chunk.text})}\n\n"
            yield f"data: {json.dumps({'done': True})}\n\n"
        except Exception as e:
            logger.error(f"Streaming failed: {e}")
            yield f"data: {json.dumps({'error': str(e)})}\n\n"
    
    return StreamingResponse(generate(), media_type="text/event-stream")

class ChatRequest(BaseModel):
    user_input: str
    context_code: str

@app.post("/api/chat")
async def chat(req: ChatRequest):
    prompt_text = f"Context:\n{req.context_code}\nUser: {req.user_input}"
    reply = await call_llm(prompt_text)
    return {"reply": reply}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)
