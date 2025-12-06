import React, { useState, useEffect } from "react";
import axios from 'axios';
import {
  FaExclamationTriangle,
  FaExclamationCircle,
  FaCheckCircle,
  FaEye,
  FaCalendarAlt,
  FaFlask,
  FaRobot,
  FaChartPie,
  FaShieldAlt,
  FaFileDownload,
  FaHeart,
  FaLightbulb,
  FaArrowRight,
} from "react-icons/fa";

import jsPDF from "jspdf";
import html2canvas from "html2canvas";

import TaperModal from "./TaperModal";
import InteractionModal from "./InteractionModal";
import MonitoringModal from "./MonitoringModal";

const ResultsDashboard = ({ results, patientData }) => {
  const [selectedMedication, setSelectedMedication] = useState(null);
  const [showTaperModal, setShowTaperModal] = useState(false);
  const [showMonitoringModal, setShowMonitoringModal] = useState(false);
  const [showInteractionModal, setShowInteractionModal] = useState(false);
  const [selectedInteraction, setSelectedInteraction] = useState(null);
  const [isPdfGenerating, setIsPdfGenerating] = useState(false);
  const [animatedCounts, setAnimatedCounts] = useState({ red: 0, yellow: 0, green: 0 });

  useEffect(() => {
    if (results?.priority_summary) {
      const targetRed = results.priority_summary.RED || 0;
      const targetYellow = results.priority_summary.YELLOW || 0;
      const targetGreen = results.priority_summary.GREEN || 0;
      
      let currentRed = 0, currentYellow = 0, currentGreen = 0;
      const interval = setInterval(() => {
        if (currentRed < targetRed) currentRed++;
        if (currentYellow < targetYellow) currentYellow++;
        if (currentGreen < targetGreen) currentGreen++;
        
        setAnimatedCounts({ red: currentRed, yellow: currentYellow, green: currentGreen });
        
        if (currentRed >= targetRed && currentYellow >= targetYellow && currentGreen >= targetGreen) {
          clearInterval(interval);
        }
      }, 100);
      
      return () => clearInterval(interval);
    }
  }, [results]);
  
  if (!results) return null;

  const generateProfessionalPDF = async () => {
    setIsPdfGenerating(true);
    try {
      console.log('Generating professional clinical PDF...');
      
      const response = await axios.post(
        'http://localhost:8000/generate-report-pdf',
        results,
        {
          responseType: 'blob',
          headers: { 'Content-Type': 'application/json' }
        }
      );

      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      const timestamp = new Date().toISOString().slice(0, 10);
      link.setAttribute('download', `Clinical_Deprescribing_Report_${timestamp}.pdf`);
      document.body.appendChild(link);
      link.click();
      link.parentNode.removeChild(link);
      window.URL.revokeObjectURL(url);

      console.log('Professional PDF downloaded successfully');
    } catch (error) {
      console.error('Error generating professional PDF:', error);
    } finally {
      setIsPdfGenerating(false);
    }
  };

  const {
    medication_analyses,
    priority_summary,
    herb_drug_interactions,
    clinical_recommendations,
    safety_alerts,
    global_start_recommendations,
  } = results;

  const redMedications =
    medication_analyses?.filter((m) => m.risk_category === "RED") || [];
  const yellowMedications =
    medication_analyses?.filter((m) => m.risk_category === "YELLOW") || [];
  const greenMedications =
    medication_analyses?.filter((m) => m.risk_category === "GREEN") || [];

  const handleViewTaper = (m) => {
    setSelectedMedication(m);
    setShowTaperModal(true);
  };

  const handleViewMonitoring = (m) => {
    setSelectedMedication(m);
    setShowMonitoringModal(true);
  };

  const handleViewInteraction = (i) => {
    setSelectedInteraction(i);
    setShowInteractionModal(true);
  };

  const handleExportPDF = async () => {
    const input = document.getElementById("results-pdf-container");
    const canvas = await html2canvas(input, { scale: 2 });
    const imgData = canvas.toDataURL("image/png");
    const pdf = new jsPDF("p", "mm", "a4");
    const imgWidth = 210;
    const imgHeight = (canvas.height * imgWidth) / canvas.width;
    pdf.addImage(imgData, "PNG", 0, 0, imgWidth, imgHeight);
    pdf.save(`Deprescribing_Report.pdf`);
  };

  return (
    <div className="animate-fade-in-up">
      <div className="flex flex-wrap gap-3 justify-end mb-6 no-print">
        <button
          onClick={generateProfessionalPDF}
          disabled={isPdfGenerating}
          className={`px-5 py-2.5 rounded-xl shadow-lg transition-all duration-300 flex items-center gap-2 font-medium ${
            isPdfGenerating
              ? 'bg-gray-300 cursor-not-allowed text-gray-500'
              : 'bg-gradient-to-r from-indigo-600 to-purple-600 text-white hover:from-indigo-700 hover:to-purple-700 hover:shadow-xl hover:scale-105'
          }`}
        >
          <FaRobot className={isPdfGenerating ? 'animate-spin' : ''} />
          {isPdfGenerating ? 'Generating...' : 'Download Clinical Report'}
        </button>

        <button
          onClick={handleExportPDF}
          className="px-5 py-2.5 bg-gray-600 text-white rounded-xl shadow-lg 
                   hover:bg-gray-700 transition-all duration-300 flex items-center gap-2 font-medium
                   hover:shadow-xl hover:scale-105"
        >
          <FaFileDownload />
          Quick Screenshot
        </button>
      </div>

      <div id="results-pdf-container" className="space-y-6">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
          <SummaryCard
            title="HIGH PRIORITY"
            count={animatedCounts.red}
            color="red"
            icon={<FaExclamationTriangle />}
            description="Medications requiring immediate attention"
          />

          <SummaryCard
            title="REVIEW NEEDED"
            count={animatedCounts.yellow}
            color="yellow"
            icon={<FaExclamationCircle />}
            description="Clinical assessment recommended"
          />

          <SummaryCard
            title="SAFE TO CONTINUE"
            count={animatedCounts.green}
            color="green"
            icon={<FaCheckCircle />}
            description="Continue with routine monitoring"
          />
        </div>

        {results.patient_summary?.calculated_egfr && (
          <div className="card-medical p-6 animate-fade-in stagger-1">
            <div className="flex items-center gap-3 mb-4">
              <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-xl 
                            flex items-center justify-center shadow-md">
                <FaChartPie className="text-white" />
              </div>
              <h3 className="text-xl font-bold text-gray-800">
                Calculated Organ Function
              </h3>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="bg-gradient-to-br from-blue-50 to-indigo-50 p-5 rounded-xl border border-blue-100">
                <div className="flex items-center gap-2 mb-2">
                  <FaHeart className="text-blue-600" />
                  <p className="text-sm font-medium text-gray-600">Kidney Function (eGFR)</p>
                </div>
                <p className="text-3xl font-bold text-blue-700">
                  {results.patient_summary.calculated_egfr}
                  <span className="text-sm font-normal text-gray-500 ml-1">mL/min/1.73m2</span>
                </p>
                <p className="text-sm text-gray-600 mt-2 bg-white/50 px-3 py-1 rounded-lg inline-block">
                  {results.patient_summary.renal_function}
                </p>
              </div>
              
              {results.patient_summary.calculated_meld && (
                <div className="bg-gradient-to-br from-amber-50 to-orange-50 p-5 rounded-xl border border-amber-100">
                  <div className="flex items-center gap-2 mb-2">
                    <FaFlask className="text-amber-600" />
                    <p className="text-sm font-medium text-gray-600">Liver Function (MELD)</p>
                  </div>
                  <p className="text-3xl font-bold text-amber-700">
                    {results.patient_summary.calculated_meld}
                  </p>
                  <p className="text-sm text-gray-600 mt-2 bg-white/50 px-3 py-1 rounded-lg inline-block">
                    {results.patient_summary.hepatic_function}
                  </p>
                </div>
              )}
            </div>
          </div>
        )}

        {safety_alerts?.length > 0 && (
          <AlertBlock
            icon={<FaExclamationTriangle />}
            title="Safety Alerts"
            color="red"
            items={safety_alerts}
          />
        )}

        {clinical_recommendations?.length > 0 && (
          <AlertBlock
            icon={<FaLightbulb />}
            title="Clinical Recommendations"
            color="blue"
            items={clinical_recommendations}
          />
        )}

        {global_start_recommendations?.length > 0 && (
          <AlertBlock
            icon={<FaCheckCircle />}
            title="Medications to Consider Starting (START v2)"
            color="green"
            items={global_start_recommendations}
          />
        )}

        {herb_drug_interactions?.length > 0 && (
          <HerbDrugInteractionsSection
            herb_drug_interactions={herb_drug_interactions}
            handleViewInteraction={handleViewInteraction}
          />
        )}

        <MedListSection
          title="HIGH PRIORITY - Deprescribe Now"
          emoji="🔴"
          meds={redMedications}
          color="red"
          handleViewTaper={handleViewTaper}
          handleViewMonitoring={handleViewMonitoring}
        />

        <MedListSection
          title="REVIEW REQUIRED - Clinical Assessment Needed"
          emoji="🟡"
          meds={yellowMedications}
          color="yellow"
          handleViewTaper={handleViewTaper}
          handleViewMonitoring={handleViewMonitoring}
        />

        <MedListSection
          title="SAFE TO CONTINUE"
          emoji="🟢"
          meds={greenMedications}
          color="green"
          handleViewTaper={handleViewTaper}
          handleViewMonitoring={handleViewMonitoring}
        />

        {showTaperModal && selectedMedication && (
          <TaperModal
            medication={selectedMedication}
            patientData={patientData}
            onClose={() => setShowTaperModal(false)}
          />
        )}

        {showMonitoringModal && selectedMedication && (
          <MonitoringModal
            medication={selectedMedication}
            onClose={() => setShowMonitoringModal(false)}
          />
        )}

        {showInteractionModal && selectedInteraction && (
          <InteractionModal
            interaction={selectedInteraction}
            onClose={() => setShowInteractionModal(false)}
          />
        )}
      </div>
    </div>
  );
};

