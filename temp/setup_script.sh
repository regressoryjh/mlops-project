#!/bin/bash

# IndoPopBase Analytics - Setup Script
# Run: bash setup.sh

echo "======================================================================"
echo "🐦 IndoPopBase Analytics - Automated Setup"
echo "======================================================================"
echo ""

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check Python
echo "🔍 Checking Python installation..."
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 is not installed${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Python 3 found${NC}"

# Check Python version
PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
echo "   Version: $PYTHON_VERSION"

# Create project structure
echo ""
echo "📁 Creating project structure..."
mkdir -p data/raw
mkdir -p data/processed
mkdir -p models
mkdir -p logs
mkdir -p scrapers
mkdir -p preprocessing
mkdir -p analysis
mkdir -p mlops
mkdir -p docker
mkdir -p .github/workflows
mkdir -p tests

echo -e "${GREEN}✅ Directories created${NC}"

# Create virtual environment
echo ""
echo "🔧 Creating virtual environment..."
python3 -m venv venv

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Virtual environment created${NC}"
else
    echo -e "${RED}❌ Failed to create virtual environment${NC}"
    exit 1
fi

# Activate virtual environment
echo ""
echo "🔄 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo ""
echo "⬆️ Upgrading pip..."
pip install --upgrade pip > /dev/null 2>&1

# Install dependencies
echo ""
echo "📦 Installing dependencies..."
echo "   This may take a few minutes..."

pip install pandas numpy tqdm > /dev/null 2>&1
echo -e "${BLUE}   ⏳ Installed: pandas, numpy, tqdm${NC}"

pip install ntscraper > /dev/null 2>&1
echo -e "${BLUE}   ⏳ Installed: ntscraper${NC}"

pip install textblob > /dev/null 2>&1
echo -e "${BLUE}   ⏳ Installed: textblob${NC}"

pip install streamlit plotly > /dev/null 2>&1
echo -e "${BLUE}   ⏳ Installed: streamlit, plotly${NC}"

pip install scikit-learn > /dev/null 2>&1
echo -e "${BLUE}   ⏳ Installed: scikit-learn${NC}"

pip install fastapi uvicorn > /dev/null 2>&1
echo -e "${BLUE}   ⏳ Installed: fastapi, uvicorn${NC}"

echo -e "${GREEN}✅ All dependencies installed${NC}"

# Create .gitignore
echo ""
echo "📝 Creating .gitignore..."
cat > .gitignore << 'EOF'
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
env/
ENV/

# Data
data/raw/*.csv
data/processed/*.csv
*.pkl
*.h5

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

# OS
.DS_Store
Thumbs.db

# MLflow
mlruns/
mlartifacts/

# Jupyter
.ipynb_checkpoints/

# Docker
*.dockerfile
docker-compose.override.yml
EOF

echo -e "${GREEN}✅ .gitignore created${NC}"

# Create .env file
echo ""
echo "🔐 Creating .env file..."
cat > .env << 'EOF'
# Environment Variables
DATABASE_URL=postgresql://admin:admin123@localhost:5432/indopopbase
LOG_LEVEL=INFO
DEBUG_MODE=false
EOF

echo -e "${GREEN}✅ .env file created${NC}"

# Initialize git
echo ""
echo "📚 Initializing git repository..."
if [ ! -d ".git" ]; then
    git init
    git add .
    git commit -m "Initial commit: IndoPopBase Analytics project"
    echo -e "${GREEN}✅ Git repository initialized${NC}"
else
    echo -e "${BLUE}ℹ️  Git repository already exists${NC}"
fi

# Create run script
echo ""
echo "🚀 Creating run script..."
cat > run.sh << 'EOF'
#!/bin/bash

# Quick run script for IndoPopBase Analytics

source venv/bin/activate

echo "======================================================================"
echo "🐦 IndoPopBase Analytics - Quick Run"
echo "======================================================================"
echo ""
echo "Select option:"
echo "1. Run scraper"
echo "2. Process data"
echo "3. Run sentiment analysis"
echo "4. Run engagement analysis"
echo "5. Run dashboard"
echo "6. Run all"
echo ""
read -p "Enter option (1-6): " option

case $option in
    1)
        echo "🔄 Running scraper..."
        python scrapers/quick_scraper.py
        ;;
    2)
        echo "🧹 Processing data..."
        python data_cleaner.py
        ;;
    3)
        echo "🎭 Running sentiment analysis..."
        python sentiment_analyzer.py
        ;;
    4)
        echo "📊 Running engagement analysis..."
        python engagement_analyzer.py
        ;;
    5)
        echo "📱 Starting dashboard..."
        streamlit run dashboard.py
        ;;
    6)
        echo "🚀 Running full pipeline..."
        python scrapers/quick_scraper.py
        python data_cleaner.py
        python sentiment_analyzer.py
        python engagement_analyzer.py
        streamlit run dashboard.py
        ;;
    *)
        echo "❌ Invalid option"
        ;;
esac
EOF

chmod +x run.sh
echo -e "${GREEN}✅ Run script created${NC}"

# Summary
echo ""
echo "======================================================================"
echo "✅ Setup Complete!"
echo "======================================================================"
echo ""
echo "📋 Next Steps:"
echo ""
echo "1. Place your scraped CSV files in data/ folder"
echo "   OR run the scraper:"
echo "   ${BLUE}./run.sh${NC} (select option 1)"
echo ""
echo "2. Process the data:"
echo "   ${BLUE}./run.sh${NC} (select option 2-4)"
echo ""
echo "3. Run the dashboard:"
echo "   ${BLUE}./run.sh${NC} (select option 5)"
echo ""
echo "📦 Using Docker:"
echo "   ${BLUE}docker-compose up${NC}"
echo ""
echo "🔗 Useful URLs:"
echo "   Dashboard: http://localhost:8501"
echo "   API: http://localhost:8000"
echo "   MLflow: http://localhost:5000"
echo ""
echo "======================================================================"
echo "🎉 Happy Analyzing!"
echo "======================================================================"
