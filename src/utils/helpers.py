"""
Utility functions for the Workday Time-Off Advisor.
"""

import os
import yaml
import logging
from pathlib import Path
from typing import Dict, Any


def load_config(config_path: str = "config/config.yaml") -> Dict[str, Any]:
    """
    Load configuration from YAML file.
    
    Args:
        config_path: Path to the configuration file
        
    Returns:
        Dictionary containing configuration settings
    """
    try:
        with open(config_path, 'r', encoding='utf-8') as file:
            config = yaml.safe_load(file)
        return config
    except FileNotFoundError:
        raise FileNotFoundError(f"Configuration file not found: {config_path}")
    except yaml.YAMLError as e:
        raise ValueError(f"Error parsing configuration file: {e}")


def setup_logging(config: Dict[str, Any] = None) -> None:
    """
    Setup logging configuration.
    
    Args:
        config: Configuration dictionary with logging settings
    """
    if config is None:
        config = load_config()
    
    log_config = config.get('logging', {})
    log_level = getattr(logging, log_config.get('level', 'INFO'))
    log_format = log_config.get('format', '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    log_file = log_config.get('file', 'logs/timeoff_advisor.log')
    
    # Create logs directory if it doesn't exist
    log_path = Path(log_file)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Configure logging
    logging.basicConfig(
        level=log_level,
        format=log_format,
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )


def validate_environment() -> bool:
    """
    Validate that required environment variables are set.
    
    Returns:
        True if all required variables are set, False otherwise
    """
    required_vars = ['ANTHROPIC_API_KEY']
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ Missing required environment variables: {', '.join(missing_vars)}")
        print("Please set these variables in your .env file or environment.")
        return False
    
    return True


def format_currency(amount: float, currency: str = "USD") -> str:
    """
    Format currency amount.
    
    Args:
        amount: Amount to format
        currency: Currency code
        
    Returns:
        Formatted currency string
    """
    currency_symbols = {
        "USD": "$",
        "EUR": "€",
        "GBP": "£"
    }
    
    symbol = currency_symbols.get(currency, currency)
    return f"{symbol}{amount:,.2f}"


def format_date(date_str: str, input_format: str = "%Y-%m-%d", output_format: str = "%B %d, %Y") -> str:
    """
    Format date string.
    
    Args:
        date_str: Date string to format
        input_format: Input date format
        output_format: Output date format
        
    Returns:
        Formatted date string
    """
    from datetime import datetime
    
    try:
        date_obj = datetime.strptime(date_str, input_format)
        return date_obj.strftime(output_format)
    except ValueError:
        return date_str


def calculate_working_days(start_date: str, end_date: str) -> int:
    """
    Calculate working days between two dates (excluding weekends).
    
    Args:
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
        
    Returns:
        Number of working days
    """
    from datetime import datetime, timedelta
    
    start = datetime.strptime(start_date, "%Y-%m-%d")
    end = datetime.strptime(end_date, "%Y-%m-%d")
    
    working_days = 0
    current = start
    
    while current <= end:
        if current.weekday() < 5:  # Monday = 0, Sunday = 6
            working_days += 1
        current += timedelta(days=1)
    
    return working_days 