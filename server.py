import base64
import json
import logging
import os
import subprocess
import tempfile
import urllib.request

from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import FileResponse, HTMLResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from google import genai
from google.genai import types
from pydantic import BaseModel

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
    repo_url: str = ""


def fetch_codebase_from_url(url: str) -> str:
    if not url.strip():
        return ""
    if "raw.githubusercontent.com" in url or "drive.google.com" in url:
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req) as response:
                return response.read().decode("utf-8", errors="ignore")
        except Exception as e:
            return f"Error fetching URL: {str(e)}"

    if "github.com" in url:
        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                subprocess.run(
                    ["git", "clone", "--depth", "1", url, temp_dir],
                    check=True,
                    capture_output=True,
                )
                code_content = []
                for root, _, files in os.walk(temp_dir):
                    if ".git" in root:
                        continue
                    for file in files:
                        if file.endswith(
                            (
                                ".py",
                                ".js",
                                ".ts",
                                ".html",
                                ".css",
                                ".md",
                                ".json",
                                ".txt",
                                ".rs",
                                ".go",
                                ".java",
                                ".cpp",
                                ".c",
                                ".h",
                            )
                        ):
                            file_path = os.path.join(root, file)
                            try:
                                with open(
                                    file_path, "r", encoding="utf-8", errors="ignore"
                                ) as f:
                                    content = f.read()
                                    rel_path = os.path.relpath(file_path, temp_dir)
                                    code_content.append(
                                        f"--- {rel_path} ---\n{content}\n"
                                    )
                            except Exception:
                                pass
                return "\n".join(code_content)
        except Exception as e:
            return f"Error cloning repository: {str(e)}"

    return "Unsupported URL. Provide a GitHub repository URL or a raw file link."


async def call_llm(prompt: str) -> str:
    if not client:
        return "Error: API key missing. Set GOOGLE_API_KEY in .env"
    try:
        response = await client.aio.models.generate_content(
            model=gemini_model,
            contents=prompt,
        )
        return response.text
    except Exception as e:
        logger.error(f"LLM call failed: {e}")
        return f"Error: {str(e)}"


async def run_agent(code: str, level: str, language: str):
    lang_hint = f"\nTarget Language: {language}" if language != "Auto-detect" else ""
    context_hint = f"\nAudience Level: {level}. Tailor explanations and optimizations for a {level} developer."

    improved = await call_llm(
        f"{pr.run_agent_prompt}\n{context_hint}{lang_hint}\n```\n{code}\n```"
    )
    if improved.startswith("Error:"):
        return "```\n// Error in Step 1: Analysis\n```", improved

    final_code = await call_llm(
        f"{pr.run_agent_prompt}\n{context_hint}{lang_hint}\n```\n{improved}\n```"
    )
    if final_code.startswith("Error:"):
        return "```\n// Error in Step 2: Optimization\n```", final_code

    explanation = await call_llm(
        f"{pr.run_agent_improve_code_prompt}\n{context_hint}{lang_hint}\nCode:\n```\n{final_code}\n```"
    )
    if explanation.startswith("Error:"):
        return final_code, explanation

    return final_code, explanation


@app.post("/api/analyze")
async def analyze(req: AnalyzeRequest):
    if req.repo_url:
        fetched = fetch_codebase_from_url(req.repo_url)
        if fetched.startswith("Error") or fetched.startswith("Unsupported"):
            return {"result": fetched}
        req.code = fetched + "\n\n" + req.code

    if not req.code.strip():
        return {"result": "Paste some code or provide a URL first."}

    if req.action == "Visualize Architecture":
        # Generate visual prompt from code
        prompt_text = (
            "Analyze the architecture and data flow of this code to generate a highly detailed visual prompt for an image generation model. "
            f"The user wants a diagram suitable for a '{req.level}' audience. Make sure the visual complexity and details match this level. "
            "CRITICAL INSTRUCTIONS FOR THE VISUAL PROMPT: "
            "1. Request a highly detailed, structured 2D software architecture diagram. "
            "2. STYLE: Clean vector whiteboard style, specifically resembling an Excalidraw, Eraser.io, or draw.io diagram. Use a clean white or light background. "
            "3. COMPONENTS: Represent all major functions, classes, APIs, databases, and modules as distinct, cleanly drawn 2D boxes or standard flowchart shapes. "
            "4. DETAIL: Ensure the diagram is COMPREHENSIVE. Do not oversimplify. Show internal components, middleware, sub-systems, and specific data models if present in the code. "
            "5. CONNECTIONS: Use clear, straight or right-angled connecting lines and arrows to show data flow and dependencies. "
            "6. LABELS: Every box and arrow must be clearly labeled with precise technical terms from the code. Use highly readable sans-serif typography. "
            "7. LAYOUT: Organize the diagram logically (e.g., layered architecture, microservices, or sequential flow) with proper grouping boxes for related components. "
            f"\nCode:\n```\n{req.code}\n```"
        )
        visual_prompt = await call_llm(prompt_text)

        try:
            image_result = await client.aio.models.generate_content(
                model="gemini-2.5-flash-image",
                contents=visual_prompt[:4000],
                config=types.GenerateContentConfig(
                    response_modalities=["IMAGE"],
                    image_config=types.ImageConfig(aspect_ratio="16:9"),
                ),
            )

            b64_img = None
            for part in image_result.parts:
                if getattr(part, "inline_data", None):
                    b64_img = base64.b64encode(part.inline_data.data).decode("utf-8")
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
        final_code, explanation = await run_agent(req.code, req.level, req.language)
        clean_code = (
            final_code.replace("```python", "")
            .replace("```javascript", "")
            .replace("```", "")
            .strip()
        )
        result = (
            f"### Improved Code\n```\n{clean_code}\n```\n\n### Analysis\n{explanation}"
        )
    else:
        lang_hint = f"\nLang: {req.language}" if req.language != "Auto-detect" else ""
        prompt_text = f"Task: {req.action}\nLevel: {req.level} (CRITICAL: You MUST tailor your response depth, tone, and terminology specifically for a {req.level} developer).\n{pr.prompt_builder}\nCode:\n```\n{req.code}\n```\n{lang_hint}"
        result = await call_llm(prompt_text)

    return {"result": result}


@app.post("/api/analyze/stream")
async def analyze_stream(req: AnalyzeRequest):
    """Streaming endpoint for text analysis (non-diagram)."""
    if req.repo_url:
        fetched = fetch_codebase_from_url(req.repo_url)
        if fetched.startswith("Error") or fetched.startswith("Unsupported"):
            # Can't easily yield error from non-generator, so just return simple json
            return {"result": fetched}
        req.code = fetched + "\n\n" + req.code

    if not req.code.strip():
        return {"result": "Paste some code or provide a URL first."}
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
