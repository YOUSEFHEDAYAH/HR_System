"""
Database Queries
===============
Common database query operations for the HR system.

This module provides a high-level query interface for:
- Employee management
- Department operations
- Leave balance tracking
- Leave request processing
- Salary history
- Statistics and reporting
"""

from sqlalchemy import func, and_, or_, desc
from datetime import datetime, timedelta
from .models import (
    Employee, Department, LeaveRequest, LeaveBalance, 
    Salary, EmployeeChatLink, EmployeeRole, LeaveStatus
)
from .config import DatabaseManager


class HRQueries:
    """
    HR database query operations.
    
    Provides methods for all HR-related database operations
    with proper error handling and transaction management.
    """
    
    def __init__(self, db_manager: DatabaseManager):
        """
        Initialize HR queries.
        
        Args:
            db_manager: DatabaseManager instance
        """
        self.db_manager = db_manager
        self.session = db_manager.get_session()
    
    # ===========================
    # Employee Queries
    # ===========================
    
    def get_employee_by_email(self, email):
        """Get employee by email address."""
        return self.session.query(Employee).filter(Employee.email == email).first()
    
    def get_employee_by_id(self, employee_id):
        """Get employee by ID."""
        return self.session.query(Employee).filter(Employee.employee_id == employee_id).first()
    
    def get_all_employees(self):
        """Get all employees."""
        return self.session.query(Employee).all()
    
    def get_employees_by_department(self, department_id):
        """Get all employees in a specific department."""
        return self.session.query(Employee).filter(
            Employee.department_id == department_id
        ).all()
    
    def get_employees_by_role(self, role: EmployeeRole):
        """Get all employees with a specific role."""
        return self.session.query(Employee).filter(Employee.role == role).all()
    
    # ===========================
    # Department Queries
    # ===========================
    
    def get_all_departments(self):
        """Get all departments."""
        return self.session.query(Department).all()
    
    def get_department_by_name(self, name):
        """Get department by name (case-insensitive search)."""
        return self.session.query(Department).filter(
            Department.department_name.ilike(f"%{name}%")
        ).first()
    
    def get_department_employee_count(self, department_id):
        """Get number of employees in a department."""
        return self.session.query(Employee).filter(
            Employee.department_id == department_id
        ).count()
    
    # ===========================
    # Leave Balance Queries
    # ===========================
    
    def get_employee_leave_balance(self, employee_id):
        """Get employee's current leave balance."""
        return self.session.query(LeaveBalance).filter(
            LeaveBalance.employee_id == employee_id
        ).first()
    
    def get_employees_with_low_balance(self, threshold=5):
        """Get employees with leave balance below threshold."""
        return self.session.query(Employee, LeaveBalance).join(
            LeaveBalance
        ).filter(
            LeaveBalance.remaining_days <= threshold
        ).all()
    
    # ===========================
    # Leave Request Queries
    # ===========================
    
    def create_leave_request(self, employee_id, start_date, end_date, reason="Personal"):
        """
        Create a new leave request.
        
        Args:
            employee_id: Employee ID
            start_date: Leave start date (date object)
            end_date: Leave end date (date object)
            reason: Reason for leave (optional)
            
        Returns:
            LeaveRequest: Created leave request object
        """
        new_request = LeaveRequest(
            employee_id=employee_id,
            start_date=start_date,
            end_date=end_date,
            reason=reason,
            status=LeaveStatus.PENDING,
            created_at=datetime.now()
        )
        self.session.add(new_request)
        self.session.commit()
        return new_request
    
    def get_employee_leave_requests(self, employee_id, status=None):
        """
        Get leave requests for an employee.
        
        Args:
            employee_id: Employee ID
            status: Optional LeaveStatus filter
            
        Returns:
            list: List of leave requests (newest first)
        """
        query = self.session.query(LeaveRequest).filter(
            LeaveRequest.employee_id == employee_id
        )
        
        if status:
            query = query.filter(LeaveRequest.status == status)
        
        return query.order_by(desc(LeaveRequest.created_at)).all()
    
    def get_pending_leave_requests(self, department_id=None):
        """
        Get all pending leave requests.
        
        Args:
            department_id: Optional department filter
            
        Returns:
            list: List of (LeaveRequest, Employee) tuples
        """
        query = self.session.query(LeaveRequest, Employee).join(
            Employee
        ).filter(
            LeaveRequest.status == LeaveStatus.PENDING
        )
        
        if department_id:
            query = query.filter(Employee.department_id == department_id)
        
        return query.order_by(LeaveRequest.created_at).all()
    
    def get_upcoming_leaves(self, days_ahead=30):
        """
        Get approved leaves starting in the next N days.
        
        Args:
            days_ahead: Number of days to look ahead
            
        Returns:
            list: List of (LeaveRequest, Employee) tuples
        """
        today = datetime.now().date()
        future_date = today + timedelta(days=days_ahead)
        
        return self.session.query(LeaveRequest, Employee).join(
            Employee
        ).filter(
            and_(
                LeaveRequest.status == LeaveStatus.APPROVED,
                LeaveRequest.start_date >= today,
                LeaveRequest.start_date <= future_date
            )
        ).order_by(LeaveRequest.start_date).all()
    
    def get_employees_on_leave_today(self):
        """Get employees currently on approved leave."""
        today = datetime.now().date()
        
        return self.session.query(Employee, LeaveRequest).join(
            LeaveRequest
        ).filter(
            and_(
                LeaveRequest.status == LeaveStatus.APPROVED,
                LeaveRequest.start_date <= today,
                LeaveRequest.end_date >= today
            )
        ).all()
    
    # ===========================
    # Salary Queries
    # ===========================
    
    def get_employee_current_salary(self, employee_id):
        """Get employee's most recent salary record."""
        return self.session.query(Salary).filter(
            Salary.employee_id == employee_id
        ).order_by(desc(Salary.effective_date)).first()
    
    def get_employee_salary_history(self, employee_id):
        """Get employee's complete salary history."""
        return self.session.query(Salary).filter(
            Salary.employee_id == employee_id
        ).order_by(desc(Salary.effective_date)).all()
    
    def get_department_average_salary(self, department_id):
        """Get average salary for a department."""
        result = self.session.query(
            func.avg(Employee.salary)
        ).filter(
            Employee.department_id == department_id
        ).scalar()
        
        return round(result, 2) if result else 0
    
    # ===========================
    # Telegram Integration Queries
    # ===========================
    
    def link_employee_to_telegram(self, employee_id, telegram_chat_id):
        """
        Link employee to Telegram chat ID.
        
        Args:
            employee_id: Employee ID
            telegram_chat_id: Telegram chat ID
            
        Returns:
            bool: True if successful
        """
        existing = self.session.query(EmployeeChatLink).filter(
            EmployeeChatLink.telegram_chat_id == telegram_chat_id
        ).first()
        
        if existing:
            existing.employee_id = employee_id
            existing.last_interaction = datetime.now()
        else:
            link = EmployeeChatLink(
                employee_id=employee_id,
                telegram_chat_id=telegram_chat_id
            )
            self.session.add(link)
        
        self.session.commit()
        return True
    
    def get_employee_by_telegram_id(self, telegram_chat_id):
        """
        Get employee by Telegram chat ID.
        
        Args:
            telegram_chat_id: Telegram chat ID
            
        Returns:
            Employee: Employee object or None
        """
        link = self.session.query(EmployeeChatLink).filter(
            EmployeeChatLink.telegram_chat_id == telegram_chat_id
        ).first()
        
        if link:
            link.last_interaction = datetime.now()
            self.session.commit()
            return self.get_employee_by_id(link.employee_id)
        return None
    
    def unlink_telegram(self, telegram_chat_id):
        """
        Unlink employee from Telegram.
        
        Args:
            telegram_chat_id: Telegram chat ID
            
        Returns:
            bool: True if successful
        """
        link = self.session.query(EmployeeChatLink).filter(
            EmployeeChatLink.telegram_chat_id == telegram_chat_id
        ).first()
        
        if link:
            self.session.delete(link)
            self.session.commit()
            return True
        return False
    
    # ===========================
    # Statistics & Reports
    # ===========================
    
    def get_employee_statistics(self):
        """Get overall employee statistics."""
        total = self.session.query(Employee).count()
        by_role = self.session.query(
            Employee.role,
            func.count(Employee.employee_id)
        ).group_by(Employee.role).all()
        
        by_dept = self.session.query(
            Department.department_name,
            func.count(Employee.employee_id)
        ).join(Employee).group_by(Department.department_name).all()
        
        return {
            'total_employees': total,
            'by_role': {role.value: count for role, count in by_role},
            'by_department': {dept: count for dept, count in by_dept}
        }
    
    def get_leave_statistics(self):
        """Get overall leave statistics."""
        total_requests = self.session.query(LeaveRequest).count()
        
        by_status = self.session.query(
            LeaveRequest.status,
            func.count(LeaveRequest.leave_id)
        ).group_by(LeaveRequest.status).all()
        
        total_balance = self.session.query(
            func.sum(LeaveBalance.total_days),
            func.sum(LeaveBalance.used_days),
            func.sum(LeaveBalance.remaining_days)
        ).first()
        
        return {
            'total_requests': total_requests,
            'by_status': {status.value: count for status, count in by_status},
            'total_days_available': total_balance[0] or 0,
            'total_days_used': total_balance[1] or 0,
            'total_days_remaining': total_balance[2] or 0
        }
    
    def get_salary_statistics(self):
        """Get overall salary statistics."""
        stats = self.session.query(
            func.min(Employee.salary).label('min_salary'),
            func.max(Employee.salary).label('max_salary'),
            func.avg(Employee.salary).label('avg_salary'),
            func.count(Employee.employee_id).label('employee_count')
        ).first()
        
        return {
            'min_salary': round(stats.min_salary, 2) if stats.min_salary else 0,
            'max_salary': round(stats.max_salary, 2) if stats.max_salary else 0,
            'avg_salary': round(stats.avg_salary, 2) if stats.avg_salary else 0,
            'employee_count': stats.employee_count
        }