const SummaryCard = ({ title, count, color, icon, description }) => {
  const colorClasses = {
    red: {
      bg: 'from-red-500 to-rose-600',
      light: 'from-red-50 to-rose-50',
      text: 'text-red-600',
      border: 'border-red-200',
      glow: 'shadow-glow-red',
    },
    yellow: {
      bg: 'from-amber-400 to-orange-500',
      light: 'from-amber-50 to-orange-50',
      text: 'text-amber-600',
      border: 'border-amber-200',
      glow: 'shadow-glow-yellow',
    },
    green: {
      bg: 'from-emerald-500 to-green-600',
      light: 'from-green-50 to-emerald-50',
      text: 'text-emerald-600',
      border: 'border-green-200',
      glow: 'shadow-glow-green',
    },
  };

  const classes = colorClasses[color];

  return (
    <div className={`card-medical overflow-hidden hover:${classes.glow} transition-all duration-300 animate-scale-in`}>
      <div className={`h-2 bg-gradient-to-r ${classes.bg}`}></div>
      <div className="p-6">
        <div className="flex items-start justify-between">
          <div>
            <p className="text-sm font-semibold text-gray-500 uppercase tracking-wide mb-1">
              {title}
            </p>
            <p className={`text-5xl font-bold ${classes.text} number-counter`}>
              {count}
            </p>
            <p className="text-xs text-gray-400 mt-2">{description}</p>
          </div>
          <div className={`w-14 h-14 bg-gradient-to-br ${classes.light} rounded-2xl 
                        flex items-center justify-center border ${classes.border}`}>
            <span className={`text-2xl ${classes.text}`}>{icon}</span>
          </div>
        </div>
      </div>
    </div>
  );
};

