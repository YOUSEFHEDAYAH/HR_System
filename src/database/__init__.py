"""
Database Package
===============
This package contains all database-related functionality including
models, queries, and configuration.
"""

from .config import DatabaseConfig, DatabaseManager
from .models import (
    Base,
    Department,
    Employee,
    LeaveRequest,
    LeaveBalance,
    Salary,
    EmployeeChatLink,
    EmployeeRole,
    LeaveStatus
)
from .queries import HRQueries

__all__ = [
    'DatabaseConfig',
    'DatabaseManager',
    'Base',
    'Department',
    'Employee',
    'LeaveRequest',
    'LeaveBalance',
    'Salary',
    'EmployeeChatLink',
    'EmployeeRole',
    'LeaveStatus',
    'HRQueries'
]
