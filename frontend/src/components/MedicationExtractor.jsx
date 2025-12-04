import React, { useState } from 'react';
import { FaUpload, FaTrash, FaCheckCircle, FaCamera, FaRobot, FaMagic } from 'react-icons/fa';
import Select from 'react-select';
import CreatableSelect from 'react-select/creatable';
import axios from 'axios';
import {
  FREQUENCY_OPTIONS,
  INDICATION_OPTIONS,
} from '../utils/medicationOptions';
import {
  DURATION_OPTIONS, 
} from '../utils/constants';


const MedicationExtractor = ({ onMedicationsExtracted }) => {
  const [extractedMeds, setExtractedMeds] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [uploadType, setUploadType] = useState('prescription');

  const handleFileUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    setIsLoading(true);
    const formData = new FormData();
    formData.append('file', file);

    try {
      const endpoint = uploadType === 'prescription' 
        ? '/extract-from-prescription'
        : '/extract-brown-bag';
      
      const response = await axios.post(`http://localhost:8000${endpoint}`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });

      setExtractedMeds(response.data.medications.map((med, idx) => ({
        ...med,
        id: idx,
        isEditing: false
      })));
    } catch (error) {
      alert('Error extracting medications: ' + error.message);
    } finally {
      setIsLoading(false);
    }
  };

  const handleEdit = (id, field, value) => {
    setExtractedMeds(meds =>
      meds.map(m => m.id === id ? { ...m, [field]: value } : m)
    );
  };

  const handleDelete = (id) => {
    setExtractedMeds(meds => meds.filter(m => m.id !== id));
  };

  const handleConfirm = () => {
    const formatted = extractedMeds.map(m => ({
      generic_name: m.generic_name,
      brand_name: m.brand_name || '',
      dose: m.dose,
      frequency: m.frequency,
      indication: m.indication || '',
      duration: m.duration || 'unknown'
    }));
    onMedicationsExtracted(formatted);
  };

  return (
    <div className="bg-gradient-to-r from-purple-50 via-indigo-50 to-blue-50 p-6 rounded-2xl border-2 border-purple-200 mb-8 
                  shadow-lg hover:shadow-xl transition-all duration-300">
      <div className="flex items-center gap-4 mb-6">
        <div className="w-14 h-14 bg-gradient-to-br from-purple-500 to-indigo-600 rounded-2xl 
                      flex items-center justify-center shadow-lg">
          <FaRobot className="text-2xl text-white" />
        </div>
        <div>
          <h3 className="text-xl font-bold text-purple-900 flex items-center gap-2">
            AI Medication Extraction
            <span className="text-xs bg-purple-200 text-purple-700 px-2 py-1 rounded-full font-medium">
              BETA
            </span>
          </h3>
          <p className="text-purple-600 text-sm">Upload prescription or photo to auto-extract medications</p>
        </div>
      </div>

      <div className="grid grid-cols-2 gap-4 mb-6">
        <button
          type="button"
          onClick={() => setUploadType('prescription')}
          className={`p-4 rounded-xl border-2 transition-all duration-300 flex items-center gap-3 ${
            uploadType === 'prescription'
              ? 'bg-gradient-to-r from-purple-500 to-indigo-600 text-white border-purple-600 shadow-lg scale-[1.02]'
              : 'bg-white text-gray-700 border-gray-200 hover:border-purple-300 hover:bg-purple-50'
          }`}
        >
          <div className={`w-10 h-10 rounded-xl flex items-center justify-center ${
            uploadType === 'prescription' ? 'bg-white/20' : 'bg-purple-100'
          }`}>
            <FaUpload className={uploadType === 'prescription' ? 'text-white' : 'text-purple-600'} />
          </div>
          <div className="text-left">
            <p className="font-bold">Prescription Upload</p>
            <p className={`text-xs ${uploadType === 'prescription' ? 'text-purple-100' : 'text-gray-500'}`}>
              PDF or image file
            </p>
          </div>
        </button>

        <button
          type="button"
          onClick={() => setUploadType('brown-bag')}
          className={`p-4 rounded-xl border-2 transition-all duration-300 flex items-center gap-3 ${
            uploadType === 'brown-bag'
              ? 'bg-gradient-to-r from-purple-500 to-indigo-600 text-white border-purple-600 shadow-lg scale-[1.02]'
              : 'bg-white text-gray-700 border-gray-200 hover:border-purple-300 hover:bg-purple-50'
          }`}
        >
          <div className={`w-10 h-10 rounded-xl flex items-center justify-center ${
            uploadType === 'brown-bag' ? 'bg-white/20' : 'bg-purple-100'
          }`}>
            <FaCamera className={uploadType === 'brown-bag' ? 'text-white' : 'text-purple-600'} />
          </div>
          <div className="text-left">
            <p className="font-bold">Brown Bag Photo</p>
            <p className={`text-xs ${uploadType === 'brown-bag' ? 'text-purple-100' : 'text-gray-500'}`}>
              Photo of medications
            </p>
          </div>
        </button>
      </div>

      <div className="mb-6">
        <label className="block w-full p-6 border-2 border-dashed border-purple-300 rounded-2xl 
                       hover:border-purple-500 cursor-pointer bg-white transition-all duration-300
                       hover:bg-purple-50 hover:shadow-md group">
          <input
            type="file"
            accept={uploadType === 'prescription' ? '.pdf,.jpg,.jpeg,.png' : 'image/*'}
            onChange={handleFileUpload}
            className="hidden"
            disabled={isLoading}
          />
          <div className="text-center">
            {isLoading ? (
              <div className="py-4">
                <div className="relative inline-block mb-4">
                  <div className="w-16 h-16 rounded-full bg-purple-100 flex items-center justify-center">
                    <FaMagic className="text-2xl text-purple-600 animate-pulse" />
                  </div>
                  <div className="absolute inset-0">
                    <svg className="w-16 h-16 animate-spin" style={{ animationDuration: '2s' }}>
                      <circle cx="32" cy="32" r="30" stroke="#7C3AED" strokeWidth="3" 
                              fill="none" strokeDasharray="50 150" strokeLinecap="round" />
                    </svg>
                  </div>
                </div>
                <p className="text-purple-700 font-bold">AI is analyzing your file...</p>
                <p className="text-purple-500 text-sm mt-1">Extracting medication information</p>
              </div>
            ) : (
              <>
                <div className="w-16 h-16 mx-auto mb-4 bg-gradient-to-br from-purple-100 to-indigo-100 
                              rounded-2xl flex items-center justify-center group-hover:scale-110 transition-transform">
                  <FaUpload className="text-2xl text-purple-600" />
                </div>
                <p className="text-purple-800 font-bold mb-1">
                  Click to upload {uploadType === 'prescription' ? 'prescription (PDF/Image)' : 'photo of medications'}
                </p>
                <p className="text-purple-500 text-sm">or drag and drop your file here</p>
              </>
            )}
          </div>
        </label>
      </div>

      {extractedMeds.length > 0 && (
        <div className="bg-white p-5 rounded-2xl shadow-lg border border-purple-100 animate-fade-in">
          <div className="flex items-center justify-between mb-4">
            <h4 className="font-bold text-gray-800 flex items-center gap-2">
              <FaCheckCircle className="text-green-500" />
              Extracted {extractedMeds.length} Medication(s)
            </h4>
            <span className="text-xs bg-green-100 text-green-700 px-3 py-1 rounded-full font-medium">
              Review & Edit
            </span>
          </div>

          <div className="space-y-4 mb-5 max-h-96 overflow-y-auto">
            {extractedMeds.map((med) => (
              <MedicationCard
                key={med.id}
                med={med}
                onEdit={handleEdit}
                onDelete={handleDelete}
              />
            ))}
          </div>

          <button
            type="button"
            onClick={handleConfirm}
            className="w-full py-4 bg-gradient-to-r from-green-500 to-emerald-600 text-white rounded-xl 
                     hover:from-green-600 hover:to-emerald-700 font-bold flex items-center justify-center gap-2
                     shadow-lg hover:shadow-xl transition-all duration-300 hover:scale-[1.02]"
          >
            <FaCheckCircle />
            Confirm & Add All Medications
          </button>
        </div>
      )}
    </div>
  );
};

