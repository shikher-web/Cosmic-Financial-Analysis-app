import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta

def fetch_historical_data(symbol, years=5):
    """Fetch historical data for given symbol and convert to INR"""
    end_date = datetime.now()
    start_date = end_date - timedelta(days=years*365)

    # Fetch data from Yahoo Finance
    data = yf.download(symbol, start=start_date, end=end_date, auto_adjust=False)

    # Flatten multi-index columns if present
    if isinstance(data.columns, pd.MultiIndex):
        data.columns = data.columns.droplevel(1)

    # Convert to INR (assuming USD base, use current USD-INR rate)
    usd_inr_rate = get_usd_inr_rate()
    data = data * usd_inr_rate

    return data

def get_usd_inr_rate():
    """Get current USD to INR exchange rate from Yahoo Finance"""
    try:
        # Use Yahoo Finance for USD-INR rate
        data = yf.download('USDINR=X', period='1d', auto_adjust=False)
        if not data.empty:
            rate = float(data['Close'].iloc[-1])
            return rate
    except:
        return 83.0  # fallback rate

def fetch_stock_data(symbol, period="1y", interval="1d"):
    """Fetch stock data from Yahoo Finance"""
    try:
        data = yf.download(symbol, period=period, interval=interval, auto_adjust=False)
        if isinstance(data.columns, pd.MultiIndex):
            data.columns = data.columns.droplevel(1)
        return data
    except Exception as e:
        st.error(f"Error fetching stock data: {e}")
        return None

def fetch_crypto_data(symbol, period="1y", interval="1d"):
    """Fetch cryptocurrency data from Yahoo Finance"""
    try:
        # Add -USD suffix if not present for crypto symbols
        if not symbol.endswith('-USD'):
            symbol = f"{symbol}-USD"

        data = yf.download(symbol, period=period, interval=interval, auto_adjust=False)
        if isinstance(data.columns, pd.MultiIndex):
            data.columns = data.columns.droplevel(1)
        return data
    except Exception as e:
        st.error(f"Error fetching crypto data: {e}")
        return None

def fetch_commodities_data(symbol, period="1y", interval="1d"):
    """Fetch commodities data from Yahoo Finance"""
    try:
        # Common commodity symbols: GC=F (Gold), SI=F (Silver), CL=F (Crude Oil), HG=F (Copper)
        commodity_symbols = {
            'GOLD': 'GC=F',
            'SILVER': 'SI=F',
            'OIL': 'CL=F',
            'COPPER': 'HG=F',
            'NATURAL_GAS': 'NG=F',
            'CORN': 'ZC=F',
            'SOYBEANS': 'ZS=F',
            'WHEAT': 'ZW=F'
        }

        # If symbol is a common name, convert to Yahoo symbol
        if symbol.upper() in commodity_symbols:
            symbol = f"{commodity_symbols[symbol.upper()]}"
        elif not symbol.endswith('=F'):  # Add futures suffix if not present
            symbol = f"{symbol}=F"

        data = yf.download(symbol, period=period, interval=interval, auto_adjust=False)
        if isinstance(data.columns, pd.MultiIndex):
            data.columns = data.columns.droplevel(1)
        return data
    except Exception as e:
        st.error(f"Error fetching commodities data: {e}")
        return None

def fetch_bonds_data(symbol, period="1y", interval="1d"):
    """Fetch bonds/treasury data from Yahoo Finance"""
    try:
        # Common bond symbols: ^TNX (10Y Treasury), ^IRX (13W Treasury), ^TYX (30Y Treasury)
        bond_symbols = {
            'US10Y': '^TNX',
            'US30Y': '^TYX',
            'US5Y': 'FV=F',
            'US2Y': 'TU=F',
            'US3M': '^IRX'
        }

        # If symbol is a common name, convert to Yahoo symbol
        if symbol.upper() in bond_symbols:
            symbol = bond_symbols[symbol.upper()]
        elif not symbol.startswith('^') and not symbol.endswith('=F'):
            # Assume it's a treasury symbol
            symbol = f"^{symbol}"

        data = yf.download(symbol, period=period, interval=interval, auto_adjust=False)
        if isinstance(data.columns, pd.MultiIndex):
            data.columns = data.columns.droplevel(1)
        return data
    except Exception as e:
        st.error(f"Error fetching bonds data: {e}")
        return None

