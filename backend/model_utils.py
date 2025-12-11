
# model_utils.py
import os
import torch
import numpy as np
import requests
from transformers import (
    BertTokenizer, BertForSequenceClassification,
    AutoTokenizer, AutoModelForSequenceClassification,
    pipeline as hf_pipeline
)
from config import Config
from typing import Tuple

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# BERT
_bert_model = None
_bert_tok = None

def load_bert_model():
    global _bert_model, _bert_tok
    if _bert_model is None or _bert_tok is None:
        try:
            print("🔄 Loading local BERT from:", Config.MODEL_PATH)
            _bert_model = BertForSequenceClassification.from_pretrained(Config.MODEL_PATH)
            _bert_tok = BertTokenizer.from_pretrained(Config.MODEL_PATH)
            _bert_model.to(DEVICE)
            _bert_model.eval()
            print("✅ BERT loaded.")
        except Exception as e:
            print("❌ Failed to load local BERT:", e)
            _bert_model, _bert_tok = None, None
    return _bert_model, _bert_tok

def predict_authenticity(text: str) -> Tuple[int, float]:
    if not text:
        return 0, 0.0
    model, tok = load_bert_model()
    if model is None or tok is None:
        return 0, 0.0
    enc = tok(text or "", return_tensors="pt", truncation=True, padding="max_length", max_length=Config.MAX_LEN)
    enc = {k: v.to(DEVICE) for k, v in enc.items()}
    with torch.no_grad():
        logits = model(**enc).logits
        probs = torch.softmax(logits, dim=1)[0].cpu().numpy()
    pred = int(np.argmax(probs))
    return pred, float(probs[pred])

# Summarizer
_summarizer = None
def load_summarizer():
    global _summarizer
    if _summarizer is None:
        _summarizer = hf_pipeline("summarization", model="t5-small", tokenizer="t5-small",
                                  device=0 if DEVICE.type == "cuda" else -1)
    return _summarizer

def summarize_text(text: str) -> str:
    if not text:
        return ""
    s = load_summarizer()
    try:
        out = s(text[:1500], max_length=80, min_length=25, do_sample=False)
        return out[0]["summary_text"]
    except Exception:
        return ""

# Fact-check
def fact_check_with_google(query):
    url = "https://www.googleapis.com/customsearch/v1"
    params = {
        "key": Config.GOOGLE_FACT_CHECK_API_KEY,
        "cx": Config.GOOGLE_CSE_ID,
        "q": "fact check " + (query or ""),
        "num": 5
    }
    try:
        resp = requests.get(url, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        items = data.get("items", [])
        if not items:
            return None
        for item in items:
            link = (item.get("link") or "").lower()
            if any(k in link for k in ["snopes", "politifact", "factcheck"]):
                return {"title": item.get("title"), "snippet": item.get("snippet"), "url": item.get("link")}
        first = items[0]
        return {"title": first.get("title"), "snippet": first.get("snippet"), "url": first.get("link")}
    except Exception as e:
        print("Fact-check API error:", e)
        return None

# Topic classifier (unchanged)
TOPIC_KEYWORDS = {
    "Technology": ["tech", "software", "ai", "robot", "computer", "smartphone","gadget","chip","semiconductor","startup","camera"],
    "Science": ["research", "scientist", "experiment", "physics", "space","nasa","biology","astronomy","chemical","study"],
    "Politics": ["election","minister","government","policy","bjp","congress","senate","president","political","vote"],
    "Economics": ["market","inflation","economy","gdp","trade","stock","crypto","investment","business","financial"],
    "Health": ["virus","covid","health","hospital","vaccine","medical","doctor","disease","treatment"],
    "Environment": ["climate","pollution","wildlife","environment","global warming","forest","green","ecology"],
    "Sports": ["match","tournament","football","cricket","athlete","goal","basketball","nfl","nba","fifa","olympics","sports","team"],
    "Business": ["startup","company","industry","financial","profit","merger","acquisition","corporate","earnings"],
    "Entertainment": ["movie","music","celebrity","film","hollywood","bollywood","tv","series","actor","actress"],
    "World": ["international","global","worldwide","united nations","diplomatic"],
    "Local": ["local","city","district","state","regional"],
    "Crime": ["murder","robbery","fraud","crime","police","investigation","theft"]
}

def classify_topic(text: str) -> str:
    if not text:
        return "World"
    text = text.lower()
    for topic, keywords in TOPIC_KEYWORDS.items():
        for word in keywords:
            if word in text:
                return topic
    return "World"

# HuggingFace model wrapper
HF_MODEL_NAME = Config.HF_MODEL_NAME
_hf_pipeline = None

def init_hf_model():
    global _hf_pipeline
    if _hf_pipeline is not None:
        return
    try:
        _hf_pipeline = hf_pipeline("text-classification", model=HF_MODEL_NAME, tokenizer=HF_MODEL_NAME,
                                   device=0 if DEVICE.type == "cuda" else -1)
        print("✅ HF model loaded:", HF_MODEL_NAME)
    except Exception as e:
        print("❌ Failed to load HF model:", e)
        _hf_pipeline = None

def predict_hf(text: str, truncation=True, max_length=512):
    try:
        if _hf_pipeline is None:
            init_hf_model()

        if _hf_pipeline is None:
            return "Unknown", 0.0

        cleaned = text[:max_length]

        res = _hf_pipeline(cleaned, truncation=True)[0]
        label = res.get("label", "")
        score = float(res.get("score", 0.0))
        label_u = label.upper()

        # Correct label mapping:
        # hamzab/roberta-fake-news-classification
        # LABEL_0 = Fake
        # LABEL_1 = Real
        # Correct mapping for hamzab/roberta-fake-news-classification
# LABEL_0 = Real
# LABEL_1 = Fake

        if "0" in label_u:
            return "Real", score       # positive for real
        if "1" in label_u:
            return "Fake", -score      # negative for fake

        

        return label, score

    except Exception as e:
        print("Error during HF prediction:", e)
        return "Unknown", 0.0

