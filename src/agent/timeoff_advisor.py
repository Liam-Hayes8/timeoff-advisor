"""
Main Time-Off Advisor agent that combines LangChain, Claude, and retrieval-augmented generation.
"""

import os
import logging
from typing import Dict, Any, List, Optional
from langchain_anthropic import ChatAnthropic
from langchain.chains import LLMChain
from langchain_core.documents import Document

from .prompts import (
    CHAT_PROMPT, QA_PROMPT, LEAVE_BALANCE_PROMPT, POLICY_PROMPT,
    REQUEST_PROCESS_PROMPT, HOLIDAY_PROMPT, DATA_ANALYSIS_PROMPT,
    get_prompt_for_query, format_context_for_prompt
)
from ..retrieval.retriever import WorkdayRetriever
from ..retrieval.vector_store import WorkdayVectorStore
from ..data.document_loader import WorkdayDocumentLoader
from ..data.data_processor import TimeOffDataProcessor
from ..utils.helpers import validate_environment

logger = logging.getLogger(__name__)


class TimeOffAdvisor:
    """Main Time-Off Advisor agent."""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the Time-Off Advisor.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.model_config = config['model']
        self.agent_config = config['agent']
        
        # Validate environment
        if not validate_environment():
            raise ValueError("Missing required environment variables")
        
        # Initialize components
        self._initialize_components()
        
        # Initialize conversation history
        self.conversation_history = []
        
        logger.info("Time-Off Advisor initialized successfully")
    
    def _initialize_components(self):
        """Initialize all components of the advisor."""
        # Initialize LLM
        self.llm = ChatAnthropic(
            model=self.model_config['model_name'],
            temperature=self.model_config['temperature'],
            max_tokens=self.model_config['max_tokens'],
            top_p=self.model_config['top_p']
        )
        
        # Initialize document loader
        self.document_loader = WorkdayDocumentLoader(self.config)
        
        # Initialize data processor
        self.data_processor = TimeOffDataProcessor(self.config)
        
        # Initialize vector store
        self.vector_store = WorkdayVectorStore(self.config)
        
        # Initialize retriever
        self.retriever = WorkdayRetriever(self.config, self.vector_store, self.data_processor)
        
        # Initialize chains
        self._initialize_chains()
        
        # Setup vector store
        self._setup_vector_store()
    
    def _initialize_chains(self):
        """Initialize LangChain chains."""
        # Main chat chain
        self.chat_chain = LLMChain(
            llm=self.llm,
            prompt=CHAT_PROMPT
        )
        
        # QA chain
        self.qa_chain = LLMChain(
            llm=self.llm,
            prompt=QA_PROMPT
        )
        
        # Specialized chains
        self.leave_balance_chain = LLMChain(
            llm=self.llm,
            prompt=LEAVE_BALANCE_PROMPT
        )
        
        self.policy_chain = LLMChain(
            llm=self.llm,
            prompt=POLICY_PROMPT
        )
        
        self.request_process_chain = LLMChain(
            llm=self.llm,
            prompt=REQUEST_PROCESS_PROMPT
        )
        
        self.holiday_chain = LLMChain(
            llm=self.llm,
            prompt=HOLIDAY_PROMPT
        )
        
        self.data_analysis_chain = LLMChain(
            llm=self.llm,
            prompt=DATA_ANALYSIS_PROMPT
        )
    
    def _setup_vector_store(self):
        """Setup the vector store with documents."""
        try:
            # Try to load existing vector store
            if not self.vector_store.load_existing_vector_store():
                # Create new vector store with sample documents
                logger.info("Creating new vector store with sample documents")
                sample_docs = self.document_loader.create_sample_documents()
                self.vector_store.create_vector_store(sample_docs)
                self.vector_store.persist()
            
        except Exception as e:
            logger.error(f"Error setting up vector store: {e}")
            raise
    
    def get_response(self, user_input: str) -> str:
        """
        Get a response from the Time-Off Advisor.
        
        Args:
            user_input: User's question or request
            
        Returns:
            Agent's response
        """
        try:
            # Add to conversation history
            self.conversation_history.append({"role": "user", "content": user_input})
            
            # Retrieve relevant context
            retrieval_results = self.retriever.retrieve_relevant_documents(user_input)
            
            # Determine the appropriate chain to use
            chain, formatted_context = self._select_chain_and_format_context(user_input, retrieval_results)
            
            # Generate response
            response = self._generate_response(chain, user_input, formatted_context)
            
            # Add response to conversation history
            self.conversation_history.append({"role": "assistant", "content": response})
            
            # Limit conversation history
            if len(self.conversation_history) > 10:
                self.conversation_history = self.conversation_history[-10:]
            
            return response
            
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return f"I apologize, but I encountered an error while processing your request. Please try again or rephrase your question. Error: {str(e)}"
    
    def _select_chain_and_format_context(self, user_input: str, retrieval_results: Dict[str, Any]) -> tuple:
        """
        Select the appropriate chain and format context for the query.
        
        Args:
            user_input: User's input
            retrieval_results: Results from retrieval
            
        Returns:
            Tuple of (chain, formatted_context)
        """
        query_lower = user_input.lower()
        
        # Determine query type and select appropriate chain
        if any(word in query_lower for word in ['balance', 'pto', 'leave', 'sick', 'personal']):
            chain = self.leave_balance_chain
            context_key = "employee_data"
            
        elif any(word in query_lower for word in ['policy', 'rules', 'guidelines', 'entitled']):
            chain = self.policy_chain
            context_key = "policy_docs"
            
        elif any(word in query_lower for word in ['request', 'submit', 'approval', 'process', 'how to']):
            chain = self.request_process_chain
            context_key = "process_docs"
            
        elif any(word in query_lower for word in ['holiday', 'holidays', 'christmas', 'thanksgiving']):
            chain = self.holiday_chain
            context_key = "holiday_data"
            
        elif any(word in query_lower for word in ['statistics', 'data', 'summary', 'report']):
            chain = self.data_analysis_chain
            context_key = "data_summary"
            
        else:
            chain = self.qa_chain
            context_key = "context"
        
        # Format context for the selected chain
        formatted_context = format_context_for_prompt(context_key, retrieval_results.get('data', {}))
        
        return chain, formatted_context
    
    def _generate_response(self, chain, user_input: str, context: str) -> str:
        """
        Generate response using the selected chain.
        
        Args:
            chain: LangChain chain to use
            user_input: User's input
            context: Formatted context
            
        Returns:
            Generated response
        """
        try:
            # Prepare inputs for the chain
            if hasattr(chain, 'prompt'):
                input_vars = chain.prompt.input_variables
                inputs = {}
                
                for var in input_vars:
                    if var == "context" or var == "question":
                        inputs[var] = context if var == "context" else user_input
                    elif var in ["employee_data", "policy_docs", "process_docs", "holiday_data", "data_summary"]:
                        inputs[var] = context
                    else:
                        inputs[var] = user_input
                
                # Generate response
                result = chain.run(**inputs)
                return result.strip()
                
            else:
                # Fallback to simple LLM call
                return self.llm.predict(f"Context: {context}\n\nQuestion: {user_input}")
                
        except Exception as e:
            logger.error(f"Error in chain execution: {e}")
            # Fallback response
            return f"I understand you're asking about: {user_input}. Let me help you with that based on the available information."
    
    def get_suggestions(self, user_input: str) -> List[str]:
        """
        Get suggested follow-up questions.
        
        Args:
            user_input: Current user input
            
        Returns:
            List of suggested questions
        """
        return self.retriever.search_similar_queries(user_input)
    
    def get_system_stats(self) -> Dict[str, Any]:
        """
        Get system statistics and status.
        
        Returns:
            Dictionary with system statistics
        """
        stats = {
            'agent_name': self.agent_config['name'],
            'model': self.model_config['model_name'],
            'conversation_history_length': len(self.conversation_history),
            'retrieval_stats': self.retriever.get_retrieval_stats(),
            'vector_store_stats': self.vector_store.get_collection_stats()
        }
        
        return stats
    
    def reset_conversation(self):
        """Reset the conversation history."""
        self.conversation_history = []
        logger.info("Conversation history reset")
    
    def add_documents(self, documents: List[Document]):
        """
        Add new documents to the vector store.
        
        Args:
            documents: List of Document objects to add
        """
        try:
            self.vector_store.add_documents(documents)
            self.vector_store.persist()
            logger.info(f"Added {len(documents)} documents to vector store")
        except Exception as e:
            logger.error(f"Error adding documents: {e}")
            raise
    
    def get_conversation_history(self) -> List[Dict[str, str]]:
        """
        Get the conversation history.
        
        Returns:
            List of conversation turns
        """
        return self.conversation_history.copy() 