def fetch_etf_data(symbol, period="1y", interval="1d"):
    """Fetch ETF data from Yahoo Finance"""
    try:
        # Common ETF symbols - just ensure they're treated as regular symbols
        data = yf.download(symbol, period=period, interval=interval, auto_adjust=False)
        if isinstance(data.columns, pd.MultiIndex):
            data.columns = data.columns.droplevel(1)
        return data
    except Exception as e:
        st.error(f"Error fetching ETF data: {e}")
        return None

def fetch_forex_data(symbol, period="1y", interval="1d"):
    """Fetch forex data from Yahoo Finance"""
    try:
        # Forex symbols typically end with =X
        if not symbol.endswith('=X'):
            symbol = f"{symbol}=X"

        data = yf.download(symbol, period=period, interval=interval, auto_adjust=False)
        if isinstance(data.columns, pd.MultiIndex):
            data.columns = data.columns.droplevel(1)
        return data
    except Exception as e:
        st.error(f"Error fetching forex data: {e}")
        return None

def detect_asset_class(symbol):
    """Detect asset class based on symbol pattern"""
    symbol = symbol.upper()

    # Crypto detection
    if any(crypto in symbol for crypto in ['BTC', 'ETH', 'BNB', 'ADA', 'SOL', 'DOT', 'DOGE', 'AVAX']):
        return 'Cryptocurrency'
    if symbol.endswith('-USD') or symbol in ['BTC-USD', 'ETH-USD', 'USDT-USD', 'BNB-USD']:
        return 'Cryptocurrency'

    # Forex detection
    if symbol.endswith('=X') or any(forex in symbol for forex in ['USD', 'EUR', 'GBP', 'JPY', 'INR']):
        return 'Forex'

    # Commodity detection
    commodity_indicators = ['=F', 'GC=F', 'SI=F', 'CL=F', 'HG=F', 'NG=F', 'ZC=F', 'ZS=F', 'ZW=F']
    if any(indicator in symbol for indicator in commodity_indicators):
        return 'Commodities'

    # Bond/Treasury detection
    bond_indicators = ['^TNX', '^TYX', '^IRX', 'FV=F', 'TU=F']
    if any(indicator in symbol for indicator in bond_indicators):
        return 'Bonds'

    # ETF detection (common ETF patterns)
    etf_indicators = ['SPY', 'QQQ', 'IWM', 'EFA', 'VWO', 'BND', 'AGG', 'VEA', 'VWO', 'VIG']
    if any(etf in symbol for etf in etf_indicators) or symbol.startswith('V') or len(symbol) <= 4:
        # This is a heuristic - many ETFs are short codes
        return 'ETF'

    # Default to Equity
    return 'Equity'

def fetch_asset_data(symbol, asset_class=None, period="1y", interval="1d"):
    """Unified function to fetch data based on asset class"""
    if asset_class is None:
        asset_class = detect_asset_class(symbol)

    if asset_class == 'Cryptocurrency':
        return fetch_crypto_data(symbol, period, interval)
    elif asset_class == 'Commodities':
        return fetch_commodities_data(symbol, period, interval)
    elif asset_class == 'Bonds':
        return fetch_bonds_data(symbol, period, interval)
    elif asset_class == 'ETF':
        return fetch_etf_data(symbol, period, interval)
    elif asset_class == 'Forex':
        return fetch_forex_data(symbol, period, interval)
    else:  # Default to stocks/equity
        return fetch_stock_data(symbol, period, interval)

