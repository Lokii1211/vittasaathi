"""
PDF Report Generator
====================
Generate beautiful PDF reports for users
Uses ReportLab for PDF generation
"""
from datetime import datetime
from typing import Dict, List, Optional
from pathlib import Path
import io
import sys

sys.path.append(str(Path(__file__).parent.parent))

from config import DATA_DIR
from database.user_repository import user_repo
from database.transaction_repository import transaction_repo
from services.analytics_service import analytics_service

# Create reports directory
REPORTS_DIR = DATA_DIR / "reports"
REPORTS_DIR.mkdir(exist_ok=True)

# Try to import reportlab
try:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch, mm
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
    from reportlab.graphics.shapes import Drawing, Rect, String
    from reportlab.graphics.charts.barcharts import VerticalBarChart
    from reportlab.graphics.charts.piecharts import Pie
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False


class PDFReportService:
    """Generate PDF reports"""
    
    def __init__(self):
        self.reports_dir = REPORTS_DIR
    
    def is_available(self) -> bool:
        return PDF_AVAILABLE
    
    def generate_monthly_report(self, user_id: str, month: str = None) -> Optional[str]:
        """Generate monthly PDF report"""
        
        if not PDF_AVAILABLE:
            return None
        
        user = user_repo.get_user(user_id)
        if not user:
            return None
        
        month = month or datetime.now().strftime("%Y-%m")
        month_name = datetime.strptime(month, "%Y-%m").strftime("%B_%Y")
        
        # Create filename
        filename = f"MoneyViya_Report_{user_id}_{month_name}.pdf"
        filepath = self.reports_dir / filename
        
        # Create document
        doc = SimpleDocTemplate(
            str(filepath),
            pagesize=A4,
            rightMargin=20*mm,
            leftMargin=20*mm,
            topMargin=20*mm,
            bottomMargin=20*mm
        )
        
        # Build content
        story = []
        styles = getSampleStyleSheet()
        
        # Custom styles
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#2E7D32'),
            spaceAfter=20,
            alignment=1  # Center
        )
        
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#1565C0'),
            spaceBefore=15,
            spaceAfter=10
        )
        
        normal_style = ParagraphStyle(
            'CustomNormal',
            parent=styles['Normal'],
            fontSize=11,
            spaceAfter=5
        )
        
        # Get all data
        name = user.get("name", "User")
        summary = transaction_repo.get_monthly_summary(user_id, month)
        breakdown = analytics_service.get_category_breakdown(user_id, month)
        savings_health = analytics_service.get_savings_health(user_id)
        prediction = analytics_service.predict_month_end(user_id)
        trends = analytics_service.get_expense_trends(user_id, 3)
        
        # ===== HEADER =====
        story.append(Paragraph("💰 MoneyViya", title_style))
        story.append(Paragraph(f"Financial Report - {month_name.replace('_', ' ')}", styles['Heading2']))
        story.append(Paragraph(f"Prepared for: {name}", normal_style))
        story.append(Paragraph(f"Generated: {datetime.now().strftime('%d %B %Y, %I:%M %p')}", normal_style))
        story.append(Spacer(1, 20))
        
        # ===== SUMMARY BOX =====
        story.append(Paragraph("📊 Monthly Summary", heading_style))
        
        summary_data = [
            ["Income", f"₹{summary.get('total_income', 0):,}"],
            ["Expenses", f"₹{summary.get('total_expense', 0):,}"],
            ["Net Savings", f"₹{summary.get('net_savings', 0):,}"],
            ["Savings Rate", f"{savings_health.get('savings_rate', 0)}%"],
            ["Grade", savings_health.get('grade', 'N/A')],
        ]
        
        summary_table = Table(summary_data, colWidths=[100, 100])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#E3F2FD')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#BBDEFB')),
        ]))
        story.append(summary_table)
        story.append(Spacer(1, 20))
        
        # ===== EXPENSE BREAKDOWN =====
        story.append(Paragraph("💸 Expense Breakdown", heading_style))
        
        expense_data = [["Category", "Amount", "Percentage"]]
        for cat in breakdown.get("categories", [])[:8]:
            expense_data.append([
                f"{cat['icon']} {cat['name']}",
                f"₹{cat['amount']:,}",
                f"{cat['percentage']}%"
            ])
        
        if expense_data:
            expense_table = Table(expense_data, colWidths=[150, 80, 60])
            expense_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1565C0')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ('TOPPADDING', (0, 0), (-1, -1), 6),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F5F5F5')]),
            ]))
            story.append(expense_table)
        story.append(Spacer(1, 20))
        
        # ===== TRENDS =====
        story.append(Paragraph("📈 3-Month Trend", heading_style))
        
        trend_data = [["Month", "Income", "Expense", "Savings"]]
        for i, month_label in enumerate(trends.get("months", [])):
            trend_data.append([
                month_label,
                f"₹{trends['total_income'][i]:,}",
                f"₹{trends['total_expense'][i]:,}",
                f"₹{trends['savings'][i]:,}"
            ])
        
        if len(trend_data) > 1:
            trend_table = Table(trend_data, colWidths=[60, 80, 80, 80])
            trend_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2E7D32')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ]))
            story.append(trend_table)
        story.append(Spacer(1, 20))
        
        # ===== SAVINGS HEALTH =====
        story.append(Paragraph("🏥 Savings Health", heading_style))
        
        health_text = f"""
        <b>Emergency Fund Required:</b> ₹{savings_health.get('emergency_fund_required', 0):,}<br/>
        <b>Current Coverage:</b> {savings_health.get('emergency_months_covered', 0)} months<br/>
        <b>Status:</b> {savings_health.get('emergency_status_percent', 0)}% complete<br/>
        <b>Message:</b> {savings_health.get('message', '')}
        """
        story.append(Paragraph(health_text, normal_style))
        story.append(Spacer(1, 15))
        
        # Tips
        story.append(Paragraph("<b>💡 Tips:</b>", normal_style))
        for tip in savings_health.get('tips', []):
            story.append(Paragraph(f"• {tip}", normal_style))
        story.append(Spacer(1, 20))
        
        # ===== PROJECTION =====
        story.append(Paragraph("🎯 Month-End Projection", heading_style))
        
        proj_text = f"""
        <b>Days Remaining:</b> {prediction.get('days_remaining', 0)}<br/>
        <b>Projected Income:</b> ₹{prediction.get('projected_income', 0):,}<br/>
        <b>Projected Expense:</b> ₹{prediction.get('projected_expense', 0):,}<br/>
        <b>Projected Savings:</b> ₹{prediction.get('projected_savings', 0):,}<br/>
        <br/>
        <b>Recommendation:</b> {prediction.get('recommendation', '')}
        """
        story.append(Paragraph(proj_text, normal_style))
        story.append(Spacer(1, 30))
        
        # ===== FOOTER =====
        footer_style = ParagraphStyle(
            'Footer',
            parent=styles['Normal'],
            fontSize=9,
            textColor=colors.grey,
            alignment=1
        )
        story.append(Paragraph("━" * 50, footer_style))
        story.append(Paragraph("Generated by MoneyViya - Your Financial Friend", footer_style))
        story.append(Paragraph('"हर रुपया मायने रखता है"', footer_style))
        
        # Build PDF
        doc.build(story)
        
        return str(filepath)
    
    def generate_yearly_summary(self, user_id: str, year: int = None) -> Optional[str]:
        """Generate yearly summary PDF"""
        
        if not PDF_AVAILABLE:
            return None
        
        year = year or datetime.now().year
        
        user = user_repo.get_user(user_id)
        if not user:
            return None
        
        # Create filename
        filename = f"MoneyViya_Annual_{user_id}_{year}.pdf"
        filepath = self.reports_dir / filename
        
        # Create document
        doc = SimpleDocTemplate(
            str(filepath),
            pagesize=A4,
            rightMargin=20*mm,
            leftMargin=20*mm,
            topMargin=20*mm,
            bottomMargin=20*mm
        )
        
        # Build content
        story = []
        styles = getSampleStyleSheet()
        
        # Title
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#2E7D32'),
            spaceAfter=20,
            alignment=1
        )
        
        story.append(Paragraph("💰 MoneyViya Annual Report", title_style))
        story.append(Paragraph(f"Year {year}", styles['Heading2']))
        story.append(Paragraph(f"Prepared for: {user.get('name', 'User')}", styles['Normal']))
        story.append(Spacer(1, 20))
        
        # Monthly breakdown
        story.append(Paragraph("📊 Monthly Overview", styles['Heading2']))
        
        data = [["Month", "Income", "Expense", "Savings"]]
        total_income = 0
        total_expense = 0
        
        for month in range(1, 13):
            month_str = f"{year}-{month:02d}"
            month_name = datetime(year, month, 1).strftime("%b")
            
            summary = transaction_repo.get_monthly_summary(user_id, month_str)
            income = summary.get('total_income', 0)
            expense = summary.get('total_expense', 0)
            savings = income - expense
            
            total_income += income
            total_expense += expense
            
            data.append([
                month_name,
                f"₹{income:,}",
                f"₹{expense:,}",
                f"₹{savings:,}"
            ])
        
        # Add totals row
        data.append([
            "TOTAL",
            f"₹{total_income:,}",
            f"₹{total_expense:,}",
            f"₹{total_income - total_expense:,}"
        ])
        
        table = Table(data, colWidths=[50, 80, 80, 80])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1565C0')),
            ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#2E7D32')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('TEXTCOLOR', (0, -1), (-1, -1), colors.white),
            ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ]))
        story.append(table)
        story.append(Spacer(1, 20))
        
        # Annual summary
        story.append(Paragraph("📈 Annual Summary", styles['Heading2']))
        
        avg_monthly_income = total_income / 12
        avg_monthly_expense = total_expense / 12
        savings_rate = (total_income - total_expense) / max(total_income, 1) * 100
        
        summary_text = f"""
        <b>Total Income:</b> ₹{total_income:,}<br/>
        <b>Total Expenses:</b> ₹{total_expense:,}<br/>
        <b>Total Savings:</b> ₹{total_income - total_expense:,}<br/>
        <b>Savings Rate:</b> {savings_rate:.1f}%<br/>
        <br/>
        <b>Average Monthly Income:</b> ₹{int(avg_monthly_income):,}<br/>
        <b>Average Monthly Expense:</b> ₹{int(avg_monthly_expense):,}
        """
        story.append(Paragraph(summary_text, styles['Normal']))
        
        # Footer
        story.append(Spacer(1, 40))
        story.append(Paragraph("━" * 50, styles['Normal']))
        story.append(Paragraph("Generated by MoneyViya", styles['Normal']))
        
        # Build PDF
        doc.build(story)
        
        return str(filepath)


# Global instance
pdf_service = PDFReportService()

