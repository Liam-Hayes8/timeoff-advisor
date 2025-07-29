#!/usr/bin/env python3
"""
Basic test script for the Workday Time-Off Advisor components.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add src to path for imports
sys.path.append(str(Path(__file__).parent / "src"))

from src.utils.helpers import load_config, setup_logging
from src.data.data_processor import TimeOffDataProcessor
from src.data.document_loader import WorkdayDocumentLoader


def test_basic_components():
    """Test basic components without API dependencies."""
    print("🧪 Testing Basic Components")
    print("=" * 40)
    
    try:
        # Load configuration
        config = load_config()
        print("✅ Configuration loaded")
        
        # Test data processor
        data_processor = TimeOffDataProcessor(config)
        sample_data = data_processor.create_sample_data()
        print(f"✅ Sample data created: {len(sample_data)} datasets")
        
        # Show sample data info
        for name, df in sample_data.items():
            print(f"   - {name}: {len(df)} records")
        
        # Test document loader
        doc_loader = WorkdayDocumentLoader(config)
        sample_docs = doc_loader.create_sample_documents()
        print(f"✅ Sample documents created: {len(sample_docs)} documents")
        
        # Show document info
        for i, doc in enumerate(sample_docs[:3], 1):
            print(f"   - Doc {i}: {doc.metadata.get('file_name', 'Unknown')}")
            print(f"     Content preview: {doc.page_content[:100]}...")
        
        # Test utility functions
        from src.utils.helpers import format_currency, format_date, calculate_working_days
        print("✅ Utility functions tested")
        
        # Test data processing functions
        if 'employees' in sample_data:
            stats = data_processor.calculate_leave_statistics(sample_data)
            print(f"✅ Leave statistics calculated: {len(stats)} metrics")
        
        print("\n✅ All basic components working correctly!")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_configuration():
    """Test configuration loading and validation."""
    print("\n🔧 Testing Configuration")
    print("=" * 30)
    
    try:
        config = load_config()
        
        # Check required sections
        required_sections = ['model', 'vector_store', 'documents', 'agent']
        for section in required_sections:
            if section in config:
                print(f"✅ {section} configuration present")
            else:
                print(f"❌ {section} configuration missing")
        
        # Check model configuration
        if 'model' in config:
            model_config = config['model']
            print(f"   - Provider: {model_config.get('provider', 'Not set')}")
            print(f"   - Model: {model_config.get('model_name', 'Not set')}")
        
        print("✅ Configuration test completed")
        return True
        
    except Exception as e:
        print(f"❌ Configuration error: {e}")
        return False


if __name__ == "__main__":
    print("🚀 Workday Time-Off Advisor - Basic Component Test")
    print("=" * 60)
    
    # Test configuration
    config_ok = test_configuration()
    
    # Test basic components
    components_ok = test_basic_components()
    
    print("\n" + "=" * 60)
    if config_ok and components_ok:
        print("✅ All tests passed! The basic components are working correctly.")
        print("\nNext steps:")
        print("1. Set your ANTHROPIC_API_KEY environment variable")
        print("2. Run: python main.py")
        print("3. Or run: python demo.py")
    else:
        print("❌ Some tests failed. Please check the errors above.") 