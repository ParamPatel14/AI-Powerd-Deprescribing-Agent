from datetime import datetime
import os
from fastapi import FastAPI, HTTPException, UploadFile, File, logger
from fastapi.middleware.cors import CORSMiddleware
from typing import List

from fastapi.responses import FileResponse, StreamingResponse
from app.models.patient import PatientInput
from app.models.api_models import *
from app.services.acb_engine import ACBEngine
from app.services.beers_engine import BeersEngine
from app.services.stopp_engine import STOPPEngine
from app.services.tapering_engine import TaperingEngine
from app.services.frailty_risk_engine import FrailtyRiskEngine
from app.services.gender_risk_engine import GenderRiskEngine
from app.services.time_to_benefit_engine import TimeToBenefitEngine
from app.services.ayurvedic_interaction_engine import AyurvedicInteractionEngine
from app.services.priority_classifier import PriorityClassifier
from app.services.analysis_service import AnalysisService
from app.services.taper_plan_service import TaperPlanService
from app.utils.data_loader import *
from app.services.taper_plan_service import TaperPlanService
from app.utils.data_loader import load_stopp_start_v2
from app.services.prescription_parser import PrescriptionParser
from app.services.pdf_generator import PDFGenerator

# Initialize PDF generator
pdf_generator = PDFGenerator()
import logging

app_logger = logging.getLogger("DocathonMain")
app_logger.setLevel(logging.INFO)


from dotenv import load_dotenv
load_dotenv()
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
prescription_parser = PrescriptionParser(gemini_api_key=GEMINI_API_KEY)

