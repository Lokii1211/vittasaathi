"""
PDF Report Generation Service
Generates beautiful PDF financial reports with charts
"""

import os
import io
import base64
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional

# Try to import PDF libraries
try:
    from reportlab.lib.pagesizes import A4, letter
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch, cm
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak
    from reportlab.graphics.shapes import Drawing
    from reportlab.graphics.charts.piecharts import Pie
    from reportlab.graphics.charts.barcharts import VerticalBarChart
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False
    print("Warning: reportlab not installed. PDF generation disabled.")


class PDFReportService:
    """Generates PDF financial reports"""
    
    def __init__(self):
        self.output_dir = os.path.join(os.path.dirname(__file__), "..", "data", "reports")
        os.makedirs(self.output_dir, exist_ok=True)
    
    def is_available(self) -> bool:
        """Check if PDF generation is available"""
        return REPORTLAB_AVAILABLE
    
    def generate_weekly_report(self, user: dict, transactions: List[dict], 
                               goals: List[dict] = None) -> Optional[str]:
        """Generate weekly financial report PDF"""
        if not REPORTLAB_AVAILABLE:
            return None
        
        try:
            phone = user.get("phone", "unknown").replace("+", "")
            filename = f"weekly_report_{phone}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            filepath = os.path.join(self.output_dir, filename)
            
            doc = SimpleDocTemplate(filepath, pagesize=A4,
                                   rightMargin=50, leftMargin=50,
                                   topMargin=50, bottomMargin=50)
            
            story = []
            styles = getSampleStyleSheet()
            
            # Custom styles
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=24,
                textColor=colors.HexColor('#4F46E5'),
                spaceAfter=20,
                alignment=1  # Center
            )
            
            subtitle_style = ParagraphStyle(
                'CustomSubtitle',
                parent=styles['Normal'],
                fontSize=12,
                textColor=colors.grey,
                spaceAfter=30,
                alignment=1
            )
            
            heading_style = ParagraphStyle(
                'CustomHeading',
                parent=styles['Heading2'],
                fontSize=16,
                textColor=colors.HexColor('#1E293B'),
                spaceBefore=20,
                spaceAfter=10
            )
            
            # Title
            story.append(Paragraph("📊 MoneyViya", title_style))
            story.append(Paragraph(f"Weekly Financial Report", subtitle_style))
            story.append(Paragraph(f"Generated: {datetime.now().strftime('%d %B %Y')}", subtitle_style))
            story.append(Spacer(1, 20))
            
            # User Info
            name = user.get("name", "User")
            income = user.get("monthly_income", 0)
            
            story.append(Paragraph(f"👋 Hello, {name}!", heading_style))
            story.append(Spacer(1, 10))
            
            # Calculate totals
            total_income = sum(t.get("amount", 0) for t in transactions if t.get("type") == "income")
            total_expense = sum(t.get("amount", 0) for t in transactions if t.get("type") == "expense")
            balance = total_income - total_expense
            
            # Summary Table
            summary_data = [
                ["Metric", "Amount"],
                ["💰 Total Income", f"₹{total_income:,}"],
                ["💸 Total Expenses", f"₹{total_expense:,}"],
                ["📈 Net Balance", f"₹{balance:,}"],
                ["📊 Monthly Budget", f"₹{income:,}"],
            ]
            
            summary_table = Table(summary_data, colWidths=[250, 150])
            summary_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4F46E5')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('TOPPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#F8FAFC')),
                ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#E2E8F0')),
                ('FONTSIZE', (0, 1), (-1, -1), 11),
                ('TOPPADDING', (0, 1), (-1, -1), 8),
                ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
            ]))
            
            story.append(summary_table)
            story.append(Spacer(1, 30))
            
            # Expense Breakdown by Category
            story.append(Paragraph("📂 Expenses by Category", heading_style))
            
            # Group expenses by category
            category_totals = {}
            for t in transactions:
                if t.get("type") == "expense":
                    cat = t.get("category", "Other")
                    category_totals[cat] = category_totals.get(cat, 0) + t.get("amount", 0)
            
            if category_totals:
                cat_data = [["Category", "Amount", "% of Total"]]
                for cat, amount in sorted(category_totals.items(), key=lambda x: x[1], reverse=True):
                    pct = (amount / total_expense * 100) if total_expense > 0 else 0
                    cat_data.append([cat.title(), f"₹{amount:,}", f"{pct:.1f}%"])
                
                cat_table = Table(cat_data, colWidths=[200, 100, 100])
                cat_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#10B981')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#E2E8F0')),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                    ('TOPPADDING', (0, 0), (-1, -1), 8),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                ]))
                story.append(cat_table)
            
            story.append(Spacer(1, 30))
            
            # Recent Transactions
            story.append(Paragraph("📝 Recent Transactions", heading_style))
            
            if transactions:
                trans_data = [["Date", "Type", "Category", "Amount"]]
                for t in transactions[:15]:  # Last 15 transactions
                    date = t.get("date", t.get("timestamp", ""))[:10]
                    ttype = "Income" if t.get("type") == "income" else "Expense"
                    cat = t.get("category", "Other").title()
                    amount = t.get("amount", 0)
                    sign = "+" if t.get("type") == "income" else "-"
                    trans_data.append([date, ttype, cat, f"{sign}₹{amount:,}"])
                
                trans_table = Table(trans_data, colWidths=[80, 80, 120, 100])
                trans_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#F59E0B')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, -1), 9),
                    ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#E2E8F0')),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                    ('TOPPADDING', (0, 0), (-1, -1), 6),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ]))
                story.append(trans_table)
            else:
                story.append(Paragraph("No transactions this week.", styles['Normal']))
            
            story.append(Spacer(1, 30))
            
            # Tips Section
            story.append(Paragraph("💡 Financial Tips", heading_style))
            
            tips = []
            if total_expense > income * 0.8:
                tips.append("⚠️ Your expenses are high! Try to reduce spending.")
            if balance > 0:
                tips.append("✅ Great job! You saved money this week.")
            if category_totals.get("food", 0) > total_expense * 0.4:
                tips.append("🍔 Food expenses are high. Consider cooking at home.")
            
            if not tips:
                tips.append("📈 Keep tracking your expenses for better insights!")
            
            for tip in tips:
                story.append(Paragraph(tip, styles['Normal']))
                story.append(Spacer(1, 5))
            
            # Footer
            story.append(Spacer(1, 40))
            footer_style = ParagraphStyle(
                'Footer',
                parent=styles['Normal'],
                fontSize=10,
                textColor=colors.grey,
                alignment=1
            )
            story.append(Paragraph("Generated by MoneyViya - Your Personal Financial Advisor", footer_style))
            story.append(Paragraph("www.MoneyViya.com", footer_style))
            
            # Build PDF
            doc.build(story)
            
            print(f"PDF Report generated: {filepath}")
            return filepath
            
        except Exception as e:
            print(f"PDF generation error: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def generate_monthly_report(self, user: dict, transactions: List[dict],
                                goals: List[dict] = None) -> Optional[str]:
        """Generate monthly financial report PDF"""
        # Similar to weekly but with monthly data
        return self.generate_weekly_report(user, transactions, goals)


# Singleton instance
pdf_report_service = PDFReportService()

