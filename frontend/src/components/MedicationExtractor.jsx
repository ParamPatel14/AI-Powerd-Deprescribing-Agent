import React, { useState } from 'react';
import { FaUpload, FaTrash, FaCheckCircle, FaCamera } from 'react-icons/fa';
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
    <div className="bg-gradient-to-r from-purple-50 to-indigo-50 p-6 rounded-lg border-2 border-purple-200 mb-6">
      <h3 className="text-xl font-bold text-purple-900 mb-4">
        🤖 AI Medication Extraction
      </h3>

      {/* Upload Type Selector */}
      <div className="flex gap-4 mb-4">
        <button
          onClick={() => setUploadType('prescription')}
          className={`flex-1 p-3 rounded-lg border-2 transition ${
            uploadType === 'prescription'
              ? 'bg-purple-600 text-white border-purple-600'
              : 'bg-white text-gray-700 border-gray-300 hover:border-purple-400'
          }`}
        >
          <FaUpload className="inline mr-2" />
          Prescription Upload
        </button>

        <button
          onClick={() => setUploadType('brown-bag')}
          className={`flex-1 p-3 rounded-lg border-2 transition ${
            uploadType === 'brown-bag'
              ? 'bg-purple-600 text-white border-purple-600'
              : 'bg-white text-gray-700 border-gray-300 hover:border-purple-400'
          }`}
        >
          <FaCamera className="inline mr-2" />
          Brown Bag Photo
        </button>
      </div>

      {/* File Upload */}
      <div className="mb-4">
        <label className="block w-full p-4 border-2 border-dashed border-purple-300 rounded-lg 
                         hover:border-purple-500 cursor-pointer bg-white transition">
          <input
            type="file"
            accept={uploadType === 'prescription' ? '.pdf,.jpg,.jpeg,.png' : 'image/*'}
            onChange={handleFileUpload}
            className="hidden"
            disabled={isLoading}
          />
          <div className="text-center">
            {isLoading ? (
              <p className="text-purple-600 font-semibold">🔄 Analyzing...</p>
            ) : (
              <>
                <FaUpload className="mx-auto text-3xl text-purple-500 mb-2" />
                <p className="text-purple-700 font-medium">
                  Click to upload {uploadType === 'prescription' ? 'prescription (PDF/Image)' : 'photo of medications'}
                </p>
              </>
            )}
          </div>
        </label>
      </div>

      {/* Extracted Medications - Review & Edit */}
      {extractedMeds.length > 0 && (
        <div className="bg-white p-4 rounded-lg shadow">
          <h4 className="font-bold text-gray-800 mb-3">
            ✅ Extracted {extractedMeds.length} Medication(s) - Review & Edit
          </h4>

          <div className="space-y-3 mb-4 max-h-96 overflow-y-auto">
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
            onClick={handleConfirm}
            className="w-full py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 
                       font-semibold flex items-center justify-center"
          >
            <FaCheckCircle className="mr-2" />
            Confirm & Add All Medications
          </button>
        </div>
      )}
    </div>
  );
};

// Individual medication card for editing
const MedicationCard = ({ med, onEdit, onDelete }) => {
  const confidenceColor = {
    high: 'bg-green-100 text-green-800',
    medium: 'bg-yellow-100 text-yellow-800',
    low: 'bg-red-100 text-red-800'
  }[med.confidence] || 'bg-gray-100 text-gray-800';

  return (
    <div className="border border-gray-300 rounded-lg p-4 hover:shadow-md transition bg-white">
      {/* Header with Generic Name and Actions */}
      <div className="flex justify-between items-start mb-3">
        <div className="flex-1">
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Generic Name *
          </label>
          <input
            type="text"
            value={med.generic_name}
            onChange={(e) => onEdit(med.id, 'generic_name', e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-md 
                       focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none"
            placeholder="Enter generic name"
          />
          {med.position && (
            <span className="text-xs text-gray-500 mt-1 block">
              📍 Position: {med.position}
            </span>
          )}
        </div>

        <div className="flex gap-2 ml-3">
          <span className={`text-xs px-2 py-1 rounded-full font-medium ${confidenceColor}`}>
            {med.confidence}
          </span>
          <button 
            onClick={() => onDelete(med.id)} 
            className="text-red-600 hover:text-red-800 p-1"
            title="Delete medication"
          >
            <FaTrash />
          </button>
        </div>
      </div>

      {/* Form Fields Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
        {/* Brand Name */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Brand Name
          </label>
          <input
            type="text"
            value={med.brand_name || ''}
            onChange={(e) => onEdit(med.id, 'brand_name', e.target.value)}
            placeholder="Enter brand name (optional)"
            className="w-full px-3 py-2 border border-gray-300 rounded-md 
                       focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          />
        </div>

        {/* Dose */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Dose / Strength *
          </label>
          <input
            type="text"
            value={med.dose}
            onChange={(e) => onEdit(med.id, 'dose', e.target.value)}
            placeholder="e.g., 500 mg, 10 mg"
            className="w-full px-3 py-2 border border-gray-300 rounded-md 
                       focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          />
        </div>

        {/* Frequency - DROPDOWN */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Frequency *
          </label>
          <CreatableSelect
            options={FREQUENCY_OPTIONS}
            value={FREQUENCY_OPTIONS.find(opt => opt.value === med.frequency) || 
                   (med.frequency ? { value: med.frequency, label: med.frequency } : null)}
            onChange={(option) => onEdit(med.id, 'frequency', option?.value || '')}
            placeholder="Select or type frequency..."
            isClearable
            className="text-sm"
          />
        </div>

        {/* Duration - DROPDOWN */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Duration
          </label>
          <Select
            options={DURATION_OPTIONS}
            value={DURATION_OPTIONS.find(opt => opt.value === med.duration)}
            onChange={(option) => onEdit(med.id, 'duration', option?.value || 'unknown')}
            placeholder="Select duration..."
            className="text-sm"
          />
        </div>

        {/* Indication - DROPDOWN (full width) */}
        <div className="md:col-span-2">
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Indication (What it's for)
          </label>
          <CreatableSelect
            options={INDICATION_OPTIONS}
            value={INDICATION_OPTIONS.find(opt => opt.value === med.indication) || 
                   (med.indication ? { value: med.indication, label: med.indication } : null)}
            onChange={(option) => onEdit(med.id, 'indication', option?.value || '')}
            placeholder="Select or type indication..."
            isClearable
            className="text-sm"
            formatGroupLabel={(data) => (
              <div className="font-semibold text-gray-700">{data.category}</div>
            )}
          />
        </div>
      </div>

      {/* Notes Section */}
      {med.notes && (
        <div className="mt-3 p-3 bg-blue-50 border border-blue-200 rounded-md">
          <p className="text-xs font-medium text-blue-900 mb-1">📝 AI Extraction Notes:</p>
          <p className="text-xs text-blue-800 italic">{med.notes}</p>
        </div>
      )}
    </div>
  );
};

export default MedicationExtractor;
