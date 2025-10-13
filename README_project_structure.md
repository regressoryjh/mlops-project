# 📁 Project Structure - IndoPopBase Analytics

## Complete Folder Structure

```
indopopbase-analytics/
│
├── 📁 data/                          # Data storage
│   ├── raw/                          # Raw scraped data
│   │   ├── IndoPopBase_tweets_*.csv
│   │   └── IndoPopBase_mentions_*.csv
│   ├── processed/                    # Cleaned data
│   │   ├── tweets_cleaned.csv
│   │   └── mentions_cleaned.csv
│   └── models/                       # Trained models
│       └── sentiment_model.pkl
│
├── 📁 scrapers/                      # Scraping scripts
│   ├── __init__.py
│   ├── quick_scraper.py             # Main scraper (ntscraper)
│   ├── twitter_scraper_alternative.py # Alternative methods
│   └── test_scraper.py              # Test all methods
│
├── 📁 preprocessing/                 # Data cleaning
│   ├── __init__.py
│   ├── cleaner.py                   # Data cleaning functions
│   ├── text_processor.py            # Text preprocessing
│   └── feature_engineering.py       # Feature creation
│
├── 📁 analysis/                      # Analysis scripts
│   ├── __init__.py
│   ├── sentiment_analysis.py        # Sentiment classification
│   ├── engagement_analysis.py       # Engagement metrics
│   ├── topic_modeling.py            # Topic extraction
│   └── trend_analysis.py            # Time-series analysis
│
├── 📁 models/                        # ML models
│   ├── __init__.py
│   ├── sentiment_model.py           # Sentiment classifier
│   ├── engagement_predictor.py      # Engagement prediction
│   └── model_utils.py               # Model utilities
│
├── 📁 mlops/                         # MLOps components
│   ├── __init__.py
│   ├── training_pipeline.py         # Training automation
│   ├── monitoring.py                # Model monitoring
│   ├── drift_detection.py           # Data drift detection
│   └── retraining.py                # Auto-retraining
│
├── 📁 dashboard/                     # Visualization
│   ├── app.py                       # Main dashboard (Streamlit)
│   ├── components/                  # Dashboard components
│   │   ├── sentiment_viz.py
│   │   ├── engagement_viz.py
│   │   └── trends_viz.py
│   └── assets/                      # Static files
│       ├── style.css
│       └── logo.png
│
├── 📁 notebooks/                     # Jupyter notebooks
│   ├── 01_data_exploration.ipynb
│   ├── 02_sentiment_analysis.ipynb
│   ├── 03_engagement_analysis.ipynb
│   └── 04_model_development.ipynb
│
├── 📁 tests/                         # Unit tests
│   ├── __init__.py
│   ├── test_scraper.py
│   ├── test_preprocessing.py
│   └── test_models.py
│
├── 📁 configs/                       # Configuration files
│   ├── config.yaml                  # Main config
│   ├── model_config.yaml            # Model parameters
│   └── scraping_config.yaml         # Scraping settings
│
├── 📁 logs/                          # Log files
│   ├── scraping.log
│   ├── training.log
│   └── monitoring.log
│
├── 📁 docker/                        # Docker setup
│   ├── Dockerfile
│   ├── docker-compose.yml
│   └── .dockerignore
│
├── 📁 .github/                       # CI/CD
│   └── workflows/
│       ├── test.yml
│       ├── deploy.yml
│       └── train.yml
│
├── 📄 requirements.txt               # Python dependencies
├── 📄 README.md                      # Project documentation
├── 📄 .env.example                   # Environment variables template
├── 📄 .gitignore                     # Git ignore rules
├── 📄 setup.py                       # Package setup
└── 📄 Makefile                       # Common commands

```

---

## 🚀 Quick Setup Commands

### 1. Initial Setup
```bash
# Clone/create project
mkdir indopopbase-analytics
cd indopopbase-analytics

# Create folder structure
mkdir -p data/{raw,processed,models}
mkdir -p scrapers preprocessing analysis models mlops dashboard notebooks tests configs logs

# Initialize git
git init

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt
```

### 2. Run Scraper
```bash
# Test scrapers
python scrapers/test_scraper.py

# Run main scraper
python scrapers/quick_scraper.py
```

### 3. Data Processing
```bash
# Clean data
python preprocessing/cleaner.py

# Preprocess text
python preprocessing/text_processor.py
```

