from telegram import Update
from telegram.ext import (
  Application,
  MessageHandler,
  CommandHandler,
  ChatMemberHandler,
  filters,
  CallbackContext
)
from telegram.constants import ChatMemberStatus  # Import ChatMemberStatus constants
import smtplib
from email.mime.text import MIMEText
from dotenv import load_dotenv
import os
import sqlite3
from contextlib import contextmanager

load_dotenv()

bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
SMTP_SERVER = os.getenv('SMTP_SERVER')
SMTP_PORT = int(os.getenv('SMTP_PORT', 587))  # Convert port to integer, with default 587
EMAIL_ADDRESS = os.getenv('EMAIL_ADDRESS')
EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD')
ADMIN_USER_ID = int(os.getenv('ADMIN_USER_ID'))  # Admin's Telegram user ID

# Database configuration
DB_FILE = 'bot.db'


@contextmanager
def get_db_connection():
  conn = sqlite3.connect(DB_FILE)
  conn.row_factory = sqlite3.Row
  try:
    yield conn
    conn.commit()
  finally:
    conn.close()


def init_db():
  with get_db_connection() as conn:
    conn.execute(
      """
      CREATE TABLE IF NOT EXISTS groups (
        group_id TEXT PRIMARY KEY,
        title TEXT NOT NULL
      )
      """
    )
    conn.execute(
      """
      CREATE TABLE IF NOT EXISTS group_configs (
        group_id TEXT PRIMARY KEY,
        hashtag TEXT NOT NULL,
        email_address TEXT NOT NULL,
        FOREIGN KEY (group_id) REFERENCES groups (group_id) ON DELETE CASCADE
      )
      """
    )


def upsert_group(group_id: str, title: str):
  with get_db_connection() as conn:
    conn.execute(
      "INSERT INTO groups (group_id, title) VALUES (?, ?) "
      "ON CONFLICT(group_id) DO UPDATE SET title = excluded.title",
      (group_id, title)
    )


def delete_group(group_id: str):
  with get_db_connection() as conn:
    conn.execute("DELETE FROM groups WHERE group_id = ?", (group_id,))


def get_group(group_id: str):
  with get_db_connection() as conn:
    cursor = conn.execute(
      "SELECT group_id, title FROM groups WHERE group_id = ?",
      (group_id,)
    )
    return cursor.fetchone()


def get_groups():
  with get_db_connection() as conn:
    cursor = conn.execute("SELECT group_id, title FROM groups ORDER BY title")
    return cursor.fetchall()


def group_exists(group_id: str) -> bool:
  with get_db_connection() as conn:
    cursor = conn.execute("SELECT 1 FROM groups WHERE group_id = ?", (group_id,))
    return cursor.fetchone() is not None


def upsert_group_config(group_id: str, hashtag: str, email_address: str):
  with get_db_connection() as conn:
    conn.execute(
      "INSERT INTO group_configs (group_id, hashtag, email_address) VALUES (?, ?, ?) "
      "ON CONFLICT(group_id) DO UPDATE SET hashtag = excluded.hashtag, email_address = excluded.email_address",
      (group_id, hashtag, email_address)
    )


def delete_group_config(group_id: str):
  with get_db_connection() as conn:
    conn.execute("DELETE FROM group_configs WHERE group_id = ?", (group_id,))


def get_group_config(group_id: str):
  with get_db_connection() as conn:
    cursor = conn.execute(
      "SELECT hashtag, email_address FROM group_configs WHERE group_id = ?",
      (group_id,)
    )
    return cursor.fetchone()

def send_email(subject, body, to_email_address):
  msg = MIMEText(body)
  msg['Subject'] = subject
  msg['From'] = EMAIL_ADDRESS
  msg['To'] = to_email_address

  with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
    server.starttls()
    server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
    server.sendmail(EMAIL_ADDRESS, to_email_address, msg.as_string())

async def message_handler(update: Update, context: CallbackContext):
  if not update.message or not update.message.text:
    return  # Ignore non-text messages

  message = update.message.text
  sender = update.message.from_user.username or update.message.from_user.first_name
  chat = update.effective_chat

  print(f"Received message from {sender} in chat {chat.id}: {message}")

  # Check if group has a configured hashtag and email address
  group_id = str(chat.id)
  config = get_group_config(group_id)
  if config:
    hashtag = config['hashtag']
    to_email_address = config['email_address']
    if hashtag and to_email_address and hashtag.lower() in message.lower():
      subject = f"New message from {sender} in Telegram Group ({chat.title})"
      body = f"Sender: {sender}\n\nMessage: {message}"
      send_email(subject, body, to_email_address)

