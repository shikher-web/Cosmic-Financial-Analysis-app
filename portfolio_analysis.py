import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime, timedelta
import plotly.graph_objects as go
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.units import inch

def fetch_portfolio_data(symbols, years=3):
    """Fetch historical data for multiple symbols"""
    end_date = datetime.now()
    start_date = end_date - timedelta(days=years*365)

    portfolio_data = {}
    for symbol in symbols:
        try:
            data = yf.download(symbol, start=start_date, end=end_date, auto_adjust=False)
            if isinstance(data.columns, pd.MultiIndex):
                data.columns = data.columns.droplevel(1)
            portfolio_data[symbol] = data['Close']
        except Exception as e:
            st.error(f"Error fetching data for {symbol}: {e}")
            portfolio_data[symbol] = None

    return pd.DataFrame(portfolio_data)

def calculate_portfolio_metrics(returns, weights):
    """Calculate portfolio metrics"""
    portfolio_return = np.sum(returns.mean() * weights) * 252  # Annualized
    portfolio_volatility = np.sqrt(np.dot(weights.T, np.dot(returns.cov() * 252, weights)))

    # Sharpe Ratio (assuming risk-free rate of 6.5% for India)
    risk_free_rate = 0.065
    sharpe_ratio = (portfolio_return - risk_free_rate) / portfolio_volatility

    return {
        'expected_return': portfolio_return,
        'volatility': portfolio_volatility,
        'sharpe_ratio': sharpe_ratio
    }

def calculate_individual_metrics(returns):
    """Calculate individual stock metrics"""
    metrics = {}
    for column in returns.columns:
        stock_returns = returns[column].dropna()
        if len(stock_returns) > 0:
            ann_return = stock_returns.mean() * 252
            ann_vol = stock_returns.std() * np.sqrt(252)
            metrics[column] = {
                'return': ann_return,
                'volatility': ann_vol,
                'sharpe_ratio': (ann_return - 0.065) / ann_vol if ann_vol > 0 else 0
            }
    return metrics

