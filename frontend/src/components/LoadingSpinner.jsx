import React from 'react';
import { FaSpinner } from 'react-icons/fa';

const LoadingSpinner = ({ message = 'Loading...' }) => {
  return (
    <div className="flex flex-col items-center justify-center py-12">
      <FaSpinner className="animate-spin text-indigo-600 text-6xl mb-4" />
      <p className="text-gray-600 text-lg">{message}</p>
    </div>
  );
};

export default LoadingSpinner;
