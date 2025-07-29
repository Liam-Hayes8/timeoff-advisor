#!/usr/bin/env python3
"""
Startup script for the Workday Time-Off Advisor Web Application.
"""

import os
import sys
from pathlib import Path

# Add src to path for imports
sys.path.append(str(Path(__file__).parent / "src"))

def main():
    """Start the web application."""
    print("🚀 Starting Workday Time-Off Advisor Web Application...")
    print("=" * 60)
    
    # Check if virtual environment is activated
    if not hasattr(sys, 'real_prefix') and not (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("⚠️  Warning: Virtual environment not detected.")
        print("   It's recommended to activate the virtual environment first:")
        print("   source venv/bin/activate")
        print()
    
    try:
        # Import and run the Flask app
        from app import app
        
        print("✅ Web application started successfully!")
        print("🌐 Open your browser and go to: http://localhost:8080")
        print("📝 API Documentation:")
        print("   - POST /api/query - Submit queries")
        print("   - GET /api/stats - System statistics")
        print("   - GET /api/suggestions - Query suggestions")
        print("   - GET /api/knowledge-base - Knowledge base info")
        print()
        print("💡 Try asking questions like:")
        print("   • What is the PTO policy?")
        print("   • How do I request time off?")
        print("   • What holidays does the company observe?")
        print("   • Can you show me employee statistics?")
        print()
        print("🛑 Press Ctrl+C to stop the server")
        print("=" * 60)
        
        # Run the Flask app
        app.run(debug=True, host='0.0.0.0', port=8080)
        
    except ImportError as e:
        print(f"❌ Error importing Flask app: {e}")
        print("   Make sure all dependencies are installed:")
        print("   pip install -r requirements.txt")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error starting web application: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 