def generate_portfolio_report(company_names, weights, equity_weight, debt_weight, wacc, metrics, individual_metrics):
    """Generate comprehensive portfolio analysis PDF report"""
    filename = f"portfolio_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    doc = SimpleDocTemplate(filename, pagesize=letter)
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        spaceAfter=30,
        alignment=1
    )

    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        spaceAfter=20,
    )

    story = []

    # Title
    story.append(Paragraph("Portfolio Analysis Report", title_style))
    story.append(Paragraph(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles['Italic']))
    story.append(Spacer(1, 20))

    # Executive Summary
    story.append(Paragraph("Executive Summary", heading_style))
    story.append(Paragraph("Comprehensive portfolio analysis including risk-return metrics, asset allocation, and performance evaluation.", styles['Normal']))
    story.append(Spacer(1, 12))

    # Portfolio Composition
    story.append(Paragraph("Portfolio Composition", heading_style))
    composition_data = [
        ["Asset Class", "Weight"],
        ["Equity", f"{equity_weight:.1%}"],
        ["Debt", f"{debt_weight:.1%}"],
    ]
    table = Table(composition_data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    story.append(table)
    story.append(Spacer(1, 12))

    # Individual Stock Holdings
    story.append(Paragraph("Individual Stock Holdings", heading_style))
    holdings_data = [["Company", "Weight", "Expected Return", "Volatility", "Sharpe Ratio"]]
    for i, company in enumerate(company_names):
        if company in individual_metrics:
            metrics_data = individual_metrics[company]
            holdings_data.append([
                company,
                f"{weights[i]:.1%}",
                f"{metrics_data['return']:.1%}",
                f"{metrics_data['volatility']:.1%}",
                f"{metrics_data['sharpe_ratio']:.2f}"
            ])
    table = Table(holdings_data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    story.append(table)
    story.append(Spacer(1, 12))

    # Portfolio Metrics
    story.append(Paragraph("Portfolio Performance Metrics", heading_style))
    portfolio_data = [
        ["Metric", "Value"],
        ["Expected Annual Return", f"{metrics['expected_return']:.1%}"],
        ["Annual Volatility", f"{metrics['volatility']:.1%}"],
        ["Sharpe Ratio", f"{metrics['sharpe_ratio']:.2f}"],
        ["WACC", f"{wacc:.1%}"],
    ]
    table = Table(portfolio_data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    story.append(table)
    story.append(Spacer(1, 12))

    # Assumptions and Methodology
    story.append(Paragraph("Assumptions and Methodology", heading_style))
    assumptions = [
        f"• Risk-free rate assumed at 6.5% (typical Indian government bond yield)",
        f"• Historical data used for return calculations (past {3} years)",
        f"• Annualized returns calculated using 252 trading days",
        f"• WACC calculated as: {wacc:.1%}",
        f"• Portfolio weights: Equity {equity_weight:.1%}, Debt {debt_weight:.1%}",
    ]
    for assumption in assumptions:
        story.append(Paragraph(assumption, styles['Normal']))
        story.append(Spacer(1, 4))

    # Recommendations
    story.append(Paragraph("Investment Recommendations", heading_style))
    recommendations = [
        "• Diversify across different sectors to reduce concentration risk",
        "• Regularly rebalance portfolio to maintain target allocations",
        "• Monitor individual stock performance and replace underperformers",
        "• Consider tax implications of portfolio rebalancing",
        "• Review portfolio risk metrics quarterly"
    ]
    for rec in recommendations:
        story.append(Paragraph(rec, styles['Normal']))
        story.append(Spacer(1, 4))

    doc.build(story)
    return filename

def display():
    st.header("📊 Portfolio Analysis")

    st.subheader("Select Companies for Portfolio")
    col1, col2 = st.columns(2)

    with col1:
        num_companies = st.slider("Number of Companies", 2, 10, 5)
        years = st.slider("Historical Data Years", 1, 5, 3)

    companies = []
    for i in range(num_companies):
        company = st.text_input(f"Company {i+1} Symbol (e.g., RELIANCE.NS)", f"RELIANCE.NS" if i == 0 else "", key=f"company_{i}")
        if company:
            companies.append(company)

    # Portfolio weights
    st.subheader("Portfolio Weights")
    if companies:
        weights = []
        cols = st.columns(len(companies))
        for i, col in enumerate(cols):
            with col:
                weight = st.slider(f"{companies[i]} Weight", 0.0, 1.0, 1.0/len(companies), 0.01, key=f"weight_{i}")
                weights.append(weight)

        # Normalize weights
        total_weight = sum(weights)
        if total_weight > 0:
            weights = [w/total_weight for w in weights]

        # Asset allocation
        st.subheader("Asset Allocation")
        col1, col2 = st.columns(2)
        with col1:
            equity_weight = st.slider("Equity Weight", 0.0, 1.0, 0.7, 0.01)
        with col2:
            debt_weight = st.slider("Debt Weight", 0.0, 1.0, 0.3, 0.01)

        # WACC calculation
        equity_cost = st.number_input("Cost of Equity (%)", 10.0, 20.0, 14.0) / 100
        debt_cost = st.number_input("Cost of Debt (%)", 5.0, 10.0, 7.0) / 100
        tax_rate = st.number_input("Tax Rate (%)", 20.0, 35.0, 25.0) / 100

        wacc = (equity_weight * equity_cost) + (debt_weight * debt_cost * (1 - tax_rate))

        st.write(f"**Calculated WACC: {wacc:.1%}**")

        if st.button("Analyze Portfolio"):
            with st.spinner("Analyzing portfolio..."):
                # Fetch data
                portfolio_data = fetch_portfolio_data(companies, years)

                if not portfolio_data.empty:
                    # Filter out companies with no data
                    valid_companies = [col for col in portfolio_data.columns if portfolio_data[col].notna().any()]
                    valid_weights = [weights[i] for i in range(len(companies)) if companies[i] in valid_companies]

                    # Normalize valid weights
                    if valid_weights:
                        total_valid_weight = sum(valid_weights)
                        if total_valid_weight > 0:
                            valid_weights = [w/total_valid_weight for w in valid_weights]

                    if not valid_companies:
                        st.error("No valid data found for any selected companies. Please check symbols and try again.")
                        return

                    # Calculate returns
                    returns = portfolio_data[valid_companies].pct_change(fill_method=None).dropna()

                    # Filter weights to match returns columns (some stocks might have all NaN after pct_change)
                    final_companies = returns.columns.tolist()
                    final_weights = [valid_weights[valid_companies.index(company)] for company in final_companies]

                    if not final_companies:
                        st.error("No valid return data found for any selected companies. Please check symbols and try again.")
                        return

                    # Portfolio metrics
                    portfolio_metrics = calculate_portfolio_metrics(returns, np.array(final_weights))
                    individual_metrics = calculate_individual_metrics(returns)

                    # Display results
                    st.subheader("📈 Portfolio Performance")

                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Expected Annual Return", f"{portfolio_metrics['expected_return']:.1%}")
                    with col2:
                        st.metric("Annual Volatility", f"{portfolio_metrics['volatility']:.1%}")
                    with col3:
                        st.metric("Sharpe Ratio", f"{portfolio_metrics['sharpe_ratio']:.2f}")

                    # Individual stock metrics
                    st.subheader("Individual Stock Metrics")
                    metrics_df = pd.DataFrame.from_dict(individual_metrics, orient='index')
                    st.dataframe(metrics_df.style.format({
                        'return': '{:.1%}',
                        'volatility': '{:.1%}',
                        'sharpe_ratio': '{:.2f}'
                    }))

                    # Portfolio chart
                    st.subheader("Portfolio Value Over Time")
                    normalized_portfolio = (portfolio_data / portfolio_data.iloc[0]) * 100
                    st.line_chart(normalized_portfolio)

                    # Correlation matrix
                    st.subheader("Correlation Matrix")
                    corr_matrix = returns.corr()
                    st.dataframe(corr_matrix.style.background_gradient(cmap='RdYlGn', axis=None))

                    # Generate PDF Report
                    if st.button("Generate Portfolio Analysis PDF Report"):
                        with st.spinner("Generating PDF report..."):
                            filename = generate_portfolio_report(
                                companies, weights, equity_weight, debt_weight,
                                wacc, portfolio_metrics, individual_metrics
                            )
                            with open(filename, "rb") as f:
                                st.download_button(
                                    label="📥 Download Portfolio Analysis Report",
                                    data=f,
                                    file_name=filename,
                                    mime="application/pdf"
                                )
                            st.success(f"Portfolio analysis report generated: {filename}")

                    # Insights and Observations
                    st.subheader("💡 Insights and Observations")

                    # Risk assessment
                    if portfolio_metrics['volatility'] > 0.25:
                        st.warning("⚠️ High portfolio volatility detected. Consider diversification.")
                    elif portfolio_metrics['volatility'] < 0.15:
                        st.success("✅ Low portfolio volatility. Good risk-adjusted returns.")

                    # Sharpe ratio assessment
                    if portfolio_metrics['sharpe_ratio'] > 1.5:
                        st.success("✅ Excellent risk-adjusted returns.")
                    elif portfolio_metrics['sharpe_ratio'] > 1.0:
                        st.info("ℹ️ Good risk-adjusted returns.")
                    else:
                        st.warning("⚠️ Consider optimizing for better risk-adjusted returns.")

                    # Correlation insights
                    high_corr = (corr_matrix > 0.7).sum().sum() - len(corr_matrix)
                    if high_corr > 0:
                        st.info(f"ℹ️ {high_corr} pairs of stocks show high correlation. Consider sector diversification.")

                else:
                    st.error("Unable to fetch data for the selected companies. Please check symbols and try again.")
    else:
        st.info("Please enter company symbols to begin portfolio analysis.")