app = FastAPI(
    title="Deprescribing Clinical Decision Support System",
    description="Complete API for medication deprescribing and safety analysis",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ========== STARTUP: Load Data & Initialize Engines ==========
print("🚀 Starting Deprescribing Engine API...")
print("📁 Loading datasets...")


acb_data = load_acb_data()
beers_data = load_beers_data()
stopp_data = load_stopp_data()
tapering_data = load_tapering_data()
cfs_data = load_cfs_map()
gender_risk_data = load_gender_risk_data()
ttb_data = load_ttb_data()
ayurvedic_interactions_data = load_ayurvedic_known_interactions()
ayurvedic_profiles_data = load_ayurvedic_pharmacological_profiles()
ayurvedic_summary_data = load_ayurvedic_herbs_summary()
stopp_v2_df, start_v2_df = load_stopp_start_v2()

print("✅ All datasets loaded!")
print("⚙️  Initializing engines...")

# Initialize all engines
engines = {
    'acb': ACBEngine(acb_data),
    'beers': BeersEngine(beers_data),
    'stopp': STOPPEngine(stopp_v2_df, start_v2_df),
    'tapering': TaperingEngine(tapering_data, cfs_data),
    'frailty': FrailtyRiskEngine(cfs_data),
    'gender': GenderRiskEngine(gender_risk_data),
    'ttb': TimeToBenefitEngine(ttb_data),
    'ayurvedic': AyurvedicInteractionEngine(
        ayurvedic_interactions_data,
        ayurvedic_profiles_data,
        ayurvedic_summary_data
    )
}


# Initialize services
taper_service = TaperPlanService(
    tapering_data, 
    cfs_data,
    gemini_api_key=GEMINI_API_KEY  # Pass API key
)
engines['taper_service'] = taper_service
analysis_service = AnalysisService(engines)
priority_classifier = PriorityClassifier()

print("✅ All engines initialized!")
print("🎉 API ready to serve requests!\n")
# After initializing taper_service
print("\n" + "="*60)
print("TAPER SERVICE DEBUG INFO:")
print(f"  Gemini enabled: {taper_service.use_gemini}")
print(f"  Gemini service: {taper_service.gemini_service}")
if taper_service.use_gemini and taper_service.gemini_service:
    print("  ✅ Taper service WILL use Gemini for unknown drugs")
else:
    print("  ⚠️  Taper service will NOT use Gemini")
print("="*60 + "\n")
api_key = os.getenv("GEMINI_API_KEY")
if api_key:
    app_logger.warning(f"Using Gemini API Key (first 8 chars): {api_key}")
else:
    app_logger.error("❌ GEMINI_API_KEY is missing from environment")


# ========== ENDPOINT 1: /analyze-patient ==========
@app.post("/analyze-patient", response_model=AnalyzePatientResponse, tags=["Analysis"])
async def analyze_patient(request: AnalyzePatientRequest):
    """
    **Comprehensive Patient Analysis**
    
    Analyzes all patient medications and herbal products through 9 clinical modules:
    - Module 1: ACB Score (Anticholinergic Burden)
    - Module 2: Beers Criteria
    - Module 3: STOPP/START
    - Module 4: Tapering Plans
    - Module 5: Frailty Risk Assessment
    - Module 6: Gender-Specific Risks
    - Module 7: Time-to-Benefit Analysis
    - Module 8: Ayurvedic-Allopathic Interactions
    - Module 9: Priority Classification (RED/YELLOW/GREEN)
    
    Returns:
    - Complete risk assessment for each medication
    - Tapering schedules
    - Monitoring plans
    - Clinical recommendations
    - Safety alerts
    """
    try:
        result = analysis_service.analyze_patient_comprehensive(request.patient)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis error: {str(e)}")

# ========== ENDPOINT 2: /get-taper-plan ==========
@app.post("/get-taper-plan", response_model=TaperPlanResponse, tags=["Tapering"])
async def get_taper_plan(request: TaperPlanRequest):
    """
    **Get Detailed Taper Plan**
    
    Returns a comprehensive tapering schedule for a specific medication including:
    - Week-by-week dosing schedule
    - Withdrawal symptom monitoring
    - Pause and reversal criteria
    - Patient education materials
    - Frailty-adjusted timing
    
    Supports:
    - Benzodiazepines (Ashton protocol)
    - SSRIs/SNRIs (Hyperbolic tapering)
    - PPIs, Z-drugs, and more
    """
    try:
        result = taper_service.get_taper_plan(request)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Taper plan error: {str(e)}")

# ========== ENDPOINT 3: /interaction-checker ==========
@app.post("/interaction-checker", response_model=InteractionCheckResponse, tags=["Interactions"])
async def check_interactions(request: InteractionCheckRequest):
    """
    **Herb-Drug Interaction Checker**
    
    Checks for interactions between Ayurvedic/herbal products and allopathic medications.
    
    Features:
    - Evidence-based interactions (from clinical literature)
    - AI-simulated interactions (for undocumented combinations)
    - Severity classification (Major/Moderate/Minor)
    - Mechanism explanations
    - Clinical recommendations
    
    Returns detailed interaction analysis with monitoring guidance.
    """
    try:
        # Convert string lists to product objects
        from app.models.patient import HerbalProduct, Medication, DurationCategory
        
        herbs = [
            HerbalProduct(generic_name=h, dose="", frequency="", duration=DurationCategory.UNKNOWN)
            for h in request.herbs
        ]
        
        meds = [
            Medication(generic_name=m, dose="", frequency="", duration=DurationCategory.UNKNOWN)
            for m in request.medications
        ]
        
        # Create minimal patient for context
        from app.models.patient import PatientInput, Gender, LifeExpectancyCategory
        patient = PatientInput(
            age=65,
            gender=Gender.OTHER,
            is_frail=False,
            life_expectancy=LifeExpectancyCategory.MORE_THAN_TEN_YEARS,
            comorbidities=request.patient_comorbidities,
            medications=meds,
            herbs=herbs
        )
        
        # Check interactions
        known = engines['ayurvedic'].check_known_interactions(herbs, meds)
        simulated = engines['ayurvedic'].simulate_unknown_interactions(herbs, meds, patient)
        all_interactions = known + simulated
        
        # Build response
        interaction_details = [
            InteractionDetail(
                herb_name=i.herb_name,
                drug_name=i.drug_name,
                interaction_type=i.interaction_type,
                severity=i.severity,
                mechanism=i.mechanism,
                clinical_effect=i.clinical_effect,
                evidence_strength=i.evidence_strength,
                recommendation=i.recommendation,
                monitoring_required=[i.clinical_effect]
            )
            for i in all_interactions
        ]
        
        major_count = sum(1 for i in all_interactions if i.severity == "Major")
        moderate_count = sum(1 for i in all_interactions if i.severity == "Moderate")
        minor_count = len(all_interactions) - major_count - moderate_count
        
        # Overall assessment
        if major_count > 0:
            overall = "HIGH RISK: Major interactions detected. Avoid these combinations."
        elif moderate_count > 0:
            overall = "MODERATE RISK: Close monitoring required."
        elif all_interactions:
            overall = "LOW RISK: Minor interactions possible. Monitor as indicated."
        else:
            overall = "NO INTERACTIONS: No documented or predicted interactions found."
        
        # Recommendations
        recommendations = []
        if major_count > 0:
            recommendations.append("URGENT: Discontinue herb or adjust medication immediately")
            recommendations.append("Consult prescribing physician before continuing")
        if moderate_count > 0:
            recommendations.append("Implement enhanced monitoring protocols")
            recommendations.append("Consider timing separation or dose adjustment")
        if not all_interactions:
            recommendations.append("No interactions found, but continue general monitoring")
        
        return InteractionCheckResponse(
            total_interactions=len(all_interactions),
            major_interactions=major_count,
            moderate_interactions=moderate_count,
            minor_interactions=minor_count,
            interactions=interaction_details,
            overall_risk_assessment=overall,
            recommendations=recommendations
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Interaction check error: {str(e)}")

# ========== ADDITIONAL UTILITY ENDPOINTS ==========
@app.post("/extract-from-prescription", tags=["Medication Extraction"])
async def extract_from_prescription(file: UploadFile = File(...)):
    """
    Extract medications from uploaded prescription (PDF or image).
    Supports: PDF, JPG, PNG
    """
    try:
        contents = await file.read()
        
        if file.filename.endswith('.pdf'):
            medications = prescription_parser.extract_from_pdf(contents)
        elif file.filename.lower().endswith(('.jpg', '.jpeg', '.png')):
            medications = prescription_parser.extract_from_image(contents)
        else:
            raise HTTPException(status_code=400, detail="Unsupported file type")
        
        return {
            "success": True,
            "medications": medications,
            "count": len(medications)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/extract-brown-bag", tags=["Medication Extraction"])
async def extract_brown_bag(file: UploadFile = File(...)):
    """Extract medications from brown bag review photo."""
    try:
        print(f"📸 Received file: {file.filename}, type: {file.content_type}")
        
        contents = await file.read()
        print(f"📦 File size: {len(contents)} bytes")
        
        medications = prescription_parser.extract_from_brown_bag(contents)
        print(f"✅ Extracted {len(medications)} medications")
        
        return {
            "success": True,
            "medications": medications,
            "count": len(medications)
        }
    except Exception as e:
        # ✅ Print full error to console
        import traceback
        print("❌ ERROR in extract_brown_bag:")
        print(traceback.format_exc())
        
        raise HTTPException(
            status_code=500, 
            detail=f"Extraction error: {str(e)}"
        )

@app.post("/generate-report-pdf", tags=["Reports"])
async def generate_report_pdf(results: AnalyzePatientResponse):
    """
    Generate professional clinical PDF report from analysis results.
    Returns formatted PDF with tables, sections, and clinical formatting.
    """
    try:
        # Generate PDF buffer
        pdf_buffer = pdf_generator.generate_patient_report_pdf(results)
        
        # Return as streaming response
        return StreamingResponse(
            pdf_buffer,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename=Clinical_Report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            }
        )
    except Exception as e:
        import traceback
        print("❌ PDF Generation Error:")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"PDF generation failed: {str(e)}")


@app.get("/", tags=["System"])
async def root():
    """API Root - System Information"""
    return {
        "system": "Deprescribing Clinical Decision Support API",
        "version": "1.0.0",
        "status": "operational",
        "modules": 9,
        "endpoints": {
            "POST /analyze-patient": "Comprehensive patient medication analysis",
            "POST /get-taper-plan": "Detailed tapering schedule for specific drug",
            "POST /interaction-checker": "Herb-drug interaction checker",
            "GET /health": "System health check",
            "GET /supported-drugs": "List of drugs in database",
            "GET /docs": "Interactive API documentation"
        }
    }

@app.get("/health", tags=["System"])
async def health_check():
    """System Health Check"""
    return {
        "status": "healthy",
        "modules_loaded": 9,
        "datasets": {
            "acb": len(acb_data),
            "beers": len(beers_data),
            "stopp": len(stopp_data),
            "tapering": len(tapering_data),
            "ayurvedic_interactions": len(ayurvedic_interactions_data),
            "ayurvedic_herbs": len(ayurvedic_summary_data)
        }
    }

@app.get("/supported-drugs", tags=["Reference"])
async def get_supported_drugs():
    """Get list of drugs with tapering protocols"""
    drugs = tapering_data[['drug_name', 'drug_class', 'risk_profile']].to_dict('records')
    return {
        "total_drugs": len(drugs),
        "drugs": drugs
    }

@app.get("/supported-herbs", tags=["Reference"])
async def get_supported_herbs():
    """Get list of supported Ayurvedic herbs"""
    herbs = ayurvedic_summary_data[['Herb Name', 'Primary Indications', 'Key Safety Concerns']].to_dict('records')
    return {
        "total_herbs": len(herbs),
        "herbs": herbs
    }

# ========== ERROR HANDLERS ==========
@app.exception_handler(404)
async def not_found_handler(request, exc):
    return {
        "error": "Endpoint not found",
        "message": "Please refer to /docs for available endpoints"
    }

@app.exception_handler(500)
async def internal_error_handler(request, exc):
    return {
        "error": "Internal server error",
        "message": "Please contact system administrator",
        "details": str(exc)
    }

# ========== RUN SERVER ==========
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
