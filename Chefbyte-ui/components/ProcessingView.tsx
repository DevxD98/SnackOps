import React, { useEffect, useState } from 'react';
import { Scan, BrainCircuit, Database, Utensils } from 'lucide-react';

const ProcessingView: React.FC = () => {
  const [step, setStep] = useState(0);
  const steps = [
    { icon: Scan, text: "Scanning visual input...", color: "text-blue-400" },
    { icon: Database, text: "Extracting ingredients...", color: "text-purple-400" },
    { icon: BrainCircuit, text: "Analyzing nutritional profiles...", color: "text-pink-400" },
    { icon: Utensils, text: "Constructing culinary plan...", color: "text-orange-400" }
  ];

  useEffect(() => {
    const interval = setInterval(() => {
      setStep((s) => (s < steps.length - 1 ? s + 1 : s));
    }, 1500);
    return () => clearInterval(interval);
  }, [steps.length]);

  return (
    <div className="w-full flex flex-col items-center justify-center py-16">
      <div className="relative w-32 h-32 mb-8">
        <div className="absolute inset-0 rounded-full bg-blue-500/20 animate-ping"></div>
        <div className="absolute inset-2 rounded-full bg-purple-500/20 animate-ping animation-delay-2000"></div>
        <div className="absolute inset-0 flex items-center justify-center">
          <div className="w-24 h-24 bg-slate-900 rounded-full border border-slate-700 flex items-center justify-center shadow-2xl shadow-blue-900/50 relative overflow-hidden">
            <div className="absolute inset-0 bg-gradient-to-tr from-slate-900 via-slate-800 to-slate-900"></div>
            {React.createElement(steps[step].icon, { 
              className: `w-10 h-10 relative z-10 animate-pulse ${steps[step].color}` 
            })}
          </div>
        </div>
      </div>

      <h2 className="text-2xl font-bold text-white mb-6 tracking-tight">Agent Working</h2>
      
      <div className="space-y-3 w-full max-w-xs">
        {steps.map((s, i) => (
          <div 
            key={i} 
            className={`flex items-center gap-3 p-3 rounded-lg transition-all duration-500 ${
              i === step 
                ? 'bg-slate-800/80 border border-slate-600 translate-x-2' 
                : i < step 
                  ? 'opacity-30' 
                  : 'opacity-10'
            }`}
          >
            <div className={`w-2 h-2 rounded-full ${i === step ? 'bg-emerald-400 animate-pulse' : 'bg-slate-600'}`}></div>
            <span className={`text-sm font-medium ${i === step ? 'text-white' : 'text-slate-400'}`}>{s.text}</span>
          </div>
        ))}
      </div>
    </div>
  );
};

export default ProcessingView;