# Updated handler for chat member updates
async def chat_member_handler(update: Update, context: CallbackContext):
  result = update.my_chat_member  # ChatMemberUpdated object
  chat = update.effective_chat
  new_status = result.new_chat_member.status

  # Check if the bot was added to a group
  if new_status in [ChatMemberStatus.MEMBER, ChatMemberStatus.ADMINISTRATOR]:
    group_id = str(chat.id)
    group_title = chat.title
    already_known = group_exists(group_id)
    upsert_group(group_id, group_title)
    if not already_known:
      print(f"Bot added to group {group_title} (ID: {group_id})")
  # Check if the bot was removed from a group
  elif new_status in [ChatMemberStatus.RESTRICTED, ChatMemberStatus.LEFT]:
    group_id = str(chat.id)
    group_row = get_group(group_id)
    group_title = group_row['title'] if group_row else "Unknown Group"
    config = get_group_config(group_id)
    if group_row:
      delete_group(group_id)
      print(f"Bot removed from group {group_title} (ID: {group_id})")
    # Remove the group's configurations
    if config:
      delete_group_config(group_id)
      print(f"Configuration for group {group_title} (ID: {group_id}) has been deleted.")
    # Optionally, notify the admin
    try:
      await context.bot.send_message(
        chat_id=ADMIN_USER_ID,
        text=f"The bot has been removed from group '{group_title}' (ID: {group_id}).\n"
             f"The group's configuration has been deleted."
      )
    except Exception as e:
      print(f"Failed to send notification to admin: {e}")

# Admin commands
async def list_groups(update: Update, context: CallbackContext):
  user_id = update.effective_user.id
  if user_id != ADMIN_USER_ID:
    await update.message.reply_text("You are not authorized to use this command.")
    return

  groups = get_groups()
  if groups:
    response = "Groups the bot is in:\n"
    for group in groups:
      response += f"ID: {group['group_id']}, Title: {group['title']}\n"
  else:
    response = "No groups found."
  await update.message.reply_text(response)

async def set_config(update: Update, context: CallbackContext):
  user_id = update.effective_user.id
  if user_id != ADMIN_USER_ID:
    await update.message.reply_text("You are not authorized to use this command.")
    return

  args = context.args
  if len(args) < 3:
    await update.message.reply_text("Usage: /set_config <group_id> <hashtag> <email_address>")
    return

  group_id = args[0]
  hashtag = args[1]
  email_address = args[2]

  if not group_exists(group_id):
    await update.message.reply_text("Group ID not found in bot's group list.")
    return

  upsert_group_config(group_id, hashtag, email_address)
  await update.message.reply_text(f"Configuration set for group ID {group_id}.")

async def start_command(update: Update, context: CallbackContext):
  """Send instructions when the /start command is issued."""
  user_id = update.effective_user.id
  if user_id != ADMIN_USER_ID:
    return  # Only respond to the admin

  instructions = (
    "Welcome to the Telegram Bot!\n\n"
    "You can use the following commands:\n"
    "/list_groups - List all groups the bot is in.\n"
    "/set_config <group_id> <hashtag> <email_address> - Set the hashtag and email for a group.\n\n"
    "Example:\n"
    "/set_config -1001234567890 #alert example@example.com"
  )
  await update.message.reply_text(instructions)

async def on_startup(application: Application):
  """Function to run when the bot starts."""
  instructions = (
    "The bot has started and is ready to use!\n\n"
    "You can use the following commands:\n"
    "/list_groups - List all groups the bot is in.\n"
    "/set_config <group_id> <hashtag> <email_address> - Set the hashtag and email for a group.\n\n"
    "Example:\n"
    "/set_config -1001234567890 #alert example@example.com"
  )
  try:
    await application.bot.send_message(chat_id=ADMIN_USER_ID, text=instructions)
    print("Startup instructions sent to the admin.")
  except Exception as e:
    print(f"Failed to send startup message to admin: {e}")

def main():
  init_db()
  application = Application.builder().token(bot_token).post_init(on_startup).build()

  application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))
  application.add_handler(CommandHandler('list_groups', list_groups))
  application.add_handler(CommandHandler('set_config', set_config))
  application.add_handler(CommandHandler('start', start_command))
  # Add ChatMemberHandler to handle bot being added to or removed from groups
  application.add_handler(ChatMemberHandler(chat_member_handler, ChatMemberHandler.MY_CHAT_MEMBER))

  application.run_polling()

if __name__ == '__main__':
  main()