const AlertBlock = ({ icon, title, color, items }) => {
  const colorClasses = {
    red: {
      bg: 'from-red-50 to-rose-50',
      border: 'border-red-400',
      icon: 'from-red-500 to-rose-600',
      title: 'text-red-800',
      text: 'text-red-700',
      item: 'bg-white border-red-100',
    },
    blue: {
      bg: 'from-blue-50 to-indigo-50',
      border: 'border-blue-400',
      icon: 'from-blue-500 to-indigo-600',
      title: 'text-blue-800',
      text: 'text-blue-700',
      item: 'bg-white border-blue-100',
    },
    green: {
      bg: 'from-green-50 to-emerald-50',
      border: 'border-green-400',
      icon: 'from-green-500 to-emerald-600',
      title: 'text-green-800',
      text: 'text-green-700',
      item: 'bg-white border-green-100',
    },
  };

  const classes = colorClasses[color];

  return (
    <div className={`bg-gradient-to-r ${classes.bg} p-6 rounded-2xl shadow-lg 
                   border-l-4 ${classes.border} animate-fade-in-up`}>
      <div className="flex items-center gap-3 mb-4">
        <div className={`w-10 h-10 bg-gradient-to-br ${classes.icon} rounded-xl 
                       flex items-center justify-center shadow-md`}>
          <span className="text-white text-lg">{icon}</span>
        </div>
        <h3 className={`text-xl font-bold ${classes.title}`}>{title}</h3>
        <span className={`ml-auto px-3 py-1 ${classes.item} rounded-full text-sm font-medium ${classes.text}`}>
          {items.length} item(s)
        </span>
      </div>
      <ul className="space-y-2">
        {items.map((item, i) => (
          <li key={i} className={`${classes.item} ${classes.text} p-3 rounded-xl border 
                                flex items-start gap-2 transition-all duration-200 hover:shadow-md`}>
            <FaArrowRight className="text-xs mt-1.5 flex-shrink-0 opacity-50" />
            <span>{item}</span>
          </li>
        ))}
      </ul>
    </div>
  );
};

