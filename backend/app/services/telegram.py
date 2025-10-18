"""
Telegram Bot Service for Scalper Bot Notifications

This service handles all Telegram bot interactions including:
- Bot initialization and webhook setup
- Connection code generation and verification
- Sending notifications to connected users
- Handling user commands (/start, /connect, /disconnect, etc.)
"""

import logging
import random
import string
from datetime import datetime, timedelta, timezone
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from telegram import Update, Bot
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

from app.core.config import settings
from app.models.bot import TelegramConnection
from app.db.session import get_db

logger = logging.getLogger(__name__)


class TelegramService:
    """
    Telegram bot service for managing connections and notifications
    """

    def __init__(self):
        self.bot_token = settings.TELEGRAM_BOT_TOKEN
        self.application: Optional[Application] = None
        self.bot: Optional[Bot] = None

    async def initialize(self):
        """
        Initialize the Telegram bot application
        """
        if not self.bot_token:
            logger.warning("Telegram bot token not configured. Telegram features will be disabled.")
            return

        try:
            self.application = Application.builder().token(self.bot_token).build()
            self.bot = self.application.bot

            # Register command handlers
            self.application.add_handler(CommandHandler("start", self.handle_start))
            self.application.add_handler(CommandHandler("connect", self.handle_connect))
            self.application.add_handler(CommandHandler("disconnect", self.handle_disconnect))
            self.application.add_handler(CommandHandler("status", self.handle_status))
            self.application.add_handler(CommandHandler("help", self.handle_help))

            # Register message handler for connection codes
            self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))

            logger.info("Telegram bot initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Telegram bot: {e}")
            raise

    async def start_polling(self):
        """
        Start the bot in polling mode (for development)
        """
        if not self.application:
            await self.initialize()

        if self.application:
            logger.info("Starting Telegram bot polling...")
            await self.application.initialize()
            await self.application.start()
            await self.application.updater.start_polling()

    async def stop(self):
        """
        Stop the bot
        """
        if self.application:
            await self.application.updater.stop()
            await self.application.stop()
            await self.application.shutdown()
            logger.info("Telegram bot stopped")

    async def handle_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Handle /start command
        """
        welcome_message = (
            "🤖 *Welcome to Scalper Bot Notifier!*\n\n"
            "Get real-time notifications for your cryptocurrency scalping bot activities.\n\n"
            "*How to connect:*\n"
            "1. Open the Scalper Bot Dashboard\n"
            "2. Click 'Connect Telegram' button\n"
            "3. Copy the 6-digit connection code\n"
            "4. Send it to me here\n\n"
            "*Available Commands:*\n"
            "/connect - Get connection instructions\n"
            "/disconnect - Disconnect from dashboard\n"
            "/status - Check connection status\n"
            "/help - Show this message\n\n"
            "Ready to connect? Send me your connection code! 🚀"
        )

        await update.message.reply_text(welcome_message, parse_mode='Markdown')

    async def handle_connect(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Handle /connect command
        """
        message = (
            "📱 *Connect to Scalper Bot Dashboard*\n\n"
            "*Steps to connect:*\n"
            "1. Go to Scalper Bot Dashboard\n"
            "2. Click the 'Connect Telegram' button\n"
            "3. Copy the 6-digit code shown\n"
            "4. Send it to me\n\n"
            "⏳ Waiting for your connection code...\n\n"
            "💡 _Connection codes expire after 10 minutes_"
        )

        await update.message.reply_text(message, parse_mode='Markdown')

    async def handle_disconnect(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Handle /disconnect command
        """
        chat_id = str(update.effective_chat.id)

        # Get database session
        async for db in get_db():
            try:
                # Find connection
                result = await db.execute(
                    select(TelegramConnection).where(
                        TelegramConnection.chat_id == chat_id,
                        TelegramConnection.is_active == True
                    )
                )
                connection = result.scalar_one_or_none()

                if not connection:
                    await update.message.reply_text(
                        "❌ You're not currently connected to any dashboard.",
                        parse_mode='Markdown'
                    )
                    return

                # Deactivate connection
                connection.is_active = False
                await db.commit()

                message = (
                    "✅ *Successfully Disconnected*\n\n"
                    "You will no longer receive notifications from the Scalper Bot Dashboard.\n\n"
                    "To reconnect, use /connect command and follow the instructions."
                )

                await update.message.reply_text(message, parse_mode='Markdown')

            except Exception as e:
                logger.error(f"Error disconnecting Telegram: {e}")
                await update.message.reply_text(
                    "❌ Failed to disconnect. Please try again later.",
                    parse_mode='Markdown'
                )
            finally:
                break

    async def handle_status(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Handle /status command
        """
        chat_id = str(update.effective_chat.id)

        # Get database session
        async for db in get_db():
            try:
                # Find connection
                result = await db.execute(
                    select(TelegramConnection).where(
                        TelegramConnection.chat_id == chat_id,
                        TelegramConnection.is_active == True
                    )
                )
                connection = result.scalar_one_or_none()

                if not connection:
                    message = (
                        "⚠️ *Not Connected*\n\n"
                        "You're not currently connected to any dashboard.\n\n"
                        "Use /connect to get started!"
                    )
                else:
                    # Calculate time since connection
                    time_diff = datetime.now(timezone.utc) - connection.connected_at
                    hours = int(time_diff.total_seconds() / 3600)

                    message = (
                        f"✅ *Connected to Scalper Bot Dashboard*\n\n"
                        f"📱 Chat ID: `{connection.chat_id}`\n"
                        f"👤 Username: @{connection.username or 'N/A'}\n"
                        f"🕐 Connected: {hours} hours ago\n\n"
                        f"*You are receiving notifications for:*\n"
                        f"• Bot events (create, start, stop)\n"
                        f"• Trading activity\n"
                        f"• System alerts\n\n"
                        f"Use /disconnect to stop notifications."
                    )

                await update.message.reply_text(message, parse_mode='Markdown')

            except Exception as e:
                logger.error(f"Error checking status: {e}")
                await update.message.reply_text(
                    "❌ Failed to check status. Please try again later.",
                    parse_mode='Markdown'
                )
            finally:
                break

    async def handle_help(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Handle /help command
        """
        help_message = (
            "📖 *Scalper Bot Commands*\n\n"
            "*Basic Commands:*\n"
            "/start - Start the bot and see welcome message\n"
            "/connect - Get instructions to connect to dashboard\n"
            "/disconnect - Disconnect from dashboard\n"
            "/status - Check your connection status\n"
            "/help - Show this help message\n\n"
            "*How It Works:*\n"
            "1. Connect your Telegram to the dashboard using a 6-digit code\n"
            "2. Receive real-time notifications when:\n"
            "   • Bots are created or updated\n"
            "   • Bots start or stop\n"
            "   • Orders are executed\n"
            "   • Errors occur\n\n"
            "*Need More Help?*\n"
            "Visit the documentation or contact support.\n\n"
            "Happy trading! 🚀"
        )

        await update.message.reply_text(help_message, parse_mode='Markdown')

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Handle text messages (primarily for connection codes)
        """
        text = update.message.text.strip()
        chat_id = str(update.effective_chat.id)

        # Check if it's a 6-digit code
        if len(text) == 6 and text.isdigit():
            await self.verify_connection_code(update, text, chat_id)
        else:
            await update.message.reply_text(
                "🤔 I didn't understand that.\n\n"
                "If you're trying to connect, please send me the 6-digit code from the dashboard.\n\n"
                "Type /help for more information."
            )

    async def verify_connection_code(self, update: Update, code: str, chat_id: str):
        """
        Verify connection code and create connection
        """
        # Get database session
        async for db in get_db():
            try:
                # Find pending connection with this code
                result = await db.execute(
                    select(TelegramConnection).where(
                        TelegramConnection.connection_code == code,
                        TelegramConnection.is_active == False,
                        TelegramConnection.code_expires_at > datetime.now(timezone.utc)
                    )
                )
                connection = result.scalar_one_or_none()

                if not connection:
                    await update.message.reply_text(
                        "❌ *Invalid or Expired Code*\n\n"
                        "This connection code is either invalid or has expired.\n\n"
                        "Please:\n"
                        "1. Go to the dashboard\n"
                        "2. Click 'Connect Telegram' to generate a new code\n"
                        "3. Send me the new code\n\n"
                        "💡 _Codes expire after 10 minutes_",
                        parse_mode='Markdown'
                    )
                    return

                # Update connection with chat info
                connection.chat_id = chat_id
                connection.username = update.effective_user.username
                connection.first_name = update.effective_user.first_name
                connection.last_name = update.effective_user.last_name
                connection.is_active = True
                connection.connected_at = datetime.now(timezone.utc)
                connection.connection_code = None  # Clear the code
                connection.code_expires_at = None

                await db.commit()

                success_message = (
                    "✅ *Successfully Connected!*\n\n"
                    "Your Telegram is now connected to the Scalper Bot Dashboard.\n\n"
                    "*You will receive notifications for:*\n"
                    "• Bot creation and updates\n"
                    "• Bot start/stop events\n"
                    "• Trading activity\n"
                    "• System alerts\n\n"
                    "Use /status to check your connection anytime.\n"
                    "Use /disconnect to stop notifications.\n\n"
                    "Happy trading! 🚀"
                )

                await update.message.reply_text(success_message, parse_mode='Markdown')

            except Exception as e:
                logger.error(f"Error verifying connection code: {e}")
                await update.message.reply_text(
                    "❌ Failed to connect. Please try again later.",
                    parse_mode='Markdown'
                )
            finally:
                break

    @staticmethod
    async def generate_connection_code(db: AsyncSession) -> tuple[str, datetime]:
        """
        Generate a unique 6-digit connection code
        """
        # Generate random 6-digit code
        code = ''.join(random.choices(string.digits, k=6))

        # Check if code already exists
        result = await db.execute(
            select(TelegramConnection).where(
                TelegramConnection.connection_code == code,
                TelegramConnection.code_expires_at > datetime.now(timezone.utc)
            )
        )
        existing = result.scalar_one_or_none()

        # If code exists, generate a new one recursively
        if existing:
            return await TelegramService.generate_connection_code(db)

        # Code expires in 10 minutes
        expires_at = datetime.now(timezone.utc) + timedelta(minutes=10)

        return code, expires_at

    async def send_notification(
        self,
        db: AsyncSession,
        message: str,
        level: str = "INFO"
    ):
        """
        Send notification to all active Telegram connections
        """
        if not self.bot:
            logger.warning("Telegram bot not initialized. Cannot send notification.")
            return

        try:
            # Get all active connections
            result = await db.execute(
                select(TelegramConnection).where(TelegramConnection.is_active == True)
            )
            connections = result.scalars().all()

            if not connections:
                logger.info("No active Telegram connections to send notification to.")
                return

            # Add emoji based on level
            emoji_map = {
                "INFO": "ℹ️",
                "SUCCESS": "✅",
                "WARNING": "⚠️",
                "ERROR": "❌",
                "TELEGRAM": "📱"
            }
            emoji = emoji_map.get(level, "📬")

            formatted_message = f"{emoji} {message}"

            # Send to all connections
            for connection in connections:
                try:
                    await self.bot.send_message(
                        chat_id=connection.chat_id,
                        text=formatted_message,
                        parse_mode='Markdown'
                    )

                    # Update last notification time
                    connection.last_notification_at = datetime.now(timezone.utc)

                except Exception as e:
                    logger.error(f"Failed to send notification to {connection.chat_id}: {e}")
                    # If user blocked the bot, deactivate connection
                    if "blocked" in str(e).lower():
                        connection.is_active = False

            await db.commit()
            logger.info(f"Sent notification to {len(connections)} Telegram connection(s)")

        except Exception as e:
            logger.error(f"Error sending Telegram notification: {e}")


# Global instance
telegram_service = TelegramService()
