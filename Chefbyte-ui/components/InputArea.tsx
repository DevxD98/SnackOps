import React, { useState, useRef } from 'react';
import { Camera, Upload, Type, X, Image as ImageIcon, ScanLine, ChefHat } from 'lucide-react';
import { InputMode } from '../types';

interface InputAreaProps {
  onAnalyze: (mode: 'image' | 'text', data: string) => void;
  isProcessing: boolean;
}

const InputArea: React.FC<InputAreaProps> = ({ onAnalyze, isProcessing }) => {
  const [mode, setMode] = useState<InputMode>('fridge');
  const [textInput, setTextInput] = useState('');
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      const reader = new FileReader();
      reader.onloadend = () => {
        setPreviewUrl(reader.result as string);
      };
      reader.readAsDataURL(file);
    }
  };

  const handleTextSubmit = () => {
    if (textInput.trim()) {
      onAnalyze('text', textInput);
    }
  };

  const handleImageSubmit = () => {
    if (previewUrl) {
      onAnalyze('image', previewUrl);
    }
  };

  const clearImage = () => {
    setPreviewUrl(null);
    if (fileInputRef.current) fileInputRef.current.value = '';
  };

  return (
    <div className="w-full max-w-2xl mx-auto">
      {/* Tabs */}
      <div className="flex p-1 bg-slate-900/80 backdrop-blur-md rounded-2xl border border-slate-800 mb-6 relative z-10">
        {(['fridge', 'receipt', 'text'] as InputMode[]).map((m) => (
          <button
            key={m}
            onClick={() => { setMode(m); setPreviewUrl(null); setTextInput(''); }}
            className={`flex-1 flex items-center justify-center gap-2 py-3 rounded-xl text-sm font-medium transition-all duration-300 ${
              mode === m 
                ? 'bg-slate-800 text-white shadow-lg shadow-orange-500/10 border border-slate-700' 
                : 'text-slate-500 hover:text-slate-300'
            }`}
          >
            {m === 'fridge' && <Camera className="w-4 h-4" />}
            {m === 'receipt' && <ScanLine className="w-4 h-4" />}
            {m === 'text' && <Type className="w-4 h-4" />}
            <span className="capitalize">{m} Input</span>
          </button>
        ))}
      </div>

      {/* Content Area */}
      <div className="glass-panel rounded-3xl p-6 md:p-8 transition-all duration-500">
        
        {mode === 'text' ? (
          <div className="space-y-4">
            <label className="block text-sm text-slate-400 mb-2">
              Enter available ingredients manually:
            </label>
            <textarea
              className="w-full h-32 bg-slate-950/50 border border-slate-700 rounded-xl p-4 text-slate-200 focus:ring-2 focus:ring-orange-500/50 focus:border-orange-500 outline-none transition-all resize-none"
              placeholder="e.g. 2 eggs, spinach, leftover chicken, soy sauce..."
              value={textInput}
              onChange={(e) => setTextInput(e.target.value)}
            />
            <button
              onClick={handleTextSubmit}
              disabled={!textInput.trim() || isProcessing}
              className="w-full py-4 bg-gradient-to-r from-orange-500 to-red-600 text-white font-bold rounded-xl hover:opacity-90 disabled:opacity-50 disabled:cursor-not-allowed transition-all shadow-lg shadow-orange-900/20 flex items-center justify-center gap-2"
            >
              {isProcessing ? <Sparkles className="w-5 h-5 animate-spin" /> : <ChefHat className="w-5 h-5" />}
              Generate Meal Plan
            </button>
          </div>
        ) : (
          <div className="space-y-6">
            <div 
              className={`relative w-full h-64 border-2 border-dashed rounded-2xl flex flex-col items-center justify-center transition-all ${
                previewUrl ? 'border-slate-700 bg-slate-900' : 'border-slate-700 hover:border-slate-500 hover:bg-slate-800/30 cursor-pointer'
              }`}
              onClick={() => !previewUrl && fileInputRef.current?.click()}
            >
              {previewUrl ? (
                <>
                  <img src={previewUrl} alt="Preview" className="h-full w-full object-contain rounded-xl opacity-80" />
                  <button 
                    onClick={(e) => { e.stopPropagation(); clearImage(); }}
                    className="absolute top-4 right-4 p-2 bg-slate-900/80 text-white rounded-full hover:bg-red-500/80 transition-colors"
                  >
                    <X className="w-5 h-5" />
                  </button>
                </>
              ) : (
                <>
                  <div className="w-16 h-16 rounded-full bg-slate-800 flex items-center justify-center mb-4">
                    {mode === 'fridge' ? <ImageIcon className="w-8 h-8 text-slate-400" /> : <ScanLine className="w-8 h-8 text-slate-400" />}
                  </div>
                  <p className="text-slate-300 font-medium">Click to upload {mode} photo</p>
                  <p className="text-slate-500 text-sm mt-2">JPG, PNG supported</p>
                </>
              )}
              <input 
                type="file" 
                ref={fileInputRef} 
                className="hidden" 
                accept="image/*" 
                onChange={handleFileChange} 
              />
            </div>

            <button
              onClick={handleImageSubmit}
              disabled={!previewUrl || isProcessing}
              className="w-full py-4 bg-gradient-to-r from-orange-500 to-red-600 text-white font-bold rounded-xl hover:opacity-90 disabled:opacity-50 disabled:cursor-not-allowed transition-all shadow-lg shadow-orange-900/20 flex items-center justify-center gap-2"
            >
              {isProcessing ? <ScanLine className="w-5 h-5 animate-pulse" /> : <Sparkles className="w-5 h-5" />}
              Analyze {mode === 'fridge' ? 'Ingredients' : 'Receipt'}
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

function Sparkles({ className }: { className?: string }) {
    return (
      <svg className={className} xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="m12 3-1.912 5.813a2 2 0 0 1-1.275 1.275L3 12l5.813 1.912a2 2 0 0 1 1.275 1.275L12 21l1.912-5.813a2 2 0 0 1 1.275-1.275L21 12l-5.813-1.912a2 2 0 0 1-1.275-1.275L12 3Z"/><path d="M5 3v4"/><path d="M9 3v4"/><path d="M3 9h4"/><path d="M3 5h4"/></svg>
    );
}

export default InputArea;