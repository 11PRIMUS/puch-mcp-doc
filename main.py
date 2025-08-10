
from fastapi import FastAPI, File, UploadFile, Form
from fastapi.responses import JSONResponse
from langdetect import detect
from transformers import pipeline
import logging


try:
    summarizer =pipeline("summarization", model="google/mt5-small")
except Exception as e:
    logging.error(f"error loading summarization model: {e}")
    summarizer =None

app=FastAPI(
    title=" Doc summarizer",
    description="document summarizer fo puch mcp hack",
    version="1.0.0"
)

async def readf(file:UploadFile):
    content = await file.read()
    return content.decode(errors="ignore")


collab_summaries = {}

@app.post("/summarize", tags=["Summarization"], summary="summarize a document", description="upload a document and get a summary and learning blocks.")
async def summarize_doc(file: UploadFile = File(...), language: str = Form("hi")):
    text = await readf(file)
    if not language:
        language =detect(text)
    if summarizer is None:
        return JSONResponse({"error": "failed to load summ model"}, status_code=500)
    try:
        summary_result =summarizer(text, max_length=150, min_length=40, do_sample=False)
        summary =summary_result[0]["summary_text"]
        blocks = [s.strip() for s in summary.split('.') if s.strip()]
        return JSONResponse({"summary": summary, "blocks": blocks, "language": language})
    except Exception as e:
        logging.error(f"error during summarization: {e}")
        return JSONResponse({"error": "failed to summarize document."}, status_code=500)

@app.post("/")
async def root_post():
    return {"message": "doc summarizer working"}

@app.get("/validate")
def validate():
    return {"number": "+918577085733"}
