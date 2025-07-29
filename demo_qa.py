#!/usr/bin/env python3
"""
Demo script showcasing the Workday Time-Off Advisor's retrieval-augmented QA capabilities.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add src to path for imports
sys.path.append(str(Path(__file__).parent / "src"))

from src.utils.helpers import load_config, setup_logging
from simple_advisor import SimpleTimeOffAdvisor


def run_qa_demo():
    """Run a demo showcasing the QA capabilities."""
    print("🚀 Workday Time-Off Advisor - Retrieval-Augmented QA Demo")
    print("=" * 60)
    
    # Load configuration and setup
    load_dotenv()
    setup_logging()
    config = load_config()
    
    # Initialize advisor
    advisor = SimpleTimeOffAdvisor(config)
    
    # Show system stats
    stats = advisor.get_system_stats()
    print(f"📊 System Statistics:")
    print(f"• Agent: {stats['agent_name']}")
    print(f"• Documents: {stats['vector_store_stats']['total_documents']}")
    print(f"• Employees: {stats['data_stats']['total_employees']}")
    print(f"• Requests: {stats['data_stats']['total_requests']}")
    print()
    
    # Demo questions covering different aspects of retrieval-augmented QA
    demo_questions = [
        {
            "question": "What is the PTO policy?",
            "category": "Policy Retrieval",
            "expected": "Should retrieve policy overview and leave balance information"
        },
        {
            "question": "How do I request time off?",
            "category": "Process Retrieval", 
            "expected": "Should retrieve vacation request process steps"
        },
        {
            "question": "What holidays does the company observe?",
            "category": "Schedule Retrieval",
            "expected": "Should retrieve holiday schedule information"
        },
        {
            "question": "How much PTO do I have?",
            "category": "Balance Retrieval",
            "expected": "Should retrieve leave balance information and sample data"
        },
        {
            "question": "What's the process for sick leave?",
            "category": "Policy Retrieval",
            "expected": "Should retrieve sick leave policy information"
        },
        {
            "question": "Can you show me employee statistics?",
            "category": "Data Analysis",
            "expected": "Should retrieve and analyze employee data"
        }
    ]
    
    print("🤖 Retrieval-Augmented QA Demo Questions")
    print("=" * 50)
    
    for i, demo in enumerate(demo_questions, 1):
        print(f"\n{i}. {demo['question']}")
        print(f"   Category: {demo['category']}")
        print(f"   Expected: {demo['expected']}")
        print("-" * 50)
        
        # Get response
        response = advisor.get_response(demo['question'])
        
        # Format response for display
        lines = response.split('\n')
        formatted_response = '\n'.join([f"   {line}" for line in lines])
        print(f"Response:\n{formatted_response}")
        
        # Show what was retrieved
        print(f"\n📋 Retrieved Information:")
        if demo['category'] == "Policy Retrieval":
            print("   • Policy documents")
            print("   • Guidelines and rules")
        elif demo['category'] == "Process Retrieval":
            print("   • Step-by-step procedures")
            print("   • Workflow information")
        elif demo['category'] == "Schedule Retrieval":
            print("   • Calendar information")
            print("   • Date-specific data")
        elif demo['category'] == "Balance Retrieval":
            print("   • Current balance data")
            print("   • Historical information")
        elif demo['category'] == "Data Analysis":
            print("   • Statistical summaries")
            print("   • Employee data")
        
        print()
    
    # Show query suggestions
    print("💡 Query Suggestions")
    print("=" * 30)
    suggestions = advisor.get_suggestions("How much PTO do I have?")
    for i, suggestion in enumerate(suggestions, 1):
        print(f"{i}. {suggestion}")
    
    print(f"\n✅ Demo completed successfully!")
    print(f"\n🎯 Key Features Demonstrated:")
    print(f"• Multi-document retrieval")
    print(f"• Structured data analysis")
    print(f"• Policy and procedure lookup")
    print(f"• Statistical data processing")
    print(f"• Context-aware responses")


def showcase_retrieval_capabilities():
    """Showcase the retrieval capabilities in detail."""
    print("\n🔍 Retrieval-Augmented QA Capabilities")
    print("=" * 50)
    
    # Load configuration
    config = load_config()
    advisor = SimpleTimeOffAdvisor(config)
    
    # Show knowledge base structure
    print("📚 Knowledge Base Structure:")
    kb = advisor.knowledge_base
    
    print(f"• Documents: {len(kb['documents'])}")
    for doc_name in kb['documents'].keys():
        print(f"  - {doc_name}")
    
    print(f"• Policies: {len(kb['policies'])}")
    for policy_name in kb['policies'].keys():
        print(f"  - {policy_name}")
    
    print(f"• Procedures: {len(kb['procedures'])}")
    for proc_name in kb['procedures'].keys():
        print(f"  - {proc_name}")
    
    # Show data summary
    if kb['data_summary']:
        print(f"• Data Summary:")
        for key, value in kb['data_summary'].items():
            print(f"  - {key}: {value}")
    
    print(f"\n📊 Sample Data Overview:")
    sample_data = advisor.sample_data
    for dataset_name, df in sample_data.items():
        print(f"• {dataset_name}: {len(df)} records")
        if len(df) > 0:
            print(f"  Columns: {list(df.columns)}")
            print(f"  Sample: {df.head(1).to_dict('records')[0] if len(df) > 0 else 'No data'}")


if __name__ == "__main__":
    # Run the main demo
    run_qa_demo()
    
    # Showcase retrieval capabilities
    showcase_retrieval_capabilities()
    
    print(f"\n🎉 Retrieval-Augmented QA Demo Complete!")
    print(f"\nNext steps:")
    print(f"1. Add your ANTHROPIC_API_KEY to .env for full LLM integration")
    print(f"2. Run: python simple_advisor.py for interactive mode")
    print(f"3. Explore the config/config.yaml for customization") 