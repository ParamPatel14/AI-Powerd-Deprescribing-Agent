import React, { useState } from 'react';
import Select from 'react-select';
import CreatableSelect from 'react-select/creatable';
import { FaPlus, FaTrash, FaUser, FaPills, FaInfoCircle, FaLeaf, FaFlask, FaHeartbeat, FaChevronDown, FaChevronUp, FaRobot } from 'react-icons/fa';
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
import MedicationExtractor from './MedicationExtractor';


const PatientForm = ({ onSubmit, isLoading }) => {
  const [formData, setFormData] = useState({
    age: '',
    gender: 'female',
    is_frail: false,
    cfs_score: '',
    life_expectancy: '2-5_years',
    comorbidities: [],
    medications: [],
    herbs: [],
    serum_creatinine_mg_dl: null,
    bilirubin_mg_dl: null,
    inr: null,
    ast: null,
    alt: null,
    sodium: null
  });

  const [expandedSections, setExpandedSections] = useState({
    basic: true,
    labs: false,
    meds: true,
    herbs: false,
  });

  const toggleSection = (section) => {
    setExpandedSections(prev => ({
      ...prev,
      [section]: !prev[section]
    }));
  };

  const handleExtractedMeds = (extractedMeds) => {
    setFormData(prev => ({
      ...prev,
      medications: [...prev.medications, ...extractedMeds]
    }));
    alert(`Added ${extractedMeds.length} medication(s)! Review and edit them below if needed.`);
  };

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
  

  const selectStyles = {
    control: (base, state) => ({
      ...base,
      borderColor: state.isFocused ? '#0891B2' : '#E5E7EB',
      boxShadow: state.isFocused ? '0 0 0 3px rgba(8, 145, 178, 0.15)' : 'none',
      '&:hover': {
        borderColor: '#0891B2'
      },
      minHeight: '48px',
      borderRadius: '12px',
      transition: 'all 0.2s ease',
    }),
    option: (base, state) => ({
      ...base,
      backgroundColor: state.isSelected 
        ? '#0891B2' 
        : state.isFocused 
        ? '#ECFEFF' 
        : 'white',
      color: state.isSelected ? 'white' : '#1F2937',
      padding: '12px 16px',
      cursor: 'pointer',
      transition: 'all 0.15s ease',
      '&:active': {
        backgroundColor: '#0E7490'
      }
    }),
    menu: (base) => ({
      ...base,
      zIndex: 100,
      borderRadius: '12px',
      boxShadow: '0 10px 40px rgba(0, 0, 0, 0.15)',
      border: '1px solid #E5E7EB',
      overflow: 'hidden',
    }),
    placeholder: (base) => ({
      ...base,
      color: '#9CA3AF'
    }),
    noOptionsMessage: (base) => ({
      ...base,
      padding: '12px 16px',
      color: '#0891B2',
      fontWeight: 500
    })
  };

  const herbSelectStyles = {
    ...selectStyles,
    control: (base, state) => ({
      ...base,
      borderColor: state.isFocused ? '#10B981' : '#E5E7EB',
      boxShadow: state.isFocused ? '0 0 0 3px rgba(16, 185, 129, 0.15)' : 'none',
      '&:hover': {
        borderColor: '#10B981'
      },
      minHeight: '48px',
      borderRadius: '12px',
      transition: 'all 0.2s ease',
    }),
    option: (base, state) => ({
      ...base,
      backgroundColor: state.isSelected 
        ? '#10B981' 
        : state.isFocused 
        ? '#ECFDF5' 
        : 'white',
      color: state.isSelected ? 'white' : '#1F2937',
      padding: '12px 16px',
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

  const SectionHeader = ({ icon: Icon, title, section, count, color = "cyan" }) => {
    const isExpanded = expandedSections[section];
    const colorClasses = {
      cyan: 'from-cyan-500 to-blue-600',
      green: 'from-green-500 to-emerald-600',
      purple: 'from-purple-500 to-indigo-600',
      blue: 'from-blue-500 to-indigo-600',
    };
    
    return (
      <button
        type="button"
        onClick={() => toggleSection(section)}
        className={`w-full flex items-center justify-between p-4 rounded-xl transition-all duration-300
                  ${isExpanded 
                    ? `bg-gradient-to-r ${colorClasses[color]} text-white shadow-lg` 
                    : 'bg-gray-50 hover:bg-gray-100 text-gray-700'}`}
      >
        <div className="flex items-center gap-3">
          <div className={`w-10 h-10 rounded-xl flex items-center justify-center
                        ${isExpanded ? 'bg-white/20' : `bg-gradient-to-br ${colorClasses[color]}`}`}>
            <Icon className={isExpanded ? 'text-white' : 'text-white'} />
          </div>
          <div className="text-left">
            <h3 className="font-bold">{title}</h3>
            {count !== undefined && (
              <p className={`text-sm ${isExpanded ? 'text-white/80' : 'text-gray-500'}`}>
                {count} item(s) added
              </p>
            )}
          </div>
        </div>
        <div className={`w-8 h-8 rounded-lg flex items-center justify-center transition-transform duration-300
                      ${isExpanded ? 'bg-white/20 rotate-180' : 'bg-gray-200'}`}>
          <FaChevronDown className={isExpanded ? 'text-white' : 'text-gray-600'} />
        </div>
      </button>
    );
  };

  return (
    <div className="card-medical p-6 lg:p-8 mb-6 animate-fade-in-up">
      <MedicationExtractor onMedicationsExtracted={handleExtractedMeds} />
      
      <div className="flex items-center gap-4 mb-6">
        <div className="w-14 h-14 bg-gradient-to-br from-cyan-500 to-blue-600 rounded-2xl 
                      flex items-center justify-center shadow-lg">
          <FaUser className="text-2xl text-white" />
        </div>
        <div>
          <h2 className="text-2xl font-bold text-gray-800">Patient Information</h2>
          <p className="text-gray-500 text-sm">Enter patient details for comprehensive analysis</p>
        </div>
      </div>

      <div className="bg-gradient-to-r from-cyan-50 to-blue-50 border border-cyan-200 p-5 mb-8 rounded-xl">
        <div className="flex items-start gap-3">
          <div className="w-10 h-10 bg-gradient-to-br from-cyan-500 to-blue-600 rounded-xl 
                        flex items-center justify-center flex-shrink-0">
            <FaInfoCircle className="text-white" />
          </div>
          <div>
            <h4 className="font-bold text-cyan-900 mb-2">Quick Tips</h4>
            <ul className="text-sm text-cyan-800 space-y-1.5">
              <li className="flex items-center gap-2">
                <span className="w-1.5 h-1.5 bg-cyan-500 rounded-full"></span>
                <strong>Search medications:</strong> Start typing to see suggestions
              </li>
              <li className="flex items-center gap-2">
                <span className="w-1.5 h-1.5 bg-cyan-500 rounded-full"></span>
                <strong>Add custom:</strong> Type any name and press Enter if not in list
              </li>
              <li className="flex items-center gap-2">
                <span className="w-1.5 h-1.5 bg-cyan-500 rounded-full"></span>
                <strong>Brand names:</strong> Optional - skip if unknown
              </li>
            </ul>
          </div>
        </div>
      </div>

      <form onSubmit={handleSubmit} className="space-y-6">
        <div className="space-y-4">
          <SectionHeader icon={FaHeartbeat} title="Basic Patient Information" section="basic" color="cyan" />
          
          {expandedSections.basic && (
            <div className="animate-fade-in p-4 bg-gray-50 rounded-xl space-y-5">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-2">
                    Age <span className="text-red-500">*</span>
                  </label>
                  <input
                    type="number"
                    name="age"
                    value={formData.age}
                    onChange={handleInputChange}
                    className="input-medical"
                    placeholder="e.g., 75"
                    min="1"
                    max="120"
                    required
                  />
                </div>

                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-2">
                    Gender <span className="text-red-500">*</span>
                  </label>
                  <select
                    name="gender"
                    value={formData.gender}
                    onChange={handleInputChange}
                    className="input-medical"
                  >
                    {GENDER_OPTIONS.map(option => (
                      <option key={option.value} value={option.value}>
                        {option.label}
                      </option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-2">
                    Clinical Frailty Scale (CFS)
                  </label>
                  <select
                    name="cfs_score"
                    value={formData.cfs_score}
                    onChange={handleInputChange}
                    className="input-medical"
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

              <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-2">
                    Life Expectancy <span className="text-red-500">*</span>
                  </label>
                  <select
                    name="life_expectancy"
                    value={formData.life_expectancy}
                    onChange={handleInputChange}
                    className="input-medical"
                  >
                    {LIFE_EXPECTANCY_OPTIONS.map(option => (
                      <option key={option.value} value={option.value}>
                        {option.label}
                      </option>
                    ))}
                  </select>
                </div>

                <div className="flex items-center h-full pt-6">
                  <label className="flex items-center gap-3 cursor-pointer group">
                    <div className="relative">
                      <input
                        type="checkbox"
                        name="is_frail"
                        checked={formData.is_frail}
                        onChange={handleInputChange}
                        className="sr-only peer"
                      />
                      <div className="w-6 h-6 border-2 border-gray-300 rounded-lg peer-checked:border-cyan-500 
                                    peer-checked:bg-cyan-500 transition-all duration-200 
                                    group-hover:border-cyan-400 flex items-center justify-center">
                        <svg className="w-4 h-4 text-white opacity-0 peer-checked:opacity-100" 
                             fill="currentColor" viewBox="0 0 20 20">
                          <path d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"/>
                        </svg>
                      </div>
                    </div>
                    <span className="text-gray-700 font-medium">Patient is clinically frail</span>
                  </label>
                </div>
              </div>

              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-3">
                  Comorbidities
                </label>
                <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-3">
                  {COMORBIDITIES.map(comorbidity => (
                    <label 
                      key={comorbidity} 
                      className={`flex items-center gap-2 p-3 rounded-xl border-2 cursor-pointer transition-all duration-200
                                ${formData.comorbidities.includes(comorbidity)
                                  ? 'border-cyan-500 bg-cyan-50 text-cyan-700'
                                  : 'border-gray-200 hover:border-gray-300 hover:bg-gray-50'}`}
                    >
                      <input
                        type="checkbox"
                        checked={formData.comorbidities.includes(comorbidity)}
                        onChange={() => handleComorbidityToggle(comorbidity)}
                        className="sr-only"
                      />
                      <div className={`w-4 h-4 rounded border-2 flex items-center justify-center transition-all
                                    ${formData.comorbidities.includes(comorbidity)
                                      ? 'border-cyan-500 bg-cyan-500'
                                      : 'border-gray-300'}`}>
                        {formData.comorbidities.includes(comorbidity) && (
                          <svg className="w-3 h-3 text-white" fill="currentColor" viewBox="0 0 20 20">
                            <path d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"/>
                          </svg>
                        )}
                      </div>
                      <span className="text-sm font-medium">{comorbidity}</span>
                    </label>
                  ))}
                </div>
              </div>
            </div>
          )}
        </div>

        <div className="space-y-4">
          <SectionHeader icon={FaFlask} title="Lab Values (Optional)" section="labs" color="purple" />
          
          {expandedSections.labs && (
            <div className="animate-fade-in p-4 bg-purple-50/50 rounded-xl">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-2">
                    Serum Creatinine (mg/dL)
                  </label>
                  <input
                    type="number"
                    step="0.1"
                    value={formData.serum_creatinine_mg_dl || ''}
                    onChange={(e) =>
                      setFormData({ ...formData, serum_creatinine_mg_dl: parseFloat(e.target.value) || null })
                    }
                    className="input-medical"
                    placeholder="e.g., 1.2"
                  />
                </div>

                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-2">Bilirubin (mg/dL)</label>
                  <input
                    type="number"
                    step="0.1"
                    value={formData.bilirubin_mg_dl || ''}
                    onChange={(e) =>
                      setFormData({ ...formData, bilirubin_mg_dl: parseFloat(e.target.value) || null })
                    }
                    className="input-medical"
                    placeholder="e.g., 0.8"
                  />
                </div>

                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-2">INR</label>
                  <input
                    type="number"
                    step="0.1"
                    value={formData.inr || ''}
                    onChange={(e) =>
                      setFormData({ ...formData, inr: parseFloat(e.target.value) || null })
                    }
                    className="input-medical"
                    placeholder="e.g., 1.1"
                  />
                </div>

                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-2">AST (U/L)</label>
                  <input
                    type="number"
                    value={formData.ast || ''}
                    onChange={(e) =>
                      setFormData({ ...formData, ast: parseFloat(e.target.value) || null })
                    }
                    className="input-medical"
                    placeholder="e.g., 22"
                  />
                </div>

                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-2">ALT (U/L)</label>
                  <input
                    type="number"
                    value={formData.alt || ''}
                    onChange={(e) =>
                      setFormData({ ...formData, alt: parseFloat(e.target.value) || null })
                    }
                    className="input-medical"
                    placeholder="e.g., 18"
                  />
                </div>

                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-2">Sodium (mmol/L)</label>
                  <input
                    type="number"
                    value={formData.sodium || ''}
                    onChange={(e) =>
                      setFormData({ ...formData, sodium: parseFloat(e.target.value) || null })
                    }
                    className="input-medical"
                    placeholder="e.g., 138"
                  />
                </div>
              </div>
            </div>
          )}
        </div>

        <div className="space-y-4">
          <SectionHeader 
            icon={FaPills} 
            title="Allopathic Medications" 
            section="meds" 
            count={formData.medications.length}
            color="blue" 
          />
          
          {expandedSections.meds && (
            <div className="animate-fade-in p-4 bg-blue-50/50 rounded-xl space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                <div className="lg:col-span-1">
                  <label className="block text-sm font-semibold text-gray-700 mb-2">
                    Generic Name <span className="text-red-500">*</span>
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
                    formatCreateLabel={(inputValue) => `Add: "${inputValue}"`}
                    noOptionsMessage={({ inputValue }) => 
                      inputValue ? `Press Enter to add "${inputValue}"` : "Start typing..."
                    }
                  />
                </div>

                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-2">
                    Brand Name <span className="text-gray-400 text-xs">(Optional)</span>
                  </label>
                  <input
                    type="text"
                    placeholder="e.g., Xanax"
                    value={currentMedication.brand_name}
                    onChange={(e) => setCurrentMedication({...currentMedication, brand_name: e.target.value})}
                    className="input-medical"
                  />
                </div>

                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-2">
                    Dose <span className="text-red-500">*</span>
                  </label>
                  <input
                    type="text"
                    placeholder="e.g., 20mg"
                    value={currentMedication.dose}
                    onChange={(e) => setCurrentMedication({...currentMedication, dose: e.target.value})}
                    className="input-medical"
                  />
                </div>

                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-2">
                    Frequency
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
                    formatCreateLabel={(inputValue) => `Use: "${inputValue}"`}
                  />
                </div>

                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-2">
                    Indication
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
                    formatCreateLabel={(inputValue) => `Add: "${inputValue}"`}
                  />
                </div>

                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-2">
                    Duration
                  </label>
                  <select
                    value={currentMedication.duration}
                    onChange={(e) => setCurrentMedication({...currentMedication, duration: e.target.value})}
                    className="input-medical"
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
                className="btn-medical flex items-center gap-2"
              >
                <FaPlus />
                Add Medication
              </button>

              {formData.medications.length > 0 && (
                <div className="mt-4">
                  <h4 className="text-sm font-bold text-gray-700 mb-3 flex items-center gap-2">
                    <FaPills className="text-blue-600" />
                    Added Medications ({formData.medications.length})
                  </h4>
                  <div className="space-y-2">
                    {formData.medications.map((med, index) => (
                      <div 
                        key={index} 
                        className="flex items-center justify-between bg-white p-4 rounded-xl border border-blue-100
                                 shadow-sm hover:shadow-md transition-all duration-200 animate-fade-in"
                      >
                        <div className="flex items-center gap-3">
                          <div className="w-10 h-10 bg-gradient-to-br from-blue-100 to-blue-200 rounded-xl 
                                        flex items-center justify-center">
                            <FaPills className="text-blue-600" />
                          </div>
                          <div>
                            <span className="font-bold text-gray-800">{med.generic_name}</span>
                            {med.brand_name && <span className="text-gray-500 ml-1">({med.brand_name})</span>}
                            <p className="text-sm text-gray-500">
                              {med.dose} {med.frequency && `- ${med.frequency}`}
                            </p>
                          </div>
                        </div>
                        <button
                          type="button"
                          onClick={() => removeMedication(index)}
                          className="w-9 h-9 bg-red-50 hover:bg-red-100 text-red-600 rounded-xl 
                                   flex items-center justify-center transition-all duration-200 hover:scale-110"
                        >
                          <FaTrash className="text-sm" />
                        </button>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}
        </div>

        <div className="space-y-4">
          <SectionHeader 
            icon={FaLeaf} 
            title="Ayurvedic / Herbal Products" 
            section="herbs" 
            count={formData.herbs.length}
            color="green" 
          />
          
          {expandedSections.herbs && (
            <div className="animate-fade-in p-4 bg-green-50/50 rounded-xl space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                <div className="lg:col-span-1">
                  <label className="block text-sm font-semibold text-gray-700 mb-2">
                    Herb Name <span className="text-red-500">*</span>
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
                    formatCreateLabel={(inputValue) => `Add: "${inputValue}"`}
                  />
                </div>

                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-2">
                    Brand Name <span className="text-gray-400 text-xs">(Optional)</span>
                  </label>
                  <input
                    type="text"
                    placeholder="Product brand"
                    value={currentHerb.brand_name}
                    onChange={(e) => setCurrentHerb({...currentHerb, brand_name: e.target.value})}
                    className="input-medical"
                  />
                </div>

                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-2">Dose</label>
                  <input
                    type="text"
                    placeholder="e.g., 500mg"
                    value={currentHerb.dose}
                    onChange={(e) => setCurrentHerb({...currentHerb, dose: e.target.value})}
                    className="input-medical"
                  />
                </div>

                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-2">Frequency</label>
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
                    placeholder="Select..."
                    styles={herbSelectStyles}
                  />
                </div>

                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-2">Intended Effect</label>
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
                    placeholder="What is it for?"
                    styles={herbSelectStyles}
                  />
                </div>

                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-2">Duration</label>
                  <select
                    value={currentHerb.duration}
                    onChange={(e) => setCurrentHerb({...currentHerb, duration: e.target.value})}
                    className="input-medical"
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
                className="px-6 py-3 bg-gradient-to-r from-green-500 to-emerald-600 text-white 
                         font-semibold rounded-xl hover:from-green-600 hover:to-emerald-700
                         transform transition-all duration-300 hover:scale-105 shadow-lg
                         flex items-center gap-2"
              >
                <FaPlus />
                Add Herb
              </button>

              {formData.herbs.length > 0 && (
                <div className="mt-4">
                  <h4 className="text-sm font-bold text-gray-700 mb-3 flex items-center gap-2">
                    <FaLeaf className="text-green-600" />
                    Added Herbs ({formData.herbs.length})
                  </h4>
                  <div className="space-y-2">
                    {formData.herbs.map((herb, index) => (
                      <div 
                        key={index} 
                        className="flex items-center justify-between bg-white p-4 rounded-xl border border-green-100
                                 shadow-sm hover:shadow-md transition-all duration-200 animate-fade-in"
                      >
                        <div className="flex items-center gap-3">
                          <div className="w-10 h-10 bg-gradient-to-br from-green-100 to-green-200 rounded-xl 
                                        flex items-center justify-center">
                            <FaLeaf className="text-green-600" />
                          </div>
                          <div>
                            <span className="font-bold text-gray-800">{herb.generic_name}</span>
                            {herb.brand_name && <span className="text-gray-500 ml-1">({herb.brand_name})</span>}
                            <p className="text-sm text-gray-500">
                              {herb.dose || 'No dose specified'} {herb.frequency && `- ${herb.frequency}`}
                            </p>
                          </div>
                        </div>
                        <button
                          type="button"
                          onClick={() => removeHerb(index)}
                          className="w-9 h-9 bg-red-50 hover:bg-red-100 text-red-600 rounded-xl 
                                   flex items-center justify-center transition-all duration-200 hover:scale-110"
                        >
                          <FaTrash className="text-sm" />
                        </button>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}
        </div>

        <div className="pt-6 border-t border-gray-100">
          <button
            type="submit"
            disabled={isLoading}
            className={`w-full py-4 rounded-2xl font-bold text-lg shadow-xl transition-all duration-300 
                      flex items-center justify-center gap-3 ${
              isLoading
                ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                : 'bg-gradient-to-r from-cyan-500 via-blue-500 to-indigo-600 text-white hover:from-cyan-600 hover:via-blue-600 hover:to-indigo-700 hover:shadow-2xl hover:scale-[1.02]'
            }`}
          >
            {isLoading ? (
              <>
                <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none"/>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"/>
                </svg>
                Analyzing...
              </>
            ) : (
              <>
                <FaRobot className="text-xl" />
                Analyze Patient with AI
              </>
            )}
          </button>
        </div>
      </form>
    </div>
  );
};

export default PatientForm;
