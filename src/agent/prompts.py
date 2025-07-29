"""
Prompt templates for the Workday Time-Off Advisor agent.
"""

from langchain_core.prompts import PromptTemplate
from langchain_core.prompts import ChatPromptTemplate, HumanMessagePromptTemplate, SystemMessagePromptTemplate


# System prompt for the Time-Off Advisor
SYSTEM_PROMPT = """You are a helpful Workday Time-Off Advisor assistant. Your role is to help employees understand and navigate Workday's time-off policies and procedures.

You have access to:
1. Workday documentation and policies
2. Employee leave balance data
3. Time-off request procedures
4. Holiday schedules
5. Company policies and guidelines

Your responsibilities:
- Answer questions about time-off policies
- Help employees understand their leave balances
- Guide users through the time-off request process
- Provide information about holidays and company observances
- Explain approval workflows and timelines
- Assist with policy compliance questions

Always be helpful, accurate, and professional. If you're unsure about something, say so and suggest where they might find more information.

Use the provided context to give accurate, specific answers based on the company's actual policies and data."""


# Prompt for general Q&A with context
QA_PROMPT = PromptTemplate(
    input_variables=["context", "question"],
    template="""Use the following context to answer the question at the end. If you don't know the answer, just say that you don't know, don't try to make up an answer.

Context:
{context}

Question: {question}

Answer:"""
)


# Chat prompt template for conversational responses
CHAT_PROMPT = ChatPromptTemplate.from_messages([
    SystemMessagePromptTemplate.from_template(SYSTEM_PROMPT),
    HumanMessagePromptTemplate.from_template("""Context information:
{context}

User question: {question}

Please provide a helpful and accurate response based on the context provided.""")
])


# Prompt for leave balance inquiries
LEAVE_BALANCE_PROMPT = PromptTemplate(
    input_variables=["employee_data", "question"],
    template="""Based on the following employee leave balance information, answer the user's question:

Employee Data:
{employee_data}

Question: {question}

Provide a clear, helpful response about their leave balance."""
)


# Prompt for policy questions
POLICY_PROMPT = PromptTemplate(
    input_variables=["policy_docs", "question"],
    template="""Use the following policy documentation to answer the user's question about Workday time-off policies:

Policy Documentation:
{policy_docs}

Question: {question}

Provide a comprehensive answer based on the policy information provided."""
)


# Prompt for request process guidance
REQUEST_PROCESS_PROMPT = PromptTemplate(
    input_variables=["process_docs", "question"],
    template="""Based on the following time-off request process documentation, guide the user through the process:

Process Documentation:
{process_docs}

Question: {question}

Provide step-by-step guidance on how to complete their time-off request."""
)


# Prompt for holiday inquiries
HOLIDAY_PROMPT = PromptTemplate(
    input_variables=["holiday_data", "question"],
    template="""Use the following holiday information to answer the user's question:

Holiday Data:
{holiday_data}

Question: {question}

Provide accurate information about company holidays."""
)


# Prompt for data analysis
DATA_ANALYSIS_PROMPT = PromptTemplate(
    input_variables=["data_summary", "question"],
    template="""Based on the following time-off data summary, answer the user's question:

Data Summary:
{data_summary}

Question: {question}

Provide insights and analysis based on the data provided."""
)


# Prompt for error handling
ERROR_PROMPT = PromptTemplate(
    input_variables=["error_context", "user_question"],
    template="""I encountered an issue while processing your request about: {user_question}

Error Context: {error_context}

Please provide a helpful response that:
1. Acknowledges the issue
2. Suggests alternative ways to get the information
3. Offers to help with a different approach"""
)


# Prompt for follow-up questions
FOLLOW_UP_PROMPT = PromptTemplate(
    input_variables=["previous_context", "current_question"],
    template="""Based on the previous conversation context and the current question, provide a helpful response:

Previous Context: {previous_context}

Current Question: {current_question}

Provide a response that builds on the previous context and addresses the current question."""
)


# Function to get appropriate prompt based on query type
def get_prompt_for_query(query: str, context: str = "") -> PromptTemplate:
    """
    Determine the appropriate prompt template based on the query type.
    
    Args:
        query: User query
        context: Available context
        
    Returns:
        Appropriate PromptTemplate
    """
    query_lower = query.lower()
    
    if any(word in query_lower for word in ['balance', 'pto', 'leave', 'sick', 'personal']):
        return LEAVE_BALANCE_PROMPT
    
    elif any(word in query_lower for word in ['policy', 'rules', 'guidelines', 'entitled']):
        return POLICY_PROMPT
    
    elif any(word in query_lower for word in ['request', 'submit', 'approval', 'process', 'how to']):
        return REQUEST_PROCESS_PROMPT
    
    elif any(word in query_lower for word in ['holiday', 'holidays', 'christmas', 'thanksgiving']):
        return HOLIDAY_PROMPT
    
    elif any(word in query_lower for word in ['statistics', 'data', 'summary', 'report']):
        return DATA_ANALYSIS_PROMPT
    
    else:
        return QA_PROMPT


# Function to format context for different prompt types
def format_context_for_prompt(prompt_type: str, context_data: dict) -> str:
    """
    Format context data for specific prompt types.
    
    Args:
        prompt_type: Type of prompt (employee_data, policy_docs, etc.)
        context_data: Raw context data
        
    Returns:
        Formatted context string
    """
    if prompt_type == "employee_data":
        if 'employee_summary' in context_data:
            emp = context_data['employee_summary']
            if 'error' not in emp:
                return f"""
Employee: {emp['employee_info']['name']}
Department: {emp['employee_info']['department']}
PTO Balance: {emp['leave_balance'].get('pto_balance', 'N/A')} days
Sick Balance: {emp['leave_balance'].get('sick_balance', 'N/A')} days
Personal Balance: {emp['leave_balance'].get('personal_balance', 'N/A')} days
Total Requests: {emp['total_requests']}
Pending Requests: {emp['pending_requests']}
"""
        return "Employee data not available."
    
    elif prompt_type == "policy_docs":
        docs = context_data.get('documents', [])
        return "\n\n".join([doc.page_content for doc in docs[:3]])
    
    elif prompt_type == "process_docs":
        docs = context_data.get('documents', [])
        return "\n\n".join([doc.page_content for doc in docs[:2]])
    
    elif prompt_type == "holiday_data":
        if 'holidays' in context_data:
            holidays = context_data['holidays']
            return "\n".join([f"{h['holiday_name']}: {h['date']}" for h in holidays])
        return "Holiday data not available."
    
    elif prompt_type == "data_summary":
        if 'leave_statistics' in context_data:
            stats = context_data['leave_statistics']
            return f"""
Total Employees: {stats['total_employees']}
Average PTO Balance: {stats['average_pto']:.1f} days
Total PTO Days: {stats['total_pto_days']:.1f}
Pending Requests: {stats['pending_requests']}
Approved Requests: {stats['approved_requests']}
"""
        return "Data summary not available."
    
    else:
        # Default context formatting
        docs = context_data.get('documents', [])
        return "\n\n".join([doc.page_content for doc in docs[:3]]) 