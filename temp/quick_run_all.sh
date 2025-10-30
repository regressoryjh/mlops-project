#!/bin/bash

# ONE-CLICK RUN SCRIPT
# Runs complete pipeline from data to dashboard

echo "======================================================================"
echo "🚀 IndoPopBase Analytics - Complete Pipeline"
echo "======================================================================"
echo ""

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Check if data exists
if [ ! -d "data" ] || [ -z "$(ls -A data/*.csv 2>/dev/null)" ]; then
    echo -e "${YELLOW}⚠️  No data found in data/ directory${NC}"
    echo "Please place your CSV files in the data/ folder first"
    echo ""
    read -p "Do you want to run the scraper now? (y/n): " run_scraper
    
    if [ "$run_scraper" = "y" ]; then
        echo ""
        echo -e "${BLUE}🔄 Step 1/5: Running Scraper...${NC}"
        python scrapers/quick_scraper.py
        
        if [ $? -ne 0 ]; then
            echo -e "${RED}❌ Scraper failed${NC}"
            exit 1
        fi
        echo -e "${GREEN}✅ Scraping completed${NC}"
    else
        echo -e "${RED}❌ Cannot proceed without data${NC}"
        exit 1
    fi
else
    echo -e "${GREEN}✅ Data found${NC}"
fi

# Step 2: Data Cleaning
echo ""
echo -e "${BLUE}🧹 Step 2/5: Cleaning Data...${NC}"
python data_cleaner.py <<EOF
2
EOF

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Data cleaning failed${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Data cleaning completed${NC}"

# Step 3: Sentiment Analysis
echo ""
echo -e "${BLUE}🎭 Step 3/5: Sentiment Analysis...${NC}"
python sentiment_analyzer.py <<EOF
all
EOF

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Sentiment analysis failed${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Sentiment analysis completed${NC}"

# Step 4: Engagement Analysis
echo ""
echo -e "${BLUE}📊 Step 4/5: Engagement Analysis...${NC}"
python engagement_analyzer.py <<EOF
1
EOF

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Engagement analysis failed${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Engagement analysis completed${NC}"

# Step 5: Summary
echo ""
echo "======================================================================"
echo -e "${GREEN}✅ Pipeline Completed Successfully!${NC}"
echo "======================================================================"
echo ""
echo "📊 Results:"
echo "   - Cleaned data: data/processed/"
echo "   - Analysis reports: data/processed/*_report.json"
echo ""
echo "🎯 Next Steps:"
echo ""
echo "1. View Dashboard:"
echo "   ${BLUE}streamlit run dashboard.py${NC}"
echo ""
echo "2. Run with Docker:"
echo "   ${BLUE}docker-compose up${NC}"
echo ""
echo "3. View Results:"
echo "   - Dashboard: http://localhost:8501"
echo "   - MLflow: http://localhost:5000"
echo ""
echo "======================================================================"
echo ""

# Ask if user wants to run dashboard
read -p "Start dashboard now? (y/n): " start_dashboard

if [ "$start_dashboard" = "y" ]; then
    echo ""
    echo -e "${BLUE}📱 Starting Dashboard...${NC}"
    echo "Access at: http://localhost:8501"
    echo ""
    streamlit run dashboard.py
fi
