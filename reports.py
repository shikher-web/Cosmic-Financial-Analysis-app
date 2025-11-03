import streamlit as st
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
import pandas as pd
from datetime import datetime
import os

def generate_comprehensive_report(company_data, technical_data, fundamental_data, news_data):
    """Generate comprehensive PDF report using ReportLab"""
    filename = f"cosmic_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    doc = SimpleDocTemplate(filename, pagesize=letter)
    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        spaceAfter=30,
        alignment=1  # Center alignment
    )

    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        spaceAfter=20,
    )

    normal_style = styles['Normal']

    story = []

    # Title
    story.append(Paragraph("Cosmic Financial Analysis Report", title_style))
    story.append(Paragraph(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles['Italic']))
    story.append(Spacer(1, 20))

    # Executive Summary
    story.append(Paragraph("Executive Summary", heading_style))
    story.append(Paragraph(f"Financial analysis report for {company_data.get('symbol', 'N/A')} generated on {datetime.now().strftime('%Y-%m-%d')}.", normal_style))
    story.append(Spacer(1, 12))

    # Fundamental Analysis
    story.append(Paragraph("Fundamental Analysis", heading_style))
    if fundamental_data:
        fundamentals = [
            ["Metric", "Value"],
            ["Market Cap", f"₹{fundamental_data.get('market_cap', 'N/A')}"],
            ["P/E Ratio", f"{fundamental_data.get('pe_ratio', 'N/A')}"],
            ["EPS", f"₹{fundamental_data.get('eps', 0):.2f}"],
            ["Dividend Yield", f"{fundamental_data.get('dividend_yield', 0):.2%}"],
        ]
        table = Table(fundamentals)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 14),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(table)
    else:
        story.append(Paragraph("Fundamental data not available.", normal_style))
    story.append(Spacer(1, 12))

    # Technical Analysis
    story.append(Paragraph("Technical Analysis", heading_style))
    if technical_data:
        technicals = [
            ["Indicator", "Value"],
            ["RSI", f"{technical_data.get('rsi', 'N/A')}"],
            ["MACD", f"{technical_data.get('macd', 'N/A')}"],
            ["Recommendation", f"{technical_data.get('recommendation', 'N/A')}"],
        ]
        table = Table(technicals)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.lightblue),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(table)
    else:
        story.append(Paragraph("Technical data not available.", normal_style))
    story.append(Spacer(1, 12))

    # News Summary
    story.append(Paragraph("Recent News Summary", heading_style))
    if news_data:
        for i, news in enumerate(news_data[:5]):
            story.append(Paragraph(f"{i+1}. {news.get('title', 'N/A')}", normal_style))
            story.append(Spacer(1, 6))
    else:
        story.append(Paragraph("No recent news available.", normal_style))
    story.append(Spacer(1, 12))

    # Recommendations
    story.append(Paragraph("Investment Recommendations", heading_style))
    recommendations = [
        "• Fundamental strength assessment",
        "• Technical indicators analysis",
        "• Market sentiment evaluation",
        "• Risk assessment and position sizing"
    ]
    for rec in recommendations:
        story.append(Paragraph(rec, normal_style))
        story.append(Spacer(1, 4))

    doc.build(story)
    return filename

def generate_excel_report(data_dict, filename="report.xlsx"):
    """Generate Excel report with multiple sheets"""
    try:
        import openpyxl
        with pd.ExcelWriter(filename, engine='openpyxl') as writer:
            for sheet_name, data in data_dict.items():
                if isinstance(data, dict):
                    df = pd.DataFrame(list(data.items()), columns=['Metric', 'Value'])
                elif isinstance(data, list):
                    df = pd.DataFrame(data)
                else:
                    df = pd.DataFrame([data])
                df.to_excel(writer, sheet_name=sheet_name, index=False)
        return filename
    except ImportError:
        st.error("openpyxl not installed. Please install it to generate Excel reports.")
        return None

