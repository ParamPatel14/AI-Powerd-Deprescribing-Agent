import React, { useState } from "react";
import {
  FaExclamationTriangle,
  FaExclamationCircle,
  FaCheckCircle,
  FaEye,
  FaCalendarAlt,
  FaFlask,
  FaRobot,
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

  if (!results) return null;

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

  // ------------------------
  // PDF EXPORT FUNCTION
  // ------------------------
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

  // ------------------------
  // COMPONENT RETURN
  // ------------------------

  return (
    <div>
      {/* PDF Button */}
      <div className="w-full flex justify-end mb-4">
        <button
          onClick={handleExportPDF}
          className="px-4 py-2 bg-indigo-600 text-white rounded-md shadow 
                     hover:bg-indigo-700 transition flex items-center"
        >
          <FaRobot className="mr-2" />
          Export PDF
        </button>
      </div>

      <div id="results-pdf-container" className="space-y-6">
        {/* SUMMARY CARDS */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <SummaryCard
            title="HIGH PRIORITY"
            count={priority_summary?.RED}
            color="red"
            icon={<FaExclamationTriangle className="text-4xl text-risk-red opacity-20" />}
          />

          <SummaryCard
            title="REVIEW NEEDED"
            count={priority_summary?.YELLOW}
            color="yellow"
            icon={<FaExclamationCircle className="text-4xl text-risk-yellow opacity-20" />}
          />

          <SummaryCard
            title="SAFE TO CONTINUE"
            count={priority_summary?.GREEN}
            color="green"
            icon={<FaCheckCircle className="text-4xl text-risk-green opacity-20" />}
          />
            </div>
            {results.patient_summary?.calculated_egfr && (
      <div className="bg-gradient-to-r from-blue-50 to-indigo-50 border border-blue-200 rounded-lg p-4 mb-4">
        <h3 className="text-lg font-bold text-blue-900 mb-3">
          📊 Calculated Organ Function
        </h3>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {/* Renal Function */}
          <div className="bg-white p-3 rounded shadow-sm">
            <p className="text-sm text-gray-600">Kidney Function (eGFR)</p>
            <p className="text-2xl font-bold text-blue-700">
              {results.patient_summary.calculated_egfr} mL/min/1.73m²
            </p>
            <p className="text-sm text-gray-700 mt-1">
              {results.patient_summary.renal_function}
            </p>
          </div>
          
          {/* Hepatic Function */}
          {results.patient_summary.calculated_meld && (
            <div className="bg-white p-3 rounded shadow-sm">
              <p className="text-sm text-gray-600">Liver Function (MELD Score)</p>
              <p className="text-2xl font-bold text-orange-700">
                {results.patient_summary.calculated_meld}
              </p>
              <p className="text-sm text-gray-700 mt-1">
                {results.patient_summary.hepatic_function}
              </p>
            </div>
          )}
        </div>
      </div>
    )}

        {/* SAFETY ALERTS */}
        {safety_alerts?.length > 0 && (
          <AlertBlock
            icon={<FaExclamationTriangle className="text-red-500 mt-1 mr-3" />}
            title="Safety Alerts"
            color="red"
            items={safety_alerts}
          />
        )}

        {/* CLINICAL RECOMMENDATIONS */}
        {clinical_recommendations?.length > 0 && (
          <AlertBlock
            icon={<FaExclamationCircle className="text-blue-500 mt-1 mr-3" />}
            title="Clinical Recommendations"
            color="blue"
            items={clinical_recommendations}
          />
        )}

        {/* START RECOMMENDATIONS */}
        {global_start_recommendations?.length > 0 && (
          <AlertBlock
            icon={<FaCheckCircle className="text-green-600 mt-1 mr-3" />}
            title="Medications to Consider Starting (START v2)"
            color="green"
            items={global_start_recommendations}
          />
        )}

        {/* HERB-DRUG INTERACTIONS */}
        {herb_drug_interactions?.length > 0 && (
          <HerbDrugInteractionsSection
            herb_drug_interactions={herb_drug_interactions}
            handleViewInteraction={handleViewInteraction}
          />
        )}

        {/* RED / YELLOW / GREEN MEDICATION SECTIONS */}
        <MedListSection
          title="🔴 HIGH PRIORITY - Deprescribe Now"
          meds={redMedications}
          color="red"
          handleViewTaper={handleViewTaper}
          handleViewMonitoring={handleViewMonitoring}
        />

        <MedListSection
          title="🟡 REVIEW REQUIRED - Clinical Assessment Needed"
          meds={yellowMedications}
          color="yellow"
          handleViewTaper={handleViewTaper}
          handleViewMonitoring={handleViewMonitoring}
        />

        <MedListSection
          title="🟢 SAFE TO CONTINUE"
          meds={greenMedications}
          color="green"
          handleViewTaper={handleViewTaper}
          handleViewMonitoring={handleViewMonitoring}
        />

        {/* MODALS */}
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

/* -----------------------------------------------------
   SUMMARY CARD
----------------------------------------------------- */
const SummaryCard = ({ title, count, color, icon }) => {
  const borderColor =
    color === "red"
      ? "border-risk-red"
      : color === "yellow"
      ? "border-risk-yellow"
      : "border-risk-green";

  const textColor =
    color === "red"
      ? "text-risk-red"
      : color === "yellow"
      ? "text-risk-yellow"
      : "text-risk-green";

  return (
    <div className={`bg-white rounded-lg shadow-lg p-6 border-l-4 ${borderColor}`}>
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm text-gray-600">{title}</p>
          <p className={`text-3xl font-bold ${textColor}`}>{count || 0}</p>
          <p className="text-sm text-gray-500">Medications</p>
        </div>
        {icon}
      </div>
    </div>
  );
};

/* -----------------------------------------------------
   ALERT BLOCK
----------------------------------------------------- */
const AlertBlock = ({ icon, title, color, items }) => {
  const border =
    color === "red"
      ? "border-red-500 bg-red-50"
      : color === "blue"
      ? "border-blue-500 bg-blue-50"
      : "border-green-500 bg-green-50";

  const textColor =
    color === "red"
      ? "text-red-700"
      : color === "blue"
      ? "text-blue-700"
      : "text-green-700";

  const titleColor =
    color === "red"
      ? "text-red-800"
      : color === "blue"
      ? "text-blue-800"
      : "text-green-800";

  return (
    <div className={`p-4 rounded-lg shadow border-l-4 ${border}`}>
      <div className="flex items-start">
        {icon}
        <div className="flex-1">
          <h3 className={`text-lg font-semibold ${titleColor} mb-2`}>{title}</h3>
          <ul className="space-y-2">
            {items.map((item, i) => (
              <li key={i} className={`${textColor}`}>{item}</li>
            ))}
          </ul>
        </div>
      </div>
    </div>
  );
};

/* -----------------------------------------------------
   HERB-DRUG INTERACTION BLOCK
----------------------------------------------------- */
const HerbDrugInteractionsSection = ({
  herb_drug_interactions,
  handleViewInteraction,
}) => {
  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      <h3 className="text-xl font-bold text-gray-800 mb-4 flex items-center">
        <FaFlask className="mr-2 text-purple-600" />
        Herb-Drug Interactions ({herb_drug_interactions.length})
      </h3>

      <div className="space-y-3">
        {herb_drug_interactions.map((interaction, index) => (
          <div
            key={index}
            onClick={() => handleViewInteraction(interaction)}
            className={`p-4 rounded-lg border-l-4 cursor-pointer hover:shadow-md transition ${
              interaction.severity === "Major"
                ? "bg-red-50 border-red-500"
                : interaction.severity === "Moderate"
                ? "bg-yellow-50 border-yellow-500"
                : "bg-gray-50 border-gray-400"
            }`}
          >
            <p className="font-semibold text-gray-800">
              {interaction.herb} + {interaction.drug}
            </p>
            <p className="text-sm text-gray-600">{interaction.effect}</p>
          </div>
        ))}
      </div>
    </div>
  );
};

/* -----------------------------------------------------
   MEDICATION LIST SECTION
----------------------------------------------------- */
const MedListSection = ({
  title,
  meds,
  color,
  handleViewTaper,
  handleViewMonitoring,
}) => {
  if (meds.length === 0) return null;

  const titleColor =
    color === "red"
      ? "text-risk-red"
      : color === "yellow"
      ? "text-risk-yellow"
      : "text-risk-green";

  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      <h3 className={`text-xl font-bold mb-4 flex items-center ${titleColor}`}>
        {title} ({meds.length})
      </h3>

      <div className="space-y-4">
        {meds.map((med, i) => (
          <MedicationCard
            key={i}
            medication={med}
            riskColor={color}
            onViewTaper={handleViewTaper}
            onViewMonitoring={handleViewMonitoring}
          />
        ))}
      </div>
    </div>
  );
};

/* -----------------------------------------------------
   MEDICATION CARD
----------------------------------------------------- */
const MedicationCard = ({ medication, riskColor, onViewTaper, onViewMonitoring }) => {
  const cardClasses = {
    red: "border-risk-red bg-red-50",
    yellow: "border-risk-yellow bg-yellow-50",
    green: "border-risk-green bg-green-50",
  };

  const badgeClasses = {
    red: "bg-risk-red text-white",
    yellow: "bg-risk-yellow text-white",
    green: "bg-risk-green text-white",
  };

  return (
    <div className={`border-l-4 ${cardClasses[riskColor]} p-4 rounded-lg`}>
      <div className="flex justify-between items-start">
        <div className="flex-1">
          <div className="flex items-center space-x-3 mb-2">
            <h4 className="text-lg font-semibold text-gray-800">{medication.name}</h4>

            <span className={`text-xs px-2 py-1 rounded-full ${badgeClasses[riskColor]}`}>
              Score: {medication.risk_score}/10
            </span>

            <span className="text-xs px-2 py-1 bg-gray-200 rounded-full">
              {medication.type}
            </span>
          </div>

          {/* STOPP FLAGS */}
          {medication.stopp_flags?.length > 0 && (
            <div className="mb-3">
              <p className="text-sm font-medium text-gray-700 mb-1">
                STOPP Criteria Flags:
              </p>

              <ul className="space-y-2">
                {medication.stopp_flags.map((flag, idx) => {
                  const badgeColor =
                    flag.severity === "High"
                      ? "bg-red-200 text-red-800"
                      : flag.severity === "Moderate"
                      ? "bg-yellow-200 text-yellow-800"
                      : "bg-gray-200 text-gray-800";

                  return (
                    <li
                      key={idx}
                      className="p-2 rounded bg-white shadow-sm border text-sm"
                    >
                      <div className="flex justify-between">
                        <span className="font-semibold">{flag.criterion}</span>
                        <span className={`text-xs px-2 py-1 rounded-full ${badgeColor}`}>
                          {flag.severity}
                        </span>
                      </div>

                      <p className="text-xs text-gray-700 italic mt-1">
                        {flag.rationale}
                      </p>

                      <p className="text-xs text-blue-700 font-medium mt-1">
                        Recommendation: {flag.action}
                      </p>
                    </li>
                  );
                })}
              </ul>
            </div>
          )}

          {/* Other Flags (Legacy) */}
          {medication.flags?.length > 0 && (
            <div className="mb-3">
              <p className="text-sm font-medium text-gray-700 mb-1">
                Issues Identified:
              </p>
              <ul className="space-y-1">
                {medication.flags.map((flag, idx) => (
                  <li key={idx} className="text-sm text-gray-600 flex">
                    <span className="mr-2">•</span> {flag}
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>

        {/* ACTION BUTTONS */}
        <div className="ml-4 flex flex-col space-y-2">
          {medication.taper_required && (
            <button
              onClick={() => onViewTaper(medication)}
              className="px-3 py-2 bg-gradient-to-r from-indigo-600 to-purple-600 
                         text-white text-sm rounded-md shadow hover:from-indigo-700 
                         hover:to-purple-700 flex items-center"
            >
              <FaRobot className="mr-2" />
              AI Taper Plan
            </button>
          )}

          <button
            onClick={() => onViewMonitoring(medication)}
            className="px-3 py-2 bg-blue-600 text-white text-sm rounded-md 
                       hover:bg-blue-700 flex items-center"
          >
            <FaEye className="mr-2" />
            Monitoring
          </button>
        </div>
      </div>
    </div>
  );
};

export default ResultsDashboard;
