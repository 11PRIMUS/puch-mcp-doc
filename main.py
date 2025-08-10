
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

@app.post("/summarize", tags=["Summarization"], summary="Summarize a document", description="Upload a document and get a summary and learning blocks.")
async def summarize_doc(file: UploadFile = File(...), language: str = Form("hi")):
    text = await readf(file)
    if not language:
        language = detect(text)
    phrase_map = {
        "summarize in hindi": "hi",
        "summarize in english": "en",
        "summarize in bengali": "bn",
        "summarize in gujarati": "gu",
        "summarize in kannada": "kn",
        "summarize in malayalam": "ml",
        "summarize in marathi": "mr",
        "summarize in tamil": "ta",
        "summarize in telugu": "te",
        "summarize in punjabi": "pa",
        "summarize in urdu": "ur",
        "isse english me kre": "en",
        "isse hindi me kre": "hi",
        "इसे हिंदी में करें": "hi",
        "इसे अंग्रेजी में करें": "en"
    }
    lang_lower = language.strip().lower()
    language_code = phrase_map.get(lang_lower, language)
    if summarizer is None:
        return JSONResponse({"error": "failed to load summ model"}, status_code=500)
    instructions = {
        "en": "Summarize in English: ",
        "hi": "हिंदी में संक्षेप करें: ",
        "bn": "বাংলায় সংক্ষেপ করুন: ",
        "gu": "ગુજરાતીમાં સંક્ષિપ્ત કરો: ",
        "kn": "ಕನ್ನಡದಲ್ಲಿ ಸಂಕ್ಷಿಪ್ತಗೊಳಿಸಿ: ",
        "ml": "മലയാളത്തിൽ സംക്ഷിപ്തം ചെയ്യുക: ",
        "mr": "मराठीत संक्षेप करा: ",
        "ta": "தமிழில் சுருக்கவும்: ",
        "te": "తెలుగులో సంక్షిప్తం చేయండి: ",
        "pa": "ਪੰਜਾਬੀ ਵਿੱਚ ਸੰਖੇਪ ਕਰੋ: ",
        "ur": "اردو میں خلاصہ کریں: "
    }
    prefix = instructions.get(language_code, f"Summarize in {language_code}: ")
    prompt = prefix + text
    try:
        summary_result = summarizer(prompt, max_length=150, min_length=40, do_sample=False)
        summary = summary_result[0]["summary_text"]
        blocks = [s.strip() for s in summary.split('.') if s.strip()]
        return JSONResponse({"summary": summary, "blocks": blocks, "language": language_code})
    except Exception as e:
        logging.error(f"error during summarization: {e}")
        return JSONResponse({"error": "failed to summarize document."}, status_code=500)
    
@app.post("/comic-strip", tags=["Comic Strip"], summary="Generate a comic strip from a document", description="Upload a document and get a comic strip of main points.")
async def comic_strip(file: UploadFile = File(...), language: str = Form("en")):
    text = await readf(file)
    phrase_map = { #common phrases
        "summarize in hindi": "hi",
        "summarize in english": "en",
        "summarize in bengali": "bn",
        "summarize in gujarati": "gu",
        "summarize in kannada": "kn",
        "summarize in malayalam": "ml",
        "summarize in marathi": "mr",
        "summarize in tamil": "ta",
        "summarize in telugu": "te",
        "summarize in punjabi": "pa",
        "summarize in urdu": "ur",
        "isse english me kre": "en",
        "isse hindi me kre": "hi",
        "इसे हिंदी में करें": "hi",
        "इसे अंग्रेजी में करें": "en"
    }
    lang_lower = language.strip().lower()
    language_code = phrase_map.get(lang_lower, language)
    if summarizer is None:
        return JSONResponse({"error": "failed to load summ model"}, status_code=500)
    instructions = {
        "en": "Summarize in English: ",
        "hi": "हिंदी में संक्षेप करें: ",
        "bn": "বাংলায় সংক্ষেপ করুন: ",
        "gu": "ગુજરાતીમાં સંક્ષિપ્ત કરો: ",
        "kn": "ಕನ್ನಡದಲ್ಲಿ ಸಂಕ್ಷಿಪ್ತಗೊಳಿಸಿ: ",
        "ml": "മലയാളത്തിൽ സംക്ഷിപ്തം ചെയ്യുക: ",
        "mr": "मराठीत संक्षेप करा: ",
        "ta": "தமிழில் சுருக்கவும்: ",
        "te": "తెలుగులో సంక్షిప్తం చేయండి: ",
        "pa": "ਪੰਜਾਬੀ ਵਿੱਚ ਸੰਖੇਪ ਕਰੋ: ",
        "ur": "اردو میں خلاصہ کریں: "
    }
    prefix = instructions.get(language_code, f"Summarize in {language_code}: ")
    prompt = prefix + text
    try:
        summary_result = summarizer(prompt, max_length=150, min_length=40, do_sample=False)
        summary = summary_result[0]["summary_text"]
        blocks = [s.strip() for s in summary.split('.') if s.strip()]
        # Turn each block into a comic panel (caption + emoji)
        emojis = ["😃", "🤔", "😲", "😂", "🎉", "📚", "🚀", "😎"]
        panels = []
        for i, block in enumerate(blocks):
            panel = {"caption": block, "emoji": emojis[i % len(emojis)]}
            panels.append(panel)
        return JSONResponse({"comic_strip": panels, "language": language_code})
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
