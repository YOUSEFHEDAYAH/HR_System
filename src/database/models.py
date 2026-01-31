"""
Database Models
==============
SQLAlchemy ORM models for the HR management system.

This module defines all database tables and their relationships:
- Department: Organizational departments
- Employee: Employee master data
- LeaveRequest: Leave applications
- LeaveBalance: Leave day tracking
- Salary: Salary history
- EmployeeChatLink: Telegram authentication
"""

from sqlalchemy import Column, Integer, String, Float, Date, DateTime, ForeignKey, Enum
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.sql import func
from datetime import datetime
import enum


# Base class for all models
Base = declarative_base()


# ===========================
# Enums
# ===========================

class EmployeeRole(enum.Enum):
    """Employee role types."""
    EMPLOYEE = "Employee"
    MANAGER = "Manager"
    HR = "HR"


class LeaveStatus(enum.Enum):
    """Leave request status types."""
    PENDING = "Pending"
    APPROVED = "Approved"
    REJECTED = "Rejected"


# ===========================
# Models
# ===========================

class Department(Base):
    """
    Department organizational structure.
    
    Represents company departments with hierarchical management.
    """
    __tablename__ = 'departments'
    
    # Columns
    department_id = Column(Integer, primary_key=True, autoincrement=True)
    department_name = Column(String(100), nullable=False, unique=True)
    manager_id = Column(Integer, ForeignKey('employees.employee_id'), nullable=True)
    
    # Relationships
    employees = relationship('Employee', back_populates='department', foreign_keys='Employee.department_id')
    manager = relationship('Employee', foreign_keys=[manager_id], post_update=True)
    
    def __repr__(self):
        return f"<Department(id={self.department_id}, name='{self.department_name}')>"


class Employee(Base):
    """
    Employee master data.
    
    Central table containing all employee information including
    personal details, role, department, and compensation.
    """
    __tablename__ = 'employees'
    
    # Columns
    employee_id = Column(Integer, primary_key=True, autoincrement=True)
    full_name = Column(String(150), nullable=False)
    email = Column(String(150), nullable=False, unique=True)
    department_id = Column(Integer, ForeignKey('departments.department_id'), nullable=False)
    role = Column(Enum(EmployeeRole), nullable=False, default=EmployeeRole.EMPLOYEE)
    hire_date = Column(Date, nullable=False, default=datetime.now().date())
    salary = Column(Float, nullable=False)
    
    # Relationships
    department = relationship('Department', back_populates='employees', foreign_keys=[department_id])
    leave_requests = relationship('LeaveRequest', back_populates='employee', cascade='all, delete-orphan')
    leave_balance = relationship('LeaveBalance', back_populates='employee', uselist=False, cascade='all, delete-orphan')
    salary_history = relationship('Salary', back_populates='employee', cascade='all, delete-orphan')
    chat_link = relationship('EmployeeChatLink', back_populates='employee', uselist=False, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f"<Employee(id={self.employee_id}, name='{self.full_name}', role='{self.role.value}')>"
    
    def is_manager(self):
        """Check if employee is a manager."""
        return self.role == EmployeeRole.MANAGER
    
    def is_hr(self):
        """Check if employee is HR staff."""
        return self.role == EmployeeRole.HR
    
    def can_access_employee_data(self, target_employee):
        """
        Check if employee can access another employee's data.
        
        Access rules:
        - HR can access all data
        - Managers can access their department's employees
        - Employees can only access their own data
        """
        if self.is_hr():
            return True
        if self.is_manager() and self.department_id == target_employee.department_id:
            return True
        return self.employee_id == target_employee.employee_id


class LeaveRequest(Base):
    """
    Leave request tracking.
    
    Stores all leave applications with dates, reasons, and approval status.
    """
    __tablename__ = 'leave_requests'
    
    # Columns
    leave_id = Column(Integer, primary_key=True, autoincrement=True)
    employee_id = Column(Integer, ForeignKey('employees.employee_id'), nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    reason = Column(String(500), nullable=True)
    status = Column(Enum(LeaveStatus), nullable=False, default=LeaveStatus.PENDING)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    employee = relationship('Employee', back_populates='leave_requests')
    
    def __repr__(self):
        return f"<LeaveRequest(id={self.leave_id}, employee_id={self.employee_id}, status='{self.status.value}')>"
    
    def get_duration_days(self):
        """Calculate leave duration in days."""
        return (self.end_date - self.start_date).days + 1


class LeaveBalance(Base):
    """
    Leave balance tracking.
    
    Maintains running balance of available leave days for each employee.
    """
    __tablename__ = 'leave_balances'
    
    # Columns
    employee_id = Column(Integer, ForeignKey('employees.employee_id'), primary_key=True)
    total_days = Column(Integer, nullable=False, default=30)
    used_days = Column(Integer, nullable=False, default=0)
    remaining_days = Column(Integer, nullable=False, default=30)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    employee = relationship('Employee', back_populates='leave_balance')
    
    def __repr__(self):
        return f"<LeaveBalance(employee_id={self.employee_id}, remaining={self.remaining_days}/{self.total_days})>"
    
    def use_days(self, days):
        """
        Deduct days from balance.
        
        Args:
            days: Number of days to use
            
        Raises:
            ValueError: If insufficient balance
        """
        if days > self.remaining_days:
            raise ValueError(f"Insufficient balance. Remaining days: {self.remaining_days}")
        self.used_days += days
        self.remaining_days -= days
    
    def can_request_leave(self, days):
        """Check if employee can request specified number of days."""
        return days <= self.remaining_days


class Salary(Base):
    """
    Salary history tracking.
    
    Records all salary changes and effective dates for audit trail.
    """
    __tablename__ = 'salaries'
    
    # Columns
    salary_id = Column(Integer, primary_key=True, autoincrement=True)
    employee_id = Column(Integer, ForeignKey('employees.employee_id'), nullable=False)
    amount = Column(Float, nullable=False)
    effective_date = Column(Date, nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    
    # Relationships
    employee = relationship('Employee', back_populates='salary_history')
    
    def __repr__(self):
        return f"<Salary(id={self.salary_id}, employee_id={self.employee_id}, amount={self.amount})>"


class EmployeeChatLink(Base):
    """
    Telegram authentication link.
    
    Links employee accounts to Telegram chat IDs for bot authentication.
    """
    __tablename__ = 'employee_chat_links'
    
    # Columns
    employee_id = Column(Integer, ForeignKey('employees.employee_id'), primary_key=True)
    telegram_chat_id = Column(String(100), unique=True, nullable=False)
    linked_at = Column(DateTime, server_default=func.now())
    last_interaction = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    employee = relationship('Employee', back_populates='chat_link')
    
    def __repr__(self):
        return f"<EmployeeChatLink(employee_id={self.employee_id}, chat_id='{self.telegram_chat_id}')>"
