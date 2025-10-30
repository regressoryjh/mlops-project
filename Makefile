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