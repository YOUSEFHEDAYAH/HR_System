# Database Schema Documentation

## Overview

The HR database uses **PostgreSQL** with a normalized relational schema designed for HR operations. The schema supports employee management, leave tracking, salary history, and Telegram integration.

## Entity Relationship Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    DEPARTMENTS                               │
├─────────────────────────────────────────────────────────────┤
│ PK │ department_id      SERIAL                              │
│    │ department_name    VARCHAR(100)  UNIQUE NOT NULL       │
│ FK │ manager_id         INTEGER  → employees.employee_id    │
└────────────┬────────────────────────────────────────────────┘
             │ 1
             │
             │ N
             ▼
┌─────────────────────────────────────────────────────────────┐
│                     EMPLOYEES                                │
├─────────────────────────────────────────────────────────────┤
│ PK │ employee_id        SERIAL                              │
│    │ full_name          VARCHAR(150)  NOT NULL              │
│    │ email              VARCHAR(150)  UNIQUE NOT NULL       │
│ FK │ department_id      INTEGER  → departments.department_id│
│    │ role               ENUM(Employee, Manager, HR)         │
│    │ hire_date          DATE  NOT NULL                      │
│    │ salary             DOUBLE PRECISION  NOT NULL          │
└────────────┬────────────────────────────────────────────────┘
             │ 1
             │
             ├─────────────────┬─────────────────┬─────────────┐
             │ N               │ 1               │ N           │ 1
             ▼                 ▼                 ▼             ▼
┌──────────────────┐  ┌─────────────────┐  ┌──────────┐  ┌──────────┐
│ LEAVE_REQUESTS   │  │ LEAVE_BALANCES  │  │ SALARIES │  │ EMPLOYEE_│
│                  │  │                 │  │          │  │ CHAT_    │
├──────────────────┤  ├─────────────────┤  ├──────────┤  │ LINKS    │
│PK│leave_id       │  │PK│employee_id   │  │PK│salary_│  ├──────────┤
│FK│employee_id    │  │FK│→employees    │  │  │id     │  │PK│employee│
│  │start_date     │  │  │total_days    │  │FK│employe│  │FK│_id     │
│  │end_date       │  │  │used_days     │  │  │e_id   │  │  │telegram│
│  │reason         │  │  │remaining_days│  │  │amount │  │  │_chat_id│
│  │status         │  │  │updated_at    │  │  │effecti│  │  │linked_ │
│  │created_at     │  │                 │  │  │ve_date│  │  │at      │
│  │updated_at     │  └─────────────────┘  │  │created│  │  │last_   │
│                  │                        │  │_at    │  │  │interact│
└──────────────────┘                        └──────────┘  └──────────┘
```

## Tables

### 1. departments

**Purpose**: Organizational structure and hierarchy

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| department_id | SERIAL | PRIMARY KEY | Auto-incrementing department ID |
| department_name | VARCHAR(100) | NOT NULL, UNIQUE | Department name |
| manager_id | INTEGER | FK → employees.employee_id | Department manager (optional) |

**Indexes:**
- PRIMARY KEY on `department_id`
- UNIQUE on `department_name`
- INDEX on `manager_id`

**Sample Data:**
```sql
INSERT INTO departments (department_name, manager_id) VALUES
  ('Information Technology', 1),
  ('Human Resources', 3),
  ('Sales', 4);
```

---

### 2. employees

**Purpose**: Employee master data

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| employee_id | SERIAL | PRIMARY KEY | Auto-incrementing employee ID |
| full_name | VARCHAR(150) | NOT NULL | Employee full name |
| email | VARCHAR(150) | NOT NULL, UNIQUE | Email address |
| department_id | INTEGER | FK → departments.department_id, NOT NULL | Department |
| role | ENUM | NOT NULL | Employee/Manager/HR |
| hire_date | DATE | NOT NULL | Date of hire |
| salary | DOUBLE PRECISION | NOT NULL | Current salary |

**Enums:**
```sql
CREATE TYPE employeerole AS ENUM ('Employee', 'Manager', 'HR');
```

**Indexes:**
- PRIMARY KEY on `employee_id`
- UNIQUE on `email`
- INDEX on `department_id`
- INDEX on `role`

**Sample Data:**
```sql
INSERT INTO employees (full_name, email, department_id, role, hire_date, salary) VALUES
  ('Ahmad Mohammad Ali', 'ahmad@company.com', 1, 'Manager', '2020-01-15', 8500.00),
  ('Sara Hassan Ibrahim', 'sara@company.com', 1, 'Employee', '2021-06-10', 5000.00);
