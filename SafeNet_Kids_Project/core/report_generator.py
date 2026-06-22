import os
import logging
from datetime import datetime, timedelta
import matplotlib
matplotlib.use('Agg') # Headless-safe for background services
import matplotlib.pyplot as plt
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

class ReportGenerator:
    """
    Handles aggregation of threat data and generation of PDF reports.
    """

    def __init__(self, log_path="data/safenet_audit.log", output_dir="data/reports"):
        self.log_path = log_path
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)
        os.makedirs("data/temp", exist_ok=True)

    def generate_report(self, days=1, report_type="Daily"):
        """Generates a PDF report for the specified time window."""
        start_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
        end_date = datetime.now().strftime("%Y-%m-%d")
        
        data = self._aggregate_data(days)
        if not data["threats"]:
            logging.info(f"ReportGenerator: No data for {report_type} report.")
            return None

        filename = f"{report_type}_Report_{end_date}.pdf"
        filepath = os.path.join(self.output_dir, filename)
        
        # 1. Generate Graphs
        chart_path = self._generate_charts(data, report_type)
        
        # 2. Build PDF
        doc = SimpleDocTemplate(filepath, pagesize=letter)
        styles = getSampleStyleSheet()
        story = []

        # Title
        story.append(Paragraph(f"SafeNet Kids - {report_type} Safety Report", styles['Title']))
        story.append(Paragraph(f"Period: {start_date} to {end_date}", styles['Normal']))
        story.append(Spacer(1, 12))

        # Executive Summary
        story.append(Paragraph("Executive Summary", styles['Heading2']))
        story.append(Paragraph(f"Total Threats Detected: {len(data['threats'])}", styles['Normal']))
        story.append(Paragraph(f"Highest Risk Category: {data['top_category']}", styles['Normal']))
        story.append(Spacer(1, 12))

        # Charts
        if chart_path:
            img = Image(chart_path, width=400, height=300)
            story.append(img)
            story.append(Spacer(1, 12))

        # Threat Table
        story.append(Paragraph("Detailed Breakdown", styles['Heading2']))
        table_data = [["Time", "Category", "Trigger", "Source"]]
        for t in data["threats"][:20]: # Limit to top 20 for PDF readability
            table_data.append([t['time'], t['category'], t['trigger'], t['source'][:30]])
        
        t = Table(table_data, colWidths=[80, 100, 100, 150])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(t)

        doc.build(story)
        logging.info(f"ReportGenerator: PDF generated at {filepath}")
        return filepath

    def _aggregate_data(self, days):
        """Parses logs to extract statistics for the timeframe."""
        threats = []
        categories = {}
        
        target_dates = [(datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d") for i in range(days + 1)]
        
        if os.path.exists(self.log_path):
            with open(self.log_path, "r", encoding="utf-8") as f:
                for line in f:
                    if any(date in line for date in target_dates) and "Threat:" in line:
                        # [2026-06-18 20:00:00] Threat: Restricted Activity (Adult), Trigger: porn, Detail: Keyboard...
                        try:
                            time_str = line.split("]")[0][1:]
                            threat_part = line.split("Threat:")[1]
                            category = threat_part.split(",")[0].strip()
                            trigger = line.split("Trigger:")[1].split(",")[0].strip().replace("'", "")
                            source = line.split("Source:")[1].strip().replace("'", "")
                            
                            threats.append({
                                "time": time_str.split(" ")[1],
                                "category": category,
                                "trigger": trigger,
                                "source": source
                            })
                            categories[category] = categories.get(category, 0) + 1
                        except:
                            continue

        top_cat = max(categories, key=categories.get) if categories else "None"
        return {"threats": threats, "categories": categories, "top_category": top_cat}

    def _generate_charts(self, data, report_type):
        """Creates a visualization of threat categories."""
        if not data["categories"]:
            return None
            
        labels = list(data["categories"].keys())
        values = list(data["categories"].values())
        
        plt.figure(figsize=(6, 4))
        plt.pie(values, labels=labels, autopct='%1.1f%%', startangle=140, colors=plt.cm.Paired.colors)
        plt.title(f"Threat Distribution - {report_type}")
        
        temp_path = f"data/temp/{report_type}_chart.png"
        plt.savefig(temp_path)
        plt.clf()
        plt.close('all')
        return temp_path
