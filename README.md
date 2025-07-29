# Workday Time-Off Advisor

An intelligent agent that combines LangChain, Claude, and Pandas to provide retrieval-augmented QA over Workday time-off policies and documentation.

## Features

- **Multi-file orchestration** with clear separation of concerns
- **YAML-based configuration** for easy customization
- **LangChain integration** for agent orchestration
- **Claude AI** for intelligent responses
- **Pandas** for data manipulation and analysis
- **Retrieval-augmented QA** over sample Workday documentation
- **Vector search** for relevant policy information

## Project Structure

```
timeoff-advisor-1/
├── config/
│   └── config.yaml          # YAML configuration
├── data/
│   ├── workday_docs/        # Sample Workday documentation
│   └── sample_data/         # Sample time-off data
├── src/
│   ├── __init__.py
│   ├── agent/
│   │   ├── __init__.py
│   │   ├── timeoff_advisor.py
│   │   └── prompts.py
│   ├── data/
│   │   ├── __init__.py
│   │   ├── document_loader.py
│   │   └── data_processor.py
│   ├── retrieval/
│   │   ├── __init__.py
│   │   ├── vector_store.py
│   │   └── retriever.py
│   └── utils/
│       ├── __init__.py
│       └── helpers.py
├── tests/
│   └── __init__.py
├── requirements.txt
├── main.py
└── README.md
```

## 🚀 Quick Start

1. **Setup the project**:
   ```bash
   python3 setup.py
   ```

2. **Test basic components**:
   ```bash
   python3 test_basic.py
   ```

3. **Run the QA demo**:
   ```bash
   python3 demo_qa.py
   ```

4. **Web interface** (recommended):
   ```bash
   python3 start_web.py
   ```
   Then open http://localhost:8080 in your browser

5. **Interactive mode**:
   ```bash
   python3 simple_advisor.py
   ```

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up your environment variables:
```bash
export ANTHROPIC_API_KEY="your-claude-api-key"
```

3. Run the application:
```bash
python main.py
```

## Usage

### Demo Scripts
- **`test_basic.py`**: Test core components without API dependencies
- **`demo_qa.py`**: Showcase retrieval-augmented QA capabilities
- **`simple_advisor.py`**: Interactive advisor (requires API key for full functionality)
- **`start_web.py`**: Start the web interface (recommended)

### Web Interface Features
- **Modern Chat Interface**: Clean, responsive design with real-time messaging
- **Sidebar Information**: System stats, query suggestions, and knowledge base overview
- **API Endpoints**: RESTful API for programmatic access
- **Mobile Responsive**: Works on desktop and mobile devices
- **Real-time Responses**: Instant query processing and response generation

### Query Examples
The Time-Off Advisor can help with:
- Time-off policy questions
- Leave balance inquiries
- Approval workflow guidance
- Holiday and PTO calculations
- Policy compliance questions

## Configuration

Edit `config/config.yaml` to customize:
- Model parameters
- Vector store settings
- Document processing options
- Agent behavior preferences