import React, { useState } from 'react';
import { FaPills, FaLeaf, FaChevronDown, FaChevronUp, FaCapsules } from 'react-icons/fa';

const MedicationTable = ({ medications, herbs }) => {
  const [showMeds, setShowMeds] = useState(true);
  const [showHerbs, setShowHerbs] = useState(true);

  return (
    <div className="card-medical p-6 mb-6 animate-fade-in-up">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3">
          <div className="w-12 h-12 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-xl 
                        flex items-center justify-center shadow-lg">
            <FaCapsules className="text-2xl text-white" />
          </div>
          <div>
            <h2 className="text-2xl font-bold text-gray-800">Current Medications & Herbs</h2>
            <p className="text-gray-500 text-sm">
              {medications?.length || 0} medications, {herbs?.length || 0} herbal products
            </p>
          </div>
        </div>
      </div>

      {medications && medications.length > 0 && (
        <div className="mb-6 animate-fade-in stagger-1">
          <button
            onClick={() => setShowMeds(!showMeds)}
            className="w-full flex items-center justify-between p-4 bg-gradient-to-r from-blue-50 to-indigo-50 
                     rounded-xl border border-blue-100 hover:border-blue-200 transition-all duration-300 mb-4"
          >
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-blue-600 rounded-lg 
                            flex items-center justify-center shadow-md">
                <FaPills className="text-white" />
              </div>
              <div className="text-left">
                <h3 className="text-lg font-semibold text-gray-800">
                  Allopathic Medications
                </h3>
                <p className="text-sm text-gray-500">{medications.length} active medication(s)</p>
              </div>
            </div>
            <div className={`w-8 h-8 bg-blue-100 rounded-lg flex items-center justify-center 
                          transition-transform duration-300 ${showMeds ? 'rotate-180' : ''}`}>
              <FaChevronDown className="text-blue-600" />
            </div>
          </button>

          {showMeds && (
            <div className="overflow-x-auto rounded-xl border border-gray-100 shadow-sm animate-fade-in">
              <table className="min-w-full divide-y divide-gray-100">
                <thead>
                  <tr className="bg-gradient-to-r from-blue-500 to-indigo-600">
                    <th className="px-5 py-4 text-left text-xs font-bold text-white uppercase tracking-wider">
                      Medication
                    </th>
                    <th className="px-5 py-4 text-left text-xs font-bold text-white uppercase tracking-wider">
                      Dose
                    </th>
                    <th className="px-5 py-4 text-left text-xs font-bold text-white uppercase tracking-wider">
                      Frequency
                    </th>
                    <th className="px-5 py-4 text-left text-xs font-bold text-white uppercase tracking-wider">
                      Duration
                    </th>
                    <th className="px-5 py-4 text-left text-xs font-bold text-white uppercase tracking-wider">
                      Indication
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-50">
                  {medications.map((med, index) => (
                    <tr 
                      key={index} 
                      className="hover:bg-blue-50/50 transition-all duration-200 animate-fade-in"
                      style={{ animationDelay: `${index * 0.05}s` }}
                    >
                      <td className="px-5 py-4">
                        <div className="flex items-center gap-3">
                          <div className="w-8 h-8 bg-gradient-to-br from-blue-100 to-blue-200 
                                        rounded-lg flex items-center justify-center">
                            <FaPills className="text-blue-600 text-sm" />
                          </div>
                          <div>
                            <p className="text-sm font-semibold text-gray-900">{med.generic_name}</p>
                            {med.brand_name && (
                              <p className="text-xs text-gray-500">({med.brand_name})</p>
                            )}
                          </div>
                        </div>
                      </td>
                      <td className="px-5 py-4">
                        <span className="inline-flex items-center px-3 py-1 bg-gray-100 text-gray-800 
                                       text-sm font-medium rounded-lg">
                          {med.dose}
                        </span>
                      </td>
                      <td className="px-5 py-4 text-sm text-gray-700 font-medium">
                        {med.frequency || '-'}
                      </td>
                      <td className="px-5 py-4">
                        <span className="text-sm text-gray-600">
                          {med.duration?.replace('_', ' ') || '-'}
                        </span>
                      </td>
                      <td className="px-5 py-4">
                        <span className="text-sm text-gray-600 line-clamp-2">
                          {med.indication || '-'}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}

      {herbs && herbs.length > 0 && (
        <div className="animate-fade-in stagger-2">
          <button
            onClick={() => setShowHerbs(!showHerbs)}
            className="w-full flex items-center justify-between p-4 bg-gradient-to-r from-green-50 to-emerald-50 
                     rounded-xl border border-green-100 hover:border-green-200 transition-all duration-300 mb-4"
          >
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-gradient-to-br from-green-500 to-emerald-600 rounded-lg 
                            flex items-center justify-center shadow-md">
                <FaLeaf className="text-white" />
              </div>
              <div className="text-left">
                <h3 className="text-lg font-semibold text-gray-800">
                  Ayurvedic / Herbal Products
                </h3>
                <p className="text-sm text-gray-500">{herbs.length} herbal product(s)</p>
              </div>
            </div>
            <div className={`w-8 h-8 bg-green-100 rounded-lg flex items-center justify-center 
                          transition-transform duration-300 ${showHerbs ? 'rotate-180' : ''}`}>
              <FaChevronDown className="text-green-600" />
            </div>
          </button>

          {showHerbs && (
            <div className="overflow-x-auto rounded-xl border border-gray-100 shadow-sm animate-fade-in">
              <table className="min-w-full divide-y divide-gray-100">
                <thead>
                  <tr className="bg-gradient-to-r from-green-500 to-emerald-600">
                    <th className="px-5 py-4 text-left text-xs font-bold text-white uppercase tracking-wider">
                      Herb
                    </th>
                    <th className="px-5 py-4 text-left text-xs font-bold text-white uppercase tracking-wider">
                      Dose
                    </th>
                    <th className="px-5 py-4 text-left text-xs font-bold text-white uppercase tracking-wider">
                      Frequency
                    </th>
                    <th className="px-5 py-4 text-left text-xs font-bold text-white uppercase tracking-wider">
                      Duration
                    </th>
                    <th className="px-5 py-4 text-left text-xs font-bold text-white uppercase tracking-wider">
                      Intended Effect
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-50">
                  {herbs.map((herb, index) => (
                    <tr 
                      key={index} 
                      className="hover:bg-green-50/50 transition-all duration-200 animate-fade-in"
                      style={{ animationDelay: `${index * 0.05}s` }}
                    >
                      <td className="px-5 py-4">
                        <div className="flex items-center gap-3">
                          <div className="w-8 h-8 bg-gradient-to-br from-green-100 to-green-200 
                                        rounded-lg flex items-center justify-center">
                            <FaLeaf className="text-green-600 text-sm" />
                          </div>
                          <div>
                            <p className="text-sm font-semibold text-gray-900">{herb.generic_name}</p>
                            {herb.brand_name && (
                              <p className="text-xs text-gray-500">({herb.brand_name})</p>
                            )}
                          </div>
                        </div>
                      </td>
                      <td className="px-5 py-4">
                        <span className="inline-flex items-center px-3 py-1 bg-gray-100 text-gray-800 
                                       text-sm font-medium rounded-lg">
                          {herb.dose || '-'}
                        </span>
                      </td>
                      <td className="px-5 py-4 text-sm text-gray-700 font-medium">
                        {herb.frequency || '-'}
                      </td>
                      <td className="px-5 py-4">
                        <span className="text-sm text-gray-600">
                          {herb.duration?.replace('_', ' ') || '-'}
                        </span>
                      </td>
                      <td className="px-5 py-4">
                        <span className="text-sm text-gray-600 line-clamp-2">
                          {herb.intended_effect || '-'}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}

      {(!medications || medications.length === 0) && (!herbs || herbs.length === 0) && (
        <div className="text-center py-12 text-gray-500">
          <FaCapsules className="text-5xl mx-auto mb-4 text-gray-300" />
          <p className="font-medium">No medications or herbs added yet</p>
        </div>
      )}
    </div>
  );
};

export default MedicationTable;
