import React, { useState, useEffect } from 'react';
import { FaTimes, FaSpinner, FaRobot, FaCheckCircle } from 'react-icons/fa';
import { getTaperPlan } from '../services/api';

const TaperModal = ({ medication, patientData, onClose }) => {
  const [taperPlan, setTaperPlan] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [isAiGenerated, setIsAiGenerated] = useState(false);

  useEffect(() => {
    const fetchTaperPlan = async () => {
      try {
        setLoading(true);
        const medData = patientData.medications.find(
          m => m.generic_name.toLowerCase() === medication.name.toLowerCase()
        );

        const request = {
          drug_name: medication.name,
          current_dose: medData?.dose || '1 tablet',
          duration_on_medication: medData?.duration || 'long_term',
          patient_cfs_score: patientData.cfs_score || null,
          patient_age: patientData.age,
          comorbidities: patientData.comorbidities
        };

        const plan = await getTaperPlan(request);
        setTaperPlan(plan);
        
        // Check if it's AI-generated (more than 4 steps = likely Gemini)
        setIsAiGenerated(plan.steps.length > 4);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchTaperPlan();
  }, [medication, patientData]);

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-xl max-w-4xl w-full max-h-[90vh] overflow-hidden">
        {/* Header with AI Badge */}
        <div className="bg-gradient-to-r from-indigo-600 to-purple-600 text-white p-6">
          <div className="flex justify-between items-center">
            <div className="flex items-center space-x-3">
              <h2 className="text-2xl font-bold">Tapering Schedule</h2>
              {isAiGenerated && (
                <span className="flex items-center bg-white bg-opacity-20 px-3 py-1 rounded-full text-sm">
                  <FaRobot className="mr-2" />
                  AI-Personalized
                </span>
              )}
            </div>
            <button onClick={onClose} className="text-white hover:text-gray-200">
              <FaTimes size={24} />
            </button>
          </div>
          <p className="text-indigo-100 mt-2">{medication.name}</p>
        </div>

        {/* Content */}
        <div className="p-6 overflow-y-auto max-h-[calc(90vh-80px)]">
          {loading && (
            <div className="flex items-center justify-center py-12">
              <FaSpinner className="animate-spin text-indigo-600 text-4xl" />
              <span className="ml-3 text-gray-600">
                {isAiGenerated ? 'Generating personalized schedule with AI...' : 'Loading taper plan...'}
              </span>
            </div>
          )}

          {error && (
            <div className="bg-red-50 border border-red-200 text-red-700 p-4 rounded-lg">
              <p className="font-semibold">Error loading taper plan:</p>
              <p>{error}</p>
            </div>
          )}

          {taperPlan && (
            <div className="space-y-6">
              {/* AI Generation Notice */}
              {isAiGenerated && (
                <div className="bg-gradient-to-r from-purple-50 to-indigo-50 border-l-4 border-purple-500 p-4 rounded-lg">
                  <div className="flex items-start">
                    <FaRobot className="text-purple-600 text-2xl mr-3 flex-shrink-0 mt-1" />
                    <div>
                      <h4 className="font-semibold text-purple-900 mb-1">
                        AI-Generated Personalized Schedule
                      </h4>
                      <p className="text-sm text-purple-800">
                        This tapering schedule has been generated using advanced AI, considering your patient's 
                        age ({patientData.age}), frailty (CFS {patientData.cfs_score || 'N/A'}), and specific 
                        comorbidities. All recommendations follow evidence-based clinical protocols.
                      </p>
                    </div>
                  </div>
                </div>
              )}

              {/* Overview */}
              <div className="bg-blue-50 p-4 rounded-lg">
                <h3 className="text-lg font-semibold text-gray-800 mb-3">Overview</h3>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <p className="text-sm text-gray-600">Drug Class</p>
                    <p className="font-medium">{taperPlan.drug_class}</p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-600">Risk Profile</p>
                    <p className="font-medium">{taperPlan.risk_profile}</p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-600">Taper Strategy</p>
                    <p className="font-medium">{taperPlan.taper_strategy}</p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-600">Total Duration</p>
                    <p className="font-medium">{taperPlan.total_duration_weeks} weeks</p>
                  </div>
                </div>
              </div>

              {/* Week-by-Week Schedule - ENHANCED */}
              <div>
                <h3 className="text-lg font-semibold text-gray-800 mb-3 flex items-center">
                  <FaCheckCircle className="mr-2 text-green-600" />
                  Week-by-Week Personalized Schedule
                </h3>
                <div className="space-y-3">
                  {taperPlan.steps.map((step, index) => (
                    <div 
                      key={index} 
                      className="border-l-4 border-indigo-500 bg-gradient-to-r from-indigo-50 to-white rounded-lg p-4 hover:shadow-md transition"
                    >
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          {/* Week Badge */}
                          <div className="flex items-center space-x-3 mb-3">
                            <span className="bg-indigo-600 text-white px-4 py-1 rounded-full text-sm font-bold">
                              Week {step.week}
                            </span>
                            <span className="text-xl font-bold text-gray-800">{step.dose}</span>
                            <span className="text-sm text-gray-600">
                              ({step.percentage_of_original}% of original)
                            </span>
                          </div>

                          {/* Instructions - Enhanced Display */}
                          <div className="bg-white p-3 rounded-lg mb-3 border border-gray-200">
                            <p className="text-sm font-medium text-gray-700 mb-1">📋 Instructions:</p>
                            <p className="text-gray-800">{step.instructions}</p>
                          </div>

                          {/* Monitoring */}
                          <div className="bg-blue-50 p-3 rounded-lg mb-3">
                            <p className="text-sm font-medium text-blue-900 mb-1">🔍 Monitoring:</p>
                            <p className="text-blue-800 text-sm">{step.monitoring}</p>
                          </div>

                          {/* Withdrawal Symptoms */}
                          {step.withdrawal_symptoms_to_watch && step.withdrawal_symptoms_to_watch.length > 0 && (
                            <div>
                              <p className="text-sm font-medium text-gray-700 mb-2">⚠️ Watch for these symptoms:</p>
                              <div className="flex flex-wrap gap-2">
                                {step.withdrawal_symptoms_to_watch.map((symptom, idx) => (
                                  <span 
                                    key={idx} 
                                    className="text-xs px-3 py-1 bg-yellow-100 text-yellow-800 rounded-full border border-yellow-300"
                                  >
                                    {symptom}
                                  </span>
                                ))}
                              </div>
                            </div>
                          )}
                        </div>

                        {/* Progress Indicator */}
                        <div className="ml-4 flex flex-col items-center">
                          <div className="relative">
                            <svg className="w-16 h-16 transform -rotate-90">
                              <circle
                                cx="32"
                                cy="32"
                                r="28"
                                stroke="#E5E7EB"
                                strokeWidth="4"
                                fill="none"
                              />
                              <circle
                                cx="32"
                                cy="32"
                                r="28"
                                stroke="#4F46E5"
                                strokeWidth="4"
                                fill="none"
                                strokeDasharray={`${(100 - step.percentage_of_original) * 1.76} 176`}
                                strokeLinecap="round"
                              />
                            </svg>
                            <div className="absolute inset-0 flex items-center justify-center">
                              <span className="text-xs font-bold text-gray-700">
                                {100 - step.percentage_of_original}%
                              </span>
                            </div>
                          </div>
                          <span className="text-xs text-gray-500 mt-1">Reduced</span>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Success Indicators (NEW from Gemini) */}
              {taperPlan.success_indicators && taperPlan.success_indicators.length > 0 && (
                <div className="bg-green-50 p-4 rounded-lg border-l-4 border-green-500">
                  <h3 className="text-lg font-semibold text-green-900 mb-3 flex items-center">
                    <FaCheckCircle className="mr-2" />
                    Success Indicators
                  </h3>
                  <ul className="space-y-2">
                    {taperPlan.success_indicators.map((indicator, index) => (
                      <li key={index} className="flex items-start text-green-800">
                        <span className="mr-2 text-green-600">✓</span>
                        <span>{indicator}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {/* Pause Criteria */}
              <div className="bg-yellow-50 p-4 rounded-lg border-l-4 border-yellow-500">
                <h3 className="text-lg font-semibold text-yellow-900 mb-3">⏸️ When to PAUSE Tapering</h3>
                <ul className="space-y-2">
                  {taperPlan.pause_criteria.map((criteria, index) => (
                    <li key={index} className="flex items-start text-yellow-800">
                      <span className="mr-2">⚠️</span>
                      <span>{criteria}</span>
                    </li>
                  ))}
                </ul>
              </div>

              {/* Reversal Criteria */}
              <div className="bg-red-50 p-4 rounded-lg border-l-4 border-red-500">
                <h3 className="text-lg font-semibold text-red-900 mb-3">🚨 When to REVERSE (Restart Medication)</h3>
                <ul className="space-y-2">
                  {taperPlan.reversal_criteria.map((criteria, index) => (
                    <li key={index} className="flex items-start text-red-800">
                      <span className="mr-2">🚨</span>
                      <span>{criteria}</span>
                    </li>
                  ))}
                </ul>
              </div>

              {/* Monitoring Schedule */}
              <div className="bg-gray-50 p-4 rounded-lg">
                <h3 className="text-lg font-semibold text-gray-800 mb-3">📅 Monitoring Schedule</h3>
                <div className="space-y-3">
                  {Object.entries(taperPlan.monitoring_schedule).map(([period, items], index) => (
                    <div key={index} className="border-l-4 border-blue-500 pl-4 bg-white p-3 rounded">
                      <p className="font-semibold text-gray-800 mb-2">{period}</p>
                      <ul className="space-y-1">
                        {items.map((item, idx) => (
                          <li key={idx} className="text-sm text-gray-700 flex items-start">
                            <span className="mr-2 text-blue-600">•</span>
                            <span>{item}</span>
                          </li>
                        ))}
                      </ul>
                    </div>
                  ))}
                </div>
              </div>

              {/* Patient Education - ENHANCED */}
              <div className="bg-gradient-to-r from-green-50 to-blue-50 p-5 rounded-lg border border-green-200">
                <h3 className="text-lg font-semibold text-gray-800 mb-3 flex items-center">
                  <span className="mr-2">📚</span>
                  Patient Education & Important Information
                </h3>
                <div className="space-y-3">
                  {taperPlan.patient_education.map((education, index) => (
                    <div key={index} className="flex items-start bg-white p-3 rounded-lg shadow-sm">
                      <span className="flex-shrink-0 w-6 h-6 bg-indigo-600 text-white rounded-full flex items-center justify-center text-xs font-bold mr-3 mt-0.5">
                        {index + 1}
                      </span>
                      <p className="text-gray-800">{education}</p>
                    </div>
                  ))}
                </div>
              </div>

              {/* Download/Print Options */}
              <div className="bg-gray-100 p-4 rounded-lg flex items-center justify-between">
                <div className="flex items-center text-gray-700">
                  <span className="text-sm">💾 Save this schedule for your records</span>
                </div>
                <div className="flex space-x-3">
                  <button
                    onClick={() => window.print()}
                    className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition text-sm"
                  >
                    🖨️ Print
                  </button>
                  <button
                    onClick={() => {
                      const data = JSON.stringify(taperPlan, null, 2);
                      const blob = new Blob([data], { type: 'application/json' });
                      const url = URL.createObjectURL(blob);
                      const a = document.createElement('a');
                      a.href = url;
                      a.download = `taper-plan-${medication.name}.json`;
                      a.click();
                    }}
                    className="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 transition text-sm"
                  >
                    💾 Download
                  </button>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="bg-gray-50 p-4 flex justify-between items-center border-t">
          <div className="text-sm text-gray-600">
            {isAiGenerated && (
              <span className="flex items-center">
                <FaRobot className="mr-2 text-purple-600" />
                Generated with AI | Always verify with healthcare provider
              </span>
            )}
          </div>
          <button
            onClick={onClose}
            className="px-6 py-2 bg-gray-600 text-white rounded-md hover:bg-gray-700 transition font-medium"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
};

export default TaperModal;
