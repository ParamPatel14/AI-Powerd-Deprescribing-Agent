import React, { useState, useEffect } from 'react';
import { FaHospitalAlt, FaUserMd, FaHeartbeat, FaShieldAlt, FaChevronUp } from 'react-icons/fa';
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
  const [showScrollTop, setShowScrollTop] = useState(false);

  useEffect(() => {
    const handleScroll = () => {
      setShowScrollTop(window.scrollY > 400);
    };
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  const scrollToTop = () => {
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

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
    <div className="min-h-screen bg-gradient-to-br from-cyan-50 via-white to-blue-50">
      <header className="medical-gradient text-white shadow-2xl sticky top-0 z-50">
        <div className="absolute inset-0 overflow-hidden">
          <div className="absolute -top-1/2 -right-1/4 w-96 h-96 bg-white/5 rounded-full blur-3xl"></div>
          <div className="absolute -bottom-1/2 -left-1/4 w-96 h-96 bg-cyan-300/10 rounded-full blur-3xl"></div>
        </div>
        
        <div className="container mx-auto px-4 py-5 relative">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4 animate-fade-in">
              <div className="relative">
                <div className="w-14 h-14 bg-white/20 backdrop-blur-sm rounded-2xl flex items-center justify-center border border-white/30 shadow-lg">
                  <FaHospitalAlt className="text-3xl text-white" />
                </div>
                <div className="absolute -top-1 -right-1 w-4 h-4 bg-green-400 rounded-full border-2 border-white animate-pulse"></div>
              </div>
              <div>
                <h1 className="text-2xl md:text-3xl font-bold tracking-tight flex items-center gap-2">
                  <span>Deprescribing</span>
                  <span className="text-cyan-200">CDS</span>
                </h1>
                <p className="text-cyan-100 text-sm font-medium flex items-center gap-2">
                  <FaShieldAlt className="text-xs" />
                  Evidence-Based Medication Review System
                </p>
              </div>
            </div>

            <div className="flex items-center gap-4">
              <div className="hidden md:flex items-center gap-6 text-sm">
                <div className="flex items-center gap-2 bg-white/10 backdrop-blur-sm px-4 py-2 rounded-xl border border-white/20">
                  <FaUserMd className="text-cyan-200" />
                  <span>9-Module Analysis</span>
                </div>
                <div className="flex items-center gap-2 bg-white/10 backdrop-blur-sm px-4 py-2 rounded-xl border border-white/20">
                  <FaHeartbeat className="text-red-300 heartbeat-icon" />
                  <span>Clinical Grade</span>
                </div>
              </div>

              {showResults && (
                <button
                  onClick={handleReset}
                  className="px-6 py-2.5 bg-white text-medical-dark rounded-xl font-semibold 
                           hover:bg-cyan-50 transform transition-all duration-300 hover:scale-105 
                           shadow-lg hover:shadow-xl flex items-center gap-2"
                >
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
                  </svg>
                  New Patient
                </button>
              )}
            </div>
          </div>
        </div>
      </header>

      <main className="container mx-auto px-4 py-8">
        {!showResults && !isLoading && (
          <div className="animate-fade-in-up">
            <div className="text-center mb-8">
              <div className="inline-flex items-center gap-2 bg-gradient-to-r from-cyan-500/10 to-blue-500/10 
                            px-4 py-2 rounded-full border border-cyan-200 mb-4">
                <span className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></span>
                <span className="text-sm font-medium text-gray-600">System Ready</span>
              </div>
              <h2 className="text-3xl font-bold text-gray-800 mb-2">
                Patient Medication Analysis
              </h2>
              <p className="text-gray-500 max-w-2xl mx-auto">
                Enter patient information below to receive comprehensive deprescribing recommendations 
                powered by evidence-based clinical decision support algorithms.
              </p>
            </div>
            <PatientForm onSubmit={handlePatientSubmit} isLoading={isLoading} />
          </div>
        )}

        {isLoading && (
          <div className="animate-scale-in">
            <div className="card-medical p-12 text-center">
              <LoadingSpinner 
                message="Analyzing patient medications through 9 clinical modules..." 
                showAI={true}
              />
              <div className="mt-8 grid grid-cols-3 gap-4 max-w-md mx-auto">
                {['STOPP/START', 'Beers Criteria', 'ACB Score'].map((module, i) => (
                  <div 
                    key={module}
                    className={`bg-gradient-to-br from-cyan-50 to-blue-50 rounded-xl p-3 border border-cyan-100
                               animate-pulse stagger-${i + 1}`}
                  >
                    <p className="text-xs font-medium text-gray-600">{module}</p>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {error && (
          <div className="animate-fade-in">
            <div className="bg-gradient-to-r from-red-50 to-rose-50 border-l-4 border-red-500 
                          p-6 rounded-2xl shadow-lg mb-6">
              <div className="flex items-start gap-4">
                <div className="w-12 h-12 bg-red-100 rounded-xl flex items-center justify-center flex-shrink-0">
                  <svg className="w-6 h-6 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} 
                          d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                  </svg>
                </div>
                <div className="flex-1">
                  <h3 className="text-lg font-bold text-red-800 mb-2">Analysis Error</h3>
                  <p className="text-red-700 mb-4">{error}</p>
                  <button
                    onClick={handleReset}
                    className="px-5 py-2.5 bg-gradient-to-r from-red-500 to-red-600 text-white 
                             rounded-xl font-medium hover:from-red-600 hover:to-red-700 
                             transform transition-all duration-300 hover:scale-105 shadow-lg"
                  >
                    Try Again
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}

        {showResults && patientData && (
          <div className="space-y-8 animate-fade-in-up">
            <div className="text-center mb-6">
              <div className="inline-flex items-center gap-2 bg-gradient-to-r from-green-500/10 to-emerald-500/10 
                            px-4 py-2 rounded-full border border-green-200 mb-4">
                <svg className="w-4 h-4 text-green-600" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                </svg>
                <span className="text-sm font-medium text-green-700">Analysis Complete</span>
              </div>
              <h2 className="text-3xl font-bold text-gray-800">
                Clinical Analysis Results
              </h2>
            </div>

            <MedicationTable
              medications={patientData.medications}
              herbs={patientData.herbs}
            />
            <ResultsDashboard results={results} patientData={patientData} />
          </div>
        )}
      </main>

      <footer className="bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900 text-white py-10 mt-12">
        <div className="container mx-auto px-4">
          <div className="flex flex-col md:flex-row items-center justify-between gap-6">
            <div className="flex items-center gap-4">
              <div className="w-12 h-12 bg-gradient-to-br from-cyan-500 to-blue-600 rounded-xl 
                            flex items-center justify-center shadow-lg">
                <FaHospitalAlt className="text-2xl text-white" />
              </div>
              <div>
                <p className="font-bold text-lg">Deprescribing Engine v1.0</p>
                <p className="text-gray-400 text-sm">9-Module Clinical Analysis System</p>
              </div>
            </div>
            
            <div className="flex items-center gap-6">
              <div className="flex items-center gap-2 text-gray-400">
                <FaShieldAlt className="text-cyan-400" />
                <span className="text-sm">HIPAA Compliant Design</span>
              </div>
              <div className="hidden md:block h-6 w-px bg-gray-700"></div>
              <div className="text-gray-400 text-sm text-center md:text-right">
                For clinical decision support purposes only.<br className="hidden md:block" />
                Always consult with healthcare professionals.
              </div>
            </div>
          </div>
        </div>
      </footer>

      {showScrollTop && (
        <button
          onClick={scrollToTop}
          className="fixed bottom-8 right-8 w-12 h-12 bg-gradient-to-br from-cyan-500 to-blue-600 
                   text-white rounded-full shadow-xl hover:shadow-2xl transform transition-all 
                   duration-300 hover:scale-110 flex items-center justify-center z-50 animate-fade-in"
        >
          <FaChevronUp className="text-lg" />
        </button>
      )}
    </div>
  );
}

export default App;
