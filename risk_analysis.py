import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime, timedelta
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import scipy.stats as stats
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.units import inch

def calculate_historical_var(returns, confidence_level=0.95, time_horizon=1):
    """
    Calculate Value at Risk using historical simulation method.
    """
    if isinstance(returns, pd.Series):
        returns = returns.values
    var = np.percentile(returns, (1 - confidence_level) * 100)
    return -var * np.sqrt(time_horizon)

def calculate_parametric_var(returns, confidence_level=0.95, time_horizon=1):
    """
    Calculate Value at Risk using parametric method (normal distribution assumption).
    """
    if isinstance(returns, pd.Series):
        returns = returns.values
    mean = np.mean(returns)
    std = np.std(returns)
    z_score = stats.norm.ppf(1 - confidence_level)
    var = mean + z_score * std
    return -var * np.sqrt(time_horizon)

def calculate_monte_carlo_var(returns, confidence_level=0.95, time_horizon=1, simulations=10000):
    """
    Calculate Value at Risk using Monte Carlo simulation.
    """
    if isinstance(returns, pd.Series):
        returns = returns.values
    mean = np.mean(returns)
    std = np.std(returns)

    # Generate random returns
    simulated_returns = np.random.normal(mean, std, (simulations, time_horizon))
    portfolio_returns = np.sum(simulated_returns, axis=1)

    var = np.percentile(portfolio_returns, (1 - confidence_level) * 100)
    return -var

def calculate_cvar(returns, confidence_level=0.95, time_horizon=1):
    """
    Calculate Conditional Value at Risk (Expected Shortfall).
    """
    if isinstance(returns, pd.Series):
        returns = returns.values
    var = calculate_historical_var(returns, confidence_level, time_horizon)
    losses = returns[returns <= -var]
    cvar = np.mean(losses) if len(losses) > 0 else var
    return -cvar

def perform_stress_testing(returns, stress_scenarios=None):
    """
    Perform stress testing with predefined scenarios.
    """
    if stress_scenarios is None:
        stress_scenarios = {
            'Market Crash (-30%)': -0.30,
            'Severe Recession (-20%)': -0.20,
            'Mild Recession (-10%)': -0.10,
            'Bull Market (+15%)': 0.15
        }

    results = {}
    for scenario, shock in stress_scenarios.items():
        stressed_return = returns + shock
        var_95 = calculate_historical_var(stressed_return)
        results[scenario] = {
            'Shock': f"{shock:.1%}",
            'VaR 95%': f"{var_95:.2%}"
        }

    return results

def calculate_risk_factors(returns):
    """
    Calculate key risk factors from returns data.
    """
    if isinstance(returns, pd.Series):
        returns = returns.values

    factors = {
        'Annualized Volatility': f"{np.std(returns) * np.sqrt(252):.2%}",
        'Sharpe Ratio': f"{np.mean(returns) / np.std(returns) * np.sqrt(252):.2f}",
        'Maximum Drawdown': f"{np.min(returns):.2%}",
        'Skewness': f"{stats.skew(returns):.2f}",
        'Kurtosis': f"{stats.kurtosis(returns):.2f}",
        'VaR 95%': f"{calculate_historical_var(returns):.2%}",
        'CVaR 95%': f"{calculate_cvar(returns):.2%}"
    }

    return factors

def create_risk_heatmap(returns, window=30):
    """
    Create a risk heatmap showing rolling volatility.
    """
    if isinstance(returns, pd.Series):
        rolling_vol = returns.rolling(window=window).std() * np.sqrt(252)
    else:
        rolling_vol = pd.Series(returns).rolling(window=window).std() * np.sqrt(252)

    fig = go.Figure(data=go.Heatmap(
        z=[rolling_vol.values],
        x=rolling_vol.index if hasattr(rolling_vol, 'index') else list(range(len(rolling_vol))),
        y=['Volatility'],
        colorscale='RdYlGn_r'
    ))

    fig.update_layout(
        title="Risk Heatmap - Rolling Volatility",
        xaxis_title="Time",
        yaxis_title="Risk Metric"
    )

    return fig

def create_var_comparison_chart(returns):
    """
    Create a comparison chart of different VaR methods.
    """
    methods = ['Historical', 'Parametric', 'Monte Carlo']
    var_values = [
        calculate_historical_var(returns),
        calculate_parametric_var(returns),
        calculate_monte_carlo_var(returns)
    ]

    fig = go.Figure(data=[
        go.Bar(
            x=methods,
            y=var_values,
            marker_color=['blue', 'green', 'red']
        )
    ])

    fig.update_layout(
        title="VaR Methods Comparison (95% Confidence)",
        xaxis_title="Method",
        yaxis_title="Value at Risk (%)",
        yaxis_tickformat=".1%"
    )

    return fig

