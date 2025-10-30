# Dockerfiles untuk Semua Services

## 1. docker/Dockerfile.scraper
```dockerfile
FROM python:3.10-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY scrapers/ /app/scrapers/
COPY data/ /app/data/

# Run scraper
CMD ["python", "scrapers/quick_scraper.py"]
```

## 2. docker/Dockerfile.processor
```dockerfile
FROM python:3.10-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY preprocessing/ /app/preprocessing/
COPY data/ /app/data/

# Run processor
CMD ["python", "preprocessing/data_cleaner.py"]
```

## 3. docker/Dockerfile.ml
```dockerfile
FROM python:3.10-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir fastapi uvicorn

# Copy application
COPY models/ /app/models/
COPY api.py /app/api.py

# Expose port
EXPOSE 8000

# Run API
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]
```

## 4. docker/Dockerfile.dashboard
```dockerfile
FROM python:3.10-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir streamlit plotly

# Copy application
COPY dashboard.py /app/dashboard.py
COPY data/ /app/data/

# Expose port
EXPOSE 8501

# Health check
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

# Run dashboard
CMD ["streamlit", "run", "dashboard.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

## 5. init.sql (Database initialization)
```sql
-- Create database schema
CREATE TABLE IF NOT EXISTS tweets (
    id SERIAL PRIMARY KEY,
    tweet_id VARCHAR(255) UNIQUE,
    date TIMESTAMP,
    username VARCHAR(255),
    content TEXT,
    content_clean TEXT,
    likes INTEGER DEFAULT 0,
    retweets INTEGER DEFAULT 0,
    replies INTEGER DEFAULT 0,
    total_engagement INTEGER DEFAULT 0,
    sentiment VARCHAR(50),
    sentiment_score FLOAT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS mentions (
    id SERIAL PRIMARY KEY,
    tweet_id VARCHAR(255) UNIQUE,
    date TIMESTAMP,
    username VARCHAR(255),
    content TEXT,
    likes INTEGER DEFAULT 0,
    retweets INTEGER DEFAULT 0,
    replies INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS model_metrics (
    id SERIAL PRIMARY KEY,
    model_name VARCHAR(255),
    accuracy FLOAT,
    f1_score FLOAT,
    precision_score FLOAT,
    recall_score FLOAT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_tweets_date ON tweets(date);
CREATE INDEX idx_tweets_sentiment ON tweets(sentiment);
CREATE INDEX idx_mentions_date ON mentions(date);
```

## 6. nginx.conf (Reverse Proxy)
```nginx
events {
    worker_connections 1024;
}

http {
    upstream dashboard {
        server dashboard:8501;
    }

    upstream mlflow {
        server mlflow:5000;
    }

    server {
        listen 80;
        server_name localhost;

        # Dashboard
        location / {
            proxy_pass http://dashboard;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            
            # WebSocket support for Streamlit
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection "upgrade";
            proxy_read_timeout 86400;
        }

        # MLflow
        location /mlflow/ {
            proxy_pass http://mlflow/;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
        }
    }
}
```

## 7. api.py (ML Service API)
```python
"""
FastAPI ML Service - Sentiment Analysis API
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
import pandas as pd

app = FastAPI(title="IndoPopBase ML API", version="1.0")

# Load sentiment analyzer
from sentiment_analyzer import SimpleSentimentAnalyzer
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
```
