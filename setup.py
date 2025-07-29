#!/usr/bin/env python3
"""
Setup script for the Workday Time-Off Advisor.

This script helps users set up the project and install dependencies.
"""

import os
import sys
import subprocess
from pathlib import Path


def check_python_version():
    """Check if Python version is compatible."""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        return False
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detected")
    return True


def install_dependencies():
    """Install project dependencies."""
    print("📦 Installing dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing dependencies: {e}")
        return False


def create_directories():
    """Create necessary directories."""
    directories = [
        "data/workday_docs",
        "data/sample_data",
        "logs",
        "chroma_db"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"✅ Created directory: {directory}")


def create_env_file():
    """Create .env file if it doesn't exist."""
    env_file = Path(".env")
    if not env_file.exists():
        env_content = """# Workday Time-Off Advisor Environment Variables

# Required: Anthropic API Key for Claude
ANTHROPIC_API_KEY=your-anthropic-api-key-here

# Optional: Logging level (DEBUG, INFO, WARNING, ERROR)
LOG_LEVEL=INFO

# Optional: Custom configuration file path
CONFIG_PATH=config/config.yaml
"""
        env_file.write_text(env_content)
        print("✅ Created .env file")
        print("⚠️  Please edit .env file and add your Anthropic API key")
    else:
        print("✅ .env file already exists")


def run_tests():
    """Run basic tests to verify setup."""
    print("🧪 Running basic tests...")
    try:
        # Test configuration loading
        sys.path.append(str(Path(__file__).parent / "src"))
        from src.utils.helpers import load_config
        config = load_config()
        print("✅ Configuration loaded successfully")
        
        # Test data processor
        from src.data.data_processor import TimeOffDataProcessor
        data_processor = TimeOffDataProcessor(config)
        sample_data = data_processor.create_sample_data()
        print(f"✅ Sample data created: {len(sample_data)} datasets")
        
        # Test document loader
        from src.data.document_loader import WorkdayDocumentLoader
        doc_loader = WorkdayDocumentLoader(config)
        sample_docs = doc_loader.create_sample_documents()
        print(f"✅ Sample documents created: {len(sample_docs)} documents")
        
        print("✅ All tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False


def main():
    """Main setup function."""
    print("🚀 Workday Time-Off Advisor Setup")
    print("=" * 40)
    
    # Check Python version
    if not check_python_version():
        return
    
    # Create directories
    create_directories()
    
    # Install dependencies
    if not install_dependencies():
        print("❌ Setup failed due to dependency installation error")
        return
    
    # Create .env file
    create_env_file()
    
    # Run tests
    if not run_tests():
        print("❌ Setup failed due to test failures")
        return
    
    print("\n🎉 Setup completed successfully!")
    print("\nNext steps:")
    print("1. Edit .env file and add your Anthropic API key")
    print("2. Run: python main.py")
    print("3. Or run: python demo.py --quick")
    print("\nFor help, see README.md")


if __name__ == "__main__":
    main() 