def display():
    st.header("📄 Report Generation")

    report_type = st.selectbox("Report Type", ["PDF Report", "Excel Report", "CSV Export"])

    # Sample comprehensive data
    company_data = {
        "symbol": "RELIANCE.NS",
        "name": "Reliance Industries Ltd",
        "sector": "Energy"
    }

    fundamental_data = {
        "market_cap": "₹15,00,000 Cr",
        "pe_ratio": "25.5",
        "eps": "₹150",
        "dividend_yield": "0.5%"
    }

    technical_data = {
        "rsi": "65.2",
        "macd": "12.5",
        "recommendation": "BUY"
    }

    news_data = [
        {"title": "Reliance Q3 results exceed expectations", "date": "2024-01-15"},
        {"title": "Reliance announces new investment in renewables", "date": "2024-01-10"}
    ]

    if report_type == "PDF Report":
        st.subheader("📊 Comprehensive PDF Report")
        if st.button("Generate PDF Report"):
            with st.spinner("Generating PDF report..."):
                filename = generate_comprehensive_report(company_data, technical_data, fundamental_data, news_data)
                with open(filename, "rb") as f:
                    st.download_button(
                        label="📥 Download PDF Report",
                        data=f,
                        file_name=filename,
                        mime="application/pdf"
                    )
                st.success(f"PDF report generated: {filename}")

    elif report_type == "Excel Report":
        st.subheader("📈 Excel Report with Multiple Sheets")
        data_dict = {
            "Company Info": company_data,
            "Fundamentals": fundamental_data,
            "Technical": technical_data,
            "News": news_data
        }
        if st.button("Generate Excel Report"):
            with st.spinner("Generating Excel report..."):
                filename = generate_excel_report(data_dict)
                if filename:
                    with open(filename, "rb") as f:
                        st.download_button(
                            label="📥 Download Excel Report",
                            data=f,
                            file_name=filename,
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                        )
                    st.success(f"Excel report generated: {filename}")

    elif report_type == "CSV Export":
        st.subheader("📋 CSV Data Export")
        export_options = st.multiselect(
            "Select data to export",
            ["Company Data", "Fundamental Data", "Technical Data", "News Data"]
        )

        if st.button("Generate CSV"):
            if export_options:
                for option in export_options:
                    if option == "Company Data":
                        df = pd.DataFrame([company_data])
                        csv = df.to_csv(index=False)
                        st.download_button(
                            label="📥 Download Company Data CSV",
                            data=csv,
                            file_name="company_data.csv",
                            mime="text/csv"
                        )
                    elif option == "Fundamental Data":
                        df = pd.DataFrame([fundamental_data])
                        csv = df.to_csv(index=False)
                        st.download_button(
                            label="📥 Download Fundamental Data CSV",
                            data=csv,
                            file_name="fundamental_data.csv",
                            mime="text/csv"
                        )
                    elif option == "Technical Data":
                        df = pd.DataFrame([technical_data])
                        csv = df.to_csv(index=False)
                        st.download_button(
                            label="📥 Download Technical Data CSV",
                            data=csv,
                            file_name="technical_data.csv",
                            mime="text/csv"
                        )
                    elif option == "News Data":
                        df = pd.DataFrame(news_data)
                        csv = df.to_csv(index=False)
                        st.download_button(
                            label="📥 Download News Data CSV",
                            data=csv,
                            file_name="news_data.csv",
                            mime="text/csv"
                        )
            else:
                st.warning("Please select at least one data type to export.")

    # Report Templates
    st.subheader("📝 Report Templates")
    template = st.selectbox("Choose Template", ["Basic Analysis", "Detailed Valuation", "Portfolio Review", "Market Outlook"])

    if template == "Basic Analysis":
        st.info("Includes: Company overview, key metrics, technical indicators, and basic recommendation")
    elif template == "Detailed Valuation":
        st.info("Includes: DCF valuation, comparative analysis, risk assessment, and investment thesis")
    elif template == "Portfolio Review":
        st.info("Includes: Portfolio performance, asset allocation, rebalancing recommendations")
    elif template == "Market Outlook":
        st.info("Includes: Market trends, sector analysis, economic indicators, and outlook")