def get_financial_years(years=5):
    """Generate list of financial years in FY format (April-March)"""
    current_year = datetime.now().year
    current_month = datetime.now().month

    # If current month is April or later, current FY is current year - next year
    # If before April, current FY is previous year - current year
    if current_month >= 4:
        current_fy_start = current_year
        current_fy_end = current_year + 1
    else:
        current_fy_start = current_year - 1
        current_fy_end = current_year

    fy_list = []
    for i in range(years):
        start_year = current_fy_start - i
        end_year = current_fy_end - i
        fy_list.append(f"FY {start_year}-{str(end_year)[-2:]}")

    return fy_list

def fetch_financial_statements(symbol):
    """Fetch financial statements using Yahoo Finance fundamentals"""
    try:
        # Use Yahoo Finance ticker object for fundamentals
        ticker = yf.Ticker(symbol)

        # Get financial data
        income_stmt = ticker.financials
        balance_sheet = ticker.balance_sheet
        cash_flow = ticker.cashflow

        financials = {
            'income_statement': {},
            'balance_sheet': {},
            'cash_flow': {}
        }

        fy_years = get_financial_years(5)

        # Process Income Statement
        if not income_stmt.empty:
            for i, fy in enumerate(fy_years[:len(income_stmt.columns)]):
                col = income_stmt.columns[i]
                financials['income_statement'][fy] = {
                    'Revenue': income_stmt.loc['Total Revenue', col] if 'Total Revenue' in income_stmt.index else 0,
                    'Operating Expenses': income_stmt.loc['Operating Expenses', col] if 'Operating Expenses' in income_stmt.index else 0,
                    'EBITDA': income_stmt.loc['EBITDA', col] if 'EBITDA' in income_stmt.index else 0,
                    'Net Profit': income_stmt.loc['Net Income', col] if 'Net Income' in income_stmt.index else 0
                }

        # Process Balance Sheet
        if not balance_sheet.empty:
            for i, fy in enumerate(fy_years[:len(balance_sheet.columns)]):
                col = balance_sheet.columns[i]
                financials['balance_sheet'][fy] = {
                    'Total Assets': balance_sheet.loc['Total Assets', col] if 'Total Assets' in balance_sheet.index else 0,
                    'Current Assets': balance_sheet.loc['Current Assets', col] if 'Current Assets' in balance_sheet.index else 0,
                    'Non-Current Assets': balance_sheet.loc['Total Non Current Assets', col] if 'Total Non Current Assets' in balance_sheet.index else 0,
                    'Total Liabilities': balance_sheet.loc['Total Liabilities Net Minority Interest', col] if 'Total Liabilities Net Minority Interest' in balance_sheet.index else 0,
                    'Current Liabilities': balance_sheet.loc['Current Liabilities', col] if 'Current Liabilities' in balance_sheet.index else 0,
                    'Equity': balance_sheet.loc['Total Equity Gross Minority Interest', col] if 'Total Equity Gross Minority Interest' in balance_sheet.index else 0
                }

        # Process Cash Flow
        if not cash_flow.empty:
            for i, fy in enumerate(fy_years[:len(cash_flow.columns)]):
                col = cash_flow.columns[i]
                financials['cash_flow'][fy] = {
                    'Operating Cash Flow': cash_flow.loc['Operating Cash Flow', col] if 'Operating Cash Flow' in cash_flow.index else 0,
                    'Investing Cash Flow': cash_flow.loc['Investing Cash Flow', col] if 'Investing Cash Flow' in cash_flow.index else 0,
                    'Financing Cash Flow': cash_flow.loc['Financing Cash Flow', col] if 'Financing Cash Flow' in cash_flow.index else 0,
                    'Net Cash Flow': cash_flow.loc['End Cash Position', col] if 'End Cash Position' in cash_flow.index else 0
                }

        return financials

    except Exception as e:
        st.error(f"Error fetching financial statements: {e}")
        return get_sample_financial_statements()

