
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
    
@app.post("/strip", tags=["Comic Strip"], summary="Generate a comic strip from a document", description="Upload a document and get a comic strip of main points.")
async def comic_strip(file: UploadFile = File(...), language: str = Form("en")):
    text = await readf(file)
    if summarizer is None:
        return JSONResponse({"error": "failed to load summ model"}, status_code=500)
    try:
        summary_result = summarizer(text, max_length=150, min_length=40, do_sample=False)
        summary = summary_result[0]["summary_text"]
        blocks = [s.strip() for s in summary.split('.') if s.strip()]

        emojis = ["😃", "🤔","😲","😂","🎉", "📚", "🚀", "😎"]
        panels = []
        for i, block in enumerate(blocks):
            panel = {"caption": block, "emoji": emojis[i % len(emojis)]}
            panels.append(panel)
        return JSONResponse({"strip": panels, "language": language})
    except Exception as e:
        logging.error(f"error during comic strip generation: {e}")
        return JSONResponse({"error": "failed to generate comic strip."}, status_code=500)

@app.post("/collabSummary", tags=["collaborative"], summary="add a collaborative summary", description="Add a user-contributed summary for a document.")
async def add_collab_summary(doc_id: str = Form(...), summary: str = Form(...), user: str = Form(...)):
    if doc_id not in collab_summaries:
        collab_summaries[doc_id] = []
    collab_summaries[doc_id].append({"user": user, "summary": summary})
    return {"message": "Summary added.", "doc_id": doc_id}

@app.get("/collabSummary/{doc_id}", tags=["collaborative"], summary="get collaborative summaries", description="Retrieve all user-contributed summaries for a document.")
async def get_collab_summary(doc_id: str):
    return {"doc_id": doc_id, "summaries": collab_summaries.get(doc_id, [])}

@app.post("/")
async def root_post():
    return {"message": "doc summarizer working"}

@app.get("/validate")
def validate():
    return {"number": "+918577085733"}
