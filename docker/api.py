# 7. api.py (ML Service API)
"""
FastAPI ML Service - Sentiment Analysis API
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
import pandas as pd

app = FastAPI(title="IndoPopBase ML API", version="1.0")

# Load sentiment analyzer
from analysis.sentiment_simple_analysis import SimpleSentimentAnalyzer
analyzer = SimpleSentimentAnalyzer()

class TextRequest(BaseModel):
    text: str

class BatchTextRequest(BaseModel):
    texts: List[str]

class SentimentResponse(BaseModel):
    text: str
    sentiment: str
    score: float

@app.get("/")
def read_root():
    return {
        "message": "IndoPopBase ML API",
        "version": "1.0",
        "endpoints": ["/analyze", "/batch_analyze", "/health"]
    }

@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.post("/analyze", response_model=SentimentResponse)
def analyze_sentiment(request: TextRequest):
    """Analyze sentiment for single text"""
    try:
        sentiment, score = analyzer.analyze(request.text)
        return SentimentResponse(
            text=request.text,
            sentiment=sentiment,
            score=float(score)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/batch_analyze")
def batch_analyze_sentiment(request: BatchTextRequest):
    """Analyze sentiment for multiple texts"""
    try:
        results = []
        for text in request.texts:
            sentiment, score = analyzer.analyze(text)
            results.append({
                "text": text,
                "sentiment": sentiment,
                "score": float(score)
            })
        return {"results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))