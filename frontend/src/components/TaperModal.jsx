import React, { useState, useEffect } from 'react';
import { FaTimes, FaSpinner } from 'react-icons/fa';
import { getTaperPlan } from '../services/api';

const TaperModal = ({ medication, patientData, onClose }) => {
  const [taperPlan, setTaperPlan] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchTaperPlan = async () => {
      try {
        setLoading(true);
        // Find the medication in patient data
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
        {/* Header */}
        <div className="bg-indigo-600 text-white p-6 flex justify-between items-center">
          <h2 className="text-2xl font-bold">Tapering Schedule - {medication.name}</h2>
          <button onClick={onClose} className="text-white hover:text-gray-200">
            <FaTimes size={24} />
          </button>
        </div>

        {/* Content */}
        <div className="p-6 overflow-y-auto max-h-[calc(90vh-80px)]">
          {loading && (
            <div className="flex items-center justify-center py-12">
              <FaSpinner className="animate-spin text-indigo-600 text-4xl" />
              <span className="ml-3 text-gray-600">Loading taper plan...</span>
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

              {/* Week-by-Week Schedule */}
              <div>
                <h3 className="text-lg font-semibold text-gray-800 mb-3">Week-by-Week Schedule</h3>
                <div className="space-y-3">
                  {taperPlan.steps.map((step, index) => (
                    <div key={index} className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition">
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <div className="flex items-center space-x-3 mb-2">
                            <span className="bg-indigo-600 text-white px-3 py-1 rounded-full text-sm font-semibold">
                              Week {step.week}
                            </span>
                            <span className="text-lg font-bold text-gray-800">{step.dose}</span>
                            <span className="text-sm text-gray-600">({step.percentage_of_original}% of original)</span>
                          </div>
                          <p className="text-gray-700 mb-2">{step.instructions}</p>
                          <p className="text-sm text-gray-600">
                            <span className="font-medium">Monitoring:</span> {step.monitoring}
                          </p>
                          {step.withdrawal_symptoms_to_watch.length > 0 && (
                            <div className="mt-2">
                              <p className="text-sm font-medium text-gray-700">Watch for:</p>
                              <div className="flex flex-wrap gap-2 mt-1">
                                {step.withdrawal_symptoms_to_watch.map((symptom, idx) => (
                                  <span key={idx} className="text-xs px-2 py-1 bg-yellow-100 text-yellow-800 rounded">
                                    {symptom}
                                  </span>
                                ))}
                              </div>
                            </div>
                          )}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Pause Criteria */}
              <div className="bg-yellow-50 p-4 rounded-lg">
                <h3 className="text-lg font-semibold text-gray-800 mb-3">When to PAUSE Tapering</h3>
                <ul className="space-y-2">
                  {taperPlan.pause_criteria.map((criteria, index) => (
                    <li key={index} className="flex items-start text-gray-700">
                      <span className="mr-2">⚠️</span>
                      <span>{criteria}</span>
                    </li>
                  ))}
                </ul>
              </div>

              {/* Reversal Criteria */}
              <div className="bg-red-50 p-4 rounded-lg">
                <h3 className="text-lg font-semibold text-gray-800 mb-3">When to REVERSE (Restart Medication)</h3>
                <ul className="space-y-2">
                  {taperPlan.reversal_criteria.map((criteria, index) => (
                    <li key={index} className="flex items-start text-gray-700">
                      <span className="mr-2">🚨</span>
                      <span>{criteria}</span>
                    </li>
                  ))}
                </ul>
              </div>

              {/* Monitoring Schedule */}
              <div>
                <h3 className="text-lg font-semibold text-gray-800 mb-3">Monitoring Schedule</h3>
                <div className="space-y-3">
                  {Object.entries(taperPlan.monitoring_schedule).map(([period, items], index) => (
                    <div key={index} className="border-l-4 border-blue-500 pl-4">
                      <p className="font-semibold text-gray-800 mb-2">{period}</p>
                      <ul className="space-y-1">
                        {items.map((item, idx) => (
                          <li key={idx} className="text-sm text-gray-600">• {item}</li>
                        ))}
                      </ul>
                    </div>
                  ))}
                </div>
              </div>

              {/* Patient Education */}
              <div className="bg-green-50 p-4 rounded-lg">
                <h3 className="text-lg font-semibold text-gray-800 mb-3">Patient Education</h3>
                <ul className="space-y-2">
                  {taperPlan.patient_education.map((education, index) => (
                    <li key={index} className="flex items-start text-gray-700">
                      <span className="mr-2">📋</span>
                      <span>{education}</span>
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="bg-gray-50 p-4 flex justify-end">
          <button
            onClick={onClose}
            className="px-6 py-2 bg-gray-600 text-white rounded-md hover:bg-gray-700 transition"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
};

export default TaperModal;
