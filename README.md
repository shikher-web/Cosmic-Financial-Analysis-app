# 🌌 Cosmic Financial Analyzer

Advanced Financial Modeling & Analysis Software for Indian Markets

## 🚀 Features

### 📊 Data Fetching & Market Handling
- Historical financial data for customizable year ranges (default: last 5 fiscal years)
- Real-time data in INR from multiple sources
- Integrated APIs: Yahoo Finance, NSE/BSE, Screener.in, Moneycontrol, NewsAPI

### 📈 Equity Share Market Analysis
- **Fundamental Analysis**: Financial ratios, statement analysis, forecasting, intrinsic valuation
- **Technical Analysis**: Interactive charts with RSI, MACD, moving averages, Bollinger Bands
- **Valuation Models**: DCF, DDM, Relative Valuation with side-by-side comparison
- **Peer Comparison**: Industry benchmarking and comparative analysis

### 💹 Derivatives, Forex & Crypto Analysis
- **Options Trading**: NSE option chains, Greeks calculation, OI analysis, recommendations
- **Forex Markets**: Currency pair analysis, correlation analytics, technical indicators
- **Cryptocurrency**: Real-time price, volume, market cap, volatility analysis

### 📰 Live Global News Feed
- Financial and economic news from reliable sources
- Categorized news: Financial Markets, Cryptocurrency, Forex

### 📄 Report Generation
- Comprehensive PDF reports with executive summaries
- Excel exports with multiple sheets
- CSV data exports
- Multiple report templates

## 🎨 Cosmic UI Theme
- Space-themed neon aesthetics with dark backgrounds
- Animated cosmic particle effects
- Responsive design for all devices

## 🛠️ Installation & Setup

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Setup Steps

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd cosmic-financial-analyzer
   ```

2. **Create virtual environment**
   ```bash
   python -m venv cosmic_env
   cosmic_env\Scripts\activate  # Windows
   # source cosmic_env/bin/activate  # macOS/Linux
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure API keys**
   - Copy `.env` file and add your API keys
   - For NewsAPI: Get key from https://newsapi.org
   - For Alpha Vantage: Get key from https://www.alphavantage.co

5. **Run the application**
   ```bash
   streamlit run main.py
   ```

6. **Access the app**
   - Open http://localhost:8501 in your browser

## 📋 Requirements

- pandas
- yfinance
- numpy
- matplotlib
- prophet
- streamlit
- requests
- plotly
- reportlab
- scipy
- openpyxl

## 🚀 Deployment

### Streamlit Cloud Deployment

1. **Push to GitHub**
   ```bash
   git add .
   git commit -m "Initial commit"
   git push origin main
   ```

2. **Deploy on Streamlit Cloud**
   - Go to [share.streamlit.io](https://share.streamlit.io)
   - Connect your GitHub repository
   - Set main file path to `main.py`
   - Add environment variables in Streamlit Cloud settings

3. **Environment Variables**
   - `ALPHA_VANTAGE_API_KEY`
   - `NEWS_API_KEY`
   - `IEX_CLOUD_API_KEY`

## 📊 Usage Guide

### Equity Analysis
1. Navigate to "Equity Analysis" section
2. Enter company symbol (e.g., RELIANCE.NS)
3. View fundamental metrics, technical charts, and valuations
4. Generate comprehensive reports

### Derivatives Analysis
1. Go to "Derivatives/Forex/Crypto" section
2. Select market type (Options, Forex, Crypto)
3. Enter symbol and analyze data
4. View Greeks, recommendations, and technical analysis

### Report Generation
1. Access "Reports" section
2. Choose report type (PDF, Excel, CSV)
3. Select data and download

## 🔧 API Integrations

- **Yahoo Finance**: Primary data source for Indian stocks
- **NSE/BSE**: Indian market data and option chains
- **NewsAPI**: Financial news feed
- **Alpha Vantage**: Additional market data
- **IEX Cloud**: Real-time market data

## 📈 Supported Markets

- **Indian Equity**: NSE/BSE listed companies
- **Derivatives**: NSE option chains
- **Forex**: Major currency pairs
- **Crypto**: Popular cryptocurrencies

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## ⚠️ Disclaimer

This software is for educational and informational purposes only. Not intended as financial advice. Always consult with qualified financial advisors before making investment decisions.

## 📞 Support

For issues and questions:
- Create an issue on GitHub
- Check the documentation
- Review the troubleshooting guide

---

**Built with ❤️ for Indian Markets**