def get_sample_financial_statements():
    """Return sample financial statements for demonstration"""
    fy_years = get_financial_years(5)

    financials = {
        'income_statement': {},
        'balance_sheet': {},
        'cash_flow': {}
    }

    # Sample data for Reliance Industries (approximate values in crores)
    base_revenue = 900000  # 9 lakh crores
    base_profit = 78000    # 78k crores
    base_assets = 2100000  # 21 lakh crores
    base_equity = 950000   # 9.5 lakh crores

    for i, fy in enumerate(fy_years):
        growth_factor = 1 + (i * 0.08)  # 8% annual growth

        # Income Statement
        financials['income_statement'][fy] = {
            'Revenue': int(base_revenue * growth_factor),
            'Operating Expenses': int(base_revenue * growth_factor * 0.85),
            'EBITDA': int(base_revenue * growth_factor * 0.15),
            'Net Profit': int(base_profit * growth_factor)
        }

        # Balance Sheet
        financials['balance_sheet'][fy] = {
            'Total Assets': int(base_assets * growth_factor),
            'Current Assets': int(base_assets * growth_factor * 0.4),
            'Non-Current Assets': int(base_assets * growth_factor * 0.6),
            'Total Liabilities': int(base_assets * growth_factor * 0.55),
            'Current Liabilities': int(base_assets * growth_factor * 0.25),
            'Equity': int(base_equity * growth_factor)
        }

        # Cash Flow
        financials['cash_flow'][fy] = {
            'Operating Cash Flow': int(base_profit * growth_factor * 1.2),
            'Investing Cash Flow': int(base_profit * growth_factor * -0.8),
            'Financing Cash Flow': int(base_profit * growth_factor * -0.3),
            'Net Cash Flow': int(base_profit * growth_factor * 0.1)
        }

    return financials

