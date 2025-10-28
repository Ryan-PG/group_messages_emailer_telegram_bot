# Telegram Group Message Emailer Bot

This project is a Telegram bot that listens to messages in groups and sends messages containing specific hashtags to designated email addresses. The bot allows an admin to manage multiple groups, assign hashtags and email addresses to each group, and provides commands to list and configure groups.

## Features

- **Monitor Multiple Groups**: The bot automatically detects when it's added to or removed from groups.
- **Hashtag-Based Email Alerts**: Sends an email when a message containing a specified hashtag is sent in a group.
- **Per-Group Configuration**: Assign different hashtags and email addresses to different groups.
- **Admin Commands**: Only the designated admin can list groups and configure hashtags and email addresses.
- **Startup Instructions**: The bot sends instructions to the admin when it starts.
- **SQLite-Backed Persistence**: Group membership and configuration data are stored in a local SQLite database instead of JSON files.

## Prerequisites

- **Python 3.7 or higher** installed on your system.
- A **Telegram bot token** created via [BotFather](https://t.me/BotFather).
- An **email account with SMTP server details** (e.g., Gmail).
- Required Python libraries: `python-telegram-bot` and `python-dotenv`.

## Setup Instructions

### 1. Clone or Download the Repository

Clone this repository or download it to your local machine:

```bash
git clone https://github.com/RyanAtNeco/group_messages_emailer_telegram_bot
cd telegram-group-message-emailer-bot
```

### 2. Install Required Python Packages

Create a virtual environment (recommended):

```bash
python3 -m venv venv
source venv/bin/activate  # For Linux/macOS
venv\Scripts\activate     # For Windows
```

Install the required packages:

```bash
pip install -r requirements.txt
```

Ensure your `requirements.txt` includes:

```
python-telegram-bot>=20.0
python-dotenv
```

### 3. Create a `.env` File

Create a `.env` file in the root directory of your project with the following contents:

```env
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
SMTP_SERVER=smtp.example.com
SMTP_PORT=587
EMAIL_ADDRESS=your_email@example.com
EMAIL_PASSWORD=your_email_password
ADMIN_USER_ID=your_telegram_user_id
```

Replace the placeholder values with your actual credentials:

- **TELEGRAM_BOT_TOKEN**: Your Telegram bot token from BotFather.
- **SMTP_SERVER**: Your email provider's SMTP server (e.g., `smtp.gmail.com` for Gmail).
- **SMTP_PORT**: The SMTP port (usually `587` for TLS).
- **EMAIL_ADDRESS**: Your email address from which the messages will be sent.
- **EMAIL_PASSWORD**: The password for your email account (or app-specific password if 2FA is enabled).
- **ADMIN_USER_ID**: Your Telegram user ID (the bot admin).

**Note**: To find your Telegram user ID, you can use a bot like [@userinfobot](https://t.me/useridbot). Start a chat with the bot, and it will tell you your user ID.

### 4. Run the Bot

Run the Python script:

```bash
python main.py
```

Upon starting, the bot will send you (the admin) a message with instructions on how to use it.

The bot automatically creates and maintains a `bot.db` SQLite database file in the project root to persist group details and configuration settings between restarts.

### 5. Add the Bot to Groups

- **Add the Bot to Groups**: Add the bot to any Telegram group where you want it to monitor messages.
- **No Need to Disable Privacy Mode**: The bot automatically detects when it's added to or removed from groups. Privacy mode can remain enabled.

### 6. Configure Groups

In a private chat with the bot, use the following commands:

#### List Groups

To list all groups the bot is in:

```
/list_groups
```

The bot will respond with a list of group IDs and titles.

#### Set Configuration for a Group

To assign a hashtag and email address to a group:

```
/set_config <group_id> <hashtag> <email_address>
```

Replace:

- `<group_id>`: The ID of the group (from the `/list_groups` command).
- `<hashtag>`: The hashtag to monitor (e.g., `#alert`).
- `<email_address>`: The email address to send alerts to.

**Example**:

```
/set_config -1001234567890 #alert alerts@example.com
```

### 7. Test the Bot

- **Send Messages in the Group**: In the group, send a message containing the configured hashtag.
- **Check Your Email**: An email should be sent to the specified email address containing the message.

## Deployment

Below are instructions to deploy the bot on Linux and Windows servers to ensure it runs continuously in the background.

### Deployment on Linux Server

#### 1. Install Required Packages

Ensure that Python 3.7 or higher is installed on your server.

```bash
python3 --version
```

If not installed, install Python 3:

```bash
sudo apt-get update
sudo apt-get install python3 python3-venv python3-pip
```

#### 2. Set Up the Bot

Navigate to your home directory or desired installation directory:

```bash
cd /home/yourusername
```

Clone your repository:

```bash
git clone https://github.com/RyanAtNeco/group_messages_emailer_telegram_bot
cd telegram-group-message-emailer-bot
```

Create a virtual environment and activate it:

```bash
python3 -m venv venv
source venv/bin/activate
```

Install the required packages:

```bash
pip install -r requirements.txt
```

#### 3. Configure Environment Variables

Create the `.env` file with your credentials in the project root directory.

```bash
nano .env
```

Paste your environment variables and save the file.

#### 4. Create a Systemd Service

Create a service file for the bot:

```bash
sudo nano /etc/systemd/system/telegram-bot.service
```

Add the following content:

```ini
[Unit]
Description=Telegram Group Message Emailer Bot
After=network.target

[Service]
User=yourusername
WorkingDirectory=/home/yourusername/telegram-group-message-emailer-bot
ExecStart=/home/yourusername/telegram-group-message-emailer-bot/venv/bin/python main.py
Restart=always

[Install]
WantedBy=multi-user.target
```

Replace `yourusername` with your actual username.

#### 5. Start and Enable the Service

Reload the systemd daemon:

```bash
sudo systemctl daemon-reload
```

Start the bot service:

```bash
sudo systemctl start telegram-bot.service
```

Enable the service to start on boot:

```bash
sudo systemctl enable telegram-bot.service
```

#### 6. Check the Service Status

Verify that the bot is running:

```bash
sudo systemctl status telegram-bot.service
```

You should see that the service is active (running).

#### 7. View Logs

To check the bot's logs:

```bash
journalctl -u telegram-bot.service -f
```

### Deployment on Windows Server

#### 1. Install Python

Download and install Python 3.7 or higher from the [official website](https://www.python.org/downloads/windows/). During installation, make sure to check the option **"Add Python to PATH"**.

#### 2. Set Up the Bot

Open Command Prompt (CMD) or PowerShell and navigate to your desired installation directory:

```cmd
cd C:\Users\YourUsername
```

Clone your repository:

```cmd
git clone https://github.com/RyanAtNeco/group_messages_emailer_telegram_bot
cd telegram-group-message-emailer-bot
```

Create a virtual environment and activate it:

```cmd
python -m venv venv
venv\Scripts\activate
```

Install the required packages:

```cmd
pip install -r requirements.txt
```

#### 3. Configure Environment Variables

Create the `.env` file with your credentials in the project root directory.

```cmd
notepad .env
```

Paste your environment variables and save the file.

#### 4. Install NSSM (Non-Sucking Service Manager)

[NSSM](https://nssm.cc/) is a tool that allows you to run any script or program as a Windows service.

- Download NSSM from [https://nssm.cc/download](https://nssm.cc/download).
- Extract the zip file.
- Copy `nssm.exe` to `C:\Windows\System32` for easy access.

#### 5. Create a Windows Service

Open an elevated Command Prompt (run as Administrator) and run:

```cmd
nssm install TelegramBot
```

An NSSM service installer window will appear.

- **Application Path**: Browse to your Python executable in the virtual environment, e.g.,
  ```
  C:\Users\YourUsername\telegram-group-message-emailer-bot\venv\Scripts\python.exe
  ```
- **Startup Directory**: Set to the bot's directory:
  ```
  C:\Users\YourUsername\telegram-group-message-emailer-bot
  ```
- **Arguments**: Specify the script to run:
  ```
  main.py
  ```

Click on the **Install service** button.

#### 6. Start the Service

Start the service via Command Prompt:

```cmd
nssm start TelegramBot
```

Or start it from the Services management console:

- Press `Win + R`, type `services.msc`, and press Enter.
- Find **TelegramBot** in the list.
- Right-click and select **Start**.

#### 7. Verify the Service

Check that the service is running in the Services management console.

#### 8. View Logs

Since Windows services don't have an interactive console, you can redirect the bot's output to a log file.

- Edit the service configuration:

  ```cmd
  nssm edit TelegramBot
  ```

- Go to the **I/O** tab.
- Set **Output (stdout)** and **Error (stderr)** to log files, e.g.:

  ```
  C:\Users\YourUsername\telegram-bot-output.log
  ```

- Save changes and restart the service:

  ```cmd
  nssm restart TelegramBot
  ```

- Check the log files for output and errors.

## Bot Commands

### In Private Chat with the Bot (Admin Only)

- **/start**: Receive the instruction message.
- **/list_groups**: Lists all groups the bot is in.
- **/set_config \<group_id> \<hashtag> \<email_address>**: Sets the hashtag and email for a group.

### In Groups

- The bot listens for messages containing the configured hashtag and sends an email when detected.

## Additional Notes

- **Admin User**: Only the user with the `ADMIN_USER_ID` can use the `/list_groups` and `/set_config` commands.
- **Persistent Storage**: The bot stores group and configuration data in `groups.json` and `group_configs.json`.
- **Security**:
  - **Do Not Share Your `.env` File**: Ensure that the `.env` file is listed in `.gitignore` to prevent it from being pushed to any public repositories.
  - **Email Security**: Use app-specific passwords if your email provider supports two-factor authentication.
- **Bot Permissions**: The bot does not require admin permissions in groups but needs to be able to read messages to detect hashtags.
- **Firewall Settings**:
  - Ensure that your server allows outbound connections on the SMTP port (`587`) to send emails.
  - Allow the bot to connect to Telegram servers (usually not an issue).

## Troubleshooting

- **Bot Not Detecting Groups**: Ensure the bot is added to the groups you want to monitor.
- **Commands Not Working**:
  - Make sure you're sending commands in a private chat with the bot.
  - Verify that you're the admin user specified by `ADMIN_USER_ID`.
- **No Emails Being Sent**:
  - Check that the hashtag is correctly configured.
  - Ensure that the messages in the group contain the exact hashtag.
  - Verify your email credentials in the `.env` file.
- **Environment Variables Not Loaded**: Ensure that the `.env` file is correctly formatted and located in the project's root directory.
- **Service Not Starting**:
  - Check the service logs for errors.
  - Ensure all paths in the service configuration are correct.
  - Verify that the virtual environment is activated correctly in the service.

## Example Usage

1. **Start the Bot**:

   ```bash
   python main.py
   ```

2. **Receive Instructions**:

   - The bot will send you a message with usage instructions.

3. **Add the Bot to a Group**:

   - Add the bot to your group.

4. **List Groups**:

   - In a private chat with the bot, send:

     ```
     /list_groups
     ```

   - The bot will list all groups it's in.

5. **Configure a Group**:

   - Set the hashtag and email for the group:

     ```
     /set_config <group_id> #yourhashtag your-email@example.com
     ```

6. **Test the Configuration**:

   - In the group, send a message containing the hashtag:

     ```
     This is a test message with #yourhashtag.
     ```

   - Check your email for the notification.

## License

This project is licensed under the MIT License.

---

### Final Optional Remarks

- **Security Considerations**:

  - Keep your server updated with the latest security patches.
  - Secure your email credentials; consider using environment variables or secret management tools.

- **Monitoring and Maintenance**:
  - Regularly check the bot's logs to ensure it's functioning correctly.
  - Restart the service if necessary after updates or changes.