```

---

### 3. leave_requests

**Purpose**: Leave application tracking

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| leave_id | SERIAL | PRIMARY KEY | Auto-incrementing leave request ID |
| employee_id | INTEGER | FK → employees.employee_id, NOT NULL | Employee requesting leave |
| start_date | DATE | NOT NULL | Leave start date |
| end_date | DATE | NOT NULL | Leave end date |
| reason | VARCHAR(500) | NULL | Reason for leave |
| status | ENUM | NOT NULL, DEFAULT 'Pending' | Request status |
| created_at | TIMESTAMP | DEFAULT NOW() | Creation timestamp |
| updated_at | TIMESTAMP | DEFAULT NOW() | Last update timestamp |

**Enums:**
```sql
CREATE TYPE leavestatus AS ENUM ('Pending', 'Approved', 'Rejected');
```

**Indexes:**
- PRIMARY KEY on `leave_id`
- INDEX on `employee_id`
- INDEX on `status`
- INDEX on `start_date`

**Sample Data:**
```sql
INSERT INTO leave_requests (employee_id, start_date, end_date, reason, status) VALUES
  (1, '2026-02-15', '2026-02-20', 'Family vacation', 'Pending'),
  (2, '2026-01-10', '2026-01-12', 'Medical', 'Approved');
```

---

### 4. leave_balances

**Purpose**: Track available leave days per employee

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| employee_id | INTEGER | PRIMARY KEY, FK → employees.employee_id | Employee reference |
| total_days | INTEGER | NOT NULL, DEFAULT 30 | Total annual leave days |
| used_days | INTEGER | NOT NULL, DEFAULT 0 | Days already used |
| remaining_days | INTEGER | NOT NULL, DEFAULT 30 | Days remaining |
| updated_at | TIMESTAMP | DEFAULT NOW() | Last update timestamp |

**Indexes:**
- PRIMARY KEY on `employee_id`

**Business Rules:**
- `remaining_days = total_days - used_days`
- Updated when leave requests are approved

**Sample Data:**
```sql
INSERT INTO leave_balances (employee_id, total_days, used_days, remaining_days) VALUES
  (1, 30, 5, 25),
  (2, 30, 0, 30);
```

---

### 5. salaries

**Purpose**: Salary history and audit trail

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| salary_id | SERIAL | PRIMARY KEY | Auto-incrementing salary record ID |
| employee_id | INTEGER | FK → employees.employee_id, NOT NULL | Employee reference |
| amount | DOUBLE PRECISION | NOT NULL | Salary amount |
| effective_date | DATE | NOT NULL | Date salary became effective |
| created_at | TIMESTAMP | DEFAULT NOW() | Record creation timestamp |

**Indexes:**
- PRIMARY KEY on `salary_id`
- INDEX on `employee_id`
- INDEX on `effective_date`

**Sample Data:**
```sql
INSERT INTO salaries (employee_id, amount, effective_date) VALUES
  (1, 7000.00, '2020-01-15'),
  (1, 8500.00, '2021-06-01');  -- Salary increase
```

---

### 6. employee_chat_links

**Purpose**: Link employees to Telegram accounts

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| employee_id | INTEGER | PRIMARY KEY, FK → employees.employee_id | Employee reference |
| telegram_chat_id | VARCHAR(100) | NOT NULL, UNIQUE | Telegram chat ID |
| linked_at | TIMESTAMP | DEFAULT NOW() | Link creation timestamp |
| last_interaction | TIMESTAMP | DEFAULT NOW() | Last bot interaction |

**Indexes:**
- PRIMARY KEY on `employee_id`
- UNIQUE on `telegram_chat_id`

**Sample Data:**
```sql
INSERT INTO employee_chat_links (employee_id, telegram_chat_id) VALUES
  (1, '123456789'),
  (2, '987654321');
```

---

## Relationships

### One-to-Many

1. **Department → Employees**
   - One department has many employees
   - `departments.department_id` ← `employees.department_id`

2. **Employee → Leave Requests**
   - One employee has many leave requests
   - `employees.employee_id` ← `leave_requests.employee_id`

3. **Employee → Salaries**
   - One employee has many salary records (history)
   - `employees.employee_id` ← `salaries.employee_id`

### One-to-One

1. **Employee → Leave Balance**
   - One employee has one leave balance
   - `employees.employee_id` ← `leave_balances.employee_id`

2. **Employee → Chat Link**
   - One employee linked to one Telegram account
   - `employees.employee_id` ← `employee_chat_links.employee_id`

### Self-Referencing

1. **Department → Manager (Employee)**
   - Department's manager is an employee
   - `departments.manager_id` → `employees.employee_id`

---

## Constraints and Validations

### Database-Level Constraints

```sql
-- Email uniqueness
ALTER TABLE employees ADD CONSTRAINT uk_employees_email UNIQUE (email);

