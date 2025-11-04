#!/bin/bash
# Setup script for Smart JPEG Renamer

echo "🚀 Setting up Smart JPEG Renamer..."

# Check Python version
echo "📋 Checking Python version..."
python3 --version

# Create virtual environment (optional but recommended)
echo "🔧 Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "✅ Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "📦 Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "📚 Installing dependencies..."
pip install -r requirements.txt

# Create secrets directory if not exists
echo "🔑 Setting up secrets directory..."
mkdir -p .streamlit

# Check if secrets.toml exists
if [ ! -f .streamlit/secrets.toml ]; then
    echo "⚠️  Creating .streamlit/secrets.toml from example..."
    cp .streamlit/secrets.example.toml .streamlit/secrets.toml
    echo "⚠️  Please edit .streamlit/secrets.toml and add your GEMINI_API_KEY"
fi

# Run tests
echo "🧪 Running tests..."
python3 tests/test_naming.py
python3 tests/test_schema.py

echo ""
echo "✅ Setup complete!"
echo ""
echo "📝 Next steps:"
echo "1. Edit .streamlit/secrets.toml and add your GEMINI_API_KEY"
echo "2. Run the app with: streamlit run app.py"
echo ""

