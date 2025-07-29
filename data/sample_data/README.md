# Sample Data Directory

This directory contains sample data files for the Workday Time-Off Advisor.

## Files

- `employees.csv` - Sample employee data
- `leave_balances.csv` - Sample leave balance data
- `timeoff_requests.csv` - Sample time-off request data
- `holidays.csv` - Sample holiday schedule data

## Usage

The sample data is automatically generated when the application starts if no existing data is found. This provides a realistic testing environment for the Time-Off Advisor agent.

## Data Structure

### Employees
- employee_id: Unique employee identifier
- name: Employee full name
- department: Employee department
- hire_date: Employee hire date
- employment_status: Employment status (Full-time, Part-time, etc.)

### Leave Balances
- employee_id: Employee identifier
- pto_balance: PTO balance in days
- sick_balance: Sick leave balance in days
- personal_balance: Personal days balance
- last_updated: Last update timestamp

### Time-Off Requests
- request_id: Unique request identifier
- employee_id: Employee identifier
- request_type: Type of time-off (Vacation, Sick, Personal, Holiday)
- start_date: Request start date
- end_date: Request end date
- days_requested: Number of days requested
- status: Request status (Pending, Approved, Denied)
- submitted_date: Date request was submitted
- approved_by: Approver name
- comments: Request comments

### Holidays
- holiday_name: Holiday name
- date: Holiday date
- is_company_holiday: Whether it's a company holiday 