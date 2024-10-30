# DexScreener-Boosts-Telegram-Bot

DexScreener Boosts Bot is a Telegram bot that provides users with the latest and top boosted tokens on DexScreener. With this bot, users can quickly access updated token information, including market cap, liquidity, price, and social links, by using commands. For automated notifications, users can subscribe to the provided public Telegram channel. The public Telegram channel managed by a second bot, which you can find here: https://github.com/adonisneon/DexScreener-Boost-Monitor-Telegram-Bot. Both bots are needed for everything to work smoothly.

## Features

- **Latest Boosted Tokens**: Retrieves the latest tokens with boost activity on DexScreener.
- **Top Boosted Tokens**: Fetches tokens with the highest boost activity.
- **Detailed Token Information**: Provides comprehensive details for each token, including market cap, price, liquidity, and social links.
- **Subscription Option**: Users can subscribe to the bot’s Telegram channel for automatic updates.

## Commands

- `/start` - Displays the welcome message with available commands.
- `/help` - Shows detailed help information.
- `/latest_boosts` - Fetches the latest boosted tokens from DexScreener.
- `/top_boosts` - Retrieves top boosted tokens with high activity.

## Setup and Installation

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/adonisneon/DexScreener-Boosts-Telegram-Bot
   ```
2. **Install Dependencies: Install all required packages by running**:
    ```bash
    pip install -r requirements.txt
    ```
3. **Environment Configuration**:
   Set your bot token in the code:
   ```bash
   TOKEN = "your-telegram-bot-token"
   ```
   Replace CHANNEL_LINK with your public channel link for automatic updates:
   ```bash
   CHANNEL_LINK = "https://t.me/your-channel-link"
   ```
4. **Run the Bot**: Start the bot by executing:
   ```bash
   python bot.py
   ```
**Contributing**
Pull requests are welcome. For major changes, please open an issue first to discuss your proposed changes.

**License**
This project is licensed under the MIT License.
