import React, { useState } from 'react';
import { FaExclamationTriangle, FaExclamationCircle, FaCheckCircle, FaEye, FaCalendarAlt, FaFlask } from 'react-icons/fa';
import TaperModal from './TaperModal';
import InteractionModal from './InteractionModal';
import MonitoringModal from './MonitoringModal';

const ResultsDashboard = ({ results, patientData }) => {
  const [selectedMedication, setSelectedMedication] = useState(null);
  const [showTaperModal, setShowTaperModal] = useState(false);
  const [showMonitoringModal, setShowMonitoringModal] = useState(false);
  const [showInteractionModal, setShowInteractionModal] = useState(false);
  const [selectedInteraction, setSelectedInteraction] = useState(null);

  if (!results) return null;

  const { medication_analyses, priority_summary, herb_drug_interactions, clinical_recommendations, safety_alerts } = results;

  const redMedications = medication_analyses?.filter(m => m.risk_category === 'RED') || [];
  const yellowMedications = medication_analyses?.filter(m => m.risk_category === 'YELLOW') || [];
  const greenMedications = medication_analyses?.filter(m => m.risk_category === 'GREEN') || [];

  const handleViewTaper = (medication) => {
    setSelectedMedication(medication);
    setShowTaperModal(true);
  };

  const handleViewMonitoring = (medication) => {
    setSelectedMedication(medication);
    setShowMonitoringModal(true);
  };

  const handleViewInteraction = (interaction) => {
    setSelectedInteraction(interaction);
    setShowInteractionModal(true);
  };

  return (
    <div className="space-y-6">
      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-white rounded-lg shadow-lg p-6 border-l-4 border-risk-red">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">HIGH PRIORITY</p>
              <p className="text-3xl font-bold text-risk-red">{priority_summary?.RED || 0}</p>
              <p className="text-sm text-gray-500">Medications</p>
            </div>
            <FaExclamationTriangle className="text-4xl text-risk-red opacity-20" />
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-lg p-6 border-l-4 border-risk-yellow">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">REVIEW NEEDED</p>
              <p className="text-3xl font-bold text-risk-yellow">{priority_summary?.YELLOW || 0}</p>
              <p className="text-sm text-gray-500">Medications</p>
            </div>
            <FaExclamationCircle className="text-4xl text-risk-yellow opacity-20" />
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-lg p-6 border-l-4 border-risk-green">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">SAFE TO CONTINUE</p>
              <p className="text-3xl font-bold text-risk-green">{priority_summary?.GREEN || 0}</p>
              <p className="text-sm text-gray-500">Medications</p>
            </div>
            <FaCheckCircle className="text-4xl text-risk-green opacity-20" />
          </div>
        </div>
      </div>

      {/* Safety Alerts */}
      {safety_alerts && safety_alerts.length > 0 && (
        <div className="bg-red-50 border-l-4 border-red-500 p-4 rounded-lg shadow">
          <div className="flex items-start">
            <FaExclamationTriangle className="text-red-500 mt-1 mr-3 flex-shrink-0" />
            <div className="flex-1">
              <h3 className="text-lg font-semibold text-red-800 mb-2">Safety Alerts</h3>
              <ul className="space-y-2">
                {safety_alerts.map((alert, index) => (
                  <li key={index} className="text-red-700">{alert}</li>
                ))}
              </ul>
            </div>
          </div>
        </div>
      )}

      {/* Clinical Recommendations */}
      {clinical_recommendations && clinical_recommendations.length > 0 && (
        <div className="bg-blue-50 border-l-4 border-blue-500 p-4 rounded-lg shadow">
          <div className="flex items-start">
            <FaExclamationCircle className="text-blue-500 mt-1 mr-3 flex-shrink-0" />
            <div className="flex-1">
              <h3 className="text-lg font-semibold text-blue-800 mb-2">Clinical Recommendations</h3>
              <ul className="space-y-2">
                {clinical_recommendations.map((rec, index) => (
                  <li key={index} className="text-blue-700">{rec}</li>
                ))}
              </ul>
            </div>
          </div>
        </div>
      )}

      {/* Herb-Drug Interactions */}
      {herb_drug_interactions && herb_drug_interactions.length > 0 && (
        <div className="bg-white rounded-lg shadow-lg p-6">
          <h3 className="text-xl font-bold text-gray-800 mb-4 flex items-center">
            <FaFlask className="mr-2 text-purple-600" />
            Herb-Drug Interactions ({herb_drug_interactions.length})
          </h3>
          <div className="space-y-3">
            {herb_drug_interactions.map((interaction, index) => (
              <div
                key={index}
                className={`p-4 rounded-lg border-l-4 cursor-pointer hover:shadow-md transition ${
                  interaction.severity === 'Major'
                    ? 'bg-red-50 border-red-500'
                    : interaction.severity === 'Moderate'
                    ? 'bg-yellow-50 border-yellow-500'
                    : 'bg-gray-50 border-gray-400'
                }`}
                onClick={() => handleViewInteraction(interaction)}
              >
                <div className="flex justify-between items-start">
                  <div className="flex-1">
                    <p className="font-semibold text-gray-800">
                      {interaction.herb} + {interaction.drug}
                    </p>
                    <p className="text-sm text-gray-600 mt-1">{interaction.effect}</p>
                    <div className="flex items-center mt-2 space-x-3">
                      <span className={`text-xs px-2 py-1 rounded-full font-medium ${
                        interaction.severity === 'Major'
                          ? 'bg-red-200 text-red-800'
                          : interaction.severity === 'Moderate'
                          ? 'bg-yellow-200 text-yellow-800'
                          : 'bg-gray-200 text-gray-800'
                      }`}>
                        {interaction.severity}
                      </span>
                      <span className="text-xs px-2 py-1 rounded-full bg-gray-200 text-gray-700">
                        {interaction.evidence}
                      </span>
                    </div>
                  </div>
                  <button className="text-blue-600 hover:text-blue-800 ml-4">
                    <FaEye />
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* RED Medications */}
      {redMedications.length > 0 && (
        <div className="bg-white rounded-lg shadow-lg p-6">
          <h3 className="text-xl font-bold text-risk-red mb-4 flex items-center">
            <FaExclamationTriangle className="mr-2" />
            🔴 HIGH PRIORITY - Deprescribe Now ({redMedications.length})
          </h3>
          <div className="space-y-4">
            {redMedications.map((med, index) => (
              <MedicationCard
                key={index}
                medication={med}
                riskColor="red"
                onViewTaper={handleViewTaper}
                onViewMonitoring={handleViewMonitoring}
              />
            ))}
          </div>
        </div>
      )}

      {/* YELLOW Medications */}
      {yellowMedications.length > 0 && (
        <div className="bg-white rounded-lg shadow-lg p-6">
          <h3 className="text-xl font-bold text-risk-yellow mb-4 flex items-center">
            <FaExclamationCircle className="mr-2" />
            🟡 REVIEW REQUIRED - Clinical Assessment Needed ({yellowMedications.length})
          </h3>
          <div className="space-y-4">
            {yellowMedications.map((med, index) => (
              <MedicationCard
                key={index}
                medication={med}
                riskColor="yellow"
                onViewTaper={handleViewTaper}
                onViewMonitoring={handleViewMonitoring}
              />
            ))}
          </div>
        </div>
      )}

      {/* GREEN Medications */}
      {greenMedications.length > 0 && (
        <div className="bg-white rounded-lg shadow-lg p-6">
          <h3 className="text-xl font-bold text-risk-green mb-4 flex items-center">
            <FaCheckCircle className="mr-2" />
            🟢 SAFE TO CONTINUE - Appropriate Therapy ({greenMedications.length})
          </h3>
          <div className="space-y-4">
            {greenMedications.map((med, index) => (
              <MedicationCard
                key={index}
                medication={med}
                riskColor="green"
                onViewTaper={handleViewTaper}
                onViewMonitoring={handleViewMonitoring}
              />
            ))}
          </div>
        </div>
      )}

      {/* Modals */}
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
  );
};

// Medication Card Component
const MedicationCard = ({ medication, riskColor, onViewTaper, onViewMonitoring }) => {
  const colorClasses = {
    red: 'border-risk-red bg-red-50',
    yellow: 'border-risk-yellow bg-yellow-50',
    green: 'border-risk-green bg-green-50'
  };

  const badgeClasses = {
    red: 'bg-risk-red text-white',
    yellow: 'bg-risk-yellow text-white',
    green: 'bg-risk-green text-white'
  };

  return (
    <div className={`border-l-4 ${colorClasses[riskColor]} p-4 rounded-lg`}>
      <div className="flex justify-between items-start">
        <div className="flex-1">
          <div className="flex items-center space-x-3 mb-2">
            <h4 className="text-lg font-semibold text-gray-800">{medication.name}</h4>
            <span className={`text-xs px-2 py-1 rounded-full font-medium ${badgeClasses[riskColor]}`}>
              Risk Score: {medication.risk_score}/10
            </span>
            <span className="text-xs px-2 py-1 rounded-full bg-gray-200 text-gray-700">
              {medication.type}
            </span>
          </div>

          {/* Flags */}
          {medication.flags && medication.flags.length > 0 && (
            <div className="mb-3">
              <p className="text-sm font-medium text-gray-700 mb-1">Issues Identified:</p>
              <ul className="space-y-1">
                {medication.flags.map((flag, idx) => (
                  <li key={idx} className="text-sm text-gray-600 flex items-start">
                    <span className="mr-2">•</span>
                    <span>{flag}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Recommendations */}
          {medication.recommendations && medication.recommendations.length > 0 && (
            <div className="mb-3">
              <p className="text-sm font-medium text-gray-700 mb-1">Recommendations:</p>
              <ul className="space-y-1">
                {medication.recommendations.map((rec, idx) => (
                  <li key={idx} className="text-sm text-blue-700 flex items-start">
                    <span className="mr-2">→</span>
                    <span>{rec}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Monitoring */}
          {medication.monitoring_required && medication.monitoring_required.length > 0 && (
            <div>
              <p className="text-sm font-medium text-gray-700 mb-1">Monitoring Required:</p>
              <div className="flex flex-wrap gap-2">
                {medication.monitoring_required.map((mon, idx) => (
                  <span key={idx} className="text-xs px-2 py-1 rounded bg-blue-100 text-blue-800">
                    {mon}
                  </span>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Action Buttons */}
        <div className="ml-4 flex flex-col space-y-2">
          {medication.taper_required && (
            <button
              onClick={() => onViewTaper(medication)}
              className="px-3 py-2 bg-indigo-600 text-white text-sm rounded-md hover:bg-indigo-700 transition flex items-center"
            >
              <FaCalendarAlt className="mr-2" />
              View Taper Plan
            </button>
          )}
          <button
            onClick={() => onViewMonitoring(medication)}
            className="px-3 py-2 bg-blue-600 text-white text-sm rounded-md hover:bg-blue-700 transition flex items-center"
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
