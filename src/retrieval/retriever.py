"""
Retriever that combines vector search with data processing for comprehensive retrieval.
"""

import logging
from typing import List, Dict, Any, Optional
from langchain_core.documents import Document
from langchain.retrievers import ContextualCompressionRetriever
from langchain.retrievers.document_compressors import LLMChainExtractor

from .vector_store import WorkdayVectorStore
from ..data.data_processor import TimeOffDataProcessor

logger = logging.getLogger(__name__)


class WorkdayRetriever:
    """Comprehensive retriever for Workday time-off information."""
    
    def __init__(self, config: Dict[str, Any], vector_store: WorkdayVectorStore, data_processor: TimeOffDataProcessor):
        """
        Initialize the retriever.
        
        Args:
            config: Configuration dictionary
            vector_store: Vector store instance
            data_processor: Data processor instance
        """
        self.config = config
        self.vector_store = vector_store
        self.data_processor = data_processor
        self.retrieval_config = config['retrieval']
        
        # Load sample data
        self.sample_data = data_processor.create_sample_data()
    
    def retrieve_relevant_documents(self, query: str) -> Dict[str, Any]:
        """
        Retrieve relevant documents and data for a query.
        
        Args:
            query: User query
            
        Returns:
            Dictionary containing retrieved information
        """
        try:
            # Get relevant documents from vector store
            documents = self.vector_store.similarity_search(query)
            
            # Extract relevant data based on query
            data_results = self._extract_relevant_data(query)
            
            # Combine results
            results = {
                'documents': documents,
                'data': data_results,
                'query': query,
                'total_documents': len(documents),
                'total_data_entries': len(data_results)
            }
            
            logger.info(f"Retrieved {len(documents)} documents and {len(data_results)} data entries for query: {query}")
            return results
            
        except Exception as e:
            logger.error(f"Error retrieving documents: {e}")
            return {'error': str(e)}
    
    def _extract_relevant_data(self, query: str) -> Dict[str, Any]:
        """
        Extract relevant data based on the query.
        
        Args:
            query: User query
            
        Returns:
            Dictionary with relevant data
        """
        query_lower = query.lower()
        data_results = {}
        
        # Check for employee-specific queries
        if any(word in query_lower for word in ['employee', 'balance', 'pto', 'leave']):
            data_results['leave_statistics'] = self.data_processor.calculate_leave_statistics(self.sample_data)
        
        # Check for specific employee queries
        if 'emp' in query_lower or 'employee' in query_lower:
            # Extract employee ID if mentioned
            import re
            emp_match = re.search(r'emp\d+', query_lower)
            if emp_match:
                employee_id = emp_match.group().upper()
                data_results['employee_summary'] = self.data_processor.get_employee_leave_summary(
                    employee_id, self.sample_data
                )
        
        # Check for holiday queries
        if any(word in query_lower for word in ['holiday', 'holidays', 'christmas', 'thanksgiving']):
            data_results['holidays'] = self.sample_data['holidays'].to_dict('records')
        
        # Check for request queries
        if any(word in query_lower for word in ['request', 'approval', 'pending', 'approved']):
            data_results['recent_requests'] = self.sample_data['timeoff_requests'].head(10).to_dict('records')
        
        # Check for policy queries
        if any(word in query_lower for word in ['policy', 'rules', 'guidelines']):
            data_results['policy_summary'] = {
                'total_employees': len(self.sample_data['employees']),
                'average_pto': self.sample_data['leave_balances']['pto_balance'].mean(),
                'total_requests': len(self.sample_data['timeoff_requests'])
            }
        
        return data_results
    
    def format_retrieved_information(self, results: Dict[str, Any]) -> str:
        """
        Format retrieved information into a readable string.
        
        Args:
            results: Retrieved results dictionary
            
        Returns:
            Formatted string with retrieved information
        """
        if 'error' in results:
            return f"Error retrieving information: {results['error']}"
        
        formatted_info = []
        
        # Format documents
        if results.get('documents'):
            formatted_info.append("📄 Relevant Documentation:")
            for i, doc in enumerate(results['documents'][:3], 1):
                content = doc.page_content.strip()[:200] + "..." if len(doc.page_content) > 200 else doc.page_content.strip()
                formatted_info.append(f"{i}. {content}")
        
        # Format data
        data = results.get('data', {})
        
        if 'leave_statistics' in data:
            stats = data['leave_statistics']
            formatted_info.append("\n📊 Leave Statistics:")
            formatted_info.append(f"• Total Employees: {stats['total_employees']}")
            formatted_info.append(f"• Average PTO Balance: {stats['average_pto']:.1f} days")
            formatted_info.append(f"• Pending Requests: {stats['pending_requests']}")
            formatted_info.append(f"• Approved Requests: {stats['approved_requests']}")
        
        if 'employee_summary' in data:
            emp = data['employee_summary']
            if 'error' not in emp:
                formatted_info.append("\n👤 Employee Summary:")
                formatted_info.append(f"• Name: {emp['employee_info']['name']}")
                formatted_info.append(f"• Department: {emp['employee_info']['department']}")
                if emp['leave_balance']:
                    formatted_info.append(f"• PTO Balance: {emp['leave_balance']['pto_balance']} days")
                    formatted_info.append(f"• Sick Balance: {emp['leave_balance']['sick_balance']} days")
        
        if 'holidays' in data:
            formatted_info.append("\n🎉 Company Holidays:")
            for holiday in data['holidays'][:5]:  # Show first 5
                formatted_info.append(f"• {holiday['holiday_name']}: {holiday['date']}")
        
        if 'recent_requests' in data:
            formatted_info.append("\n📋 Recent Time-Off Requests:")
            for req in data['recent_requests'][:3]:  # Show first 3
                formatted_info.append(f"• {req['request_type']}: {req['start_date']} to {req['end_date']} ({req['status']})")
        
        return "\n".join(formatted_info) if formatted_info else "No relevant information found."
    
    def get_context_for_query(self, query: str) -> str:
        """
        Get formatted context for a query.
        
        Args:
            query: User query
            
        Returns:
            Formatted context string
        """
        results = self.retrieve_relevant_documents(query)
        return self.format_retrieved_information(results)
    
    def search_similar_queries(self, query: str) -> List[str]:
        """
        Find similar queries that might be relevant.
        
        Args:
            query: Original query
            
        Returns:
            List of similar query suggestions
        """
        query_lower = query.lower()
        suggestions = []
        
        # Common query patterns
        if 'pto' in query_lower or 'vacation' in query_lower:
            suggestions.extend([
                "How much PTO do I have?",
                "What's my vacation balance?",
                "How do I request PTO?",
                "What's the PTO policy?"
            ])
        
        if 'sick' in query_lower:
            suggestions.extend([
                "How do I report sick leave?",
                "What's the sick leave policy?",
                "How much sick time do I have?"
            ])
        
        if 'holiday' in query_lower:
            suggestions.extend([
                "What holidays does the company observe?",
                "When is the next holiday?",
                "Do I get paid for holidays?"
            ])
        
        if 'request' in query_lower or 'approval' in query_lower:
            suggestions.extend([
                "How do I submit a time-off request?",
                "How long does approval take?",
                "Who approves my requests?"
            ])
        
        # Remove duplicates and limit results
        return list(set(suggestions))[:5]
    
    def get_retrieval_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the retriever.
        
        Returns:
            Dictionary with retrieval statistics
        """
        vector_stats = self.vector_store.get_collection_stats()
        
        stats = {
            'vector_store': vector_stats,
            'sample_data_size': {
                'employees': len(self.sample_data['employees']),
                'leave_balances': len(self.sample_data['leave_balances']),
                'timeoff_requests': len(self.sample_data['timeoff_requests']),
                'holidays': len(self.sample_data['holidays'])
            }
        }
        
        return stats 