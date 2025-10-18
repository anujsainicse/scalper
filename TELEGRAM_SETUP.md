# Telegram Bot Setup Guide

This guide will help you create and configure a Telegram bot for the Scalper Bot notifications.

## Step 1: Create a Telegram Bot

1. **Open Telegram** and search for `@BotFather`
2. **Start a conversation** with BotFather by clicking "Start" or sending `/start`
3. **Create a new bot** by sending the command:
   ```
   /newbot
   ```

4. **Choose a name** for your bot (e.g., "Scalper Bot Notifier")
   - This is the display name users will see

5. **Choose a username** for your bot (must end in `bot`)
   - Example: `scalper_notifier_bot` or `my_scalper_bot`
   - Must be unique across all Telegram

6. **Save your bot token** - BotFather will send you a message like:
   ```
   Done! Congratulations on your new bot. You will find it at t.me/your_bot_username
   Here is your token: 1234567890:ABCdefGHIjklMNOpqrsTUVwxyz

   Keep your token secure and store it safely, it can be used by anyone to control your bot.
   ```

## Step 2: Configure Bot Settings (Optional but Recommended)

1. **Set bot description** (shown when users first interact):
   ```
   /setdescription
   ```
   Then select your bot and enter:
   ```
   Receive real-time notifications for your cryptocurrency scalping bot activities.
   ```

2. **Set about text** (shown in bot profile):
   ```
   /setabouttext
   ```
   Then select your bot and enter:
   ```
   Official notification bot for Scalper Bot Dashboard
   ```

3. **Set bot photo** (optional):
   ```
   /setuserpic
   ```
   Then upload an image for your bot avatar

4. **Set commands** (helps users see available commands):
   ```
   /setcommands
   ```
   Then select your bot and enter:
   ```
   start - Start the bot and get connection code
   connect - Get connection code for dashboard
   disconnect - Disconnect from dashboard
   status - Check connection status
   help - Show help message
   ```

## Step 3: Add Token to Environment Variables

1. **Copy your bot token** from the BotFather message

2. **Update backend/.env file**:
   ```bash
   cd backend
   nano .env
   ```

3. **Replace the placeholder** with your actual token:
   ```env
   TELEGRAM_BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
   ```
   Replace `1234567890:ABCdefGHIjklMNOpqrsTUVwxyz` with your actual token

4. **Save the file** (Ctrl+O, Enter, Ctrl+X in nano)

## Step 4: Install Python Dependencies

```bash
cd backend
source venv/bin/activate
pip install -r requirements.txt
```

This will install `python-telegram-bot==20.7` which is required for Telegram integration.

## Step 5: Start Your Bot

Once you've completed the setup:

1. **Start the backend server**:
   ```bash
   cd backend
   source venv/bin/activate
   uvicorn app.main:app --reload
   ```

2. **The Telegram bot will automatically start** and be ready to accept connections

## Step 6: Connect from Dashboard

1. **Open the Scalper Bot Dashboard** at http://localhost:3000

2. **Click the "Connect Telegram" button** in the Activity Log panel

3. **Follow the connection flow**:
   - A connection code will be generated
   - Open your Telegram bot (click the provided link or search for your bot)
   - Send `/start` to your bot
   - Send the connection code to your bot
   - Your Telegram will be connected!

4. **Start receiving notifications** for:
   - Bot created
   - Bot started/stopped
   - Dip detected (when implemented)
   - Order executed (when implemented)
   - Errors and warnings

## Bot Commands

Users can interact with your bot using these commands:

### `/start`
Start the bot and receive a welcome message with connection instructions.

Example:
```
User: /start
Bot: Welcome to Scalper Bot Notifier! 🤖

To connect your Telegram to the Scalper Bot Dashboard:
1. Click "Connect Telegram" in the dashboard
2. Send me the 6-digit connection code
3. Start receiving real-time notifications!

Type /help for more commands.
```

### `/connect`
Get a connection code to link your Telegram to the dashboard.

Example:
```
User: /connect
Bot: To connect your Telegram account:
1. Go to the Scalper Bot Dashboard
2. Click "Connect Telegram" button
3. Copy the 6-digit code shown
4. Send it to me here

Waiting for your connection code... ⏳
```