def generate_risk_analysis_report(symbol, hist_var, param_var, mc_var, cvar, risk_factors, filename=None):
    """
    Generate a PDF risk analysis report.
    """
    if filename is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"risk_analysis_{symbol}_{timestamp}.pdf"

    doc = SimpleDocTemplate(filename, pagesize=letter)
    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=16,
        spaceAfter=30,
    )

    content = []

    # Title
    content.append(Paragraph(f"Risk Analysis Report - {symbol}", title_style))
    content.append(Spacer(1, 12))

    # Executive Summary
    content.append(Paragraph("Executive Summary", styles['Heading2']))
    content.append(Spacer(1, 12))
    content.append(Paragraph(
        f"This report provides a comprehensive risk analysis for {symbol} using multiple Value at Risk (VaR) methodologies.",
        styles['Normal']
    ))
    content.append(Spacer(1, 12))

    # VaR Results
    content.append(Paragraph("Value at Risk Results", styles['Heading2']))
    content.append(Spacer(1, 12))

    var_data = [
        ['Method', 'VaR (95%)'],
        ['Historical Simulation', f"{hist_var:.2%}"],
        ['Parametric (Normal)', f"{param_var:.2%}"],
        ['Monte Carlo', f"{mc_var:.2%}"],
        ['Conditional VaR', f"{cvar:.2%}"]
    ]

    var_table = Table(var_data)
    var_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 14),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))

    content.append(var_table)
    content.append(Spacer(1, 20))

    # Risk Factors
    content.append(Paragraph("Key Risk Factors", styles['Heading2']))
    content.append(Spacer(1, 12))

    risk_data = [['Factor', 'Value']]
    for factor, value in risk_factors.items():
        risk_data.append([factor, value])

    risk_table = Table(risk_data)
    risk_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))

    content.append(risk_table)
    content.append(Spacer(1, 20))

    # Methodology
    content.append(Paragraph("Methodology", styles['Heading2']))
    content.append(Spacer(1, 12))
    content.append(Paragraph(
        "This analysis uses historical price data to calculate risk metrics using multiple methodologies. "
        "VaR represents the maximum potential loss over a specific time period with a given confidence level.",
        styles['Normal']
    ))

    # Build PDF
    doc.build(content)
    return filename

def display():
    st.header("🛡️ Risk Analysis & Management")

    # Asset selection
    asset_type = st.selectbox(
        "Select Asset Type",
        ["Stock", "Portfolio", "Cryptocurrency", "Forex"]
    )

    if asset_type == "Stock":
        symbol = st.text_input("Enter Stock Symbol (e.g., RELIANCE.NS)", "RELIANCE.NS")
    elif asset_type == "Portfolio":
        st.write("Portfolio risk analysis coming soon...")
        return
    elif asset_type == "Cryptocurrency":
        symbol = st.selectbox("Select Cryptocurrency", ["BTC-USD", "ETH-USD", "BNB-USD"])
    else:  # Forex
        symbol = st.selectbox("Select Currency Pair", ["EURUSD=X", "GBPUSD=X", "USDJPY=X"])

    if st.button("Analyze Risk"):
        with st.spinner("Performing risk analysis..."):
            try:
                # Fetch data
                data = yf.download(symbol, period="2y")
                returns = data['Close'].pct_change().dropna()

                # Calculate VaR methods
                col1, col2, col3 = st.columns(3)

                with col1:
                    st.subheader("Historical VaR")
                    hist_var = calculate_historical_var(returns)
                    st.metric("95% VaR", f"{hist_var:.2%}")

                with col2:
                    st.subheader("Parametric VaR")
                    param_var = calculate_parametric_var(returns)
                    st.metric("95% VaR", f"{param_var:.2%}")

                with col3:
                    st.subheader("Monte Carlo VaR")
                    mc_var = calculate_monte_carlo_var(returns)
                    st.metric("95% VaR", f"{mc_var:.2%}")

                # CVaR
                st.subheader("Conditional VaR (CVaR)")
                cvar = calculate_cvar(returns)
                st.metric("95% CVaR", f"{cvar:.2%}")

                # Risk Factors
                st.subheader("Risk Factors")
                risk_factors = calculate_risk_factors(returns)
                # Display risk factors in a table format
                risk_df = pd.DataFrame(list(risk_factors.items()), columns=['Factor', 'Value'])
                st.dataframe(risk_df.style.format({'Value': lambda x: x}))

                # Stress Testing
                st.subheader("Stress Testing")
                stress_results = perform_stress_testing(returns)
                st.write(stress_results)

                # Risk Heatmap
                st.subheader("Risk Heatmap")
                fig = create_risk_heatmap(returns)
                st.plotly_chart(fig)

                # VaR Comparison Chart
                st.subheader("VaR Methods Comparison")
                fig = create_var_comparison_chart(returns)
                st.plotly_chart(fig)

                # Generate Report
                if st.button("Generate Risk Analysis Report"):
                    report_path = generate_risk_analysis_report(
                        symbol, hist_var, param_var, mc_var, cvar, risk_factors
                    )
                    st.success(f"Report generated: {report_path}")

            except Exception as e:
                st.error(f"Error in risk analysis: {str(e)}")
