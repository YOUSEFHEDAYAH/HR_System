"""
Telegram Bot
============
Modern Telegram bot with agent-based architecture.

This bot serves as a thin layer that:
- Handles Telegram API interactions
- Manages employee authentication
- Delegates all business logic to the AI agent
- Contains ZERO hardcoded business rules
"""

import os
import telebot
from dotenv import load_dotenv

from database.config import DatabaseConfig, DatabaseManager
from database.queries import HRQueries
from agent import HRAgent

# Load environment variables
load_dotenv()

# ===========================
# Configuration
# ===========================

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN not found in environment variables")

# ===========================
# Database Setup
# ===========================

print("🔧 Initializing bot...")

# Database configuration from environment
db_config = DatabaseConfig()

# Initialize database manager
db_manager = DatabaseManager(db_config)
if not db_manager.initialize():
    raise Exception("Failed to initialize database connection")

# Create database tables if they don't exist
from database.models import Base
Base.metadata.create_all(db_manager.engine)

# Initialize queries
queries = HRQueries(db_manager)

# Agent cache (one agent per employee)
agent_cache = {}

# ===========================
# Bot Initialization
# ===========================

bot = telebot.TeleBot(BOT_TOKEN)


# ===========================
# Helper Functions
# ===========================

def get_employee_from_message(message):
    """
    Get employee from Telegram message.
    
    Args:
        message: Telegram message object
        
    Returns:
        Employee: Employee object or None
    """
    telegram_id = str(message.chat.id)
    return queries.get_employee_by_telegram_id(telegram_id)


def get_or_create_agent(employee):
    """
    Get or create agent for employee.
    
    Uses caching to avoid recreating agents for the same employee.
    
    Args:
        employee: Employee object
        
    Returns:
        HRAgent: Agent instance for the employee
    """
    if employee.employee_id not in agent_cache:
        agent_cache[employee.employee_id] = HRAgent(queries, employee)
    return agent_cache[employee.employee_id]


# ===========================
# Bot Commands
# ===========================

@bot.message_handler(commands=['start'])
def start_command(message):
    """Handle /start command."""
    telegram_id = str(message.chat.id)
    emp = queries.get_employee_by_telegram_id(telegram_id)
    
    if emp:
        text = f"👋 Welcome back, {emp.full_name}!\n\n"
        text += "🤖 I'm your AI-powered HR assistant.\n\n"
        text += "💬 **Just chat naturally!**\n"
        text += "I understand:\n"
        text += "• Arabic & English\n"
        text += "• Natural requests\n"
        text += "• Context from previous messages\n\n"
        text += "**Examples:**\n"
        text += "• 'What's my leave balance?'\n"
        text += "• 'بدي أطلب إجازة'\n"
        text += "• 'Show me my salary'\n\n"
        text += "⚙️ Commands: /unlink to disconnect"
    else:
        text = "👋 Welcome to HR Bot!\n\n"
        text += "🔐 **Get Started:**\n"
        text += "Send your **Employee ID** to link your account.\n\n"
        text += "Example: `123`"
    
    bot.reply_to(message, text, parse_mode='Markdown')


@bot.message_handler(commands=['help'])
def help_command(message):
    """Handle /help command."""
    emp = get_employee_from_message(message)
    
    if not emp:
        bot.reply_to(message, "⚠️ Please register first by sending your Employee ID.")
        return
    
    # Delegate to agent (even help is handled intelligently)
    agent = get_or_create_agent(emp)
    bot.send_chat_action(message.chat.id, 'typing')
    
    try:
        response = agent.handle_message("What can you help me with?")
        bot.reply_to(message, response)
    except Exception as e:
        print(f"❌ Error in help: {e}")
        bot.reply_to(
            message, 
            "I can help you with:\n• Leave balance\n• Employee info\n• Salary details\n• Leave requests"
        )


