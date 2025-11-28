import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// API Methods
export const analyzePatient = async (patientData) => {
  try {
    const response = await api.post('/analyze-patient', { patient: patientData });
    return response.data;
  } catch (error) {
    console.error('Error analyzing patient:', error);
    throw error;
  }
};

export const getTaperPlan = async (taperRequest) => {
  try {
    const response = await api.post('/get-taper-plan', taperRequest);
    return response.data;
  } catch (error) {
    console.error('Error getting taper plan:', error);
    throw error;
  }
};

export const checkInteractions = async (interactionRequest) => {
  try {
    const response = await api.post('/interaction-checker', interactionRequest);
    return response.data;
  } catch (error) {
    console.error('Error checking interactions:', error);
    throw error;
  }
};

export const getHealthCheck = async () => {
  try {
    const response = await api.get('/health');
    return response.data;
  } catch (error) {
    console.error('Error checking health:', error);
    throw error;
  }
};

export const getSupportedDrugs = async () => {
  try {
    const response = await api.get('/supported-drugs');
    return response.data;
  } catch (error) {
    console.error('Error getting supported drugs:', error);
    throw error;
  }
};

export default api;