### 4. Analysis
```bash
# Sentiment analysis
python analysis/sentiment_analysis.py

# Engagement analysis
python analysis/engagement_analysis.py
```

### 5. Run Dashboard
```bash
streamlit run dashboard/app.py
```

---

## 📝 Configuration Files

### config.yaml
```yaml
# Project Configuration

project:
  name: "IndoPopBase Analytics"
  version: "1.0.0"
  target_account: "IndoPopBase"

scraping:
  max_tweets: 1000
  max_mentions: 500
  since_date: "2024-01-01"
  update_frequency: "daily"  # daily, weekly
  
data:
  raw_dir: "data/raw"
  processed_dir: "data/processed"
  models_dir: "data/models"

preprocessing:
  remove_urls: true
  remove_mentions: false
  remove_hashtags: false
  lowercase: true
  remove_stopwords: true
  language: "indonesian"

models:
  sentiment:
    model_name: "indobert"
    threshold: 0.5
  engagement:
    features: ["hour", "day_of_week", "text_length", "hashtag_count"]
    model_type: "random_forest"

mlops:
  experiment_tracking: "mlflow"
  model_registry: true
  monitoring_enabled: true
  drift_threshold: 0.1
  retraining_schedule: "weekly"

dashboard:
  host: "0.0.0.0"
  port: 8501
  theme: "light"
```

### .env.example
```bash
# Environment Variables Template
# Copy to .env and fill in your values

# Twitter Credentials (if using API)
TWITTER_API_KEY=your_api_key_here
TWITTER_API_SECRET=your_api_secret_here
TWITTER_ACCESS_TOKEN=your_access_token_here
TWITTER_ACCESS_SECRET=your_access_secret_here

# Database (optional)
DATABASE_URL=postgresql://user:pass@localhost:5432/dbname

# MLflow (optional)
MLFLOW_TRACKING_URI=http://localhost:5000

# Other
LOG_LEVEL=INFO
DEBUG_MODE=false
```

### .gitignore
```
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
env/
ENV/

# Data files
data/raw/*.csv
data/processed/*.csv
*.pkl
*.h5
*.model

# Logs
logs/*.log
*.log

# Environment
.env
.env.local

# IDEs
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# MLflow
mlruns/
mlartifacts/

# Jupyter
.ipynb_checkpoints/
*.ipynb_checkpoints

# Testing
.pytest_cache/
.coverage
htmlcov/

# Docker
*.dockerfile
docker-compose.override.yml
```

---

## 🔧 Makefile (Common Commands)

```makefile
.PHONY: install test scrape clean dashboard

install:
	pip install -r requirements.txt

test:
	python scrapers/test_scraper.py

scrape:
	python scrapers/quick_scraper.py

clean-data:
	python preprocessing/cleaner.py

sentiment:
	python analysis/sentiment_analysis.py

engagement:
	python analysis/engagement_analysis.py

dashboard:
	streamlit run dashboard/app.py

train:
	python models/sentiment_model.py --train

mlflow:
	mlflow ui

docker-build:
	docker build -t indopopbase-analytics .

docker-run:
	docker-compose up

test-unit:
	pytest tests/

lint:
	flake8 scrapers/ analysis/ models/

format:
	black scrapers/ analysis/ models/

clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -rf logs/*.log

help:
	@echo "Available commands:"
	@echo "  make install    - Install dependencies"
	@echo "  make test       - Test scrapers"
	@echo "  make scrape     - Run scraper"
	@echo "  make sentiment  - Run sentiment analysis"
	@echo "  make dashboard  - Run dashboard"
	@echo "  make train      - Train models"
	@echo "  make clean      - Clean cache files"
```

---

## 📋 Step-by-Step Workflow

### Phase 1: Data Collection (Week 1-2)
```bash
# 1. Test scrapers
make test

# 2. Run initial scraping
make scrape

# 3. Verify data
ls -lh data/raw/
```

### Phase 2: Data Preprocessing (Week 2-3)
```bash
# 1. Clean data
python preprocessing/cleaner.py

# 2. Preprocess text
python preprocessing/text_processor.py

# 3. Feature engineering
python preprocessing/feature_engineering.py
```