-- Department name uniqueness
ALTER TABLE departments ADD CONSTRAINT uk_departments_name UNIQUE (department_name);

-- Telegram chat ID uniqueness
ALTER TABLE employee_chat_links ADD CONSTRAINT uk_chat_links_telegram 
  UNIQUE (telegram_chat_id);

-- Leave date validation (start <= end)
ALTER TABLE leave_requests ADD CONSTRAINT chk_leave_dates 
  CHECK (start_date <= end_date);

-- Leave balance validation (used <= total)
ALTER TABLE leave_balances ADD CONSTRAINT chk_balance_valid 
  CHECK (used_days <= total_days);
```

### Application-Level Validations

Implemented in `agent.py` → `_request_leave()`:

1. **Date Validations:**
   - Start date must be before end date
   - Cannot request leave for past dates
   - Dates must be valid calendar dates

2. **Balance Validations:**
   - Sufficient remaining days
   - Maximum 2 pending requests per employee

3. **Business Rules:**
   - Leave duration = (end_date - start_date) + 1 days
   - Automatic status = 'Pending' on creation

---

## Queries

### Common Queries

**1. Get employee with department:**
```sql
SELECT e.*, d.department_name 
FROM employees e
JOIN departments d ON e.department_id = d.department_id
WHERE e.employee_id = ?;
```

**2. Get pending leave requests:**
```sql
SELECT lr.*, e.full_name
FROM leave_requests lr
JOIN employees e ON lr.employee_id = e.employee_id
WHERE lr.status = 'Pending'
ORDER BY lr.created_at;
```

**3. Get employees on leave today:**
```sql
SELECT e.full_name, lr.start_date, lr.end_date
FROM employees e
JOIN leave_requests lr ON e.employee_id = lr.employee_id
WHERE lr.status = 'Approved'
  AND CURRENT_DATE BETWEEN lr.start_date AND lr.end_date;
```

**4. Department statistics:**
```sql
SELECT d.department_name, 
       COUNT(e.employee_id) as employee_count,
       AVG(e.salary) as avg_salary
FROM departments d
LEFT JOIN employees e ON d.department_id = e.department_id
GROUP BY d.department_id, d.department_name;
```

---

## Indexes Strategy

### Primary Indexes (Auto-created)
- All PRIMARY KEY columns
- All UNIQUE columns

### Secondary Indexes (Recommended)
```sql
CREATE INDEX idx_employees_department ON employees(department_id);
CREATE INDEX idx_employees_role ON employees(role);
CREATE INDEX idx_leave_requests_employee ON leave_requests(employee_id);
CREATE INDEX idx_leave_requests_status ON leave_requests(status);
CREATE INDEX idx_leave_requests_dates ON leave_requests(start_date, end_date);
CREATE INDEX idx_salaries_employee ON salaries(employee_id);
CREATE INDEX idx_salaries_effective ON salaries(effective_date);
```

---

## Backup and Maintenance

### Backup Commands

```bash
# Full database backup
pg_dump -U postgres hr_db > backup_$(date +%Y%m%d).sql

# Schema only
pg_dump -U postgres -s hr_db > schema.sql

# Data only
pg_dump -U postgres -a hr_db > data.sql
```

### Restore Commands

```bash
# Restore full backup
psql -U postgres hr_db < backup_20260131.sql
```

---

## Migration Strategy

When making schema changes:

1. **Add column** (safe):
   ```sql
   ALTER TABLE employees ADD COLUMN phone VARCHAR(20);
   ```

2. **Modify column** (requires planning):
   ```sql
   -- 1. Add new column
   ALTER TABLE employees ADD COLUMN new_salary NUMERIC(10,2);
   -- 2. Migrate data
   UPDATE employees SET new_salary = salary;
   -- 3. Drop old column
   ALTER TABLE employees DROP COLUMN salary;
   -- 4. Rename new column
   ALTER TABLE employees RENAME COLUMN new_salary TO salary;
   ```

3. **Future**: Use Alembic for migrations

---

## Performance Considerations

1. **Connection Pooling**: Use SQLAlchemy pool
2. **Query Optimization**: Add indexes for frequent queries
3. **Partitioning**: Consider partitioning `leave_requests` by year for large datasets
4. **Archiving**: Move old salary records to archive table

---

## Security

1. **Passwords**: Never store in plaintext (use environment variables)
2. **SQL Injection**: Prevented by SQLAlchemy parameterized queries
3. **Access Control**: Role-based access in application layer
4. **Auditing**: Timestamps on all mutable tables
