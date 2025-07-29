#!/usr/bin/env python3
"""
Demo script for the Workday Time-Off Advisor.

This script demonstrates the key features of the Time-Off Advisor agent.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add src to path for imports
sys.path.append(str(Path(__file__).parent / "src"))

from src.agent.timeoff_advisor import TimeOffAdvisor
from src.utils.helpers import load_config, setup_logging


def run_demo():
    """Run the Time-Off Advisor demo."""
    # Load environment variables
    load_dotenv()
    
    # Setup logging
    setup_logging()
    
    # Load configuration
    config = load_config()
    
    print("🚀 Workday Time-Off Advisor Demo")
    print("=" * 50)
    
    try:
        # Initialize the advisor
        print("Initializing Time-Off Advisor...")
        advisor = TimeOffAdvisor(config)
        print("✅ Advisor initialized successfully!")
        
        # Get system stats
        stats = advisor.get_system_stats()
        print(f"\n📊 System Statistics:")
        print(f"• Agent: {stats['agent_name']}")
        print(f"• Model: {stats['model']}")
        print(f"• Vector Store Documents: {stats['vector_store_stats'].get('total_documents', 0)}")
        
        # Demo questions
        demo_questions = [
            "What is the PTO policy?",
            "How do I request time off?",
            "What holidays does the company observe?",
            "How much PTO do I have?",
            "What's the process for sick leave?",
            "Can you show me employee statistics?"
        ]
        
        print(f"\n🤖 Demo Questions:")
        print("-" * 30)
        
        for i, question in enumerate(demo_questions, 1):
            print(f"\n{i}. {question}")
            print("Response:")
            
            try:
                response = advisor.get_response(question)
                print(f"   {response[:200]}...")
                if len(response) > 200:
                    print(f"   [Response truncated for demo]")
            except Exception as e:
                print(f"   Error: {e}")
        
        # Show suggestions
        print(f"\n💡 Query Suggestions:")
        print("-" * 30)
        suggestions = advisor.get_suggestions("How much PTO do I have?")
        for i, suggestion in enumerate(suggestions[:3], 1):
            print(f"{i}. {suggestion}")
        
        print(f"\n✅ Demo completed successfully!")
        
    except ValueError as e:
        if "Missing required environment variables" in str(e):
            print("❌ Error: ANTHROPIC_API_KEY environment variable is required.")
            print("Please set your Anthropic API key:")
            print("export ANTHROPIC_API_KEY='your-api-key-here'")
        else:
            print(f"❌ Error: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")


def run_quick_test():
    """Run a quick test without API calls."""
    print("🧪 Quick Test (No API Required)")
    print("=" * 40)
    
    try:
        # Load configuration
        config = load_config()
        print("✅ Configuration loaded")
        
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
        
        # Test vector store (without embeddings)
        from src.retrieval.vector_store import WorkdayVectorStore
        vector_store = WorkdayVectorStore(config)
        print("✅ Vector store initialized")
        
        # Test retriever
        from src.retrieval.retriever import WorkdayRetriever
        retriever = WorkdayRetriever(config, vector_store, data_processor)
        print("✅ Retriever initialized")
        
        print("\n✅ All components working correctly!")
        
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Workday Time-Off Advisor Demo")
    parser.add_argument("--quick", action="store_true", help="Run quick test without API calls")
    
    args = parser.parse_args()
    
    if args.quick:
        run_quick_test()
    else:
        run_demo() 