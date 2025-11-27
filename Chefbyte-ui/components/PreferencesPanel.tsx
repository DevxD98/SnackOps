import React from 'react';
import { UserPreferences, DietType } from '../types';
import { Clock, Flame, Users, Leaf } from 'lucide-react';

interface PreferencesPanelProps {
  prefs: UserPreferences;
  setPrefs: React.Dispatch<React.SetStateAction<UserPreferences>>;
}

const PreferencesPanel: React.FC<PreferencesPanelProps> = ({ prefs, setPrefs }) => {
  
  const handleChange = (key: keyof UserPreferences, value: any) => {
    setPrefs(prev => ({ ...prev, [key]: value }));
  };

  return (
    <div className="w-full max-w-2xl mx-auto mt-6 grid grid-cols-2 md:grid-cols-4 gap-4">
      
      <div className="glass-panel p-3 rounded-xl flex flex-col gap-2 relative overflow-hidden group">
        <div className="absolute inset-0 bg-gradient-to-br from-green-500/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity" />
        <div className="flex items-center gap-2 text-green-400 text-xs font-bold uppercase tracking-wider">
          <Leaf className="w-3 h-3" /> Diet
        </div>
        <select 
          value={prefs.diet}
          onChange={(e) => handleChange('diet', e.target.value)}
          className="bg-transparent text-white font-medium outline-none cursor-pointer text-sm"
        >
          {Object.values(DietType).map(d => (
            <option key={d} value={d} className="bg-slate-900">{d}</option>
          ))}
        </select>
      </div>

      <div className="glass-panel p-3 rounded-xl flex flex-col gap-2 relative overflow-hidden group">
        <div className="absolute inset-0 bg-gradient-to-br from-blue-500/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity" />
        <div className="flex items-center gap-2 text-blue-400 text-xs font-bold uppercase tracking-wider">
          <Clock className="w-3 h-3" /> Time
        </div>
        <select 
          value={prefs.timeLimit}
          onChange={(e) => handleChange('timeLimit', e.target.value)}
          className="bg-transparent text-white font-medium outline-none cursor-pointer text-sm"
        >
          <option value="15 minutes" className="bg-slate-900">Quick (15m)</option>
          <option value="30 minutes" className="bg-slate-900">Medium (30m)</option>
          <option value="45 minutes" className="bg-slate-900">Standard (45m)</option>
          <option value="60 minutes" className="bg-slate-900">Long (1h+)</option>
        </select>
      </div>

      <div className="glass-panel p-3 rounded-xl flex flex-col gap-2 relative overflow-hidden group">
        <div className="absolute inset-0 bg-gradient-to-br from-orange-500/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity" />
        <div className="flex items-center gap-2 text-orange-400 text-xs font-bold uppercase tracking-wider">
          <Flame className="w-3 h-3" /> Calories
        </div>
        <select 
          value={prefs.calories}
          onChange={(e) => handleChange('calories', parseInt(e.target.value))}
          className="bg-transparent text-white font-medium outline-none cursor-pointer text-sm"
        >
          <option value="400" className="bg-slate-900">Light (400)</option>
          <option value="600" className="bg-slate-900">Standard (600)</option>
          <option value="800" className="bg-slate-900">Heavy (800)</option>
          <option value="1000" className="bg-slate-900">Bulk (1000+)</option>
        </select>
      </div>

      <div className="glass-panel p-3 rounded-xl flex flex-col gap-2 relative overflow-hidden group">
        <div className="absolute inset-0 bg-gradient-to-br from-purple-500/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity" />
        <div className="flex items-center gap-2 text-purple-400 text-xs font-bold uppercase tracking-wider">
          <Users className="w-3 h-3" /> Servings
        </div>
        <select 
          value={prefs.servings}
          onChange={(e) => handleChange('servings', parseInt(e.target.value))}
          className="bg-transparent text-white font-medium outline-none cursor-pointer text-sm"
        >
          {[1, 2, 3, 4, 5, 6].map(n => (
            <option key={n} value={n} className="bg-slate-900">{n} People</option>
          ))}
        </select>
      </div>

    </div>
  );
};

export default PreferencesPanel;
