import io
from datetime import datetime
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, 
    PageBreak, Image as RLImage
)
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from app.models.api_models import AnalyzePatientResponse


class PDFGenerator:
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._create_custom_styles()
    
    def _create_custom_styles(self):
        """Create custom paragraph styles"""
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
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
            fontName='Helvetica-Bold',
            borderColor=colors.HexColor('#1e40af'),
            borderWidth=2,
            borderPadding=8
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
        
        self.styles.add(ParagraphStyle(
            name='Alert',
            parent=self.styles['Normal'],
            fontSize=10,
            textColor=colors.white,
            backColor=colors.HexColor('#dc2626'),
            borderColor=colors.HexColor('#7f1d1d'),
            borderWidth=1,
            borderPadding=8,
            spaceAfter=8
        ))
    
    def generate_patient_report_pdf(self, analysis_results: AnalyzePatientResponse) -> io.BytesIO:
        """Generate comprehensive patient analysis PDF"""
        
        pdf_buffer = io.BytesIO()
        doc = SimpleDocTemplate(pdf_buffer, pagesize=letter,
                              rightMargin=0.75*inch,
                              leftMargin=0.75*inch,
                              topMargin=0.75*inch,
                              bottomMargin=0.75*inch)
        
        story = []
        
        # ===== TITLE PAGE =====
        story.append(Paragraph("MEDICATION SAFETY ANALYSIS REPORT", self.styles['Title']))
        story.append(Spacer(1, 0.2*inch))
        
        # Header info
        patient_summary = analysis_results.patient_summary
        header_data = [
            ['Patient Age:', f"{patient_summary['age']} years"],
            ['Gender:', patient_summary['gender'].title()],
            ['Frailty Status:', patient_summary['frailty_status']],
            ['Life Expectancy:', patient_summary['life_expectancy'].replace('_', ' ').title()],
            ['Report Generated:', datetime.now().strftime("%d %B %Y at %H:%M")],
        ]
        
        header_table = Table(header_data, colWidths=[2*inch, 4*inch])
        header_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f0f9ff')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ]))
        story.append(header_table)
        story.append(Spacer(1, 0.3*inch))
        
        # ===== CLINICAL PARAMETERS =====
        story.append(Paragraph("Clinical Parameters", self.styles['SectionHeading']))
        
        clinical_data = [
            ['Parameter', 'Value', 'Status'],
            ['CFS Score', str(patient_summary.get('cfs_score', 'N/A')), ''],
            ['Comorbidities', ', '.join(patient_summary.get('comorbidities', [])), ''],
            ['Total Medications', str(patient_summary['total_medications']), ''],
            ['Total Herbal Products', str(patient_summary['total_herbs']), ''],
        ]
        
        # Add calculated values if available
        if patient_summary.get('calculated_egfr'):
            clinical_data.append([
                'eGFR (Kidney Function)',
                f"{patient_summary['calculated_egfr']} mL/min/1.73m²",
                patient_summary.get('renal_function', '')
            ])
        
        if patient_summary.get('calculated_meld'):
            clinical_data.append([
                'MELD Score (Liver Function)',
                str(patient_summary['calculated_meld']),
                patient_summary.get('hepatic_function', '')
            ])
        
        clinical_table = Table(clinical_data, colWidths=[2.5*inch, 2.5*inch, 1.5*inch])
        clinical_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e40af')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f0f9ff')])
        ]))
        story.append(clinical_table)
        story.append(Spacer(1, 0.2*inch))
        
        # ===== PRIORITY SUMMARY =====
        priority = analysis_results.priority_summary
        story.append(Paragraph("Medication Risk Summary", self.styles['SectionHeading']))
        
        priority_data = [
            ['Risk Level', 'Count', 'Action Required'],
            ['🔴 HIGH RISK (RED)', str(priority['RED']), 'Review and consider deprescribing'],
            ['🟡 MODERATE RISK (YELLOW)', str(priority['YELLOW']), 'Monitor closely and review necessity'],
            ['🟢 LOW RISK (GREEN)', str(priority['GREEN']), 'Continue with routine monitoring'],
        ]
        
        priority_table = Table(priority_data, colWidths=[2*inch, 1.5*inch, 3*inch])
        priority_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e40af')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [
                colors.HexColor('#fee2e2'),  # Red
                colors.HexColor('#fef3c7'),  # Yellow
                colors.HexColor('#dcfce7')   # Green
            ])
        ]))
        story.append(priority_table)
        story.append(Spacer(1, 0.3*inch))
        
        # ===== MEDICATIONS ANALYSIS =====
        story.append(Paragraph("Detailed Medication Analysis", self.styles['SectionHeading']))
        
        for med in analysis_results.medication_analyses:
            # Medication header
            med_color = {
                'RED': colors.HexColor('#dc2626'),
                'YELLOW': colors.HexColor('#f59e0b'),
                'GREEN': colors.HexColor('#059669')
            }.get(med.risk_category.value, colors.grey)
            
            med_header = f"{'🔴' if med.risk_category.value == 'RED' else '🟡' if med.risk_category.value == 'YELLOW' else '🟢'} {med.name} | Risk Score: {med.risk_score}/100"
            story.append(Paragraph(med_header, self.styles['SubHeading']))
            
            # Medication details table
            med_details = [
                ['Category', med.type.upper()],
                ['Risk Level', f"<b>{med.risk_category.value}</b>"],
                ['Risk Score', f"{med.risk_score}/100"],
            ]
            
            if med.taper_required:
                med_details.append(['Tapering Required', '<font color="red"><b>YES</b></font>'])
            
            med_detail_table = Table(med_details, colWidths=[2*inch, 4*inch])
            med_detail_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f0f9ff')),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                ('GRID', (0, 0), (-1, -1), 1, colors.lightgrey),
            ]))
            story.append(med_detail_table)
            story.append(Spacer(1, 0.1*inch))
            
            # Flags
            if med.flags:
                story.append(Paragraph("<b>Clinical Concerns:</b>", self.styles['BodyText']))
                for flag in med.flags:
                    story.append(Paragraph(f"• {flag}", self.styles['BodyText']))
            
            # Recommendations
            if med.recommendations:
                story.append(Paragraph("<b>Recommendations:</b>", self.styles['BodyText']))
                for rec in med.recommendations:
                    story.append(Paragraph(f"• {rec}", self.styles['BodyText']))
            
            # Monitoring
            if med.monitoring_required:
                story.append(Paragraph("<b>Monitoring Required:</b>", self.styles['BodyText']))
                for monitor in med.monitoring_required:
                    story.append(Paragraph(f"• {monitor}", self.styles['BodyText']))
            
            story.append(Spacer(1, 0.15*inch))
        
        # ===== PAGE BREAK =====
        story.append(PageBreak())
        
        # ===== HERB-DRUG INTERACTIONS =====
        if analysis_results.herb_drug_interactions:
            story.append(Paragraph("Herb-Drug Interactions", self.styles['SectionHeading']))
            
            interaction_data = [
                ['Herb', 'Drug', 'Severity', 'Effect'],
            ]
            
            for interaction in analysis_results.herb_drug_interactions:
                interaction_data.append([
                    interaction.get('herb', 'N/A'),
                    interaction.get('drug', 'N/A'),
                    interaction.get('severity', 'N/A'),
                    interaction.get('effect', 'N/A')
                ])
            
            interaction_table = Table(interaction_data, colWidths=[1.5*inch, 1.5*inch, 1.5*inch, 2*inch])
            interaction_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e40af')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f0f9ff')])
            ]))
            story.append(interaction_table)
            story.append(Spacer(1, 0.3*inch))
        
        # ===== CLINICAL RECOMMENDATIONS =====
        if analysis_results.clinical_recommendations:
            story.append(Paragraph("Clinical Recommendations", self.styles['SectionHeading']))
            for rec in analysis_results.clinical_recommendations:
                story.append(Paragraph(f"• {rec}", self.styles['BodyText']))
            story.append(Spacer(1, 0.2*inch))
        
        # ===== SAFETY ALERTS =====
        if analysis_results.safety_alerts:
            story.append(Paragraph("Safety Alerts", self.styles['SectionHeading']))
            for alert in analysis_results.safety_alerts:
                story.append(Paragraph(alert, self.styles['Alert']))
            story.append(Spacer(1, 0.2*inch))
        
        # ===== START RECOMMENDATIONS =====
        if analysis_results.global_start_recommendations:
            story.append(Paragraph("Medications to Consider Adding (START Criteria)", self.styles['SectionHeading']))
            for rec in analysis_results.global_start_recommendations:
                story.append(Paragraph(f"• {rec}", self.styles['BodyText']))
            story.append(Spacer(1, 0.2*inch))
        
        # ===== MONITORING PLANS =====
        if analysis_results.monitoring_plans:
            story.append(Paragraph("Monitoring Plans", self.styles['SectionHeading']))
            for plan in analysis_results.monitoring_plans:
                story.append(Paragraph(f"<b>{plan.drug_name}</b>", self.styles['SubHeading']))
                for param in plan.parameters:
                    story.append(Paragraph(f"• {param}", self.styles['BodyText']))
        
        # ===== FOOTER =====
        story.append(Spacer(1, 0.2*inch))
        footer_text = "This report is generated by AI and should be reviewed by a qualified healthcare professional before implementation."
        story.append(Paragraph(footer_text, self.styles['Alert']))
        
        # Build PDF
        doc.build(story)
        pdf_buffer.seek(0)
        return pdf_buffer
