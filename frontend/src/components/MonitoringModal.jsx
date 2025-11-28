import React from 'react';
import { FaTimes, FaHeartbeat } from 'react-icons/fa';

const MonitoringModal = ({ medication, onClose }) => {
  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-hidden">
        {/* Header */}
        <div className="bg-blue-600 text-white p-6 flex justify-between items-center">
          <h2 className="text-2xl font-bold flex items-center">
            <FaHeartbeat className="mr-3" />
            Monitoring Plan - {medication.name}
          </h2>
          <button onClick={onClose} className="text-white hover:text-gray-200">
            <FaTimes size={24} />
          </button>
        </div>

        {/* Content */}
        <div className="p-6 overflow-y-auto max-h-[calc(90vh-80px)]">
          <div className="space-y-6">
            {/* Risk Summary */}
            <div className="bg-gray-50 p-4 rounded-lg">
              <h3 className="text-lg font-semibold text-gray-800 mb-3">Risk Summary</h3>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <p className="text-sm text-gray-600">Risk Category</p>
                  <p className={`font-bold text-lg ${
                    medication.risk_category === 'RED' ? 'text-risk-red' :
                    medication.risk_category === 'YELLOW' ? 'text-risk-yellow' :
                    'text-risk-green'
                  }`}>
                    {medication.risk_category}
                  </p>
                </div>
                <div>
                  <p className="text-sm text-gray-600">Risk Score</p>
                  <p className="font-bold text-lg">{medication.risk_score}/10</p>
                </div>
              </div>
            </div>

            {/* Monitoring Parameters */}
            {medication.monitoring_required && medication.monitoring_required.length > 0 && (
              <div>
                <h3 className="text-lg font-semibold text-gray-800 mb-3">Monitoring Parameters</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                  {medication.monitoring_required.map((param, index) => (
                    <div key={index} className="bg-blue-50 p-3 rounded-lg border-l-4 border-blue-500">
                      <p className="font-medium text-gray-800">{param}</p>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Identified Issues */}
            {medication.flags && medication.flags.length > 0 && (
              <div>
                <h3 className="text-lg font-semibold text-gray-800 mb-3">Identified Issues</h3>
                <ul className="space-y-2">
                  {medication.flags.map((flag, index) => (
                    <li key={index} className="flex items-start text-gray-700 bg-yellow-50 p-3 rounded">
                      <span className="mr-2 text-yellow-600">⚠️</span>
                      <span>{flag}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {/* Monitoring Frequency */}
            <div className="bg-blue-50 p-4 rounded-lg">
              <h3 className="text-lg font-semibold text-gray-800 mb-3">Recommended Monitoring Schedule</h3>
              <div className="space-y-3">
                {medication.risk_category === 'RED' && (
                  <>
                    <div className="border-l-4 border-red-500 pl-4">
                      <p className="font-semibold text-gray-800">Week 1-2</p>
                      <p className="text-gray-700">Daily to every other day assessment</p>
                    </div>
                    <div className="border-l-4 border-orange-500 pl-4">
                      <p className="font-semibold text-gray-800">Week 3-4</p>
                      <p className="text-gray-700">Twice weekly assessment</p>
                    </div>
                    <div className="border-l-4 border-yellow-500 pl-4">
                      <p className="font-semibold text-gray-800">Week 5+</p>
                      <p className="text-gray-700">Weekly until stable</p>
                    </div>
                  </>
                )}
                {medication.risk_category === 'YELLOW' && (
                  <>
                    <div className="border-l-4 border-yellow-500 pl-4">
                      <p className="font-semibold text-gray-800">First Month</p>
                      <p className="text-gray-700">Bi-weekly assessment</p>
                    </div>
                    <div className="border-l-4 border-blue-500 pl-4">
                      <p className="font-semibold text-gray-800">Ongoing</p>
                      <p className="text-gray-700">Monthly review</p>
                    </div>
                  </>
                )}
                {medication.risk_category === 'GREEN' && (
                  <div className="border-l-4 border-green-500 pl-4">
                    <p className="font-semibold text-gray-800">Routine Monitoring</p>
                    <p className="text-gray-700">Every 3-6 months or as clinically indicated</p>
                  </div>
                )}
              </div>
            </div>

            {/* Safety Instructions */}
            <div className="bg-red-50 border-l-4 border-red-500 p-4 rounded">
              <h3 className="text-lg font-semibold text-red-900 mb-3">Safety Instructions</h3>
              <ul className="space-y-2 text-red-800">
                <li>• Contact healthcare provider immediately if concerning symptoms develop</li>
                <li>• Keep a symptom diary for tracking changes</li>
                <li>• Do not adjust doses without medical supervision</li>
                <li>• Report any new medications or supplements started</li>
                {medication.risk_category === 'RED' && (
                  <li className="font-semibold">• This is a HIGH PRIORITY medication - enhanced vigilance required</li>
                )}
              </ul>
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="bg-gray-50 p-4 flex justify-end space-x-3">
          <button
            onClick={() => window.print()}
            className="px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition"
          >
            Print Plan
          </button>
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

export default MonitoringModal;
