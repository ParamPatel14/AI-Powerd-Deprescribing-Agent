import React from 'react';
import { FaTimes, FaHeartbeat, FaPrint, FaExclamationTriangle, FaCalendarAlt, FaShieldAlt } from 'react-icons/fa';

const MonitoringModal = ({ medication, onClose }) => {
  const riskConfig = {
    'RED': {
      bg: 'from-red-500 to-rose-600',
      light: 'from-red-50 to-rose-50',
      border: 'border-red-400',
      text: 'text-red-600',
      badge: 'bg-red-100 text-red-700',
    },
    'YELLOW': {
      bg: 'from-amber-400 to-orange-500',
      light: 'from-amber-50 to-yellow-50',
      border: 'border-amber-400',
      text: 'text-amber-600',
      badge: 'bg-amber-100 text-amber-700',
    },
    'GREEN': {
      bg: 'from-emerald-500 to-green-600',
      light: 'from-green-50 to-emerald-50',
      border: 'border-green-400',
      text: 'text-emerald-600',
      badge: 'bg-green-100 text-green-700',
    },
  };

  const config = riskConfig[medication.risk_category] || riskConfig['GREEN'];

  return (
    <div className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-50 p-4 modal-overlay">
      <div className="bg-white rounded-3xl shadow-2xl max-w-2xl w-full max-h-[90vh] overflow-hidden modal-content">
        <div className={`bg-gradient-to-r ${config.bg} text-white p-6 relative overflow-hidden`}>
          <div className="absolute inset-0 overflow-hidden">
            <div className="absolute -top-1/2 -right-1/4 w-64 h-64 bg-white/10 rounded-full blur-3xl"></div>
          </div>
          
          <div className="relative flex justify-between items-start">
            <div className="flex items-center gap-4">
              <div className="w-14 h-14 bg-white/20 backdrop-blur-sm rounded-2xl flex items-center justify-center border border-white/30">
                <FaHeartbeat className="text-2xl" />
              </div>
              <div>
                <h2 className="text-2xl font-bold">Monitoring Plan</h2>
                <p className="text-white/80 mt-1">{medication.name}</p>
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

        <div className="p-6 overflow-y-auto max-h-[calc(90vh-160px)] space-y-6 animate-fade-in">
          <div className={`bg-gradient-to-br ${config.light} p-5 rounded-2xl border ${config.border}`}>
            <h3 className="text-lg font-bold text-gray-800 mb-4">Risk Summary</h3>
            <div className="grid grid-cols-2 gap-4">
              <div className="bg-white p-4 rounded-xl shadow-sm">
                <p className="text-sm text-gray-500 mb-1">Risk Category</p>
                <p className={`text-2xl font-bold ${config.text}`}>
                  {medication.risk_category}
                </p>
              </div>
              <div className="bg-white p-4 rounded-xl shadow-sm">
                <p className="text-sm text-gray-500 mb-1">Risk Score</p>
                <p className="text-2xl font-bold text-gray-800">
                  {medication.risk_score}<span className="text-lg text-gray-400">/10</span>
                </p>
              </div>
            </div>
          </div>

          {medication.monitoring_required?.length > 0 && (
            <div className="bg-gray-50 p-5 rounded-2xl">
              <h3 className="text-lg font-bold text-gray-800 mb-4 flex items-center gap-2">
                <FaShieldAlt className="text-blue-600" />
                Monitoring Parameters
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                {medication.monitoring_required.map((param, index) => (
                  <div 
                    key={index} 
                    className="bg-white p-4 rounded-xl border-l-4 border-blue-500 shadow-sm
                             hover:shadow-md transition-all duration-200"
                  >
                    <p className="font-medium text-gray-800">{param}</p>
                  </div>
                ))}
              </div>
            </div>
          )}

          {medication.flags?.length > 0 && (
            <div className="bg-gradient-to-r from-amber-50 to-yellow-50 p-5 rounded-2xl border-l-4 border-amber-500">
              <h3 className="text-lg font-bold text-amber-800 mb-4 flex items-center gap-2">
                <FaExclamationTriangle />
                Identified Issues
              </h3>
              <ul className="space-y-2">
                {medication.flags.map((flag, index) => (
                  <li key={index} className="flex items-start gap-3 text-amber-800 bg-white p-3 rounded-xl">
                    <FaExclamationTriangle className="text-amber-500 mt-0.5 flex-shrink-0" />
                    <span>{flag}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}

          <div className="bg-gradient-to-br from-blue-50 to-indigo-50 p-5 rounded-2xl border border-blue-100">
            <h3 className="text-lg font-bold text-gray-800 mb-4 flex items-center gap-2">
              <FaCalendarAlt className="text-blue-600" />
              Recommended Monitoring Schedule
            </h3>
            <div className="space-y-3">
              {medication.risk_category === 'RED' && (
                <>
                  {[
                    { period: 'Week 1-2', schedule: 'Daily to every other day assessment', color: 'red' },
                    { period: 'Week 3-4', schedule: 'Twice weekly assessment', color: 'orange' },
                    { period: 'Week 5+', schedule: 'Weekly until stable', color: 'yellow' },
                  ].map((item, i) => (
                    <div key={i} className={`bg-white p-4 rounded-xl border-l-4 border-${item.color}-500 shadow-sm`}>
                      <p className="font-bold text-gray-800">{item.period}</p>
                      <p className="text-gray-600">{item.schedule}</p>
                    </div>
                  ))}
                </>
              )}
              {medication.risk_category === 'YELLOW' && (
                <>
                  {[
                    { period: 'First Month', schedule: 'Bi-weekly assessment', color: 'amber' },
                    { period: 'Ongoing', schedule: 'Monthly review', color: 'blue' },
                  ].map((item, i) => (
                    <div key={i} className="bg-white p-4 rounded-xl border-l-4 border-amber-500 shadow-sm">
                      <p className="font-bold text-gray-800">{item.period}</p>
                      <p className="text-gray-600">{item.schedule}</p>
                    </div>
                  ))}
                </>
              )}
              {medication.risk_category === 'GREEN' && (
                <div className="bg-white p-4 rounded-xl border-l-4 border-green-500 shadow-sm">
                  <p className="font-bold text-gray-800">Routine Monitoring</p>
                  <p className="text-gray-600">Every 3-6 months or as clinically indicated</p>
                </div>
              )}
            </div>
          </div>

          <div className="bg-gradient-to-r from-red-50 to-rose-50 p-5 rounded-2xl border-l-4 border-red-500">
            <h3 className="text-lg font-bold text-red-900 mb-4 flex items-center gap-2">
              <FaExclamationTriangle />
              Safety Instructions
            </h3>
            <ul className="space-y-2">
              {[
                'Contact healthcare provider immediately if concerning symptoms develop',
                'Keep a symptom diary for tracking changes',
                'Do not adjust doses without medical supervision',
                'Report any new medications or supplements started',
                ...(medication.risk_category === 'RED' 
                  ? ['This is a HIGH PRIORITY medication - enhanced vigilance required'] 
                  : [])
              ].map((instruction, index) => (
                <li 
                  key={index} 
                  className={`flex items-start gap-3 text-red-800 bg-white p-3 rounded-xl
                            ${index === 4 ? 'font-bold border-2 border-red-200' : ''}`}
                >
                  <span className="text-red-500 mt-0.5">&#9888;</span>
                  <span>{instruction}</span>
                </li>
              ))}
            </ul>
          </div>
        </div>

        <div className="bg-gray-50 p-4 flex justify-end gap-3 border-t">
          <button
            onClick={() => window.print()}
            className="px-5 py-2.5 bg-gradient-to-r from-blue-500 to-blue-600 text-white rounded-xl 
                     font-medium hover:from-blue-600 hover:to-blue-700 transition-all duration-200
                     flex items-center gap-2 shadow-md"
          >
            <FaPrint />
            Print Plan
          </button>
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

export default MonitoringModal;
