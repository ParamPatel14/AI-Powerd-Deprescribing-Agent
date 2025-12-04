import React, { useState, useEffect } from 'react';
import { FaTimes, FaSpinner, FaRobot, FaCheckCircle, FaPrint, FaDownload, FaExclamationTriangle, FaPause, FaUndo } from 'react-icons/fa';
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
    <div className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-50 p-4 modal-overlay">
      <div className="bg-white rounded-3xl shadow-2xl max-w-4xl w-full max-h-[90vh] overflow-hidden modal-content">
        <div className="bg-gradient-to-r from-indigo-600 via-purple-600 to-indigo-700 text-white p-6 relative overflow-hidden">
          <div className="absolute inset-0 overflow-hidden">
            <div className="absolute -top-1/2 -right-1/4 w-64 h-64 bg-white/10 rounded-full blur-3xl"></div>
            <div className="absolute -bottom-1/2 -left-1/4 w-64 h-64 bg-purple-300/10 rounded-full blur-3xl"></div>
          </div>
          
          <div className="relative flex justify-between items-start">
            <div className="flex items-center gap-4">
              <div className="w-14 h-14 bg-white/20 backdrop-blur-sm rounded-2xl flex items-center justify-center border border-white/30">
                <FaRobot className="text-2xl" />
              </div>
              <div>
                <h2 className="text-2xl font-bold flex items-center gap-3">
                  Tapering Schedule
                  {isAiGenerated && (
                    <span className="text-xs bg-white/20 px-3 py-1 rounded-full backdrop-blur-sm border border-white/30">
                      AI-Personalized
                    </span>
                  )}
                </h2>
                <p className="text-indigo-100 font-medium mt-1">{medication.name}</p>
              </div>
            </div>
            <button 
              onClick={onClose} 
              className="w-10 h-10 bg-white/20 hover:bg-white/30 rounded-xl flex items-center justify-center 
                       transition-all duration-200 backdrop-blur-sm"
            >
              <FaTimes size={18} />
            </button>
          </div>
        </div>

        <div className="p-6 overflow-y-auto max-h-[calc(90vh-160px)]">
          {loading && (
            <div className="flex flex-col items-center justify-center py-16">
              <div className="relative mb-6">
                <div className="w-20 h-20 rounded-full bg-gradient-to-br from-indigo-100 to-purple-100 
                              flex items-center justify-center animate-pulse">
                  <FaRobot className="text-3xl text-indigo-600" />
                </div>
                <div className="absolute inset-0">
                  <svg className="w-20 h-20 animate-spin" style={{ animationDuration: '2s' }}>
                    <circle cx="40" cy="40" r="38" stroke="url(#modalGradient)" strokeWidth="3" 
                            fill="none" strokeDasharray="60 180" strokeLinecap="round" />
                    <defs>
                      <linearGradient id="modalGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                        <stop offset="0%" stopColor="#4F46E5" />
                        <stop offset="100%" stopColor="#7C3AED" />
                      </linearGradient>
                    </defs>
                  </svg>
                </div>
              </div>
              <p className="text-gray-600 font-medium">Generating personalized taper plan...</p>
              <p className="text-gray-400 text-sm mt-1">Analyzing patient factors with AI</p>
            </div>
          )}

          {error && (
            <div className="bg-gradient-to-r from-red-50 to-rose-50 border-l-4 border-red-500 p-5 rounded-xl">
              <div className="flex items-start gap-3">
                <FaExclamationTriangle className="text-red-500 text-xl flex-shrink-0 mt-0.5" />
                <div>
                  <p className="font-bold text-red-800">Error loading taper plan</p>
                  <p className="text-red-700 mt-1">{error}</p>
                </div>
              </div>
            </div>
          )}

          {taperPlan && (
            <div className="space-y-6 animate-fade-in">
              {isAiGenerated && (
                <div className="bg-gradient-to-r from-purple-50 to-indigo-50 border border-purple-200 p-5 rounded-2xl">
                  <div className="flex items-start gap-4">
                    <div className="w-12 h-12 bg-gradient-to-br from-purple-500 to-indigo-600 rounded-xl 
                                  flex items-center justify-center shadow-lg flex-shrink-0">
                      <FaRobot className="text-white text-xl" />
                    </div>
                    <div>
                      <h4 className="font-bold text-purple-900 mb-1">AI-Generated Personalized Schedule</h4>
                      <p className="text-sm text-purple-800">
                        This tapering schedule considers your patient's age ({patientData.age}), 
                        frailty (CFS {patientData.cfs_score || 'N/A'}), and specific comorbidities. 
                        All recommendations follow evidence-based clinical protocols.
                      </p>
                    </div>
                  </div>
                </div>
              )}

              <div className="bg-gradient-to-br from-blue-50 to-indigo-50 p-5 rounded-2xl border border-blue-100">
                <h3 className="text-lg font-bold text-gray-800 mb-4">Overview</h3>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  {[
                    { label: 'Drug Class', value: taperPlan.drug_class },
                    { label: 'Risk Profile', value: taperPlan.risk_profile },
                    { label: 'Strategy', value: taperPlan.taper_strategy },
                    { label: 'Duration', value: `${taperPlan.total_duration_weeks} weeks` },
                  ].map((item, i) => (
                    <div key={i} className="bg-white p-4 rounded-xl shadow-sm">
                      <p className="text-xs text-gray-500 uppercase tracking-wide mb-1">{item.label}</p>
                      <p className="font-bold text-gray-800">{item.value}</p>
                    </div>
                  ))}
                </div>
              </div>

              <div>
                <h3 className="text-lg font-bold text-gray-800 mb-4 flex items-center gap-2">
                  <FaCheckCircle className="text-green-600" />
                  Week-by-Week Schedule
                </h3>
                <div className="space-y-4">
                  {taperPlan.steps.map((step, index) => (
                    <div 
                      key={index} 
                      className="bg-white border border-gray-100 rounded-2xl p-5 shadow-sm 
                               hover:shadow-lg transition-all duration-300 animate-fade-in"
                      style={{ animationDelay: `${index * 0.1}s` }}
                    >
                      <div className="flex items-start justify-between gap-4">
                        <div className="flex-1">
                          <div className="flex flex-wrap items-center gap-3 mb-4">
                            <span className="bg-gradient-to-r from-indigo-600 to-purple-600 text-white 
                                           px-4 py-1.5 rounded-full text-sm font-bold shadow-md">
                              Week {step.week}
                            </span>
                            <span className="text-xl font-bold text-gray-800">{step.dose}</span>
                            <span className="text-sm text-gray-500 bg-gray-100 px-3 py-1 rounded-full">
                              {step.percentage_of_original}% of original
                            </span>
                          </div>

                          <div className="space-y-3">
                            <div className="bg-gray-50 p-4 rounded-xl">
                              <p className="text-sm font-semibold text-gray-700 mb-1">Instructions:</p>
                              <p className="text-gray-800">{step.instructions}</p>
                            </div>

                            <div className="bg-blue-50 p-4 rounded-xl border border-blue-100">
                              <p className="text-sm font-semibold text-blue-900 mb-1">Monitoring:</p>
                              <p className="text-blue-800 text-sm">{step.monitoring}</p>
                            </div>

                            {step.withdrawal_symptoms_to_watch?.length > 0 && (
                              <div>
                                <p className="text-sm font-semibold text-gray-700 mb-2">Watch for:</p>
                                <div className="flex flex-wrap gap-2">
                                  {step.withdrawal_symptoms_to_watch.map((symptom, idx) => (
                                    <span 
                                      key={idx} 
                                      className="text-xs px-3 py-1.5 bg-amber-100 text-amber-800 
                                               rounded-full border border-amber-200 font-medium"
                                    >
                                      {symptom}
                                    </span>
                                  ))}
                                </div>
                              </div>
                            )}
                          </div>
                        </div>

                        <div className="flex flex-col items-center">
                          <div className="relative w-16 h-16">
                            <svg className="w-full h-full transform -rotate-90">
                              <circle cx="32" cy="32" r="28" stroke="#E5E7EB" strokeWidth="4" fill="none" />
                              <circle
                                cx="32" cy="32" r="28"
                                stroke="url(#progressGradient)"
                                strokeWidth="4"
                                fill="none"
                                strokeDasharray={`${(100 - step.percentage_of_original) * 1.76} 176`}
                                strokeLinecap="round"
                              />
                              <defs>
                                <linearGradient id="progressGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                                  <stop offset="0%" stopColor="#4F46E5" />
                                  <stop offset="100%" stopColor="#7C3AED" />
                                </linearGradient>
                              </defs>
                            </svg>
                            <div className="absolute inset-0 flex items-center justify-center">
                              <span className="text-sm font-bold text-gray-700">
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

              {taperPlan.success_indicators?.length > 0 && (
                <div className="bg-gradient-to-r from-green-50 to-emerald-50 p-5 rounded-2xl border-l-4 border-green-500">
                  <h3 className="text-lg font-bold text-green-900 mb-3 flex items-center gap-2">
                    <FaCheckCircle />
                    Success Indicators
                  </h3>
                  <ul className="space-y-2">
                    {taperPlan.success_indicators.map((indicator, index) => (
                      <li key={index} className="flex items-start text-green-800 gap-2">
                        <span className="text-green-500 mt-1">&#10003;</span>
                        <span>{indicator}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              <div className="bg-gradient-to-r from-amber-50 to-yellow-50 p-5 rounded-2xl border-l-4 border-amber-500">
                <h3 className="text-lg font-bold text-amber-900 mb-3 flex items-center gap-2">
                  <FaPause />
                  When to PAUSE Tapering
                </h3>
                <ul className="space-y-2">
                  {taperPlan.pause_criteria.map((criteria, index) => (
                    <li key={index} className="flex items-start text-amber-800 gap-2">
                      <FaExclamationTriangle className="text-amber-500 mt-1 flex-shrink-0" />
                      <span>{criteria}</span>
                    </li>
                  ))}
                </ul>
              </div>

              <div className="bg-gradient-to-r from-red-50 to-rose-50 p-5 rounded-2xl border-l-4 border-red-500">
                <h3 className="text-lg font-bold text-red-900 mb-3 flex items-center gap-2">
                  <FaUndo />
                  When to REVERSE (Restart Medication)
                </h3>
                <ul className="space-y-2">
                  {taperPlan.reversal_criteria.map((criteria, index) => (
                    <li key={index} className="flex items-start text-red-800 gap-2">
                      <span className="text-red-500 mt-1">&#9888;</span>
                      <span>{criteria}</span>
                    </li>
                  ))}
                </ul>
              </div>

              <div className="bg-gray-50 p-5 rounded-2xl">
                <h3 className="text-lg font-bold text-gray-800 mb-4">Monitoring Schedule</h3>
                <div className="space-y-3">
                  {Object.entries(taperPlan.monitoring_schedule).map(([period, items], index) => (
                    <div key={index} className="bg-white p-4 rounded-xl shadow-sm border-l-4 border-blue-500">
                      <p className="font-bold text-gray-800 mb-2">{period}</p>
                      <ul className="space-y-1">
                        {items.map((item, idx) => (
                          <li key={idx} className="text-sm text-gray-700 flex items-start gap-2">
                            <span className="text-blue-500">&#8226;</span>
                            <span>{item}</span>
                          </li>
                        ))}
                      </ul>
                    </div>
                  ))}
                </div>
              </div>

              <div className="bg-gradient-to-br from-green-50 to-blue-50 p-5 rounded-2xl border border-green-200">
                <h3 className="text-lg font-bold text-gray-800 mb-4">Patient Education</h3>
                <div className="space-y-3">
                  {taperPlan.patient_education.map((education, index) => (
                    <div key={index} className="flex items-start gap-3 bg-white p-4 rounded-xl shadow-sm">
                      <span className="w-7 h-7 bg-gradient-to-br from-indigo-500 to-purple-600 text-white 
                                     rounded-lg flex items-center justify-center text-xs font-bold flex-shrink-0">
                        {index + 1}
                      </span>
                      <p className="text-gray-800">{education}</p>
                    </div>
                  ))}
                </div>
              </div>

              <div className="bg-gray-100 p-4 rounded-xl flex flex-wrap items-center justify-between gap-4">
                <span className="text-sm text-gray-600">Save this schedule for your records</span>
                <div className="flex gap-3">
                  <button
                    onClick={() => window.print()}
                    className="px-4 py-2.5 bg-gradient-to-r from-blue-500 to-blue-600 text-white rounded-xl 
                             font-medium hover:from-blue-600 hover:to-blue-700 transition-all duration-200
                             flex items-center gap-2 shadow-md hover:shadow-lg"
                  >
                    <FaPrint />
                    Print
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
                    className="px-4 py-2.5 bg-gradient-to-r from-green-500 to-emerald-600 text-white rounded-xl 
                             font-medium hover:from-green-600 hover:to-emerald-700 transition-all duration-200
                             flex items-center gap-2 shadow-md hover:shadow-lg"
                  >
                    <FaDownload />
                    Download
                  </button>
                </div>
              </div>
            </div>
          )}
        </div>

        <div className="bg-gray-50 p-4 flex justify-between items-center border-t">
          {isAiGenerated && (
            <span className="text-sm text-gray-500 flex items-center gap-2">
              <FaRobot className="text-purple-600" />
              AI-generated | Verify with healthcare provider
            </span>
          )}
          {!isAiGenerated && <span></span>}
          <button
            onClick={onClose}
            className="px-6 py-2.5 bg-gray-600 text-white rounded-xl font-medium 
                     hover:bg-gray-700 transition-all duration-200 shadow-md"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
};

export default TaperModal;
