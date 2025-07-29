"""
Document loader for processing Workday documentation files.
"""

import os
import logging
from pathlib import Path
from typing import List, Dict, Any
from langchain_community.document_loaders import (
    PyPDFLoader,
    Docx2txtLoader,
    TextLoader,
    UnstructuredMarkdownLoader
)
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

logger = logging.getLogger(__name__)


class WorkdayDocumentLoader:
    """Loader for Workday documentation files."""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the document loader.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.supported_formats = config['documents']['supported_formats']
        self.data_directory = Path(config['documents']['data_directory'])
        self.chunk_size = config['vector_store']['chunk_size']
        self.chunk_overlap = config['vector_store']['chunk_overlap']
        
        # Initialize text splitter
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", " ", ""]
        )
    
    def load_documents(self) -> List[Document]:
        """
        Load all documents from the data directory.
        
        Returns:
            List of Document objects
        """
        documents = []
        
        if not self.data_directory.exists():
            logger.warning(f"Data directory does not exist: {self.data_directory}")
            return documents
        
        for file_path in self.data_directory.rglob("*"):
            if file_path.is_file() and file_path.suffix.lower() in self.supported_formats:
                try:
                    file_docs = self._load_single_file(file_path)
                    documents.extend(file_docs)
                    logger.info(f"Loaded {len(file_docs)} chunks from {file_path.name}")
                except Exception as e:
                    logger.error(f"Error loading file {file_path}: {e}")
        
        return documents
    
    def _load_single_file(self, file_path: Path) -> List[Document]:
        """
        Load a single file and split it into chunks.
        
        Args:
            file_path: Path to the file to load
            
        Returns:
            List of Document chunks
        """
        suffix = file_path.suffix.lower()
        
        # Choose appropriate loader based on file type
        if suffix == '.pdf':
            loader = PyPDFLoader(str(file_path))
        elif suffix == '.docx':
            loader = Docx2txtLoader(str(file_path))
        elif suffix == '.txt':
            loader = TextLoader(str(file_path), encoding='utf-8')
        elif suffix == '.md':
            loader = UnstructuredMarkdownLoader(str(file_path))
        else:
            raise ValueError(f"Unsupported file type: {suffix}")
        
        # Load and split documents
        raw_docs = loader.load()
        split_docs = self.text_splitter.split_documents(raw_docs)
        
        # Add metadata
        for doc in split_docs:
            doc.metadata.update({
                'source': str(file_path),
                'file_name': file_path.name,
                'file_type': suffix,
                'chunk_id': f"{file_path.stem}_{len(split_docs)}"
            })
        
        return split_docs
    
    def create_sample_documents(self) -> List[Document]:
        """
        Create sample Workday documentation for testing.
        
        Returns:
            List of sample Document objects
        """
        sample_docs = [
            Document(
                page_content="""
                Workday Time-Off Policy Overview
                
                Employees are entitled to various types of leave including:
                - Vacation/PTO: 20 days per year for full-time employees
                - Sick Leave: 10 days per year
                - Personal Days: 5 days per year
                - Holidays: Company observes 10 federal holidays
                
                All time-off requests must be submitted through Workday at least 2 weeks in advance for vacation and 24 hours for sick leave.
                """,
                metadata={
                    'source': 'sample_policy_overview.txt',
                    'file_name': 'policy_overview.txt',
                    'file_type': '.txt',
                    'chunk_id': 'policy_overview_1'
                }
            ),
            Document(
                page_content="""
                Vacation Request Process
                
                1. Log into Workday
                2. Navigate to Time Off > Request Time Off
                3. Select vacation as the time-off type
                4. Choose start and end dates
                5. Add comments explaining the reason
                6. Submit for manager approval
                
                Managers have 5 business days to approve or deny requests.
                """,
                metadata={
                    'source': 'sample_vacation_process.txt',
                    'file_name': 'vacation_process.txt',
                    'file_type': '.txt',
                    'chunk_id': 'vacation_process_1'
                }
            ),
            Document(
                page_content="""
                Leave Balance Calculation
                
                PTO accrual rates:
                - 0-2 years: 15 days/year
                - 3-5 years: 20 days/year
                - 6-10 years: 25 days/year
                - 10+ years: 30 days/year
                
                Unused PTO can be carried over up to 5 days to the next year.
                Maximum PTO balance cannot exceed 30 days.
                """,
                metadata={
                    'source': 'sample_leave_balance.txt',
                    'file_name': 'leave_balance.txt',
                    'file_type': '.txt',
                    'chunk_id': 'leave_balance_1'
                }
            ),
            Document(
                page_content="""
                Holiday Schedule 2024
                
                Company observes the following holidays:
                - New Year's Day: January 1
                - Martin Luther King Jr. Day: January 15
                - Memorial Day: May 27
                - Independence Day: July 4
                - Labor Day: September 2
                - Thanksgiving Day: November 28
                - Christmas Day: December 25
                
                Employees receive holiday pay for these dates.
                """,
                metadata={
                    'source': 'sample_holiday_schedule.txt',
                    'file_name': 'holiday_schedule.txt',
                    'file_type': '.txt',
                    'chunk_id': 'holiday_schedule_1'
                }
            ),
            Document(
                page_content="""
                Sick Leave Policy
                
                Sick leave can be used for:
                - Personal illness or injury
                - Medical appointments
                - Caring for sick family members
                
                Documentation may be required for absences longer than 3 consecutive days.
                Sick leave does not accrue and is not paid out upon termination.
                """,
                metadata={
                    'source': 'sample_sick_leave.txt',
                    'file_name': 'sick_leave.txt',
                    'file_type': '.txt',
                    'chunk_id': 'sick_leave_1'
                }
            )
        ]
        
        return sample_docs 