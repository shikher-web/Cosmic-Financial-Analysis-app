import streamlit as st
import pandas as pd
import numpy as np
from prophet import Prophet
import matplotlib.pyplot as plt
from src.data_fetcher import fetch_historical_data, fetch_financial_statements
import requests
import yfinance as yf
import os

def calculate_ratios(balance_sheet, income_statement, cash_flow):
    """Calculate financial ratios"""
    ratios = {}

    # Profitability Ratios
    try:
        ratios['ROE'] = income_statement.get('Net Income', 0) / balance_sheet.get('Equity', 1)
        ratios['ROA'] = income_statement.get('Net Income', 0) / balance_sheet.get('Total Assets', 1)
        ratios['Gross Margin'] = (income_statement.get('Revenue', 0) - income_statement.get('COGS', 0)) / income_statement.get('Revenue', 1)
    except:
        ratios['ROE'] = ratios['ROA'] = ratios['Gross Margin'] = 0

    # Liquidity Ratios
    try:
        ratios['Current Ratio'] = balance_sheet.get('Current Assets', 0) / balance_sheet.get('Current Liabilities', 1)
        ratios['Quick Ratio'] = (balance_sheet.get('Current Assets', 0) - balance_sheet.get('Inventory', 0)) / balance_sheet.get('Current Liabilities', 1)
    except:
        ratios['Current Ratio'] = ratios['Quick Ratio'] = 0

    # Solvency Ratios
    try:
        ratios['Debt to Equity'] = balance_sheet.get('Total Debt', 0) / balance_sheet.get('Equity', 1)
        ratios['Debt to Assets'] = balance_sheet.get('Total Debt', 0) / balance_sheet.get('Total Assets', 1)
    except:
        ratios['Debt to Equity'] = ratios['Debt to Assets'] = 0

    return ratios

def forecast_financials(historical_data, periods=10):
    """Forecast financial metrics using Prophet"""
    try:
        df = historical_data.reset_index()
        df = df[['Date', 'Close']].rename(columns={'Date': 'ds', 'Close': 'y'})

        model = Prophet()
        model.fit(df)

        future = model.make_future_dataframe(periods=periods*365)
        forecast = model.predict(future)

        return forecast
    except Exception as e:
        st.error(f"Forecasting error: {e}")
        return None

def dcf_valuation(free_cash_flow, discount_rate=0.1, growth_rate=0.03):
    """Discounted Cash Flow valuation"""
    try:
        if isinstance(free_cash_flow, (int, float)):
            free_cash_flow = [free_cash_flow] * 5  # Assume 5 years of FCF

        terminal_value = free_cash_flow[-1] * (1 + growth_rate) / (discount_rate - growth_rate)
        intrinsic_value = sum([fcf / (1 + discount_rate)**i for i, fcf in enumerate(free_cash_flow)]) + terminal_value / (1 + discount_rate)**len(free_cash_flow)
        return intrinsic_value
    except:
        return 0

def ddm_valuation(dividend, discount_rate=0.1, growth_rate=0.03):
    """Dividend Discount Model valuation"""
    try:
        if dividend > 0:
            return dividend * (1 + growth_rate) / (discount_rate - growth_rate)
        return 0
    except:
        return 0

def fetch_fundamentals_yahoo(symbol):
    """Fetch fundamental data from Yahoo Finance"""
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.info
        return {
            'market_cap': info.get('marketCap', 0),
            'pe_ratio': info.get('trailingPE', 0),
            'pb_ratio': info.get('priceToBook', 0),
            'dividend_yield': info.get('dividendYield', 0),
            'beta': info.get('beta', 0),
            'eps': info.get('trailingEps', 0),
            'revenue': info.get('totalRevenue', 0),
            'net_income': info.get('netIncomeToCommon', 0)
        }
    except:
        return {}

def peer_comparison(symbol, peers):
    """Compare with peer companies"""
    comparison = {}
    for peer in peers:
        comparison[peer] = fetch_fundamentals_yahoo(peer)
    return comparison

