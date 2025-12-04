import React from 'react';
import { FaTimes, FaFlask, FaExclamationTriangle, FaInfoCircle, FaShieldAlt } from 'react-icons/fa';

const InteractionModal = ({ interaction, onClose }) => {
  const severityConfig = {
    'Major': {
      bg: 'from-red-500 to-rose-600',
      light: 'from-red-50 to-rose-50',
      border: 'border-red-400',
      text: 'text-red-800',
      badge: 'bg-red-100 text-red-700',
    },
    'Moderate': {
      bg: 'from-amber-400 to-orange-500',
      light: 'from-amber-50 to-yellow-50',
      border: 'border-amber-400',
      text: 'text-amber-800',
      badge: 'bg-amber-100 text-amber-700',
    },
    'Minor': {
      bg: 'from-gray-400 to-slate-500',
      light: 'from-gray-50 to-slate-50',
      border: 'border-gray-400',
      text: 'text-gray-700',
      badge: 'bg-gray-100 text-gray-700',
    },
  };

  const config = severityConfig[interaction.severity] || severityConfig['Minor'];

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
                <FaFlask className="text-2xl" />
              </div>
              <div>
                <h2 className="text-2xl font-bold">Herb-Drug Interaction</h2>
                <p className="text-white/80 mt-1">Detailed Analysis</p>
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
          <div className={`bg-gradient-to-r ${config.light} p-6 rounded-2xl border ${config.border}`}>
            <div className="text-center">
              <p className="text-3xl font-bold text-gray-800 flex items-center justify-center gap-4">
                <span className="text-green-600">{interaction.herb}</span>
                <span className="text-2xl text-purple-500">+</span>
                <span className="text-blue-600">{interaction.drug}</span>
              </p>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div className={`bg-gradient-to-br ${config.light} p-5 rounded-2xl border-2 ${config.border}`}>
              <div className="flex items-center gap-2 mb-2">
                <FaExclamationTriangle className={config.text} />
                <p className="text-sm font-semibold text-gray-600">Severity Level</p>
              </div>
              <p className={`text-2xl font-bold ${config.text}`}>{interaction.severity}</p>
            </div>
            <div className="bg-gradient-to-br from-blue-50 to-indigo-50 p-5 rounded-2xl border-2 border-blue-200">
              <div className="flex items-center gap-2 mb-2">
                <FaInfoCircle className="text-blue-600" />
                <p className="text-sm font-semibold text-gray-600">Evidence Strength</p>
              </div>
              <p className="text-2xl font-bold text-blue-700 capitalize">{interaction.evidence}</p>
            </div>
          </div>

          <div className="bg-gray-50 p-5 rounded-2xl">
            <h3 className="text-lg font-bold text-gray-800 mb-3 flex items-center gap-2">
              <FaShieldAlt className="text-purple-600" />
              Clinical Effect
            </h3>
            <p className="text-gray-700 bg-white p-4 rounded-xl border border-gray-100 shadow-sm">
              {interaction.effect}
            </p>
          </div>

          <div className="bg-gray-50 p-5 rounded-2xl">
            <h3 className="text-lg font-bold text-gray-800 mb-3">Mechanism</h3>
            <p className="text-gray-700 bg-white p-4 rounded-xl border border-gray-100 shadow-sm">
              {interaction.mechanism || 'Pharmacodynamic or pharmacokinetic interaction possible'}
            </p>
          </div>

          <div className={`bg-gradient-to-r ${config.light} p-5 rounded-2xl border-l-4 ${config.border}`}>
            <h3 className={`text-lg font-bold ${config.text} mb-4 flex items-center gap-2`}>
              <FaShieldAlt />
              Clinical Recommendations
            </h3>
            
            {interaction.severity === 'Major' && (
              <ul className="space-y-3">
                {[
                  { text: 'AVOID this combination if possible', bold: true },
                  { text: 'Discontinue the herbal product or consider alternative medication' },
                  { text: 'If continuation is necessary, implement intensive monitoring' },
                  { text: 'Consult with prescribing physician immediately' },
                ].map((item, i) => (
                  <li key={i} className="flex items-start gap-3 text-red-800">
                    <span className="w-6 h-6 bg-red-200 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5">
                      <span className="text-red-700 text-xs font-bold">{i + 1}</span>
                    </span>
                    <span className={item.bold ? 'font-bold' : ''}>{item.text}</span>
                  </li>
                ))}
              </ul>
            )}
            
            {interaction.severity === 'Moderate' && (
              <ul className="space-y-3">
                {[
                  { text: 'Use with CAUTION', bold: true },
                  { text: 'Implement enhanced monitoring protocols' },
                  { text: 'Consider dose adjustment or timing separation' },
                  { text: 'Patient education about warning signs' },
                ].map((item, i) => (
                  <li key={i} className="flex items-start gap-3 text-amber-800">
                    <span className="w-6 h-6 bg-amber-200 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5">
                      <span className="text-amber-700 text-xs font-bold">{i + 1}</span>
                    </span>
                    <span className={item.bold ? 'font-bold' : ''}>{item.text}</span>
                  </li>
                ))}
              </ul>
            )}
            
            {interaction.severity === 'Minor' && (
              <ul className="space-y-3">
                {[
                  { text: 'Generally safe to continue' },
                  { text: 'Routine monitoring recommended' },
                  { text: 'Inform patient of possible mild effects' },
                ].map((item, i) => (
                  <li key={i} className="flex items-start gap-3 text-gray-700">
                    <span className="w-6 h-6 bg-gray-200 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5">
                      <span className="text-gray-600 text-xs font-bold">{i + 1}</span>
                    </span>
                    <span>{item.text}</span>
                  </li>
                ))}
              </ul>
            )}
          </div>

          {interaction.evidence === 'simulated' && (
            <div className="bg-gradient-to-r from-amber-50 to-yellow-50 border border-amber-200 p-5 rounded-2xl">
              <div className="flex items-start gap-3">
                <FaInfoCircle className="text-amber-500 text-xl flex-shrink-0 mt-0.5" />
                <div>
                  <p className="font-bold text-amber-800 mb-1">AI-Simulated Interaction</p>
                  <p className="text-sm text-amber-700">
                    This interaction is based on AI simulation using pharmacological profiles.
                    Clinical evidence may be limited. Use clinical judgment and consider consulting 
                    a pharmacist or clinical decision support specialist.
                  </p>
                </div>
              </div>
            </div>
          )}
        </div>

        <div className="bg-gray-50 p-4 flex justify-end border-t">
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

export default InteractionModal;
