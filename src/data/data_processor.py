"""
Data processor for handling time-off data with Pandas.
"""

import pandas as pd
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from pathlib import Path

logger = logging.getLogger(__name__)


class TimeOffDataProcessor:
    """Processor for time-off data using Pandas."""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the data processor.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.date_format = config['data_processing']['date_format']
        self.timezone = config['data_processing']['timezone']
        self.currency = config['data_processing']['default_currency']
    
    def create_sample_data(self) -> Dict[str, pd.DataFrame]:
        """
        Create sample time-off data for testing.
        
        Returns:
            Dictionary containing sample DataFrames
        """
        # Sample employee data
        employees_df = pd.DataFrame({
            'employee_id': ['EMP001', 'EMP002', 'EMP003', 'EMP004', 'EMP005'],
            'name': ['John Smith', 'Jane Doe', 'Mike Johnson', 'Sarah Wilson', 'David Brown'],
            'department': ['Engineering', 'Marketing', 'Sales', 'HR', 'Finance'],
            'hire_date': ['2020-01-15', '2019-03-20', '2021-06-10', '2018-11-05', '2022-02-28'],
            'employment_status': ['Full-time', 'Full-time', 'Full-time', 'Full-time', 'Full-time']
        })
        
        # Sample leave balances
        leave_balances_df = pd.DataFrame({
            'employee_id': ['EMP001', 'EMP002', 'EMP003', 'EMP004', 'EMP005'],
            'pto_balance': [15.5, 22.0, 8.75, 30.0, 12.25],
            'sick_balance': [8.0, 10.0, 5.5, 7.0, 9.5],
            'personal_balance': [3.0, 5.0, 2.0, 4.0, 1.5],
            'last_updated': ['2024-01-15', '2024-01-15', '2024-01-15', '2024-01-15', '2024-01-15']
        })
        
        # Sample time-off requests
        timeoff_requests_df = pd.DataFrame({
            'request_id': ['REQ001', 'REQ002', 'REQ003', 'REQ004', 'REQ005'],
            'employee_id': ['EMP001', 'EMP002', 'EMP003', 'EMP004', 'EMP005'],
            'request_type': ['Vacation', 'Sick', 'Personal', 'Vacation', 'Holiday'],
            'start_date': ['2024-02-15', '2024-01-20', '2024-03-10', '2024-04-01', '2024-01-01'],
            'end_date': ['2024-02-20', '2024-01-20', '2024-03-10', '2024-04-05', '2024-01-01'],
            'days_requested': [4.0, 1.0, 1.0, 3.0, 1.0],
            'status': ['Approved', 'Approved', 'Pending', 'Approved', 'Approved'],
            'submitted_date': ['2024-01-10', '2024-01-19', '2024-02-15', '2024-03-01', '2024-01-01'],
            'approved_by': ['Manager1', 'Manager2', None, 'Manager1', 'System'],
            'comments': ['Family vacation', 'Not feeling well', 'Doctor appointment', 'Spring break', 'New Year holiday']
        })
        
        # Sample holidays
        holidays_df = pd.DataFrame({
            'holiday_name': [
                'New Year\'s Day',
                'Martin Luther King Jr. Day',
                'Memorial Day',
                'Independence Day',
                'Labor Day',
                'Thanksgiving Day',
                'Christmas Day'
            ],
            'date': [
                '2024-01-01',
                '2024-01-15',
                '2024-05-27',
                '2024-07-04',
                '2024-09-02',
                '2024-11-28',
                '2024-12-25'
            ],
            'is_company_holiday': [True, True, True, True, True, True, True]
        })
        
        return {
            'employees': employees_df,
            'leave_balances': leave_balances_df,
            'timeoff_requests': timeoff_requests_df,
            'holidays': holidays_df
        }
    
    def calculate_leave_statistics(self, data: Dict[str, pd.DataFrame]) -> Dict[str, Any]:
        """
        Calculate leave statistics from the data.
        
        Args:
            data: Dictionary containing DataFrames
            
        Returns:
            Dictionary with calculated statistics
        """
        employees_df = data['employees']
        leave_balances_df = data['leave_balances']
        timeoff_requests_df = data['timeoff_requests']
        
        # Merge employee and leave balance data
        employee_stats = employees_df.merge(leave_balances_df, on='employee_id', how='left')
        
        # Calculate statistics
        stats = {
            'total_employees': len(employees_df),
            'average_pto_balance': leave_balances_df['pto_balance'].mean(),
            'total_pto_days': leave_balances_df['pto_balance'].sum(),
            'pending_requests': len(timeoff_requests_df[timeoff_requests_df['status'] == 'Pending']),
            'approved_requests': len(timeoff_requests_df[timeoff_requests_df['status'] == 'Approved']),
            'total_requests': len(timeoff_requests_df),
            'most_requested_type': timeoff_requests_df['request_type'].mode().iloc[0] if not timeoff_requests_df.empty else None
        }
        
        return stats
    
    def get_employee_leave_summary(self, employee_id: str, data: Dict[str, pd.DataFrame]) -> Dict[str, Any]:
        """
        Get leave summary for a specific employee.
        
        Args:
            employee_id: Employee ID to look up
            data: Dictionary containing DataFrames
            
        Returns:
            Dictionary with employee leave summary
        """
        employees_df = data['employees']
        leave_balances_df = data['leave_balances']
        timeoff_requests_df = data['timeoff_requests']
        
        # Get employee info
        employee = employees_df[employees_df['employee_id'] == employee_id]
        if employee.empty:
            return {'error': 'Employee not found'}
        
        # Get leave balance
        leave_balance = leave_balances_df[leave_balances_df['employee_id'] == employee_id]
        
        # Get time-off requests
        employee_requests = timeoff_requests_df[timeoff_requests_df['employee_id'] == employee_id]
        
        summary = {
            'employee_info': employee.iloc[0].to_dict(),
            'leave_balance': leave_balance.iloc[0].to_dict() if not leave_balance.empty else {},
            'total_requests': len(employee_requests),
            'approved_requests': len(employee_requests[employee_requests['status'] == 'Approved']),
            'pending_requests': len(employee_requests[employee_requests['status'] == 'Pending']),
            'recent_requests': employee_requests.head(5).to_dict('records')
        }
        
        return summary
    
    def calculate_working_days(self, start_date: str, end_date: str, holidays: pd.DataFrame) -> int:
        """
        Calculate working days between two dates, excluding holidays.
        
        Args:
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            holidays: DataFrame containing holiday dates
            
        Returns:
            Number of working days
        """
        start = datetime.strptime(start_date, '%Y-%m-%d')
        end = datetime.strptime(end_date, '%Y-%m-%d')
        
        # Get holiday dates
        holiday_dates = set(pd.to_datetime(holidays['date']).dt.date)
        
        working_days = 0
        current = start
        
        while current <= end:
            current_date = current.date()
            if current.weekday() < 5 and current_date not in holiday_dates:
                working_days += 1
            current += timedelta(days=1)
        
        return working_days
    
    def save_sample_data(self, data: Dict[str, pd.DataFrame], output_dir: str = "data/sample_data"):
        """
        Save sample data to CSV files.
        
        Args:
            data: Dictionary containing DataFrames
            output_dir: Directory to save the files
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        for name, df in data.items():
            file_path = output_path / f"{name}.csv"
            df.to_csv(file_path, index=False)
            logger.info(f"Saved {name} data to {file_path}")
    
    def load_data_from_csv(self, data_dir: str = "data/sample_data") -> Dict[str, pd.DataFrame]:
        """
        Load data from CSV files.
        
        Args:
            data_dir: Directory containing CSV files
            
        Returns:
            Dictionary containing DataFrames
        """
        data_path = Path(data_dir)
        data = {}
        
        if not data_path.exists():
            logger.warning(f"Data directory does not exist: {data_path}")
            return data
        
        for csv_file in data_path.glob("*.csv"):
            try:
                df_name = csv_file.stem
                data[df_name] = pd.read_csv(csv_file)
                logger.info(f"Loaded {df_name} from {csv_file}")
            except Exception as e:
                logger.error(f"Error loading {csv_file}: {e}")
        
        return data 