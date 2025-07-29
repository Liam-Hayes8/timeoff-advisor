#!/usr/bin/env python3
"""
Flask web application for the Workday Time-Off Advisor.
"""

import os
import sys
from pathlib import Path
from flask import Flask, render_template, request, jsonify, session
from dotenv import load_dotenv

# Add src to path for imports
sys.path.append(str(Path(__file__).parent / "src"))

from src.utils.helpers import load_config, setup_logging
from simple_advisor import SimpleTimeOffAdvisor

# Load environment variables
load_dotenv()

# Setup logging
setup_logging()

# Load configuration
config = load_config()

# Initialize the advisor
advisor = SimpleTimeOffAdvisor(config)

app = Flask(__name__)
app.secret_key = 'workday-timeoff-advisor-secret-key'

@app.route('/')
def index():
    """Main page."""
    # Get system stats
    stats = advisor.get_system_stats()
    return render_template('index.html', stats=stats)

@app.route('/api/query', methods=['POST'])
def query():
    """Handle query requests."""
    try:
        data = request.get_json()
        query_text = data.get('query', '').strip()
        
        if not query_text:
            return jsonify({'error': 'Query is required'}), 400
        
        # Get response from advisor
        response = advisor.get_response(query_text)
        
        # Get suggestions for follow-up
        suggestions = advisor.get_suggestions(query_text)
        
        return jsonify({
            'response': response,
            'suggestions': suggestions[:3],  # Limit to 3 suggestions
            'query': query_text
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/stats')
def get_stats():
    """Get system statistics."""
    try:
        stats = advisor.get_system_stats()
        return jsonify(stats)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/suggestions')
def get_suggestions():
    """Get query suggestions."""
    try:
        suggestions = advisor.get_suggestions("")
        return jsonify({'suggestions': suggestions})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/knowledge-base')
def get_knowledge_base():
    """Get knowledge base structure."""
    try:
        kb = advisor.knowledge_base
        return jsonify({
            'documents': list(kb['documents'].keys()),
            'policies': list(kb['policies'].keys()),
            'procedures': list(kb['procedures'].keys()),
            'data_summary': kb['data_summary']
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("🚀 Starting Workday Time-Off Advisor Web Application...")
    print("📊 System Statistics:")
    stats = advisor.get_system_stats()
    print(f"• Agent: {stats['agent_name']}")
    print(f"• Documents: {stats['vector_store_stats']['total_documents']}")
    print(f"• Employees: {stats['data_stats']['total_employees']}")
    print(f"• Requests: {stats['data_stats']['total_requests']}")
    print(f"\n🌐 Web interface available at: http://localhost:8080")
    print(f"📝 API endpoints:")
    print(f"  - POST /api/query - Submit queries")
    print(f"  - GET /api/stats - System statistics")
    print(f"  - GET /api/suggestions - Query suggestions")
    print(f"  - GET /api/knowledge-base - Knowledge base info")
    
    app.run(debug=True, host='0.0.0.0', port=8080) 