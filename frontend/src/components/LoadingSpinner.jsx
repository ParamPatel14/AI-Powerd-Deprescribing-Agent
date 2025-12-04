import React from 'react';
import { FaHeartbeat, FaRobot, FaBrain, FaFlask, FaChartLine } from 'react-icons/fa';

const LoadingSpinner = ({ message = 'Loading...', showAI = false }) => {
  return (
    <div className="flex flex-col items-center justify-center py-8">
      <div className="relative mb-8">
        <div className="w-24 h-24 rounded-full bg-gradient-to-br from-cyan-100 to-blue-100 
                      flex items-center justify-center animate-pulse">
          <div className="w-20 h-20 rounded-full bg-gradient-to-br from-cyan-50 to-white 
                        flex items-center justify-center shadow-inner">
            <FaHeartbeat className="text-4xl text-medical-primary heartbeat-icon" />
          </div>
        </div>
        
        <div className="absolute inset-0 w-24 h-24">
          <svg className="w-full h-full animate-spin" style={{ animationDuration: '3s' }}>
            <circle
              cx="48"
              cy="48"
              r="46"
              stroke="url(#gradient)"
              strokeWidth="3"
              fill="none"
              strokeDasharray="80 200"
              strokeLinecap="round"
            />
            <defs>
              <linearGradient id="gradient" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" stopColor="#0891B2" />
                <stop offset="100%" stopColor="#164E63" />
              </linearGradient>
            </defs>
          </svg>
        </div>

        {showAI && (
          <div className="absolute -top-2 -right-2 w-10 h-10 bg-gradient-to-br from-purple-500 to-indigo-600 
                        rounded-xl flex items-center justify-center shadow-lg animate-bounce-soft">
            <FaRobot className="text-white text-lg" />
          </div>
        )}

        <div className="absolute -bottom-1 left-1/2 transform -translate-x-1/2">
          <div className="flex gap-1">
            {[0, 1, 2].map((i) => (
              <div
                key={i}
                className="w-2 h-2 bg-medical-primary rounded-full animate-bounce"
                style={{ animationDelay: `${i * 0.15}s` }}
              />
            ))}
          </div>
        </div>
      </div>

      <div className="text-center max-w-md">
        <p className="text-gray-700 text-lg font-medium mb-2">{message}</p>
        {showAI && (
          <p className="text-medical-primary text-sm font-medium flex items-center justify-center gap-2">
            <FaBrain className="animate-pulse" />
            AI-Powered Clinical Analysis in Progress
          </p>
        )}
      </div>

      {showAI && (
        <div className="mt-8 w-full max-w-sm">
          <div className="flex justify-between items-center mb-3">
            <span className="text-xs font-medium text-gray-500 uppercase tracking-wide">
              Analysis Progress
            </span>
            <span className="text-xs font-bold text-medical-primary">Processing...</span>
          </div>
          
          <div className="h-2 bg-gray-100 rounded-full overflow-hidden">
            <div className="h-full bg-gradient-to-r from-cyan-500 via-blue-500 to-cyan-500 
                          rounded-full shimmer" 
                 style={{ width: '100%', backgroundSize: '200% 100%' }}>
            </div>
          </div>

          <div className="mt-6 grid grid-cols-4 gap-3">
            {[
              { icon: FaFlask, label: 'Beers', color: 'from-red-400 to-rose-500' },
              { icon: FaChartLine, label: 'STOPP', color: 'from-amber-400 to-orange-500' },
              { icon: FaBrain, label: 'ACB', color: 'from-purple-400 to-indigo-500' },
              { icon: FaHeartbeat, label: 'TTB', color: 'from-green-400 to-emerald-500' },
            ].map((item, index) => (
              <div
                key={item.label}
                className="flex flex-col items-center gap-2 animate-fade-in"
                style={{ animationDelay: `${index * 0.2}s` }}
              >
                <div className={`w-10 h-10 bg-gradient-to-br ${item.color} rounded-xl 
                              flex items-center justify-center shadow-md animate-pulse`}
                     style={{ animationDelay: `${index * 0.3}s` }}>
                  <item.icon className="text-white text-sm" />
                </div>
                <span className="text-xs font-medium text-gray-500">{item.label}</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default LoadingSpinner;
