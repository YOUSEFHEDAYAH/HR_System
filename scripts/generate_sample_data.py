"""
Generate Sample Data
====================
Generate realistic sample data for testing and development.

This script uses Faker to create:
- Departments
- Employees with different roles
- Leave balances
- Leave requests (pending and historical)
- Salary history

Usage:
    python scripts/generate_sample_data.py
"""

import sys
import os
from datetime import datetime, timedelta, date
import random

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from faker import Faker
from src.database.config import DatabaseConfig, DatabaseManager
from src.database.models import (
    Department, Employee, LeaveRequest, LeaveBalance, 
    Salary, EmployeeRole, LeaveStatus
)


class SampleDataGenerator:
    """Generate realistic sample data for the HR system."""
    
    def __init__(self, db_manager: DatabaseManager, locale='en_US'):
        """
        Initialize data generator.
        
        Args:
            db_manager: DatabaseManager instance
            locale: Faker locale (default: en_US)
        """
        self.db_manager = db_manager
        self.session = db_manager.get_session()
        self.fake = Faker(locale)
    
    def clear_all_data(self):
        """Clear all existing data from database."""
        try:
            print("🧹 Clearing existing data...")
            self.session.query(LeaveRequest).delete()
            self.session.query(LeaveBalance).delete()
            self.session.query(Salary).delete()
            self.session.query(Employee).delete()
            self.session.query(Department).delete()
            self.session.commit()
            print("✅ Database cleared\n")
        except Exception as e:
            self.session.rollback()
            print(f"❌ Failed to clear data: {e}\n")
    
    def generate_departments(self, count=5):
        """Generate departments."""
        print(f"🏢 Generating {count} departments...")
        
        names = [
            'Information Technology', 'Human Resources', 'Sales',
            'Marketing', 'Finance', 'Operations', 'Legal'
        ]
        
        departments = []
        for name in random.sample(names, min(count, len(names))):
            dept = Department(department_name=name)
            self.session.add(dept)
            self.session.flush()
            print(f"   ➕ {name} (ID: {dept.department_id})")
            departments.append(dept)
        
        self.session.commit()
        print(f"✅ Created {len(departments)} departments\n")
        return departments
    
    def generate_employees(self, departments, per_dept=5):
        """Generate employees for each department."""
        print(f"👨‍💼 Generating employees ({per_dept} per department)...")
        
        employees = []
        
        for dept in departments:
            for i in range(per_dept):
                # First employee is manager
                if i == 0:
                    role = EmployeeRole.MANAGER
                    salary = random.uniform(8000, 12000)
                # HR department gets HR role
                elif dept.department_name == 'Human Resources' and i == 1:
                    role = EmployeeRole.HR
                    salary = random.uniform(6000, 9000)
                else:
                    role = EmployeeRole.EMPLOYEE
                    salary = random.uniform(3000, 7000)
                
                emp = Employee(
                    full_name=self.fake.name(),
                    email=self.fake.unique.email(),
                    department_id=dept.department_id,
                    role=role,
                    hire_date=self.fake.date_between('-10y', '-1y'),
                    salary=round(salary, 2)
                )
                
                self.session.add(emp)
                self.session.flush()
                print(f"   ➕ {emp.full_name} - {role.value} (ID: {emp.employee_id})")
                employees.append(emp)
        
        # Assign managers to departments
        for dept in departments:
            manager = next(
                e for e in employees 
                if e.department_id == dept.department_id and e.role == EmployeeRole.MANAGER
            )
            dept.manager_id = manager.employee_id
            print(f"   👔 {dept.department_name} manager: {manager.full_name}")
        
        self.session.commit()
        print(f"✅ Created {len(employees)} employees\n")
        return employees
    
    def generate_leave_balances(self, employees):
        """Generate leave balances for employees."""
        print("🏖️  Generating leave balances...")
        
        for emp in employees:
            # Calculate years of service
            years = (datetime.now().date() - emp.hire_date).days // 365
            total = min(30 + years * 2, 45)  # Max 45 days
            used = random.randint(0, total // 2)
            
            balance = LeaveBalance(
                employee_id=emp.employee_id,
                total_days=total,
                used_days=used,
                remaining_days=total - used
            )
            
            self.session.add(balance)
        
        self.session.commit()
        print(f"✅ Created {len(employees)} leave balances\n")
    
    def generate_leave_requests(self, employees):
        """Generate leave requests (historical and pending)."""
        print("📝 Generating leave requests...")
        
        today = datetime.now().date()
        count = 0
        
        for emp in employees:
            # Each employee gets 1-3 requests
            for _ in range(random.randint(1, 3)):
                # Mix of past and future dates
                offset = random.randint(-180, 90)
                start = today + timedelta(days=offset)
                duration = random.randint(1, 10)
                end = start + timedelta(days=duration - 1)
                
                # Past requests are approved, future are pending
                status = LeaveStatus.APPROVED if offset < 0 else LeaveStatus.PENDING
                
                req = LeaveRequest(
                    employee_id=emp.employee_id,
                    start_date=start,
                    end_date=end,
                    reason=self.fake.sentence(6),
                    status=status
                )
                
                self.session.add(req)
                count += 1
        
        self.session.commit()
        print(f"✅ Created {count} leave requests\n")
    
    def generate_salary_history(self, employees):
        """Generate salary history records."""
        print("💰 Generating salary history...")
        
        count = 0
        for emp in employees:
            salary = emp.salary
            eff_date = emp.hire_date
            
            # Initial salary record
            record = Salary(
                employee_id=emp.employee_id,
                amount=salary,
                effective_date=eff_date
            )
            self.session.add(record)
            count += 1
            
            # Add 0-2 salary increases
            for _ in range(random.randint(0, 2)):
                eff_date += timedelta(days=random.randint(180, 540))
                if eff_date > datetime.now().date():
                    break
                
                salary = round(salary * random.uniform(1.05, 1.15), 2)
                self.session.add(Salary(
                    employee_id=emp.employee_id,
                    amount=salary,
                    effective_date=eff_date
                ))
                count += 1
        
        self.session.commit()
        print(f"✅ Created {count} salary records\n")
    
    def generate_all(self, dept_count=5, emp_per_dept=5):
        """Generate complete sample dataset."""
        print("\n🎲 STARTING DATA GENERATION")
        print("=" * 60)
        print()
        
        self.clear_all_data()
        
        depts = self.generate_departments(dept_count)
        emps = self.generate_employees(depts, emp_per_dept)
        self.generate_leave_balances(emps)
        self.generate_leave_requests(emps)
        self.generate_salary_history(emps)
        
        print("=" * 60)
        print("🎉 DATA GENERATION COMPLETED!")
        print("=" * 60)
        print()
        print(f"📊 Summary:")
        print(f"   • {len(depts)} departments")
        print(f"   • {len(emps)} employees")
        print(f"   • {len(emps)} leave balances")
        print()
        print("Sample employee IDs for testing:")
        for emp in emps[:5]:
            print(f"   • ID {emp.employee_id}: {emp.full_name} ({emp.role.value})")
        print()


def main():
    """Main entry point."""
    print("=" * 60)
    print("🎲 HR Sample Data Generator")
    print("=" * 60)
    print()
    
    # Initialize database
    db_config = DatabaseConfig()
    db_manager = DatabaseManager(db_config)
    
    if not db_manager.initialize():
        print("❌ Failed to connect to database!")
        return False
    
    # Generate data
    generator = SampleDataGenerator(db_manager)
    generator.generate_all(dept_count=5, emp_per_dept=5)
    
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
