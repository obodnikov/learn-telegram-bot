# Telegram Bot Commands Menu

## Overview

The Telegram Learning Bot now includes an interactive commands menu that appears in the Telegram app, similar to the BotFather's command menu. This makes it easy for users to discover and access all available bot commands.

## Implementation

The commands menu is automatically set up when the bot starts using the Telegram Bot API's `set_my_commands` method.

### Location

The implementation is in [src/bot.py](src/bot.py):
- `_set_bot_commands()` method (lines 123-138)
- Called during bot startup in the `start()` method (line 134)

### Available Commands

The following commands are registered in the menu:

| Command | Description |
|---------|-------------|
| `/start` | Initialize bot and register |
| `/help` | Show all commands |
| `/topics` | View available learning topics |
| `/stats` | Show your learning statistics |
| `/cancel` | Cancel current quiz session |

## How It Works

1. **Automatic Setup**: When the bot starts, it calls `_set_bot_commands()` which registers all commands with Telegram
2. **User Experience**: Users can access the menu by tapping the menu button (☰) next to the message input in Telegram
3. **Command Descriptions**: Each command has a helpful description that appears in the menu
4. **Persistent**: The menu persists across bot restarts and is available to all users

## User Interface

The commands menu appears in Telegram clients as:
- A menu button icon next to the message input field
- Tapping the button shows a list of all commands with their descriptions
- Users can tap a command to quickly insert it into the message field

## Code Example

```python
async def _set_bot_commands(self) -> None:
    """Set bot commands menu for Telegram."""
    commands = [
        BotCommand(command="start", description="Initialize bot and register"),
        BotCommand(command="help", description="Show all commands"),
        BotCommand(command="topics", description="View available learning topics"),
        BotCommand(command="stats", description="Show your learning statistics"),
        BotCommand(command="cancel", description="Cancel current quiz session"),
    ]

    try:
        await self.application.bot.set_my_commands(commands)
        logger.info("Bot commands menu set successfully")
    except Exception as e:
        logger.error(f"Failed to set bot commands: {e}")
```

## Benefits

1. **Discoverability**: Users can easily find all available commands without reading documentation
2. **Convenience**: Quick access to frequently used commands
3. **Professional**: Provides a polished user experience similar to popular bots
4. **Self-documenting**: Command descriptions explain what each command does

## Testing

To verify the commands menu is working:

1. Start the bot:
   ```bash
   python main.py
   ```

2. Check the logs for:
   ```
   Bot commands menu set successfully
   ```

3. Open your bot in Telegram and look for the menu button (☰) next to the message input
4. Tap the menu button to see all available commands with descriptions

## Troubleshooting

**Menu not appearing:**
- Ensure the bot has started successfully
- Check logs for "Bot commands menu set successfully"
- Try refreshing your Telegram client
- The menu only appears in chats with the bot

**Commands not updating:**
- Restart the bot to re-register commands
- Commands are cached by Telegram, changes may take a few minutes to propagate

## Future Enhancements

Possible improvements for the commands menu:

- **Localized Commands**: Support multiple languages for command descriptions
- **Scope-based Commands**: Different command sets for admins vs regular users
- **Dynamic Commands**: Add/remove commands based on user permissions or bot state
