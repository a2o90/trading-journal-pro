# Trading Journal Pro 📈

A comprehensive trading journal application built with Streamlit to track, analyze, and improve your trading performance.

## Features

### 📊 Core Functionality
- **Multi-Account Support** - Manage multiple trading accounts
- **Currency Selection** - Choose between $ and €
- **Trade Management** - Add, edit, and delete trades with detailed information
- **Persistent Storage** - All data saved locally in JSON files

### 📈 Analytics & Insights
- **Performance Metrics** - Win rate, expectancy, total profit, R-multiples
- **Equity Curve** - Visual representation of cumulative P&L over time
- **Calendar View** - Monthly calendar with daily P&L visualization
- **Per-Symbol Analysis** - Detailed breakdown by trading symbol/pair
- **Weekly Price Action Calendar** - Analyze weekly candlestick patterns and market sentiment per symbol

### 🧠 Psychology Tracking
- **Mental State Analysis** - Track mood, focus, stress, sleep quality
- **Trade Psychology** - Pre-trade confidence levels
- **Influence Tracking** - Record why you took each trade (FOMO, Analysis, etc.)
- **Correlation Analysis** - Discover how your mental state affects performance
- **Optimal Conditions** - Find your best trading setups with dates for review

### 📥 Export & Reporting
- **CSV Export** - Export trades with all data fields
- **Filtered Exports** - Export by setup, mood, or other criteria
- **Monthly Summaries** - Aggregate statistics by month
- **Dates for Best Trades** - Easily go back to your most successful days

### 📋 Trade Details Tracked
- Date, Symbol, Side (Long/Short)
- Entry/Exit Price, Quantity
- Duration (in minutes)
- Setup/Strategy, Trade Type
- Market Condition
- Mood, Focus, Stress, Sleep Quality, Confidence
- Influence/Reason for taking the trade
- Notes/Lessons learned
- Auto-calculated: PnL, R-multiple

## Installation

### Local Setup

1. Clone this repository
```bash
git clone <your-repo-url>
cd TradeJournal
```

2. Install dependencies
```bash
pip install -r requirements.txt
```

3. Run the app
```bash
streamlit run trading_journal.py
```

## Deployment

### Streamlit Community Cloud (Recommended - FREE)

1. Push your code to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Sign in with GitHub
4. Click "New app"
5. Select your repository and `trading_journal.py`
6. Click "Deploy"

### Other Options
- **Heroku** - [See Heroku deployment guide](https://devcenter.heroku.com/articles/python-gunicorn)
- **AWS EC2** - Deploy on your own server
- **Digital Ocean** - Use App Platform
- **Google Cloud Run** - Containerized deployment

## Data Privacy

⚠️ **Important**: Your trading data is stored in JSON files:
- `trades.json` - All your trades
- `accounts.json` - Your accounts
- `settings.json` - App settings

**For online deployment**, be aware:
- Data is stored on the server
- Consider using authentication
- For sensitive data, host on your own private server

## Usage Tips

1. **Set up accounts first** - Add your trading accounts in the sidebar
2. **Choose currency** - Select $ or € at the top of sidebar
3. **Track everything** - The more data you track, the better insights you get
4. **Review regularly** - Use the Psychology tab to find your optimal trading conditions
5. **Use dates** - Check the dates of your best trades and review what made them successful

## Technology Stack

- **Streamlit** - Web application framework
- **Pandas** - Data manipulation and analysis
- **Matplotlib** - Data visualization
- **Plotly** - Interactive charts and visualizations
- **yfinance** - Real-time financial data
- **Python 3.11+** - Programming language

## Contributing

Feel free to fork this project and customize it for your needs!

## License

MIT License - Feel free to use and modify

## Support

For issues or questions, please open an issue on GitHub.

---

**Happy Trading! 📈💰**