### Phase 3: Exploratory Analysis (Week 3-4)
```bash
# 1. Open Jupyter
jupyter notebook notebooks/01_data_exploration.ipynb

# 2. Run basic analysis
python analysis/engagement_analysis.py
```

### Phase 4: Model Development (Week 4-6)
```bash
# 1. Train sentiment model
python models/sentiment_model.py --train

# 2. Evaluate model
python models/sentiment_model.py --evaluate

# 3. Track experiments
make mlflow
```

### Phase 5: MLOps Setup (Week 6-8)
```bash
# 1. Setup CI/CD
git add .github/workflows/

# 2. Setup monitoring
python mlops/monitoring.py

# 3. Test pipeline
python mlops/training_pipeline.py --dry-run
```

### Phase 6: Dashboard (Week 8-10)
```bash
# 1. Run dashboard locally
make dashboard

# 2. Deploy
docker-compose up
```

---

## 🐳 Docker Setup

### Dockerfile
```dockerfile
FROM python:3.10-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Expose port
EXPOSE 8501

# Run dashboard
CMD ["streamlit", "run", "dashboard/app.py"]
```

### docker-compose.yml
```yaml
version: '3.8'

services:
  app:
    build: .
    ports:
      - "8501:8501"
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
    environment:
      - LOG_LEVEL=INFO
    restart: unless-stopped

  mlflow:
    image: ghcr.io/mlflow/mlflow:latest
    ports:
      - "5000:5000"
    volumes:
      - ./mlruns:/mlflow/mlruns
    command: mlflow server --host 0.0.0.0 --port 5000
```

---

## 🧪 Testing Strategy

### Unit Tests Structure
```
tests/
├── test_scraper.py          # Test scraping functions
├── test_preprocessing.py    # Test data cleaning
├── test_models.py          # Test ML models
├── test_mlops.py           # Test MLOps components
└── conftest.py             # Pytest fixtures
```

### Run Tests
```bash
# All tests
pytest

# Specific test
pytest tests/test_scraper.py

# With coverage
pytest --cov=scrapers --cov=models
```

---

## 📊 Expected Data Volumes

### Initial Scraping
- Tweets: ~500-1000 tweets
- Mentions: ~200-500 mentions
- File size: ~1-5 MB (CSV)

### After 1 Month
- Tweets: ~3000-5000 tweets
- Mentions: ~1000-2000 mentions
- File size: ~10-20 MB

### Storage Requirements
- Raw data: ~50 MB
- Processed data: ~30 MB
- Models: ~500 MB (if using BERT)
- Logs: ~10 MB
- Total: ~600 MB

---

## 🔒 Security Best Practices

1. **Never commit credentials**
   - Use .env files
   - Add .env to .gitignore

2. **Data Privacy**
   - Anonymize usernames in reports
   - Don't publish raw data
   - Aggregate data only

3. **API Keys**
   - Rotate regularly
   - Use environment variables
   - Set proper permissions

4. **Docker**
   - Don't run as root
   - Use specific versions
   - Scan for vulnerabilities

---

## 📈 Monitoring & Alerting

### What to Monitor
- Scraping success rate
- Data quality metrics
- Model performance (accuracy, F1)
- Data drift
- System resources (CPU, memory)
- API rate limits

### Alerting Rules
```python
# Example: Alert if scraping fails
if scraping_success_rate < 0.8:
    send_alert("Scraping success rate below 80%")

# Alert if model performance drops
if model_accuracy < 0.85:
    send_alert("Model accuracy below threshold")
```

---

## 🎯 Success Metrics

### Technical Metrics
- Data collection: >95% success rate
- Model accuracy: >85%
- Dashboard uptime: >99%
- Pipeline execution time: <10 minutes

### Business Metrics
- Total tweets analyzed: 5000+
- Sentiment trends identified: Clear patterns
- Engagement insights: Actionable recommendations
- Dashboard users: Stakeholders can self-serve

---

## 💡 Next Steps After Setup

1. **Week 1**: Setup environment + initial scraping
2. **Week 2**: Data exploration + cleaning
3. **Week 3**: Sentiment model development
4. **Week 4**: Engagement analysis
5. **Week 5**: MLOps setup
6. **Week 6**: Dashboard development
7. **Week 7**: Testing + refinement
8. **Week 8**: Documentation + presentation

---

**🚀 Ready to start? Run:**
```bash
make install && make test && make scrape
```