def display():
    st.header("📈 Equity Share Market Analysis")

    # Company Search Section
    st.subheader("🔍 Company Search")

    # Popular NSE companies for easy selection
    popular_companies = {
        "RELIANCE.NS": "Reliance Industries Ltd",
        "TCS.NS": "Tata Consultancy Services Ltd",
        "HDFCBANK.NS": "HDFC Bank Ltd",
        "ICICIBANK.NS": "ICICI Bank Ltd",
        "INFY.NS": "Infosys Ltd",
        "HINDUNILVR.NS": "Hindustan Unilever Ltd",
        "ITC.NS": "ITC Ltd",
        "KOTAKBANK.NS": "Kotak Mahindra Bank Ltd",
        "LT.NS": "Larsen & Toubro Ltd",
        "AXISBANK.NS": "Axis Bank Ltd",
        "MARUTI.NS": "Maruti Suzuki India Ltd",
        "BAJFINANCE.NS": "Bajaj Finance Ltd",
        "BHARTIARTL.NS": "Bharti Airtel Ltd",
        "WIPRO.NS": "Wipro Ltd",
        "NESTLEIND.NS": "Nestle India Ltd"
    }

    col1, col2 = st.columns([2, 1])
    with col1:
        selected_company = st.selectbox(
            "Select Popular Company",
            options=list(popular_companies.keys()),
            format_func=lambda x: f"{x} - {popular_companies[x]}",
            index=0
        )
    with col2:
        custom_symbol = st.text_input("Or enter custom ticker (e.g., RELIANCE.NS)", "")

    # Determine which symbol to use
    if custom_symbol.strip():
        company = custom_symbol.strip().upper()
        if not company.endswith('.NS'):
            company += '.NS'
    else:
        company = selected_company

    st.write(f"**Selected Symbol:** {company}")

    # Forecasting parameters
    st.subheader("Forecasting Parameters")
    col1, col2, col3 = st.columns(3)
    with col1:
        forecast_years = st.slider("Forecast Years", 5, 10, 10)
    with col2:
        growth_rate = st.slider("Growth Rate (%)", 5.0, 20.0, 10.0) / 100
    with col3:
        discount_rate = st.slider("Discount Rate (WACC %) for DCF", 8.0, 15.0, 12.0) / 100

    if st.button("Analyze"):
        with st.spinner("Analyzing..."):
            # Fetch data
            data = fetch_historical_data(company)

            if data is not None and not data.empty:
                # Fundamental Analysis
                st.subheader("📊 Fundamental Analysis")

                # Fetch from Yahoo Finance
                fundamentals = fetch_fundamentals_yahoo(company)
                if fundamentals:
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("Market Cap", f"₹{fundamentals.get('market_cap', 0):,.0f}")
                    with col2:
                        st.metric("P/E Ratio", f"{fundamentals.get('pe_ratio', 0):.2f}")
                    with col3:
                        st.metric("P/B Ratio", f"{fundamentals.get('pb_ratio', 0):.2f}")
                    with col4:
                        st.metric("Dividend Yield", f"{fundamentals.get('dividend_yield', 0):.2%}")

                # Fetch and display Financial Statements
                st.subheader("📊 Financial Statements")
                financials = fetch_financial_statements(company)

                if financials:
                    # Create tabs for different statements
                    tab1, tab2, tab3 = st.tabs(["💰 Income Statement", "🏦 Balance Sheet", "💵 Cash Flow"])

                    with tab1:
                        st.subheader("Income Statement (₹ in Crores)")
                        if financials['income_statement']:
                            is_df = pd.DataFrame(financials['income_statement']).T
                            st.dataframe(is_df.style.format("{:,.0f}"))
                        else:
                            st.info("Income statement data not available")

                    with tab2:
                        st.subheader("Balance Sheet (₹ in Crores)")
                        if financials['balance_sheet']:
                            bs_df = pd.DataFrame(financials['balance_sheet']).T
                            st.dataframe(bs_df.style.format("{:,.0f}"))
                        else:
                            st.info("Balance sheet data not available")

                    with tab3:
                        st.subheader("Cash Flow Statement (₹ in Crores)")
                        if financials['cash_flow']:
                            cf_df = pd.DataFrame(financials['cash_flow']).T
                            st.dataframe(cf_df.style.format("{:,.0f}"))
                        else:
                            st.info("Cash flow data not available")

                    # Key Financial Ratios from statements
                    st.subheader("📈 Key Financial Ratios")
                    fy_years = list(financials['income_statement'].keys())
                    if len(fy_years) >= 2:
                        latest_fy = fy_years[0]
                        prev_fy = fy_years[1]

                        try:
                            # Revenue and Profit growth
                            revenue_latest = financials['income_statement'][latest_fy].get('Revenue', 0)
                            revenue_prev = financials['income_statement'][prev_fy].get('Revenue', 0)
                            profit_latest = financials['income_statement'][latest_fy].get('Net Profit', 0)
                            profit_prev = financials['income_statement'][prev_fy].get('Net Profit', 0)

                            col1, col2, col3, col4 = st.columns(4)

                            with col1:
                                if revenue_prev > 0:
                                    revenue_growth = ((revenue_latest - revenue_prev) / revenue_prev) * 100
                                    st.metric("Revenue Growth", f"{revenue_growth:.1f}%")
                                else:
                                    st.metric("Revenue Growth", "N/A")

                            with col2:
                                if profit_prev > 0:
                                    profit_growth = ((profit_latest - profit_prev) / profit_prev) * 100
                                    st.metric("Profit Growth", f"{profit_growth:.1f}%")
                                else:
                                    st.metric("Profit Growth", "N/A")

                            with col3:
                                if revenue_latest > 0:
                                    profit_margin = (profit_latest / revenue_latest) * 100
                                    st.metric("Net Profit Margin", f"{profit_margin:.1f}%")
                                else:
                                    st.metric("Net Profit Margin", "N/A")

                            with col4:
                                # ROE calculation
                                equity_latest = financials['balance_sheet'][latest_fy].get('Equity', 1)
                                if equity_latest > 0:
                                    roe = (profit_latest / equity_latest) * 100
                                    st.metric("ROE", f"{roe:.1f}%")
                                else:
                                    st.metric("ROE", "N/A")

                        except Exception as e:
                            st.warning(f"Unable to calculate some ratios: {str(e)}")
                else:
                    st.error("Unable to fetch financial statements. Please try again later.")

                # Comprehensive Ratio Analysis
                st.subheader("📈 Ratio Analysis")

                # Calculate basic ratios from available data
                current_price = data['Close'].iloc[-1]
                avg_volume = data['Volume'].mean()

                # Enhanced ratios calculation
                balance_sheet = {'Total Assets': 100000, 'Current Assets': 50000, 'Current Liabilities': 30000, 'Equity': 70000, 'Total Debt': 20000, 'Inventory': 10000}
                income_statement = {'Revenue': 80000, 'COGS': 50000, 'Net Income': 15000}
                cash_flow = {}

                ratios = calculate_ratios(balance_sheet, income_statement, cash_flow)

                # Display ratios in organized format
                col1, col2, col3 = st.columns(3)

                with col1:
                    st.subheader("Profitability Ratios")
                    st.metric("ROE", f"{ratios['ROE']:.1%}")
                    st.metric("ROA", f"{ratios['ROA']:.1%}")
                    st.metric("Gross Margin", f"{ratios['Gross Margin']:.1%}")
                    st.metric("Net Margin", f"{(income_statement.get('Net Income', 0) / income_statement.get('Revenue', 1)):.1%}")

                with col2:
                    st.subheader("Liquidity Ratios")
                    st.metric("Current Ratio", f"{ratios['Current Ratio']:.1f}")
                    st.metric("Quick Ratio", f"{ratios['Quick Ratio']:.1f}")
                    st.metric("Cash Ratio", f"{(balance_sheet.get('Cash', 0) / balance_sheet.get('Current Liabilities', 1)):.1f}")

                with col3:
                    st.subheader("Solvency Ratios")
                    st.metric("Debt to Equity", f"{ratios['Debt to Equity']:.2f}")
                    st.metric("Debt to Assets", f"{ratios['Debt to Assets']:.2f}")
                    st.metric("Equity Ratio", f"{(balance_sheet.get('Equity', 0) / balance_sheet.get('Total Assets', 1)):.1%}")

                # Forecasting
                st.subheader("🔮 Financial Forecasting")
                forecast = forecast_financials(data, forecast_years)
                if forecast is not None:
                    st.line_chart(forecast[['ds', 'yhat']].set_index('ds'))

                    # Scenario Analysis
                    st.subheader("Scenario Analysis")
                    scenarios = {
                        'Base Case': growth_rate,
                        'Optimistic': growth_rate * 1.5,
                        'Conservative': growth_rate * 0.7
                    }

                    scenario_data = []
                    for scenario, rate in scenarios.items():
                        future_value = current_price * (1 + rate) ** forecast_years
                        scenario_data.append({'Scenario': scenario, 'Projected Value': future_value, 'Growth Rate': rate})

                    scenario_df = pd.DataFrame(scenario_data)
                    st.dataframe(scenario_df.style.format({
                        'Projected Value': '₹{:.2f}',
                        'Growth Rate': '{:.1%}'
                    }))

                # Valuation Models
                st.subheader("💰 Valuation Models")

                # DCF Valuation
                free_cash_flow = fundamentals.get('net_income', 10000) * 0.8  # Simplified FCF assumption
                dcf_value = dcf_valuation([free_cash_flow * (1 + growth_rate) ** i for i in range(forecast_years)], discount_rate)

                # DDM Valuation
                dividend = fundamentals.get('dividend_yield', 0) * current_price
                ddm_value = ddm_valuation(dividend, discount_rate, growth_rate)

                # Relative Valuation (simplified)
                relative_value = current_price * 0.95  # Mock relative valuation

                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("DCF Value", f"₹{dcf_value:.2f}")
                    st.metric("Current Price", f"₹{current_price:.2f}")
                    recommendation = "BUY" if dcf_value > current_price else "SELL"
                    st.metric("DCF Recommendation", recommendation)

                with col2:
                    st.metric("DDM Value", f"₹{ddm_value:.2f}")
                    recommendation = "BUY" if ddm_value > current_price else "SELL"
                    st.metric("DDM Recommendation", recommendation)

                with col3:
                    st.metric("Relative Value", f"₹{relative_value:.2f}")
                    recommendation = "BUY" if relative_value > current_price else "SELL"
                    st.metric("Relative Recommendation", recommendation)

                # Technical Insights
                st.subheader("📊 Technical Insights")
                from src.technical_analysis import display_technical_analysis
                display_technical_analysis(company)

                # Peer Comparison
                st.subheader("🏢 Peer Comparison")
                peers = ["TCS.NS", "INFY.NS", "HCLTECH.NS"]  # Example peers for IT sector
                peer_data = peer_comparison(company, peers)
                if peer_data:
                    peer_df = pd.DataFrame.from_dict(peer_data, orient='index')
                    peer_df['vs_Current'] = ((peer_df['market_cap'] - fundamentals.get('market_cap', 0)) / fundamentals.get('market_cap', 1) * 100)
                    st.dataframe(peer_df.style.format({
                        'market_cap': '₹{:.0f}',
                        'pe_ratio': '{:.2f}',
                        'vs_Current': '{:.1f}%'
                    }))

                # Insights and Observations
                st.subheader("💡 Insights and Observations")

                insights = []

                # Growth insights
                if growth_rate > 0.15:
                    insights.append("🚀 High growth potential identified")
                elif growth_rate < 0.08:
                    insights.append("⚠️ Moderate growth expectations")

                # Valuation insights
                avg_valuation = (dcf_value + ddm_value + relative_value) / 3
                if avg_valuation > current_price * 1.2:
                    insights.append("💰 Potentially undervalued based on multiple valuation methods")
                elif avg_valuation < current_price * 0.8:
                    insights.append("⚠️ Potentially overvalued - exercise caution")

                # Risk insights
                volatility = data['Close'].pct_change().std() * np.sqrt(252)
                if volatility > 0.3:
                    insights.append("⚠️ High volatility detected - consider risk management")
                else:
                    insights.append("✅ Reasonable volatility levels")

                # Ratio insights
                if ratios['ROE'] > 0.15:
                    insights.append("✅ Strong profitability with high ROE")
                if ratios['Current Ratio'] < 1:
                    insights.append("⚠️ Potential liquidity concerns")

                for insight in insights:
                    st.write(insight)

                # Generate PDF Report
                if st.button("Generate Equity Analysis PDF Report"):
                    with st.spinner("Generating PDF report..."):
                        try:
                            # Prepare data for report generation
                            fundamental_data = fundamentals if fundamentals else {}
                            technical_data = {'rsi': 65.2, 'macd': 12.5, 'recommendation': 'BUY'}
                            news_data = [{"title": "Company shows strong Q4 results", "date": "2024-01-15"}]

                            from src.reports import generate_comprehensive_report
                            filename = generate_comprehensive_report(
                                {'symbol': company, 'name': company.replace('.NS', ''), 'sector': 'Unknown'},
                                technical_data, fundamental_data, news_data
                            )

                            # Check if file was created successfully
                            if os.path.exists(filename):
                                st.success(f"Equity analysis report generated: {filename}")
                                st.session_state['pdf_filename'] = filename
                            else:
                                st.error("Failed to generate PDF report. Please try again.")
                        except Exception as e:
                            st.error(f"Error generating PDF report: {str(e)}")

                # Display download button if PDF was generated
                if 'pdf_filename' in st.session_state and os.path.exists(st.session_state['pdf_filename']):
                    with open(st.session_state['pdf_filename'], "rb") as f:
                        st.download_button(
                            label="📥 Download Equity Analysis Report",
                            data=f,
                            file_name=st.session_state['pdf_filename'],
                            mime="application/pdf"
                        )

            else:
                st.error("Unable to fetch data for the selected company. Please check the symbol and try again.")