def display():
    """Main display function for data fetching module"""
    st.header("📊 Data Fetching & Market Analysis")

    # Asset class selection
    asset_classes = ["Equity", "Cryptocurrency", "Commodities", "Bonds", "ETF", "Forex"]
    selected_asset_class = st.selectbox("Select Asset Class", asset_classes)

    # Symbol input based on asset class
    if selected_asset_class == "Equity":
        symbol = st.text_input("Enter Stock Symbol (e.g., RELIANCE.NS, AAPL)", "RELIANCE.NS")
    elif selected_asset_class == "Cryptocurrency":
        symbol = st.selectbox("Select Cryptocurrency", ["BTC", "ETH", "BNB", "ADA", "SOL"])
    elif selected_asset_class == "Commodities":
        symbol = st.selectbox("Select Commodity", ["GOLD", "SILVER", "OIL", "COPPER", "NATURAL_GAS"])
    elif selected_asset_class == "Bonds":
        symbol = st.selectbox("Select Bond/Treasury", ["US10Y", "US30Y", "US5Y", "US2Y", "US3M"])
    elif selected_asset_class == "ETF":
        symbol = st.text_input("Enter ETF Symbol (e.g., SPY, QQQ)", "SPY")
    elif selected_asset_class == "Forex":
        symbol = st.selectbox("Select Forex Pair", ["USDINR", "EURUSD", "GBPUSD", "USDJPY"])

    # Time period selection
    periods = ["1mo", "3mo", "6mo", "1y", "2y", "5y", "10y", "max"]
    selected_period = st.selectbox("Select Time Period", periods, index=3)

    # Fetch data button
    if st.button("Fetch Data"):
        with st.spinner("Fetching data..."):
            data = fetch_asset_data(symbol, selected_asset_class, period=selected_period)

            if data is not None and not data.empty:
                # Display basic info
                st.success(f"Data fetched successfully for {symbol}")

                # Current price and basic metrics
                if 'Close' in data.columns:
                    current_price = data['Close'].iloc[-1]
                    prev_price = data['Close'].iloc[-2] if len(data) > 1 else current_price

                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("Current Price", f"₹{current_price:.2f}")
                    with col2:
                        change = current_price - prev_price
                        change_pct = (change / prev_price) * 100
                        st.metric("Change", f"₹{change:.2f}", f"{change_pct:.2f}%")
                    with col3:
                        st.metric("High", f"₹{data['High'].max():.2f}")
                    with col4:
                        st.metric("Low", f"₹{data['Low'].min():.2f}")

                # Price chart
                st.subheader("Price Chart")
                st.line_chart(data['Close'])

                # Volume chart if available
                if 'Volume' in data.columns and data['Volume'].sum() > 0:
                    st.subheader("Volume Chart")
                    st.bar_chart(data['Volume'])

                # Raw data table
                with st.expander("View Raw Data"):
                    st.dataframe(data)

                # Download options
                csv = data.to_csv().encode('utf-8')
                st.download_button(
                    label="Download CSV",
                    data=csv,
                    file_name=f'{symbol}_{selected_period}.csv',
                    mime='text/csv'
                )
            else:
                st.error("Failed to fetch data. Please check the symbol and try again.")

    # Financial Statements Display (for equity)
    if selected_asset_class == "Equity":
        st.subheader("📈 Financial Statements")
        if st.button("Show Financial Statements"):
            with st.spinner("Fetching financial statements..."):
                # Fetch real financial statements from Yahoo Finance
                financials = fetch_financial_statements(symbol)

                if financials:
                    # Show last 5 financial years
                    fy_years = list(financials['income_statement'].keys())
                    st.info(f"Displaying data for: {', '.join(fy_years)}")

                    # Display Income Statement
                    st.subheader("💰 Income Statement (₹ in Crores)")
                    if financials['income_statement']:
                        is_df = pd.DataFrame(financials['income_statement']).T
                        st.dataframe(is_df.style.format("{:,.0f}"))

                    # Display Balance Sheet
                    st.subheader("🏦 Balance Sheet (₹ in Crores)")
                    if financials['balance_sheet']:
                        bs_df = pd.DataFrame(financials['balance_sheet']).T
                        st.dataframe(bs_df.style.format("{:,.0f}"))

                    # Display Cash Flow Statement
                    st.subheader("💵 Cash Flow Statement (₹ in Crores)")
                    if financials['cash_flow']:
                        cf_df = pd.DataFrame(financials['cash_flow']).T
                        st.dataframe(cf_df.style.format("{:,.0f}"))

                    # Key Financial Ratios
                    st.subheader("📊 Key Financial Ratios")
                    if len(fy_years) >= 2:
                        latest_fy = fy_years[0]
                        prev_fy = fy_years[1]

                        # Calculate growth rates
                        try:
                            revenue_latest = financials['income_statement'][latest_fy].get('Revenue', 0)
                            revenue_prev = financials['income_statement'][prev_fy].get('Revenue', 0)
                            profit_latest = financials['income_statement'][latest_fy].get('Net Profit', 0)
                            profit_prev = financials['income_statement'][prev_fy].get('Net Profit', 0)

                            if revenue_prev > 0:
                                revenue_growth = ((revenue_latest - revenue_prev) / revenue_prev) * 100
                            else:
                                revenue_growth = 0

                            if profit_prev > 0:
                                profit_growth = ((profit_latest - profit_prev) / profit_prev) * 100
                            else:
                                profit_growth = 0

                            col1, col2, col3 = st.columns(3)
                            with col1:
                                st.metric("Revenue Growth", f"{revenue_growth:.1f}%")
                            with col2:
                                st.metric("Profit Growth", f"{profit_growth:.1f}%")
                            with col3:
                                profit_margin = (profit_latest / revenue_latest * 100) if revenue_latest > 0 else 0
                                st.metric("Net Profit Margin", f"{profit_margin:.1f}%")
                        except:
                            st.info("Unable to calculate growth rates with available data.")

                else:
                    st.error("Unable to fetch financial statements. Please try again later.")
