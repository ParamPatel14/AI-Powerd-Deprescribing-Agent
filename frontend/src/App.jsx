import React, { useState } from 'react';
import { FaHospitalAlt } from 'react-icons/fa';
import PatientForm from './components/PatientForm';
import MedicationTable from './components/MedicationTable';
import ResultsDashboard from './components/ResultsDashboard';
import LoadingSpinner from './components/LoadingSpinner';
import { analyzePatient } from './services/api';
import './App.css';

function App() {
  const [patientData, setPatientData] = useState(null);
  const [results, setResults] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [showResults, setShowResults] = useState(false);

  const handlePatientSubmit = async (formData) => {
    setIsLoading(true);
    setError(null);
    setShowResults(false);

    try {
      console.log('Submitting patient data:', formData);
      const analysisResults = await analyzePatient(formData);
      console.log('Analysis results:', analysisResults);
      
      setPatientData(formData);
      setResults(analysisResults);
      setShowResults(true);
      
      // Scroll to results
      setTimeout(() => {
        window.scrollTo({ top: document.body.scrollHeight, behavior: 'smooth' });
      }, 100);
    } catch (err) {
      console.error('Error analyzing patient:', err);
      setError(err.response?.data?.detail || err.message || 'An error occurred during analysis');
    } finally {
      setIsLoading(false);
    }
  };

  const handleReset = () => {
    setPatientData(null);
    setResults(null);
    setShowResults(false);
    setError(null);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  return (
    <div className="min-h-screen bg-gray-100">
      {/* Header */}
      <header className="bg-indigo-700 text-white shadow-lg">
        <div className="container mx-auto px-4 py-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <FaHospitalAlt className="text-4xl" />
              <div>
                <h1 className="text-3xl font-bold">Deprescribing Clinical Decision Support</h1>
                <p className="text-indigo-200 text-sm">Evidence-Based Medication Review System</p>
              </div>
            </div>
            {showResults && (
              <button
                onClick={handleReset}
                className="px-6 py-2 bg-white text-indigo-700 rounded-md hover:bg-indigo-50 transition font-semibold"
              >
                New Patient
              </button>
            )}
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-8">
        {!showResults && (
          <PatientForm onSubmit={handlePatientSubmit} isLoading={isLoading} />
        )}

        {isLoading && (
          <div className="bg-white rounded-lg shadow-lg p-12">
            <LoadingSpinner message="Analyzing patient medications through 9 clinical modules..." />
          </div>
        )}

        {error && (
          <div className="bg-red-50 border-l-4 border-red-500 p-6 rounded-lg shadow mb-6">
            <div className="flex items-start">
              <span className="text-red-500 text-2xl mr-3">⚠️</span>
              <div>
                <h3 className="text-lg font-semibold text-red-800 mb-2">Analysis Error</h3>
                <p className="text-red-700">{error}</p>
                <button
                  onClick={handleReset}
                  className="mt-4 px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700 transition"
                >
                  Try Again
                </button>
              </div>
            </div>
          </div>
        )}

        {showResults && patientData && (
          <>
            <MedicationTable
              medications={patientData.medications}
              herbs={patientData.herbs}
            />
            <ResultsDashboard results={results} patientData={patientData} />
          </>
        )}
      </main>

      {/* Footer */}
      <footer className="bg-gray-800 text-white py-6 mt-12">
        <div className="container mx-auto px-4 text-center">
          <p className="text-gray-400">
            Deprescribing Engine v1.0 | 9-Module Clinical Analysis System
          </p>
          <p className="text-gray-500 text-sm mt-2">
            For clinical decision support purposes only. Always consult with healthcare professionals.
          </p>
        </div>
      </footer>
    </div>
  );
}

export default App;
