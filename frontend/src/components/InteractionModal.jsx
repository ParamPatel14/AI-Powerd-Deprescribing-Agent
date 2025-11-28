import React from 'react';
import { FaTimes, FaFlask } from 'react-icons/fa';

const InteractionModal = ({ interaction, onClose }) => {
  const severityColors = {
    'Major': 'bg-red-100 text-red-800 border-red-500',
    'Moderate': 'bg-yellow-100 text-yellow-800 border-yellow-500',
    'Minor': 'bg-gray-100 text-gray-800 border-gray-500'
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-hidden">
        {/* Header */}
        <div className="bg-purple-600 text-white p-6 flex justify-between items-center">
          <h2 className="text-2xl font-bold flex items-center">
            <FaFlask className="mr-3" />
            Herb-Drug Interaction Details
          </h2>
          <button onClick={onClose} className="text-white hover:text-gray-200">
            <FaTimes size={24} />
          </button>
        </div>

        {/* Content */}
        <div className="p-6 overflow-y-auto max-h-[calc(90vh-80px)]">
          <div className="space-y-6">
            {/* Interaction Pair */}
            <div className="bg-gradient-to-r from-green-50 to-blue-50 p-4 rounded-lg">
              <div className="text-center">
                <p className="text-2xl font-bold text-gray-800">
                  {interaction.herb}
                  <span className="mx-3 text-purple-600">+</span>
                  {interaction.drug}
                </p>
              </div>
            </div>

            {/* Severity & Evidence */}
            <div className="flex space-x-4">
              <div className={`flex-1 p-4 rounded-lg border-2 ${severityColors[interaction.severity]}`}>
                <p className="text-sm font-medium mb-1">Severity</p>
                <p className="text-xl font-bold">{interaction.severity}</p>
              </div>
              <div className="flex-1 p-4 rounded-lg border-2 bg-blue-50 text-blue-800 border-blue-500">
                <p className="text-sm font-medium mb-1">Evidence Strength</p>
                <p className="text-xl font-bold capitalize">{interaction.evidence}</p>
              </div>
            </div>

            {/* Clinical Effect */}
            <div>
              <h3 className="text-lg font-semibold text-gray-800 mb-2">Clinical Effect</h3>
              <p className="text-gray-700 bg-gray-50 p-4 rounded-lg">{interaction.effect}</p>
            </div>

            {/* Mechanism (if available from full data) */}
            <div>
              <h3 className="text-lg font-semibold text-gray-800 mb-2">Mechanism</h3>
              <p className="text-gray-700 bg-gray-50 p-4 rounded-lg">
                {interaction.mechanism || 'Pharmacodynamic or pharmacokinetic interaction possible'}
              </p>
            </div>

            {/* Recommendations */}
            <div className="bg-blue-50 border-l-4 border-blue-500 p-4 rounded">
              <h3 className="text-lg font-semibold text-blue-900 mb-3">Clinical Recommendations</h3>
              {interaction.severity === 'Major' && (
                <div className="space-y-2 text-blue-800">
                  <p>• <strong>AVOID</strong> this combination if possible</p>
                  <p>• Discontinue the herbal product or consider alternative medication</p>
                  <p>• If continuation is necessary, implement intensive monitoring</p>
                  <p>• Consult with prescribing physician immediately</p>
                </div>
              )}
              {interaction.severity === 'Moderate' && (
                <div className="space-y-2 text-yellow-800">
                  <p>• Use with <strong>CAUTION</strong></p>
                  <p>• Implement enhanced monitoring protocols</p>
                  <p>• Consider dose adjustment or timing separation</p>
                  <p>• Patient education about warning signs</p>
                </div>
              )}
              {interaction.severity === 'Minor' && (
                <div className="space-y-2 text-gray-700">
                  <p>• Generally safe to continue</p>
                  <p>• Routine monitoring recommended</p>
                  <p>• Inform patient of possible mild effects</p>
                </div>
              )}
            </div>

            {/* Evidence Note */}
            {interaction.evidence === 'simulated' && (
              <div className="bg-yellow-50 border border-yellow-300 p-4 rounded-lg">
                <p className="text-sm text-yellow-800">
                  <strong>Note:</strong> This interaction is based on AI simulation using pharmacological profiles.
                  Clinical evidence may be limited. Use clinical judgment and consider consulting a pharmacist or
                  clinical decision support specialist.
                </p>
              </div>
            )}
          </div>
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

export default InteractionModal;
