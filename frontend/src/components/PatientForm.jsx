import React, { useState } from 'react';
import Select from 'react-select';
import CreatableSelect from 'react-select/creatable';
import { FaPlus, FaTrash, FaUser, FaPills, FaInfoCircle } from 'react-icons/fa';
import { 
  GENDER_OPTIONS, 
  LIFE_EXPECTANCY_OPTIONS, 
  DURATION_OPTIONS, 
  COMORBIDITIES, 
  CFS_DESCRIPTIONS 
} from '../utils/constants';
import {
  COMMON_MEDICATIONS,
  COMMON_HERBS,
  FREQUENCY_OPTIONS,
  INDICATION_OPTIONS,
  HERBAL_EFFECTS
} from '../utils/medicationOptions';

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

  // Custom styles for react-select
  const selectStyles = {
    control: (base, state) => ({
      ...base,
      borderColor: state.isFocused ? '#4F46E5' : '#D1D5DB',
      boxShadow: state.isFocused ? '0 0 0 2px rgba(79, 70, 229, 0.2)' : 'none',
      '&:hover': {
        borderColor: '#4F46E5'
      },
      minHeight: '42px'
    }),
    option: (base, state) => ({
      ...base,
      backgroundColor: state.isSelected 
        ? '#4F46E5' 
        : state.isFocused 
        ? '#EEF2FF' 
        : 'white',
      color: state.isSelected ? 'white' : '#1F2937',
      padding: '8px 12px',
      cursor: 'pointer',
      '&:active': {
        backgroundColor: '#4338CA'
      }
    }),
    menu: (base) => ({
      ...base,
      zIndex: 100,
      boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)'
    }),
    placeholder: (base) => ({
      ...base,
      color: '#9CA3AF'
    }),
    noOptionsMessage: (base) => ({
      ...base,
      padding: '8px 12px',
      color: '#059669',
      fontWeight: 500
    })
  };

  const herbSelectStyles = {
    ...selectStyles,
    control: (base, state) => ({
      ...base,
      borderColor: state.isFocused ? '#10B981' : '#D1D5DB',
      boxShadow: state.isFocused ? '0 0 0 2px rgba(16, 185, 129, 0.2)' : 'none',
      '&:hover': {
        borderColor: '#10B981'
      },
      minHeight: '42px'
    }),
    option: (base, state) => ({
      ...base,
      backgroundColor: state.isSelected 
        ? '#10B981' 
        : state.isFocused 
        ? '#ECFDF5' 
        : 'white',
      color: state.isSelected ? 'white' : '#1F2937',
      padding: '8px 12px',
      cursor: 'pointer'
    })
  };

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
    } else {
      alert('Please enter at least the generic name and dose');
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
    } else {
      alert('Please enter the herb name');
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
    
    if (!formData.age || formData.medications.length === 0) {
      alert('Please fill in age and add at least one medication');
      return;
    }

    onSubmit(formData);
  };

  return (
    <div className="bg-white rounded-lg shadow-lg p-6 mb-6">
      <h2 className="text-2xl font-bold text-gray-800 mb-4 flex items-center">
        <FaUser className="mr-2" />
        Patient Information
      </h2>

      {/* Info Box */}
      <div className="bg-blue-50 border-l-4 border-blue-500 p-4 mb-6 rounded-lg">
        <div className="flex items-start">
          <FaInfoCircle className="text-blue-600 mt-1 mr-3 flex-shrink-0" />
          <div>
            <h4 className="text-sm font-semibold text-blue-900 mb-1">
              💡 Quick Tips
            </h4>
            <ul className="text-sm text-blue-800 space-y-1">
              <li>• <strong>Search medications:</strong> Start typing to see suggestions (e.g., "Alp..." → Alprazolam)</li>
              <li>• <strong>Add custom medications:</strong> If not in list, just type the name and press Enter</li>
              <li>• <strong>Brand names are optional:</strong> Skip if you don't know it</li>
              <li>• <strong>Dropdowns are flexible:</strong> Select from list OR type your own</li>
            </ul>
          </div>
        </div>
      </div>

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
            {/* Generic Name - CREATABLE */}
            <div className="lg:col-span-1">
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Generic Name * 
                <span className="text-xs text-indigo-600 ml-2">
                  <FaInfoCircle className="inline mr-1" />
                  Type to search or add custom
                </span>
              </label>
              <CreatableSelect
                options={COMMON_MEDICATIONS}
                value={currentMedication.generic_name ? {
                  value: currentMedication.generic_name,
                  label: currentMedication.generic_name
                } : null}
                onChange={(selected) => setCurrentMedication({
                  ...currentMedication,
                  generic_name: selected ? selected.value : ''
                })}
                onCreateOption={(inputValue) => {
                  setCurrentMedication({
                    ...currentMedication,
                    generic_name: inputValue
                  });
                }}
                isClearable
                isSearchable
                placeholder="Type medication name..."
                styles={selectStyles}
                formatCreateLabel={(inputValue) => `✨ Add custom: "${inputValue}"`}
                formatGroupLabel={(data) => (
                  <div className="text-xs font-semibold text-gray-500 uppercase py-1">
                    {data.category}
                  </div>
                )}
                noOptionsMessage={({ inputValue }) => 
                  inputValue ? `Press Enter to add "${inputValue}"` : "Start typing..."
                }
              />
            </div>

            {/* Brand Name - OPTIONAL */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Brand Name <span className="text-xs text-gray-500">(Optional)</span>
              </label>
              <input
                type="text"
                placeholder="e.g., Xanax (optional)"
                value={currentMedication.brand_name}
                onChange={(e) => setCurrentMedication({...currentMedication, brand_name: e.target.value})}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>

            {/* Dose */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Dose *
              </label>
              <input
                type="text"
                placeholder="e.g., 20mg, 1 tablet"
                value={currentMedication.dose}
                onChange={(e) => setCurrentMedication({...currentMedication, dose: e.target.value})}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>

            {/* Frequency - CREATABLE */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Frequency <span className="text-xs text-gray-500">(or type custom)</span>
              </label>
              <CreatableSelect
                options={FREQUENCY_OPTIONS}
                value={currentMedication.frequency ? {
                  value: currentMedication.frequency,
                  label: currentMedication.frequency
                } : null}
                onChange={(selected) => setCurrentMedication({
                  ...currentMedication,
                  frequency: selected ? selected.value : ''
                })}
                onCreateOption={(inputValue) => {
                  setCurrentMedication({
                    ...currentMedication,
                    frequency: inputValue
                  });
                }}
                isClearable
                isSearchable
                placeholder="Select or type..."
                styles={selectStyles}
                formatCreateLabel={(inputValue) => `✨ Use: "${inputValue}"`}
              />
            </div>

            {/* Indication - CREATABLE */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Indication <span className="text-xs text-gray-500">(or type custom)</span>
              </label>
              <CreatableSelect
                options={INDICATION_OPTIONS}
                value={currentMedication.indication ? {
                  value: currentMedication.indication,
                  label: currentMedication.indication
                } : null}
                onChange={(selected) => setCurrentMedication({
                  ...currentMedication,
                  indication: selected ? selected.value : ''
                })}
                onCreateOption={(inputValue) => {
                  setCurrentMedication({
                    ...currentMedication,
                    indication: inputValue
                  });
                }}
                isClearable
                isSearchable
                placeholder="Why prescribed?"
                styles={selectStyles}
                formatCreateLabel={(inputValue) => `✨ Add: "${inputValue}"`}
                formatGroupLabel={(data) => (
                  <div className="text-xs font-semibold text-gray-500 uppercase py-1">
                    {data.category}
                  </div>
                )}
              />
            </div>

            {/* Duration */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Duration
              </label>
              <select
                value={currentMedication.duration}
                onChange={(e) => setCurrentMedication({...currentMedication, duration: e.target.value})}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                {DURATION_OPTIONS.map(option => (
                  <option key={option.value} value={option.value}>
                    {option.label}
                  </option>
                ))}
              </select>
            </div>
          </div>
          
          <button
            type="button"
            onClick={addMedication}
            className="flex items-center px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition"
          >
            <FaPlus className="mr-2" />
            Add Medication
          </button>

          {/* Added Medications List */}
          {formData.medications.length > 0 && (
            <div className="mt-4">
              <h4 className="text-sm font-medium text-gray-700 mb-2">
                Added Medications ({formData.medications.length}):
              </h4>
              <div className="space-y-2">
                {formData.medications.map((med, index) => (
                  <div key={index} className="flex items-center justify-between bg-blue-50 p-3 rounded-md">
                    <div>
                      <span className="font-medium">{med.generic_name}</span>
                      {med.brand_name && <span className="text-gray-600"> ({med.brand_name})</span>}
                      <span className="text-gray-600"> - {med.dose}</span>
                      {med.frequency && <span className="text-gray-600"> {med.frequency}</span>}
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
            {/* Herb Name - CREATABLE */}
            <div className="lg:col-span-1">
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Herb Name *
                <span className="text-xs text-green-600 ml-2">
                  <FaInfoCircle className="inline mr-1" />
                  Type to search or add custom
                </span>
              </label>
              <CreatableSelect
                options={COMMON_HERBS}
                value={currentHerb.generic_name ? {
                  value: currentHerb.generic_name,
                  label: currentHerb.generic_name
                } : null}
                onChange={(selected) => setCurrentHerb({
                  ...currentHerb,
                  generic_name: selected ? selected.value : ''
                })}
                onCreateOption={(inputValue) => {
                  setCurrentHerb({
                    ...currentHerb,
                    generic_name: inputValue
                  });
                }}
                isClearable
                isSearchable
                placeholder="Type herb name..."
                styles={herbSelectStyles}
                formatCreateLabel={(inputValue) => `✨ Add custom: "${inputValue}"`}
                formatGroupLabel={(data) => (
                  <div className="text-xs font-semibold text-green-600 uppercase py-1">
                    {data.category}
                  </div>
                )}
                noOptionsMessage={({ inputValue }) => 
                  inputValue ? `Press Enter to add "${inputValue}"` : "Start typing..."
                }
              />
            </div>

            {/* Brand Name - OPTIONAL */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Brand Name <span className="text-xs text-gray-500">(Optional)</span>
              </label>
              <input
                type="text"
                placeholder="Product brand (optional)"
                value={currentHerb.brand_name}
                onChange={(e) => setCurrentHerb({...currentHerb, brand_name: e.target.value})}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
              />
            </div>

            {/* Dose */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Dose
              </label>
              <input
                type="text"
                placeholder="e.g., 300mg, 1 tsp"
                value={currentHerb.dose}
                onChange={(e) => setCurrentHerb({...currentHerb, dose: e.target.value})}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
              />
            </div>

            {/* Frequency - CREATABLE */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Frequency <span className="text-xs text-gray-500">(or type custom)</span>
              </label>
              <CreatableSelect
                options={FREQUENCY_OPTIONS}
                value={currentHerb.frequency ? {
                  value: currentHerb.frequency,
                  label: currentHerb.frequency
                } : null}
                onChange={(selected) => setCurrentHerb({
                  ...currentHerb,
                  frequency: selected ? selected.value : ''
                })}
                onCreateOption={(inputValue) => {
                  setCurrentHerb({
                    ...currentHerb,
                    frequency: inputValue
                  });
                }}
                isClearable
                isSearchable
                placeholder="Select or type..."
                styles={herbSelectStyles}
                formatCreateLabel={(inputValue) => `✨ Use: "${inputValue}"`}
              />
            </div>

            {/* Intended Effect - CREATABLE */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Intended Effect <span className="text-xs text-gray-500">(or type custom)</span>
              </label>
              <CreatableSelect
                options={HERBAL_EFFECTS}
                value={currentHerb.intended_effect ? {
                  value: currentHerb.intended_effect,
                  label: currentHerb.intended_effect
                } : null}
                onChange={(selected) => setCurrentHerb({
                  ...currentHerb,
                  intended_effect: selected ? selected.value : ''
                })}
                onCreateOption={(inputValue) => {
                  setCurrentHerb({
                    ...currentHerb,
                    intended_effect: inputValue
                  });
                }}
                isClearable
                isSearchable
                placeholder="Why are you taking this?"
                styles={herbSelectStyles}
                formatCreateLabel={(inputValue) => `✨ Add: "${inputValue}"`}
              />
            </div>

            {/* Duration */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Duration
              </label>
              <select
                value={currentHerb.duration}
                onChange={(e) => setCurrentHerb({...currentHerb, duration: e.target.value})}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
              >
                {DURATION_OPTIONS.map(option => (
                  <option key={option.value} value={option.value}>
                    {option.label}
                  </option>
                ))}
              </select>
            </div>
          </div>
          
          <button
            type="button"
            onClick={addHerb}
            className="flex items-center px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 transition"
          >
            <FaPlus className="mr-2" />
            Add Herbal Product
          </button>

          {/* Added Herbs List */}
          {formData.herbs.length > 0 && (
            <div className="mt-4">
              <h4 className="text-sm font-medium text-gray-700 mb-2">
                Added Herbs ({formData.herbs.length}):
              </h4>
              <div className="space-y-2">
                {formData.herbs.map((herb, index) => (
                  <div key={index} className="flex items-center justify-between bg-green-50 p-3 rounded-md">
                    <div>
                      <span className="font-medium">{herb.generic_name}</span>
                      {herb.brand_name && <span className="text-gray-600"> ({herb.brand_name})</span>}
                      {herb.dose && <span className="text-gray-600"> - {herb.dose}</span>}
                      {herb.frequency && <span className="text-gray-600"> {herb.frequency}</span>}
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