### `/disconnect`
Disconnect your Telegram from the dashboard.

Example:
```
User: /disconnect
Bot: Are you sure you want to disconnect? You will stop receiving notifications.

Send /confirm_disconnect to confirm, or /cancel to keep your connection.
```

### `/status`
Check your current connection status.

Example:
```
User: /status
Bot: ✅ Connected to Scalper Bot Dashboard
📱 Chat ID: 123456789
🕐 Connected: 2 hours ago

You are receiving notifications for:
• Bot events
• Trading activity
• System alerts
```

### `/help`
Show help message with all available commands.

Example:
```
User: /help
Bot: 📖 Scalper Bot Commands:

/start - Start the bot
/connect - Connect to dashboard
/disconnect - Disconnect from dashboard
/status - Check connection status
/help - Show this message

Need help? Visit: https://your-docs-url.com
```

## Notification Examples

Once connected, you'll receive notifications like:

### Bot Created
```
✅ Bot Created

Ticker: BTC/USDT
Exchange: Binance
Buy Price: $45,000.00
Sell Price: $46,000.00
Quantity: 0.01

Status: ACTIVE 🟢
```

### Bot Started
```
▶️ Bot Started

BTC/USDT bot is now active and monitoring for dips.

Buy: $45,000.00
Sell: $46,000.00
```

### Bot Stopped
```
⏸️ Bot Stopped

BTC/USDT bot has been stopped.

Total Trades: 5
PnL: +$250.50 📈
```

### Order Executed
```
💰 Order Executed

Symbol: BTC/USDT
Side: BUY
Quantity: 0.01
Price: $45,000.00

Total Cost: $450.00
```

### Error Alert
```
❌ Error Alert

Bot: BTC/USDT
Error: Insufficient balance

Action Required: Check your exchange balance.
```

## Security Best Practices

1. **Never share your bot token** - Anyone with the token can control your bot
2. **Don't commit .env file** - The .env file is already in .gitignore
3. **Regenerate token if exposed**:
   - Go to @BotFather
   - Send `/revoke`
   - Select your bot
   - Get new token
   - Update .env file

4. **Verify bot ownership**:
   - Only the bot creator (you) can access the bot API
   - Users can only send messages to the bot
   - Connection codes expire after 10 minutes

## Troubleshooting

### Bot doesn't respond
1. Check if backend server is running
2. Verify TELEGRAM_BOT_TOKEN in .env is correct
3. Make sure python-telegram-bot is installed
4. Check backend logs for errors

### Can't connect from dashboard
1. Make sure backend is running
2. Check browser console for errors
3. Verify API endpoint is accessible (http://localhost:8000/docs)
4. Try generating a new connection code

### Not receiving notifications
1. Check Telegram connection status in dashboard
2. Verify bot is not blocked in Telegram
3. Check if notifications are muted in Telegram
4. Look for errors in backend logs

### Connection code expired
- Connection codes expire after 10 minutes
- Click "Connect Telegram" again to generate a new code
- Send the new code to your bot

## Advanced Configuration

### Custom Welcome Message
Edit `backend/app/services/telegram.py` and modify the welcome message in the `/start` command handler.

### Custom Notification Templates
Edit notification templates in `backend/app/services/telegram.py` to customize message format, emojis, and styling.

### Webhook vs Polling
- Default: Polling (bot checks for messages every few seconds)
- Production: Webhook (Telegram sends messages to your server)
- To enable webhook, set TELEGRAM_WEBHOOK_URL in .env to your public HTTPS URL

### Bot Analytics
Access @BotFather stats:
```
/mybots
[Select your bot]
/stats
```

This shows:
- Total users
- Messages sent/received
- User retention

## Resources

- [BotFather Documentation](https://core.telegram.org/bots#6-botfather)
- [Telegram Bot API](https://core.telegram.org/bots/api)
- [python-telegram-bot Docs](https://docs.python-telegram-bot.org/)
- [Scalper Bot Documentation](./DOCS.md)

## Support

If you encounter issues:
1. Check this guide
2. Review backend logs
3. Check [Troubleshooting section](./DOCS.md#troubleshooting)
4. Open an issue on GitHub

---

**Happy Trading! 🚀**

Made with ❤️ by the Scalper Bot Team
