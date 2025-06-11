# Telegram Gifts Buyer

<img src="https://github.com/user-attachments/assets/a8d750d3-500c-4372-9733-3bbd509643e8" alt="Program Preview" width="100%" />

Advanced Telegram userbot for automated gift purchasing with intelligent prioritization, multiple recipients support,
and comprehensive balance management.

> 🌐 [Русская версия документации](README-RU.md)

## ✨ Key Features

- **🤖 Smart Automation**: Continuous monitoring with intelligent gift detection
- **🎯 Advanced Prioritization**: Automatically prioritizes low-supply gifts matching your ranges
- **👥 Multi-Recipient Support**: Send different quantities to multiple users/channels per range
- **💰 Smart Balance Management**: Partial purchases when balance insufficient, prevents failed transactions
- **📊 Comprehensive Notifications**: Detailed purchase reports, balance alerts, and processing summaries
- **🔧 Flexible Configuration**: Unified range format with price, supply, quantity, and recipient controls
- **🌍 Multi-Language**: Full English and Russian support
- **📝 Session Management**: Continue from last session or start fresh

## 🚀 Quick Start

1. **Clone & Install**:
   ```bash
   git clone https://github.com/bohd4nx/Gifts-Buyer.git
   cd Gifts-Buyer
   pip install -r requirements.txt
   ```

2. **Configure**: Edit `config.ini` with your credentials and preferences

3. **Run**: `python main.py`

## ⚙️ Configuration

### Essential Settings

```ini
[Telegram]
API_ID = your_api_id                    # From https://my.telegram.org/apps
API_HASH = your_api_hash               # From https://my.telegram.org/apps
PHONE_NUMBER = +1234567890             # International format
CHANNEL_ID = @notifications            # Channel for updates (-100 to disable)

[Bot]
INTERVAL = 10                          # Check frequency (seconds)
LANGUAGE = EN                          # Interface language (EN/RU)

[Gifts]
# Unified format: price_range: supply_limit x quantity: recipients
GIFT_RANGES = 1-1000: 500000 x 1: @user1, 123456, 1001-5000: 100000 x 2: @channel

PURCHASE_NON_LIMITED_GIFTS = False     # Buy unlimited gifts
PURCHASE_ONLY_UPGRADABLE_GIFTS = False # Only upgradable gifts
PRIORITIZE_LOW_SUPPLY = True           # Smart supply-based prioritization
```

### Advanced Range Configuration

**Unified Format**: `min_price-max_price: supply_limit x quantity: recipients`

**Real Examples**:

- `1-1000: 500000 x 1: @johndoe, 123456789` - Cheap gifts, 1 copy each
- `1001-5000: 100000 x 2: @premium_channel, @vip_user` - Mid-range, 2 copies each
- `5001-50000: 50000 x 5: 987654321` - Expensive gifts, 5 copies to specific user

**Smart Features**:

- **Channel Support**: Gift directly to channels using `@channelname`
- **Mixed Recipients**: Combine usernames, IDs, and channels freely
- **Per-Range Logic**: Different strategies for different price tiers
- **Quantity Control**: Specify exact amounts per range

### Intelligent Prioritization

With `PRIORITIZE_LOW_SUPPLY = True`:

1. **Priority Queue**: Gifts matching ranges, sorted by supply (lowest first)
2. **Smart Timing**: Processes rarest gifts immediately
3. **Range Optimization**: Focuses on your configured targets

**Example Scenario**:

```
Gift A: 2500⭐, 25K supply, quantity=3  ← Processed first (lowest supply)
Gift B: 1800⭐, 150K supply, quantity=1 ← Processed second  
Gift C: 15000⭐, 5K supply             ← Skipped (outside ranges)
```

## 🧠 Smart Balance Management

**Intelligent Purchase Logic**:

- **Pre-Check**: Calculates maximum affordable quantity before purchase
- **Partial Buying**: Buys what's possible, reports shortfall
- **No Failed Attempts**: Prevents unnecessary API calls and errors
- **Detailed Reporting**: Shows purchased vs requested quantities

**Example**:

```
Config: Buy 4 copies of 1500⭐ gift
Balance: 4500⭐ 
Result: Buys 3 copies, reports "Missing 1500⭐ for remaining 1 gift"
```

## 📊 Advanced Monitoring

**Notification Types**:

- ✅ **Success**: Purchase confirmations with recipient details
- 💰 **Balance**: Insufficient funds alerts with exact requirements
- 📈 **Partial**: Partial purchase reports with missing amounts
- 📊 **Summary**: Batch processing statistics
- ⚠️ **Errors**: Detailed error explanations and solutions

**Processing Intelligence**:

- Real-time balance tracking
- Supply-based prioritization
- Automatic range matching
- Recipient validation

## 🎯 Use Cases

**Conservative Strategy**:

```ini
GIFT_RANGES = 1-500: 1000000 x 1: @myself
PRIORITIZE_LOW_SUPPLY = False
```

**Aggressive Collector**:

```ini  
GIFT_RANGES = 1-2000: 200000 x 3: @main, @backup, 1001-10000: 50000 x 5: @premium
PRIORITIZE_LOW_SUPPLY = True
```

**Channel Distribution**:

```ini
GIFT_RANGES = 1-1000: 500000 x 2: @public_channel, @private_channel, @archive_channel
```

## 🔧 Advanced Features

- **Session Persistence**: Seamless restart capability
- **Error Recovery**: Automatic retry logic for network issues
- **Rate Limiting**: Built-in API respect mechanisms
- **Batch Processing**: Efficient multi-gift handling
- **Channel Gifting**: Direct channel distribution support
- **Localization**: Native language support

## 📝 Best Practices

- **Balance**: Maintain 2-3x your highest range for safety
- **Ranges**: Use multiple tiers for different strategies
- **Monitoring**: Enable notifications for real-time updates
- **Testing**: Start with small ranges to validate configuration
- **VPS**: Run continuously for competitive advantage

## 🆕 Version 2025.7.1 Features

- ✨ **Smart Balance Management**: Partial purchases, no failed transactions
- 🎯 **Advanced Prioritization**: Supply-based intelligent ordering
- 👥 **Enhanced Multi-Recipient**: Channel support, flexible formats
- 📊 **Comprehensive Reporting**: Detailed notifications and summaries
- 🔧 **Improved Configuration**: Cleaner, more intuitive setup
- 🌍 **Better Localization**: Full multi-language support

---

<div align="center">
    <h4>🚀 Built with ❤️ by <a href="https://t.me/bohd4nx">@bohd4nx</a> • ⭐ Star on <a href="https://github.com/bohd4nx/Gifts-Buyer">GitHub</a></h4>
</div>
