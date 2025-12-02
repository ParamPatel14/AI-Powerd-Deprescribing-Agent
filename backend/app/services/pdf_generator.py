# backend/app/services/pdf_generator.py

import io
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
)
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from app.models.api_models import AnalyzePatientResponse


class PDFGenerator:
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._create_custom_styles()
    
    def _create_custom_styles(self):
        """Create custom paragraph styles"""
        self.styles.add(ParagraphStyle(
            name='DumTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1e3a8a'),
            spaceAfter=30,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))
        
        self.styles.add(ParagraphStyle(
            name='SectionHeading',
            parent=self.styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#1e40af'),
            spaceAfter=12,
            spaceBefore=12,
            fontName='Helvetica-Bold'
        ))
        
        self.styles.add(ParagraphStyle(
            name='SubHeading',
            parent=self.styles['Heading3'],
            fontSize=12,
            textColor=colors.HexColor('#334155'),
            spaceAfter=8,
            fontName='Helvetica-Bold'
        ))
        
        self.styles.add(ParagraphStyle(
            name='BodyText1',
            parent=self.styles['Normal'],
            fontSize=10,
            alignment=TA_JUSTIFY,
            spaceAfter=8
        ))
        
        # ✅ RED/YELLOW medication styles
        self.styles.add(ParagraphStyle(
            name='HighRiskMed',
            parent=self.styles['Normal'],
            fontSize=11,
            textColor=colors.HexColor('#dc2626'),
            fontName='Helvetica-Bold',
            spaceAfter=6
        ))
        
        self.styles.add(ParagraphStyle(
            name='ModerateMed',
            parent=self.styles['Normal'],
            fontSize=11,
            textColor=colors.HexColor('#ea580c'),
            fontName='Helvetica-Bold',
            spaceAfter=6
        ))
        
        self.styles.add(ParagraphStyle(
            name='TaperInstruction',
            parent=self.styles['Normal'],
            fontSize=9,
            textColor=colors.HexColor('#374151'),
            leftIndent=0.2*inch,
            spaceAfter=4
        ))
    
    def generate_patient_report_pdf(self, analysis_results: AnalyzePatientResponse) -> io.BytesIO:
        """Generate comprehensive patient analysis PDF with taper plans"""
        
        pdf_buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            pdf_buffer, 
            pagesize=letter,
            rightMargin=0.75*inch,
            leftMargin=0.75*inch,
            topMargin=0.75*inch,
            bottomMargin=0.75*inch
        )
        
        story = []
        
        # Title
        story.append(Paragraph("MEDICATION SAFETY ANALYSIS REPORT", self.styles['Title']))
        story.append(Spacer(1, 0.3*inch))
        
        # Patient Summary
        patient_summary = analysis_results.patient_summary
        
        summary_data = [
            ['Patient Age:', f"{patient_summary['age']} years"],
            ['Gender:', patient_summary['gender'].title()],
            ['Frailty Status:', patient_summary['frailty_status']],
            ['Life Expectancy:', patient_summary['life_expectancy'].replace('_', ' ').title()],
            ['Total Medications:', str(patient_summary['total_medications'])],
            ['Report Generated:', datetime.now().strftime("%d %B %Y at %H:%M IST")],
        ]
        
        summary_table = Table(summary_data, colWidths=[2.5*inch, 3.5*inch])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#e0f2fe')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ]))
        story.append(summary_table)
        story.append(Spacer(1, 0.3*inch))
        
        # Risk Summary
        story.append(Paragraph("Medication Risk Summary", self.styles['SectionHeading']))
        priority = analysis_results.priority_summary
        
        risk_data = [
            ['Risk Level', 'Count'],
            ['HIGH RISK (RED)', str(priority.get('RED', 0))],
            ['MODERATE RISK (YELLOW)', str(priority.get('YELLOW', 0))],
            ['LOW RISK (GREEN)', str(priority.get('GREEN', 0))],
        ]
        
        risk_table = Table(risk_data, colWidths=[4*inch, 2*inch])
        risk_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e40af')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('BACKGROUND', (0, 1), (-1, 1), colors.HexColor('#fee2e2')),
            ('BACKGROUND', (0, 2), (-1, 2), colors.HexColor('#fef3c7')),
            ('BACKGROUND', (0, 3), (-1, 3), colors.HexColor('#dcfce7')),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        story.append(risk_table)
        story.append(Spacer(1, 0.3*inch))
        
        # ✅ MEDICATIONS WITH TAPER PLANS (RED/YELLOW first)
        story.append(Paragraph("Detailed Medication Analysis", self.styles['SectionHeading']))
        
        # Separate RED/YELLOW from GREEN
        high_risk_meds = [m for m in analysis_results.medication_analyses 
                         if m.risk_category.value in ['RED', 'YELLOW']]
        low_risk_meds = [m for m in analysis_results.medication_analyses 
                        if m.risk_category.value == 'GREEN']
        
        # Display HIGH RISK medications first (with taper plans)
        if high_risk_meds:
            story.append(Paragraph("🚨 Priority Medications Requiring Action", 
                                 self.styles['SectionHeading']))
            
            for med in high_risk_meds:
                # Medication header with color coding
                if med.risk_category.value == 'RED':
                    med_header = f"⛔ {med.name} - HIGH RISK (RED)"
                    style = self.styles['HighRiskMed']
                else:
                    med_header = f"⚠️ {med.name} - MODERATE RISK (YELLOW)"
                    style = self.styles['ModerateMed']
                
                story.append(Paragraph(med_header, style))
                story.append(Paragraph(f"<b>Risk Score:</b> {med.risk_score}/100", 
                                     self.styles['BodyText']))
                
                # Flags
                if med.flags:
                    story.append(Paragraph("<b>Concerns:</b>", self.styles['BodyText']))
                    for flag in med.flags:
                        story.append(Paragraph(f"• {flag}", self.styles['BodyText']))
                
                # Recommendations
                if med.recommendations:
                    story.append(Paragraph("<b>Recommendations:</b>", self.styles['BodyText']))
                    for rec in med.recommendations:
                        story.append(Paragraph(f"• {rec}", self.styles['BodyText']))
                
                # ✅ TAPER PLAN (if available and taper_required)
                if med.taper_required and hasattr(med, 'taper_plan') and med.taper_plan:
                    story.append(Paragraph("<b>📋 Deprescribing Plan:</b>", 
                                         self.styles['SubHeading']))
                    story.append(self._build_taper_table(med.taper_plan))
                elif med.taper_required:
                    story.append(Paragraph(
                        "<b>⚠️ REQUIRES DEPRESCRIBING:</b> Taper plan should be generated based on current dosage and medication type.",
                        self.styles['BodyText']
                    ))
                
                # Monitoring
                if med.monitoring_required:
                    story.append(Paragraph("<b>Monitoring:</b>", self.styles['BodyText']))
                    for monitor in med.monitoring_required:
                        story.append(Paragraph(f"• {monitor}", self.styles['BodyText']))
                
                story.append(Spacer(1, 0.2*inch))
            
            story.append(PageBreak())
        
        # Display LOW RISK medications
        if low_risk_meds:
            story.append(Paragraph("✅ Low Risk Medications", self.styles['SectionHeading']))
            
            for med in low_risk_meds:
                story.append(Paragraph(f"{med.name} - LOW RISK (GREEN)", 
                                     self.styles['SubHeading']))
                story.append(Paragraph(f"<b>Risk Score:</b> {med.risk_score}/100", 
                                     self.styles['BodyText']))
                
                if med.flags:
                    story.append(Paragraph("<b>Notes:</b>", self.styles['BodyText']))
                    for flag in med.flags:
                        story.append(Paragraph(f"• {flag}", self.styles['BodyText']))
                
                if med.recommendations:
                    story.append(Paragraph("<b>Recommendations:</b>", self.styles['BodyText']))
                    for rec in med.recommendations:
                        story.append(Paragraph(f"• {rec}", self.styles['BodyText']))
                
                story.append(Spacer(1, 0.15*inch))
        
        # Safety Alerts
        if analysis_results.safety_alerts:
            story.append(PageBreak())
            story.append(Paragraph("Safety Alerts", self.styles['SectionHeading']))
            for alert in analysis_results.safety_alerts:
                story.append(Paragraph(f"⚠️ {alert}", self.styles['BodyText']))
        
        # Build PDF
        doc.build(story)
        pdf_buffer.seek(0)
        return pdf_buffer
    
    # ✅ NEW METHOD: Build taper plan table
    def _build_taper_table(self, taper_plan: dict) -> Table:
        """Generate a formatted taper plan table"""
        
        # Extract taper steps
        steps = taper_plan.get('steps', [])
        
        if not steps:
            return Paragraph("No specific taper steps available.", self.styles['BodyText'])
        
        # Build table data
        table_data = [
            ['Week', 'Dose', 'Frequency', 'Instructions']
        ]
        
        for step in steps:
            week = step.get('week', '')
            dose = step.get('dose', '')
            frequency = step.get('frequency', '')
            instructions = step.get('instructions', '')
            
            table_data.append([str(week), str(dose), str(frequency), str(instructions)])
        
        # Create table
        taper_table = Table(table_data, colWidths=[1*inch, 1.2*inch, 1.2*inch, 2.1*inch])
        taper_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#fef3c7')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#92400e')),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        
        return taper_table
