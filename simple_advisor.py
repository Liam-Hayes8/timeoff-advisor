#!/usr/bin/env python3
"""
Simplified Workday Time-Off Advisor

This version works with the current dependency setup and provides
the core functionality without the complex LangChain agent setup.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
import json

# Add src to path for imports
sys.path.append(str(Path(__file__).parent / "src"))

from src.utils.helpers import load_config, setup_logging
from src.data.data_processor import TimeOffDataProcessor
from src.data.document_loader import WorkdayDocumentLoader


class SimpleTimeOffAdvisor:
    """Simplified Time-Off Advisor that works with current dependencies."""
    
    def __init__(self, config):
        """Initialize the advisor."""
        self.config = config
        self.data_processor = TimeOffDataProcessor(config)
        self.doc_loader = WorkdayDocumentLoader(config)
        
        # Load sample data
        self.sample_data = self.data_processor.create_sample_data()
        self.sample_documents = self.doc_loader.create_sample_documents()
        
        # Create knowledge base
        self.knowledge_base = self._create_knowledge_base()
    
    def _create_knowledge_base(self):
        """Create a simple knowledge base from documents and data."""
        knowledge = {
            'documents': {},
            'data_summary': {},
            'policies': {},
            'procedures': {}
        }
        
        # Process documents
        for doc in self.sample_documents:
            content = doc.page_content.lower()
            metadata = doc.metadata
            
            if 'policy' in content or 'overview' in content:
                knowledge['policies'][metadata.get('file_name', 'unknown')] = doc.page_content
            elif 'process' in content or 'request' in content:
                knowledge['procedures'][metadata.get('file_name', 'unknown')] = doc.page_content
            else:
                knowledge['documents'][metadata.get('file_name', 'unknown')] = doc.page_content
        
        # Process data summary
        if 'employees' in self.sample_data:
            knowledge['data_summary']['total_employees'] = len(self.sample_data['employees'])
            knowledge['data_summary']['average_pto'] = self.sample_data['leave_balances']['pto_balance'].mean()
            knowledge['data_summary']['total_requests'] = len(self.sample_data['timeoff_requests'])
        
        return knowledge
    
    def get_response(self, query: str) -> str:
        """Get a response to a user query."""
        query_lower = query.lower()
        
        # Simple keyword-based response system
        if any(word in query_lower for word in ['pto', 'vacation', 'time off', 'leave']):
            return self._handle_pto_query(query)
        elif any(word in query_lower for word in ['policy', 'rule', 'guideline']):
            return self._handle_policy_query(query)
        elif any(word in query_lower for word in ['request', 'submit', 'apply']):
            return self._handle_request_query(query)
        elif any(word in query_lower for word in ['holiday', 'holidays']):
            return self._handle_holiday_query(query)
        elif any(word in query_lower for word in ['sick', 'illness']):
            return self._handle_sick_leave_query(query)
        elif any(word in query_lower for word in ['balance', 'remaining', 'available']):
            return self._handle_balance_query(query)
        elif any(word in query_lower for word in ['statistic', 'summary', 'overview']):
            return self._handle_statistics_query(query)
        else:
            return self._handle_general_query(query)
    
    def _handle_pto_query(self, query: str) -> str:
        """Handle PTO-related queries."""
        response = "Based on the Workday Time-Off Policy:\n\n"
        
        if 'policy_overview.txt' in self.knowledge_base['policies']:
            response += self.knowledge_base['policies']['policy_overview.txt']
        
        if 'leave_balance.txt' in self.knowledge_base['documents']:
            response += "\n\n" + self.knowledge_base['documents']['leave_balance.txt']
        
        return response
    
    def _handle_policy_query(self, query: str) -> str:
        """Handle policy-related queries."""
        response = "Workday Time-Off Policies:\n\n"
        
        for filename, content in self.knowledge_base['policies'].items():
            response += f"📄 {filename}:\n{content}\n\n"
        
        return response
    
    def _handle_request_query(self, query: str) -> str:
        """Handle request-related queries."""
        response = "Time-Off Request Process:\n\n"
        
        if 'vacation_process.txt' in self.knowledge_base['procedures']:
            response += self.knowledge_base['procedures']['vacation_process.txt']
        
        return response
    
    def _handle_holiday_query(self, query: str) -> str:
        """Handle holiday-related queries."""
        response = "Company Holiday Schedule:\n\n"
        
        if 'holiday_schedule.txt' in self.knowledge_base['documents']:
            response += self.knowledge_base['documents']['holiday_schedule.txt']
        
        return response
    
    def _handle_sick_leave_query(self, query: str) -> str:
        """Handle sick leave queries."""
        response = "Sick Leave Information:\n\n"
        
        if 'sick_leave.txt' in self.knowledge_base['documents']:
            response += self.knowledge_base['documents']['sick_leave.txt']
        
        return response
    
    def _handle_balance_query(self, query: str) -> str:
        """Handle balance-related queries."""
        response = "Leave Balance Information:\n\n"
        
        if 'leave_balance.txt' in self.knowledge_base['documents']:
            response += self.knowledge_base['documents']['leave_balance.txt']
        
        # Add sample data summary
        if self.knowledge_base['data_summary']:
            response += f"\n📊 Sample Data Summary:\n"
            response += f"• Total Employees: {self.knowledge_base['data_summary']['total_employees']}\n"
            response += f"• Average PTO Balance: {self.knowledge_base['data_summary']['average_pto']:.1f} days\n"
            response += f"• Total Requests: {self.knowledge_base['data_summary']['total_requests']}\n"
        
        return response
    
    def _handle_statistics_query(self, query: str) -> str:
        """Handle statistics queries."""
        response = "Workday Time-Off Statistics:\n\n"
        
        if self.knowledge_base['data_summary']:
            response += f"📊 Employee Statistics:\n"
            response += f"• Total Employees: {self.knowledge_base['data_summary']['total_employees']}\n"
            response += f"• Average PTO Balance: {self.knowledge_base['data_summary']['average_pto']:.1f} days\n"
            response += f"• Total Time-Off Requests: {self.knowledge_base['data_summary']['total_requests']}\n"
        
        # Add sample employee data
        if 'employees' in self.sample_data:
            response += f"\n👥 Sample Employee Data:\n"
            for _, employee in self.sample_data['employees'].head(3).iterrows():
                response += f"• {employee['name']} (ID: {employee['employee_id']}) - {employee['department']}\n"
        
        return response
    
    def _handle_general_query(self, query: str) -> str:
        """Handle general queries."""
        response = "I can help you with Workday Time-Off questions. Here are some topics I can assist with:\n\n"
        response += "• PTO and vacation policies\n"
        response += "• How to request time off\n"
        response += "• Holiday schedules\n"
        response += "• Sick leave policies\n"
        response += "• Leave balance information\n"
        response += "• Employee statistics\n\n"
        response += "Please ask a specific question about any of these topics!"
        
        return response
    
    def get_suggestions(self, query: str) -> list:
        """Get query suggestions based on the current query."""
        suggestions = [
            "What is the PTO policy?",
            "How do I request time off?",
            "What holidays does the company observe?",
            "How much PTO do I have?",
            "What's the process for sick leave?",
            "Can you show me employee statistics?"
        ]
        
        # Filter suggestions based on query
        query_lower = query.lower()
        if any(word in query_lower for word in ['pto', 'vacation']):
            return [s for s in suggestions if 'pto' in s.lower() or 'vacation' in s.lower()]
        elif any(word in query_lower for word in ['request', 'submit']):
            return [s for s in suggestions if 'request' in s.lower()]
        elif any(word in query_lower for word in ['holiday']):
            return [s for s in suggestions if 'holiday' in s.lower()]
        else:
            return suggestions[:3]
    
    def get_system_stats(self) -> dict:
        """Get system statistics."""
        return {
            'agent_name': self.config.get('agent', {}).get('name', 'Simple Time-Off Advisor'),
            'model': self.config.get('model', {}).get('model_name', 'N/A'),
            'vector_store_stats': {
                'total_documents': len(self.sample_documents)
            },
            'data_stats': {
                'total_datasets': len(self.sample_data),
                'total_employees': len(self.sample_data.get('employees', [])),
                'total_requests': len(self.sample_data.get('timeoff_requests', []))
            }
        }


def run_interactive_demo():
    """Run an interactive demo of the Time-Off Advisor."""
    print("🚀 Workday Time-Off Advisor - Interactive Demo")
    print("=" * 50)
    print("Type 'quit' to exit, 'help' for suggestions\n")
    
    # Load configuration
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
    
    while True:
        try:
            query = input("🤖 You: ").strip()
            
            if query.lower() in ['quit', 'exit', 'q']:
                print("👋 Goodbye!")
                break
            elif query.lower() == 'help':
                suggestions = advisor.get_suggestions("")
                print("💡 Try asking:")
                for i, suggestion in enumerate(suggestions, 1):
                    print(f"   {i}. {suggestion}")
                print()
                continue
            elif not query:
                continue
            
            # Get response
            response = advisor.get_response(query)
            print(f"🤖 Advisor: {response}")
            print()
            
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")


if __name__ == "__main__":
    # Load environment variables
    load_dotenv()
    
    # Setup logging
    setup_logging()
    
    # Run the interactive demo
    run_interactive_demo() 