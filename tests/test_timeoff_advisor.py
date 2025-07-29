"""
Tests for the Time-Off Advisor agent.
"""

import pytest
import sys
from pathlib import Path

# Add src to path for imports
sys.path.append(str(Path(__file__).parent.parent / "src"))

from src.agent.timeoff_advisor import TimeOffAdvisor
from src.utils.helpers import load_config


class TestTimeOffAdvisor:
    """Test cases for the Time-Off Advisor."""
    
    @pytest.fixture
    def config(self):
        """Load test configuration."""
        return load_config("config/config.yaml")
    
    @pytest.fixture
    def advisor(self, config):
        """Create a Time-Off Advisor instance for testing."""
        # Note: This requires ANTHROPIC_API_KEY to be set
        try:
            return TimeOffAdvisor(config)
        except ValueError as e:
            if "Missing required environment variables" in str(e):
                pytest.skip("ANTHROPIC_API_KEY not set")
            else:
                raise
    
    def test_config_loading(self, config):
        """Test that configuration loads correctly."""
        assert 'model' in config
        assert 'vector_store' in config
        assert 'agent' in config
        assert config['model']['provider'] == 'anthropic'
    
    def test_advisor_initialization(self, advisor):
        """Test that the advisor initializes correctly."""
        assert advisor is not None
        assert hasattr(advisor, 'llm')
        assert hasattr(advisor, 'retriever')
        assert hasattr(advisor, 'vector_store')
    
    def test_get_system_stats(self, advisor):
        """Test getting system statistics."""
        stats = advisor.get_system_stats()
        assert 'agent_name' in stats
        assert 'model' in stats
        assert 'conversation_history_length' in stats
    
    def test_conversation_history(self, advisor):
        """Test conversation history management."""
        # Test initial state
        history = advisor.get_conversation_history()
        assert len(history) == 0
        
        # Test adding conversation
        advisor.conversation_history.append({"role": "user", "content": "test"})
        history = advisor.get_conversation_history()
        assert len(history) == 1
        
        # Test reset
        advisor.reset_conversation()
        history = advisor.get_conversation_history()
        assert len(history) == 0
    
    def test_get_suggestions(self, advisor):
        """Test getting query suggestions."""
        suggestions = advisor.get_suggestions("How much PTO do I have?")
        assert isinstance(suggestions, list)
        assert len(suggestions) > 0
    
    @pytest.mark.skipif(True, reason="Requires API key and may take time")
    def test_get_response(self, advisor):
        """Test getting a response from the advisor."""
        response = advisor.get_response("What is the PTO policy?")
        assert isinstance(response, str)
        assert len(response) > 0


class TestDataProcessor:
    """Test cases for the data processor."""
    
    @pytest.fixture
    def config(self):
        """Load test configuration."""
        return load_config("config/config.yaml")
    
    @pytest.fixture
    def data_processor(self, config):
        """Create a data processor instance."""
        from src.data.data_processor import TimeOffDataProcessor
        return TimeOffDataProcessor(config)
    
    def test_create_sample_data(self, data_processor):
        """Test creating sample data."""
        data = data_processor.create_sample_data()
        assert 'employees' in data
        assert 'leave_balances' in data
        assert 'timeoff_requests' in data
        assert 'holidays' in data
        
        # Check data structure
        assert len(data['employees']) > 0
        assert len(data['leave_balances']) > 0
        assert len(data['timeoff_requests']) > 0
        assert len(data['holidays']) > 0
    
    def test_calculate_leave_statistics(self, data_processor):
        """Test calculating leave statistics."""
        data = data_processor.create_sample_data()
        stats = data_processor.calculate_leave_statistics(data)
        
        assert 'total_employees' in stats
        assert 'average_pto_balance' in stats
        assert 'pending_requests' in stats
        assert 'approved_requests' in stats
    
    def test_get_employee_leave_summary(self, data_processor):
        """Test getting employee leave summary."""
        data = data_processor.create_sample_data()
        summary = data_processor.get_employee_leave_summary('EMP001', data)
        
        assert 'employee_info' in summary
        assert 'leave_balance' in summary
        assert 'total_requests' in summary
    
    def test_calculate_working_days(self, data_processor):
        """Test calculating working days."""
        data = data_processor.create_sample_data()
        working_days = data_processor.calculate_working_days('2024-01-01', '2024-01-05', data['holidays'])
        
        assert isinstance(working_days, int)
        assert working_days >= 0


class TestDocumentLoader:
    """Test cases for the document loader."""
    
    @pytest.fixture
    def config(self):
        """Load test configuration."""
        return load_config("config/config.yaml")
    
    @pytest.fixture
    def document_loader(self, config):
        """Create a document loader instance."""
        from src.data.document_loader import WorkdayDocumentLoader
        return WorkdayDocumentLoader(config)
    
    def test_create_sample_documents(self, document_loader):
        """Test creating sample documents."""
        docs = document_loader.create_sample_documents()
        assert len(docs) > 0
        
        for doc in docs:
            assert hasattr(doc, 'page_content')
            assert hasattr(doc, 'metadata')
            assert len(doc.page_content) > 0


if __name__ == "__main__":
    pytest.main([__file__]) 