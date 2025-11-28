import React, { useState } from 'react';
import { FaPlus, FaTrash, FaUser, FaCalendar, FaPills } from 'react-icons/fa';
import { GENDER_OPTIONS, LIFE_EXPECTANCY_OPTIONS, DURATION_OPTIONS, COMORBIDITIES, CFS_DESCRIPTIONS } from '../utils/constants';

const PatientForm = ({ onSubmit, isLoading }) => {
  const [formData, setFormData] = useState({
    age: '',
    gender: 'female',
    is_frail: false,
    cfs_score: '',
    life_expectancy: '2-5_years',
    comorbidities: [],
    medications: [],
    herbs: []
  });

  const [currentMedication, setCurrentMedication] = useState({
    generic_name: '',
    brand_name: '',
    dose: '',
    frequency: '',
    indication: '',
    duration: 'long_term'
  });

  const [currentHerb, setCurrentHerb] = useState({
    generic_name: '',
    brand_name: '',
    dose: '',
    frequency: '',
    intended_effect: '',
    duration: 'long_term'
  });

  const handleInputChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData({
      ...formData,
      [name]: type === 'checkbox' ? checked : value
    });
  };

  const handleComorbidityToggle = (comorbidity) => {
    setFormData({
      ...formData,
      comorbidities: formData.comorbidities.includes(comorbidity)
        ? formData.comorbidities.filter(c => c !== comorbidity)
        : [...formData.comorbidities, comorbidity]
    });
  };

  const addMedication = () => {
    if (currentMedication.generic_name && currentMedication.dose) {
      setFormData({
        ...formData,
        medications: [...formData.medications, currentMedication]
      });
      setCurrentMedication({
        generic_name: '',
        brand_name: '',
        dose: '',
        frequency: '',
        indication: '',
        duration: 'long_term'
      });
    }
  };

  const removeMedication = (index) => {
    setFormData({
      ...formData,
      medications: formData.medications.filter((_, i) => i !== index)
    });
  };

  const addHerb = () => {
    if (currentHerb.generic_name) {
      setFormData({
        ...formData,
        herbs: [...formData.herbs, currentHerb]
      });
      setCurrentHerb({
        generic_name: '',
        brand_name: '',
        dose: '',
        frequency: '',
        intended_effect: '',
        duration: 'long_term'
      });
    }
  };

  const removeHerb = (index) => {
    setFormData({
      ...formData,
      herbs: formData.herbs.filter((_, i) => i !== index)
    });
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    
    // Validate
    if (!formData.age || formData.medications.length === 0) {
      alert('Please fill in age and add at least one medication');
      return;
    }

    onSubmit(formData);
  };

  return (
    <div className="bg-white rounded-lg shadow-lg p-6 mb-6">
      <h2 className="text-2xl font-bold text-gray-800 mb-6 flex items-center">
        <FaUser className="mr-2" />
        Patient Information
      </h2>

      <form onSubmit={handleSubmit}>
        {/* Basic Information */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Age *
            </label>
            <input
              type="number"
              name="age"
              value={formData.age}
              onChange={handleInputChange}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="e.g., 75"
              min="1"
              max="120"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Gender *
            </label>
            <select
              name="gender"
              value={formData.gender}
              onChange={handleInputChange}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              {GENDER_OPTIONS.map(option => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Clinical Frailty Scale (CFS)
            </label>
            <select
              name="cfs_score"
              value={formData.cfs_score}
              onChange={handleInputChange}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="">Not assessed</option>
              {Object.entries(CFS_DESCRIPTIONS).map(([score, description]) => (
                <option key={score} value={score}>
                  {score} - {description}
                </option>
              ))}
            </select>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Life Expectancy *
            </label>
            <select
              name="life_expectancy"
              value={formData.life_expectancy}
              onChange={handleInputChange}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              {LIFE_EXPECTANCY_OPTIONS.map(option => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
          </div>

          <div className="flex items-center">
            <input
              type="checkbox"
              name="is_frail"
              checked={formData.is_frail}
              onChange={handleInputChange}
              className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
            />
            <label className="ml-2 block text-sm text-gray-700">
              Patient is clinically frail
            </label>
          </div>
        </div>

        {/* Comorbidities */}
        <div className="mb-6">
          <label className="block text-sm font-medium text-gray-700 mb-3">
            Comorbidities
          </label>
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-3">
            {COMORBIDITIES.map(comorbidity => (
              <div key={comorbidity} className="flex items-center">
                <input
                  type="checkbox"
                  checked={formData.comorbidities.includes(comorbidity)}
                  onChange={() => handleComorbidityToggle(comorbidity)}
                  className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                />
                <label className="ml-2 text-sm text-gray-700">
                  {comorbidity}
                </label>
              </div>
            ))}
          </div>
        </div>

        {/* Add Medication Section */}
        <div className="border-t pt-6 mb-6">
          <h3 className="text-lg font-semibold text-gray-800 mb-4 flex items-center">
            <FaPills className="mr-2 text-blue-600" />
            Allopathic Medications
          </h3>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mb-4">
            <input
              type="text"
              placeholder="Generic Name *"
              value={currentMedication.generic_name}
              onChange={(e) => setCurrentMedication({...currentMedication, generic_name: e.target.value})}
              className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            <input
              type="text"
              placeholder="Brand Name"
              value={currentMedication.brand_name}
              onChange={(e) => setCurrentMedication({...currentMedication, brand_name: e.target.value})}
              className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            <input
              type="text"
              placeholder="Dose (e.g., 20mg)"
              value={currentMedication.dose}
              onChange={(e) => setCurrentMedication({...currentMedication, dose: e.target.value})}
              className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            <input
              type="text"
              placeholder="Frequency (e.g., once daily)"
              value={currentMedication.frequency}
              onChange={(e) => setCurrentMedication({...currentMedication, frequency: e.target.value})}
              className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            <input
              type="text"
              placeholder="Indication"
              value={currentMedication.indication}
              onChange={(e) => setCurrentMedication({...currentMedication, indication: e.target.value})}
              className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            <select
              value={currentMedication.duration}
              onChange={(e) => setCurrentMedication({...currentMedication, duration: e.target.value})}
              className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              {DURATION_OPTIONS.map(option => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
          </div>
          
          <button
            type="button"
            onClick={addMedication}
            className="flex items-center px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition"
          >
            <FaPlus className="mr-2" />
            Add Medication
          </button>

          {formData.medications.length > 0 && (
            <div className="mt-4">
              <h4 className="text-sm font-medium text-gray-700 mb-2">Added Medications:</h4>
              <div className="space-y-2">
                {formData.medications.map((med, index) => (
                  <div key={index} className="flex items-center justify-between bg-blue-50 p-3 rounded-md">
                    <div>
                      <span className="font-medium">{med.generic_name}</span>
                      {med.brand_name && <span className="text-gray-600"> ({med.brand_name})</span>}
                      <span className="text-gray-600"> - {med.dose} {med.frequency}</span>
                      {med.indication && <span className="text-gray-500 text-sm"> • {med.indication}</span>}
                    </div>
                    <button
                      type="button"
                      onClick={() => removeMedication(index)}
                      className="text-red-600 hover:text-red-800"
                    >
                      <FaTrash />
                    </button>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Add Herb Section */}
        <div className="border-t pt-6 mb-6">
          <h3 className="text-lg font-semibold text-gray-800 mb-4 flex items-center">
            <span className="mr-2">🌿</span>
            Ayurvedic / Herbal Products
          </h3>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mb-4">
            <input
              type="text"
              placeholder="Herb Name *"
              value={currentHerb.generic_name}
              onChange={(e) => setCurrentHerb({...currentHerb, generic_name: e.target.value})}
              className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
            />
            <input
              type="text"
              placeholder="Brand Name"
              value={currentHerb.brand_name}
              onChange={(e) => setCurrentHerb({...currentHerb, brand_name: e.target.value})}
              className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
            />
            <input
              type="text"
              placeholder="Dose (e.g., 300mg)"
              value={currentHerb.dose}
              onChange={(e) => setCurrentHerb({...currentHerb, dose: e.target.value})}
              className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
            />
            <input
              type="text"
              placeholder="Frequency"
              value={currentHerb.frequency}
              onChange={(e) => setCurrentHerb({...currentHerb, frequency: e.target.value})}
              className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
            />
            <input
              type="text"
              placeholder="Intended Effect (e.g., sleep, immunity)"
              value={currentHerb.intended_effect}
              onChange={(e) => setCurrentHerb({...currentHerb, intended_effect: e.target.value})}
              className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
            />
            <select
              value={currentHerb.duration}
              onChange={(e) => setCurrentHerb({...currentHerb, duration: e.target.value})}
              className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
            >
              {DURATION_OPTIONS.map(option => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
          </div>
          
          <button
            type="button"
            onClick={addHerb}
            className="flex items-center px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 transition"
          >
            <FaPlus className="mr-2" />
            Add Herbal Product
          </button>

          {formData.herbs.length > 0 && (
            <div className="mt-4">
              <h4 className="text-sm font-medium text-gray-700 mb-2">Added Herbs:</h4>
              <div className="space-y-2">
                {formData.herbs.map((herb, index) => (
                  <div key={index} className="flex items-center justify-between bg-green-50 p-3 rounded-md">
                    <div>
                      <span className="font-medium">{herb.generic_name}</span>
                      {herb.brand_name && <span className="text-gray-600"> ({herb.brand_name})</span>}
                      {herb.dose && <span className="text-gray-600"> - {herb.dose} {herb.frequency}</span>}
                      {herb.intended_effect && <span className="text-gray-500 text-sm"> • {herb.intended_effect}</span>}
                    </div>
                    <button
                      type="button"
                      onClick={() => removeHerb(index)}
                      className="text-red-600 hover:text-red-800"
                    >
                      <FaTrash />
                    </button>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Submit Button */}
        <div className="flex justify-end">
          <button
            type="submit"
            disabled={isLoading}
            className={`px-8 py-3 rounded-md text-white font-semibold transition ${
              isLoading
                ? 'bg-gray-400 cursor-not-allowed'
                : 'bg-indigo-600 hover:bg-indigo-700'
            }`}
          >
            {isLoading ? 'Analyzing...' : 'Analyze Patient'}
          </button>
        </div>
      </form>
    </div>
  );
};

export default PatientForm;