const HerbDrugInteractionsSection = ({ herb_drug_interactions, handleViewInteraction }) => {
  return (
    <div className="card-medical p-6 animate-fade-in-up">
      <div className="flex items-center gap-3 mb-6">
        <div className="w-12 h-12 bg-gradient-to-br from-purple-500 to-indigo-600 rounded-xl 
                      flex items-center justify-center shadow-lg">
          <FaFlask className="text-2xl text-white" />
        </div>
        <div>
          <h3 className="text-xl font-bold text-gray-800">Herb-Drug Interactions</h3>
          <p className="text-sm text-gray-500">{herb_drug_interactions.length} potential interaction(s) detected</p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {herb_drug_interactions.map((interaction, index) => (
          <div
            key={index}
            onClick={() => handleViewInteraction(interaction)}
            className={`p-5 rounded-xl border-l-4 cursor-pointer transition-all duration-300 
                      hover:shadow-lg hover:scale-[1.02] animate-fade-in ${
              interaction.severity === "Major"
                ? "bg-gradient-to-r from-red-50 to-rose-50 border-red-500 hover:border-red-600"
                : interaction.severity === "Moderate"
                ? "bg-gradient-to-r from-amber-50 to-yellow-50 border-amber-500 hover:border-amber-600"
                : "bg-gradient-to-r from-gray-50 to-slate-50 border-gray-400 hover:border-gray-500"
            }`}
            style={{ animationDelay: `${index * 0.1}s` }}
          >
            <div className="flex items-center justify-between mb-2">
              <p className="font-bold text-gray-800 flex items-center gap-2">
                <span className="text-green-600">{interaction.herb}</span>
                <span className="text-gray-400">+</span>
                <span className="text-blue-600">{interaction.drug}</span>
              </p>
              <span className={`text-xs px-2 py-1 rounded-full font-medium ${
                interaction.severity === "Major" ? "bg-red-100 text-red-700" :
                interaction.severity === "Moderate" ? "bg-amber-100 text-amber-700" :
                "bg-gray-100 text-gray-700"
              }`}>
                {interaction.severity}
              </span>
            </div>
            <p className="text-sm text-gray-600 line-clamp-2">{interaction.effect}</p>
            <div className="flex items-center gap-1 mt-3 text-xs text-medical-primary font-medium">
              <FaEye />
              <span>Click for details</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

const MedListSection = ({ title, emoji, meds, color, handleViewTaper, handleViewMonitoring }) => {
  if (meds.length === 0) return null;

  const colorClasses = {
    red: {
      header: 'from-red-500 to-rose-600',
      text: 'text-red-600',
      bg: 'from-red-50 to-rose-50',
      border: 'border-red-200',
    },
    yellow: {
      header: 'from-amber-400 to-orange-500',
      text: 'text-amber-600',
      bg: 'from-amber-50 to-yellow-50',
      border: 'border-amber-200',
    },
    green: {
      header: 'from-emerald-500 to-green-600',
      text: 'text-emerald-600',
      bg: 'from-green-50 to-emerald-50',
      border: 'border-green-200',
    },
  };

  const classes = colorClasses[color];

  return (
    <div className="card-medical overflow-hidden animate-fade-in-up">
      <div className={`bg-gradient-to-r ${classes.header} px-6 py-4`}>
        <h3 className="text-xl font-bold text-white flex items-center gap-3">
          <span>{emoji}</span>
          <span>{title}</span>
          <span className="ml-auto bg-white/20 backdrop-blur-sm px-3 py-1 rounded-full text-sm">
            {meds.length} medication(s)
          </span>
        </h3>
      </div>

      <div className="p-6 space-y-4">
        {meds.map((med, i) => (
          <MedicationCard
            key={i}
            medication={med}
            riskColor={color}
            classes={classes}
            onViewTaper={handleViewTaper}
            onViewMonitoring={handleViewMonitoring}
            index={i}
          />
        ))}
      </div>
    </div>
  );
};

const MedicationCard = ({ medication, riskColor, classes, onViewTaper, onViewMonitoring, index }) => {
  return (
    <div 
      className={`bg-gradient-to-r ${classes.bg} p-5 rounded-xl border ${classes.border} 
                transition-all duration-300 hover:shadow-lg animate-fade-in`}
      style={{ animationDelay: `${index * 0.1}s` }}
    >
      <div className="flex flex-col lg:flex-row lg:justify-between lg:items-start gap-4">
        <div className="flex-1">
          <div className="flex flex-wrap items-center gap-3 mb-3">
            <h4 className="text-lg font-bold text-gray-800">{medication.name}</h4>
            <span className={`risk-badge-${riskColor}`}>
              Score: {medication.risk_score}/10
            </span>
            <span className="text-xs px-3 py-1 bg-gray-100 rounded-full text-gray-600 font-medium">
              {medication.type}
            </span>
          </div>

          {medication.stopp_flags?.length > 0 && (
            <div className="mb-4">
              <p className="text-sm font-semibold text-gray-700 mb-2 flex items-center gap-2">
                <FaShieldAlt className="text-medical-primary" />
                STOPP Criteria Flags
              </p>
              <div className="space-y-2">
                {medication.stopp_flags.map((flag, idx) => (
                  <div key={idx} className="bg-white p-4 rounded-xl shadow-sm border border-gray-100">
                    <div className="flex flex-wrap items-center justify-between gap-2 mb-2">
                      <span className="font-semibold text-gray-800">{flag.criterion}</span>
                      <span className={`text-xs px-2 py-1 rounded-full font-medium ${
                        flag.severity === "High" ? "bg-red-100 text-red-700" :
                        flag.severity === "Moderate" ? "bg-amber-100 text-amber-700" :
                        "bg-gray-100 text-gray-700"
                      }`}>
                        {flag.severity}
                      </span>
                    </div>
                    <p className="text-sm text-gray-600 italic mb-2">{flag.rationale}</p>
                    <p className="text-sm text-medical-primary font-medium flex items-center gap-1">
                      <FaArrowRight className="text-xs" />
                      {flag.action}
                    </p>
                  </div>
                ))}
              </div>
            </div>
          )}

          {medication.flags?.length > 0 && (
            <div className="mb-3">
              <p className="text-sm font-semibold text-gray-700 mb-2">Issues Identified:</p>
              <ul className="space-y-1">
                {medication.flags.map((flag, idx) => (
                  <li key={idx} className="text-sm text-gray-600 flex items-start gap-2">
                    <span className="text-amber-500 mt-0.5">&#9679;</span>
                    <span>{flag}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>

        <div className="flex lg:flex-col gap-2 flex-shrink-0">
          {medication.taper_required && (
            <button
              onClick={() => onViewTaper(medication)}
              className="px-4 py-2.5 bg-gradient-to-r from-indigo-600 to-purple-600 
                       text-white text-sm rounded-xl shadow-md hover:from-indigo-700 
                       hover:to-purple-700 flex items-center gap-2 font-medium
                       transition-all duration-300 hover:shadow-lg hover:scale-105"
            >
              <FaRobot />
              AI Taper Plan
            </button>
          )}

          <button
            onClick={() => onViewMonitoring(medication)}
            className="px-4 py-2.5 bg-gradient-to-r from-blue-500 to-blue-600 
                     text-white text-sm rounded-xl shadow-md hover:from-blue-600 
                     hover:to-blue-700 flex items-center gap-2 font-medium
                     transition-all duration-300 hover:shadow-lg hover:scale-105"
          >
            <FaEye />
            Monitoring
          </button>
        </div>
      </div>
    </div>
  );
};

export default ResultsDashboard;
