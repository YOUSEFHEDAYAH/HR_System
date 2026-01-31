"""
Gemini AI Agent
===============
Autonomous HR agent using Google Gemini's function calling.

This agent uses an agent-based architecture where:
- No hardcoded if/else intent matching
- LLM autonomously decides which functions to call
- Self-extending through tool definitions
- Context-aware and conversational
"""

import os
from datetime import datetime, date
from dotenv import load_dotenv
from google import genai
from google.genai import types

# Load environment variables
load_dotenv()

# Initialize Gemini client
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY not found in environment variables")

client = genai.Client(api_key=GEMINI_API_KEY)


class HRAgent:
    """
    Autonomous HR Agent using Gemini with function calling.
    
    The agent handles employee requests by:
    1. Understanding natural language (Arabic/English)
    2. Autonomously selecting appropriate functions
    3. Executing database operations
    4. Generating natural language responses
    
    Key difference from traditional chatbots:
    - No manual intent classification
    - No hardcoded business logic in bot layer
    - AI decides the execution flow
    """
    
    def __init__(self, hr_queries, employee):
        """
        Initialize HR Agent.
        
        Args:
            hr_queries: HRQueries instance (database operations)
            employee: Current employee object (for context)
        """
        self.queries = hr_queries
        self.employee = employee
        self.model_id = "models/gemini-2.5-flash"
        
        # Define available tools/functions
        self.tools = self._define_tools()
        
        # Map tool names to actual implementations
        self.function_map = {
            'get_leave_balance': self._get_leave_balance,
            'get_employee_info': self._get_employee_info,
            'get_salary_info': self._get_salary_info,
            'get_leave_requests': self._get_leave_requests,
            'request_leave': self._request_leave,
        }
    
    def _define_tools(self):
        """
        Define available tools for the AI agent.
        
        These tools are presented to Gemini, which autonomously
        decides which ones to call based on user requests.
        
        Returns:
            list: List of Tool objects with function declarations
        """
        return [
            types.Tool(
                function_declarations=[
                    types.FunctionDeclaration(
                        name='get_leave_balance',
                        description='Get the employee\'s current leave balance (total, used, remaining days)',
                        parameters=types.Schema(
                            type=types.Type.OBJECT,
                            properties={},
                            required=[]
                        )
                    ),
                    types.FunctionDeclaration(
                        name='get_employee_info',
                        description='Get employee information (name, email, department, position, salary, hire date)',
                        parameters=types.Schema(
                            type=types.Type.OBJECT,
                            properties={},
                            required=[]
                        )
                    ),
                    types.FunctionDeclaration(
                        name='get_salary_info',
                        description='Get employee salary information and history',
                        parameters=types.Schema(
                            type=types.Type.OBJECT,
                            properties={},
                            required=[]
                        )
                    ),
                    types.FunctionDeclaration(
                        name='get_leave_requests',
                        description='Get employee\'s leave request history with status',
                        parameters=types.Schema(
                            type=types.Type.OBJECT,
                            properties={},
                            required=[]
                        )
                    ),
                    types.FunctionDeclaration(
                        name='request_leave',
                        description='Submit a new leave request for the employee',
                        parameters=types.Schema(
                            type=types.Type.OBJECT,
                            properties={
                                'start_date': types.Schema(
                                    type=types.Type.STRING,
                                    description='Leave start date in YYYY-MM-DD format'
                                ),
                                'end_date': types.Schema(
                                    type=types.Type.STRING,
                                    description='Leave end date in YYYY-MM-DD format'
                                ),
                                'reason': types.Schema(
                                    type=types.Type.STRING,
                                    description='Reason for leave (optional, default: Personal)'
                                )
                            },
                            required=['start_date', 'end_date']
                        )
                    ),
                ]
            )
        ]
    
    # ===========================
    # Tool Implementations
    # ===========================
    
    def _get_leave_balance(self, **kwargs):
        """Get employee leave balance."""
        balance = self.queries.get_employee_leave_balance(self.employee.employee_id)
        
        if not balance:
            return {"error": "No leave balance found"}
        
        return {
            "total_days": balance.total_days,
            "used_days": balance.used_days,
            "remaining_days": balance.remaining_days
        }
    
    def _get_employee_info(self, **kwargs):
        """Get employee information."""
        dept_name = self.employee.department.department_name if self.employee.department else "N/A"
        
        return {
            "name": self.employee.full_name,
            "email": self.employee.email,
            "department": dept_name,
            "position": self.employee.role.value,
            "hire_date": str(self.employee.hire_date),
            "salary": float(self.employee.salary)
        }
    
    def _get_salary_info(self, **kwargs):
        """Get employee salary information."""
        salary_history = self.queries.get_employee_salary_history(self.employee.employee_id)
        
        if not salary_history:
            return {"error": "No salary information found"}
        
        latest = salary_history[0]
        return {
            "current_salary": float(latest.amount),
            "effective_date": str(latest.effective_date),
            "history_count": len(salary_history)
        }
    
    def _get_leave_requests(self, **kwargs):
        """Get employee leave requests."""
        requests = self.queries.get_employee_leave_requests(self.employee.employee_id)
        
        if not requests:
            return {"message": "No leave requests found"}
        
        result = []
        for req in requests[:5]:  # Last 5 requests
            duration = (req.end_date - req.start_date).days + 1
            result.append({
                "start_date": str(req.start_date),
                "end_date": str(req.end_date),
                "duration_days": duration,
                "status": req.status.value,
                "reason": req.reason or "N/A"
            })
        
        return {"requests": result, "total": len(requests)}
    
    def _request_leave(self, start_date, end_date, reason="Personal"):
        """Submit leave request."""
        try:
            # Parse dates
            start = datetime.strptime(start_date, '%Y-%m-%d').date()
            end = datetime.strptime(end_date, '%Y-%m-%d').date()
            
            # Validation
            if start > end:
                return {"error": "Start date must be before end date"}
            
            if start < date.today():
                return {"error": "Cannot request leave for past dates"}
            
            # Check balance
            duration = (end - start).days + 1
            balance = self.queries.get_employee_leave_balance(self.employee.employee_id)
            
            if not balance or balance.remaining_days < duration:
                return {
                    "error": f"Insufficient balance. Remaining: {balance.remaining_days if balance else 0} days"
                }
            
            # Check pending requests limit
            from .database.models import LeaveStatus
            pending = self.queries.get_employee_leave_requests(
                self.employee.employee_id, 
                status=LeaveStatus.PENDING
            )
            
            if len(pending) >= 2:
                return {"error": "You already have 2 pending requests"}
            
            # Create request
            new_request = self.queries.create_leave_request(
                self.employee.employee_id,
                start,
                end,
                reason
            )
            
            return {
                "success": True,
                "start_date": str(start),
                "end_date": str(end),
                "duration_days": duration,
                "reason": reason,
                "status": "Pending approval"
            }
            
        except ValueError as e:
            return {"error": f"Invalid date format: {str(e)}"}
        except Exception as e:
            return {"error": f"Failed to create request: {str(e)}"}
    
    # ===========================
    # Agent Core Logic
    # ===========================
    
    def handle_message(self, user_message):
        """
        Main agent loop - handles user message autonomously.
        
        Flow:
        1. Send message + tools to LLM
        2. LLM decides which function(s) to call
        3. Execute function(s)
        4. Send results back to LLM
        5. LLM generates final response
        
        This is the key architectural difference:
        - No manual intent matching
        - No if/else chains
        - LLM autonomously orchestrates the interaction
        
        Args:
            user_message: User's natural language request
            
        Returns:
            str: AI-generated response
        """
        
        # System instruction for the agent
        system_instruction = f"""You are an HR assistant helping {self.employee.full_name}.

You have access to various HR functions. Use them to help the employee.

Guidelines:
- Be friendly and professional
- Use function calls to get data
- Respond in the same language as the user (Arabic/English)
- For greetings, respond naturally without calling functions
- For help requests, explain available capabilities
- Always confirm actions before executing (especially leave requests)

Available capabilities:
- Check leave balance
- View employee information
- Check salary details
- View leave request history
- Submit leave requests"""
        
        # Initial API call with tools
        response = client.models.generate_content(
            model=self.model_id,
            contents=user_message,
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                tools=self.tools,
                temperature=0.2
            )
        )
        
        # Check if LLM wants to call functions
        function_calls = []
        if response.candidates[0].content.parts:
            for part in response.candidates[0].content.parts:
                if hasattr(part, 'function_call') and part.function_call:
                    function_calls.append(part.function_call)
        
        # If no function calls, return text response directly
        if not function_calls:
            return response.text
        
        # Execute function calls
        function_responses = []
        for func_call in function_calls:
            func_name = func_call.name
            func_args = dict(func_call.args) if func_call.args else {}
            
            # Execute the function
            if func_name in self.function_map:
                result = self.function_map[func_name](**func_args)
                function_responses.append(
                    types.Part.from_function_response(
                        name=func_name,
                        response=result
                    )
                )
        
        # Send function results back to LLM for final response
        final_response = client.models.generate_content(
            model=self.model_id,
            contents=[
                user_message,
                response.candidates[0].content,
                types.Content(
                    role='function',
                    parts=function_responses
                )
            ],
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                tools=self.tools
            )
        )
        
        return final_response.text
