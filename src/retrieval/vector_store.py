"""
Vector store for document embeddings and storage.
"""

import logging
from typing import List, Dict, Any
from langchain_core.documents import Document
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

logger = logging.getLogger(__name__)


class WorkdayVectorStore:
    """Vector store for Workday documentation."""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the vector store.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.vector_config = config['vector_store']
        self.collection_name = self.vector_config['collection_name']
        self.embedding_model = self.vector_config['embedding_model']
        self.similarity_threshold = self.vector_config['similarity_threshold']
        
        # Initialize embeddings
        self.embeddings = HuggingFaceEmbeddings(
            model_name=self.embedding_model,
            model_kwargs={'device': 'cpu'}
        )
        
        # Initialize text splitter
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.vector_config['chunk_size'],
            chunk_overlap=self.vector_config['chunk_overlap'],
            length_function=len,
            separators=["\n\n", "\n", " ", ""]
        )
        
        # Initialize vector store
        self.vector_store = None
    
    def create_vector_store(self, documents: List[Document]) -> None:
        """
        Create and populate the vector store with documents.
        
        Args:
            documents: List of Document objects to add to the vector store
        """
        try:
            # Split documents if they haven't been split already
            if documents and not hasattr(documents[0], 'metadata'):
                documents = self.text_splitter.split_documents(documents)
            
            # Create vector store
            self.vector_store = Chroma.from_documents(
                documents=documents,
                embedding=self.embeddings,
                collection_name=self.collection_name,
                persist_directory="./chroma_db"
            )
            
            logger.info(f"Created vector store with {len(documents)} documents")
            
        except Exception as e:
            logger.error(f"Error creating vector store: {e}")
            raise
    
    def load_existing_vector_store(self) -> bool:
        """
        Load existing vector store from disk.
        
        Returns:
            True if successfully loaded, False otherwise
        """
        try:
            self.vector_store = Chroma(
                collection_name=self.collection_name,
                embedding_function=self.embeddings,
                persist_directory="./chroma_db"
            )
            
            # Check if collection exists and has documents
            collection = self.vector_store._collection
            if collection and collection.count() > 0:
                logger.info(f"Loaded existing vector store with {collection.count()} documents")
                return True
            else:
                logger.warning("No existing vector store found or collection is empty")
                return False
                
        except Exception as e:
            logger.error(f"Error loading vector store: {e}")
            return False
    
    def similarity_search(self, query: str, k: int = None) -> List[Document]:
        """
        Perform similarity search on the vector store.
        
        Args:
            query: Search query
            k: Number of results to return
            
        Returns:
            List of relevant Document objects
        """
        if not self.vector_store:
            logger.error("Vector store not initialized")
            return []
        
        if k is None:
            k = self.config['retrieval']['top_k']
        
        try:
            results = self.vector_store.similarity_search_with_score(
                query=query,
                k=k
            )
            
            # Filter by similarity threshold
            filtered_results = []
            for doc, score in results:
                if score <= (1 - self.similarity_threshold):  # Convert similarity to distance
                    filtered_results.append(doc)
            
            logger.info(f"Found {len(filtered_results)} relevant documents for query: {query}")
            return filtered_results
            
        except Exception as e:
            logger.error(f"Error performing similarity search: {e}")
            return []
    
    def add_documents(self, documents: List[Document]) -> None:
        """
        Add new documents to the vector store.
        
        Args:
            documents: List of Document objects to add
        """
        if not self.vector_store:
            logger.error("Vector store not initialized")
            return
        
        try:
            # Split documents if needed
            if documents and not hasattr(documents[0], 'metadata'):
                documents = self.text_splitter.split_documents(documents)
            
            # Add to vector store
            self.vector_store.add_documents(documents)
            logger.info(f"Added {len(documents)} documents to vector store")
            
        except Exception as e:
            logger.error(f"Error adding documents to vector store: {e}")
            raise
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the vector store collection.
        
        Returns:
            Dictionary with collection statistics
        """
        if not self.vector_store:
            return {'error': 'Vector store not initialized'}
        
        try:
            collection = self.vector_store._collection
            stats = {
                'total_documents': collection.count() if collection else 0,
                'collection_name': self.collection_name,
                'embedding_model': self.embedding_model
            }
            return stats
            
        except Exception as e:
            logger.error(f"Error getting collection stats: {e}")
            return {'error': str(e)}
    
    def delete_collection(self) -> None:
        """
        Delete the entire collection from the vector store.
        """
        if not self.vector_store:
            logger.warning("Vector store not initialized")
            return
        
        try:
            collection = self.vector_store._collection
            if collection:
                collection.delete()
                logger.info("Deleted vector store collection")
            
        except Exception as e:
            logger.error(f"Error deleting collection: {e}")
    
    def persist(self) -> None:
        """
        Persist the vector store to disk.
        """
        if self.vector_store:
            try:
                self.vector_store.persist()
                logger.info("Vector store persisted to disk")
            except Exception as e:
                logger.error(f"Error persisting vector store: {e}") 