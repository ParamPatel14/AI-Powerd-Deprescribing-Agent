import React from 'react';
import { FaSpinner, FaRobot } from 'react-icons/fa';

const LoadingSpinner = ({ message = 'Loading...', showAI = false }) => {
  return (
    <div className="flex flex-col items-center justify-center py-12">
      {showAI ? (
        <>
          <FaRobot className="text-purple-600 text-6xl mb-4 animate-pulse" />
          <FaSpinner className="animate-spin text-indigo-600 text-4xl mb-4" />
        </>
      ) : (
        <FaSpinner className="animate-spin text-indigo-600 text-6xl mb-4" />
      )}
      <p className="text-gray-600 text-lg text-center max-w-md">{message}</p>
      {showAI && (
        <p className="text-purple-600 text-sm mt-2">Powered by AI</p>
      )}
    </div>
  );
};

export default LoadingSpinner;
