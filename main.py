#!/usr/bin/env python3
"""
Workday Time-Off Advisor - Main Application Entry Point

This application provides an intelligent agent for Workday time-off policy questions
using LangChain, Claude, and retrieval-augmented generation.
"""

import os
import sys
import logging
from pathlib import Path
from dotenv import load_dotenv

# Add src to path for imports
sys.path.append(str(Path(__file__).parent / "src"))

from src.agent.timeoff_advisor import TimeOffAdvisor
from src.utils.helpers import setup_logging, load_config

def main():
    """Main application entry point."""
    # Load environment variables
    load_dotenv()
    
    # Setup logging
    setup_logging()
    logger = logging.getLogger(__name__)
    
    # Load configuration
    config = load_config()
    
    # Initialize the Time-Off Advisor
    advisor = TimeOffAdvisor(config)
    
    # Start interactive session
    print("\n" + "="*60)
    print("🚀 Workday Time-Off Advisor")
    print("="*60)
    print(config['ui']['welcome_message'])
    print("\nType 'quit' or 'exit' to end the session.")
    print("-" * 60)
    
    try:
        while True:
            user_input = input("\n💬 You: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("\n👋 Thank you for using the Workday Time-Off Advisor!")
                break
            
            if not user_input:
                continue
            
            # Get response from advisor
            response = advisor.get_response(user_input)
            print(f"\n🤖 Advisor: {response}")
            
    except KeyboardInterrupt:
        print("\n\n👋 Session ended. Goodbye!")
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        print(f"\n❌ An error occurred: {e}")

if __name__ == "__main__":
    main() 