@bot.message_handler(commands=['unlink'])
def unlink_command(message):
    """Handle /unlink command."""
    telegram_id = str(message.chat.id)
    emp = queries.get_employee_by_telegram_id(telegram_id)
    
    if not emp:
        bot.reply_to(message, "⚠️ You are not linked to any account.")
        return
    
    # Remove from cache
    if emp.employee_id in agent_cache:
        del agent_cache[emp.employee_id]
    
    queries.unlink_telegram(telegram_id)
    bot.reply_to(message, "✅ Account disconnected. Send your Employee ID to link again.")


# ===========================
# Message Handlers
# ===========================

@bot.message_handler(func=lambda m: m.text and m.text.isdigit() and len(m.text) <= 10)
def register_employee(message):
    """Handle employee registration."""
    telegram_id = str(message.chat.id)
    employee_id = int(message.text)
    
    # Check if already linked
    existing_emp = queries.get_employee_by_telegram_id(telegram_id)
    if existing_emp:
        bot.reply_to(
            message,
            f"⚠️ Already linked to {existing_emp.full_name}.\nUse /unlink first to change."
        )
        return
    
    # Check if employee exists
    emp = queries.get_employee_by_id(employee_id)
    
    if not emp:
        bot.reply_to(message, "❌ Employee not found. Check your Employee ID.")
        return
    
    # Link employee
    queries.link_employee_to_telegram(employee_id, telegram_id)
    
    text = f"✅ Welcome, {emp.full_name}!\n\n"
    text += "🤖 Your AI assistant is ready.\n\n"
    text += "💬 Try asking:\n"
    text += "• 'What's my balance?'\n"
    text += "• 'بدي أعرف رصيدي'\n"
    text += "• 'Request 3 days leave next week'"
    
    bot.reply_to(message, text)


@bot.message_handler(func=lambda m: True)
def handle_message(message):
    """
    Main message handler - delegates everything to the agent.
    
    CRITICAL ARCHITECTURAL DIFFERENCE:
    - Legacy: if/else chains based on intent
    - Modern: Single agent.handle_message() call
    
    The agent autonomously:
    - Understands the request
    - Calls appropriate functions
    - Validates data
    - Generates response
    
    This handler is a thin layer with ZERO business logic.
    
    Args:
        message: Telegram message object
    """
    emp = get_employee_from_message(message)
    
    if not emp:
        bot.reply_to(message, "⚠️ Please register first. Send your Employee ID.")
        return
    
    user_text = message.text.strip()
    
    # Show typing indicator
    bot.send_chat_action(message.chat.id, 'typing')
    
    # Get or create agent for this employee
    agent = get_or_create_agent(emp)
    
    # Delegate to agent (THE ENTIRE LOGIC)
    print(f"📥 [{emp.full_name}]: {user_text}")
    
    try:
        response = agent.handle_message(user_text)
        print(f"🤖 Response: {response[:100]}...")
        bot.reply_to(message, response)
    except Exception as e:
        print(f"❌ Agent error: {e}")
        import traceback
        traceback.print_exc()
        bot.reply_to(
            message,
            "❌ Sorry, I encountered an error. Please try again or use commands like /help"
        )


# ===========================
# Main Entry Point
# ===========================

def main():
    """Start the bot."""
    print("=" * 70)
    print("🤖 HR Telegram Bot Started")
    print("=" * 70)
    
    try:
        bot_info = bot.get_me()
        print(f"✅ Bot: @{bot_info.username}")
    except Exception as e:
        print(f"⚠️ Could not fetch bot info: {e}")
    
    print("🧠 Architecture: Agent-based")
    print("🔧 LLM: Google Gemini 2.5 Flash")
    print("💾 Database: PostgreSQL")
    print("=" * 70)
    print("⏳ Waiting for messages...\n")
    
    # Start bot
    try:
        bot.infinity_polling()
    except KeyboardInterrupt:
        print("\n🛑 Bot stopped by user")
    except Exception as e:
        print(f"\n❌ Bot error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