const MedicationCard = ({ med, onEdit, onDelete }) => {
  const confidenceColors = {
    high: 'bg-green-100 text-green-700 border-green-200',
    medium: 'bg-amber-100 text-amber-700 border-amber-200',
    low: 'bg-red-100 text-red-700 border-red-200'
  };

  const confidenceClass = confidenceColors[med.confidence] || 'bg-gray-100 text-gray-700 border-gray-200';

  const selectStyles = {
    control: (base, state) => ({
      ...base,
      borderColor: state.isFocused ? '#7C3AED' : '#E5E7EB',
      boxShadow: state.isFocused ? '0 0 0 2px rgba(124, 58, 237, 0.15)' : 'none',
      borderRadius: '10px',
      minHeight: '40px',
    }),
    menu: (base) => ({
      ...base,
      borderRadius: '10px',
      boxShadow: '0 10px 40px rgba(0, 0, 0, 0.15)',
    }),
  };

  return (
    <div className="border border-gray-200 rounded-xl p-5 hover:shadow-lg transition-all duration-300 bg-gradient-to-br from-white to-gray-50">
      <div className="flex justify-between items-start mb-4">
        <div className="flex-1 mr-4">
          <label className="block text-sm font-semibold text-gray-700 mb-2">
            Generic Name <span className="text-red-500">*</span>
          </label>
          <input
            type="text"
            value={med.generic_name}
            onChange={(e) => onEdit(med.id, 'generic_name', e.target.value)}
            className="w-full px-4 py-2.5 border-2 border-gray-200 rounded-xl 
                     focus:ring-2 focus:ring-purple-500 focus:border-purple-500 outline-none
                     transition-all duration-200"
            placeholder="Enter generic name"
          />
          {med.position && (
            <span className="text-xs text-gray-500 mt-1 block">
              Position: {med.position}
            </span>
          )}
        </div>

        <div className="flex gap-2 items-start">
          <span className={`text-xs px-3 py-1.5 rounded-full font-medium border ${confidenceClass}`}>
            {med.confidence || 'unknown'}
          </span>
          <button 
            type="button"
            onClick={() => onDelete(med.id)} 
            className="w-9 h-9 bg-red-50 hover:bg-red-100 text-red-600 rounded-xl 
                     flex items-center justify-center transition-all duration-200 hover:scale-110"
            title="Delete medication"
          >
            <FaTrash className="text-sm" />
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-semibold text-gray-700 mb-2">Brand Name</label>
          <input
            type="text"
            value={med.brand_name || ''}
            onChange={(e) => onEdit(med.id, 'brand_name', e.target.value)}
            placeholder="Optional"
            className="w-full px-4 py-2.5 border-2 border-gray-200 rounded-xl 
                     focus:ring-2 focus:ring-purple-500 focus:border-purple-500"
          />
        </div>

        <div>
          <label className="block text-sm font-semibold text-gray-700 mb-2">
            Dose <span className="text-red-500">*</span>
          </label>
          <input
            type="text"
            value={med.dose}
            onChange={(e) => onEdit(med.id, 'dose', e.target.value)}
            placeholder="e.g., 500 mg"
            className="w-full px-4 py-2.5 border-2 border-gray-200 rounded-xl 
                     focus:ring-2 focus:ring-purple-500 focus:border-purple-500"
          />
        </div>

        <div>
          <label className="block text-sm font-semibold text-gray-700 mb-2">
            Frequency <span className="text-red-500">*</span>
          </label>
          <CreatableSelect
            options={FREQUENCY_OPTIONS}
            value={FREQUENCY_OPTIONS.find(opt => opt.value === med.frequency) || 
                   (med.frequency ? { value: med.frequency, label: med.frequency } : null)}
            onChange={(option) => onEdit(med.id, 'frequency', option?.value || '')}
            placeholder="Select..."
            isClearable
            styles={selectStyles}
          />
        </div>

        <div>
          <label className="block text-sm font-semibold text-gray-700 mb-2">Duration</label>
          <Select
            options={DURATION_OPTIONS}
            value={DURATION_OPTIONS.find(opt => opt.value === med.duration)}
            onChange={(option) => onEdit(med.id, 'duration', option?.value || 'unknown')}
            placeholder="Select..."
            styles={selectStyles}
          />
        </div>

        <div className="md:col-span-2">
          <label className="block text-sm font-semibold text-gray-700 mb-2">Indication</label>
          <CreatableSelect
            options={INDICATION_OPTIONS}
            value={INDICATION_OPTIONS.find(opt => opt.value === med.indication) || 
                   (med.indication ? { value: med.indication, label: med.indication } : null)}
            onChange={(option) => onEdit(med.id, 'indication', option?.value || '')}
            placeholder="What is it for?"
            isClearable
            styles={selectStyles}
          />
        </div>
      </div>

      {med.notes && (
        <div className="mt-4 p-4 bg-gradient-to-r from-blue-50 to-indigo-50 border border-blue-200 rounded-xl">
          <p className="text-xs font-bold text-blue-900 mb-1">AI Extraction Notes:</p>
          <p className="text-sm text-blue-700 italic">{med.notes}</p>
        </div>
      )}
    </div>
  );
};

export default MedicationExtractor;
