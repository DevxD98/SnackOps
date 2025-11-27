
import React, { useState, useEffect } from 'react';
import { ChefResponse, UserPreferences } from '../types';
import RecipeCard from './RecipeCard';
import IngredientVisualizer from './IngredientVisualizer';
import { Quote, RotateCcw, Users, RefreshCw, Receipt, Calendar, Store, DollarSign, ArrowLeft } from 'lucide-react';

interface ResultsViewProps {
  data: ChefResponse;
  userPrefs: UserPreferences;
  onReset: () => void;
  onGenerateAlternatives: () => void;
  isRegenerating: boolean;
  onBack: () => void;
}

const ResultsView: React.FC<ResultsViewProps> = ({
  data,
  userPrefs,
  onReset,
  onGenerateAlternatives,
  isRegenerating,
  onBack
}) => {
  const [servings, setServings] = useState(userPrefs.servings);

  // Reset local servings if new data comes in
  useEffect(() => {
    setServings(userPrefs.servings);
  }, [data, userPrefs.servings]);

  const handleServingsChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setServings(parseInt(e.target.value));
  };

  return (
    <div className="w-full max-w-4xl mx-auto animate-in fade-in duration-700 slide-in-from-bottom-8">

      {/* Back Button */}
      <div className="mb-6">
        <button
          onClick={onBack}
          className="px-4 py-2 bg-slate-800 hover:bg-slate-700 border border-slate-600 rounded-lg text-sm font-medium text-slate-300 flex items-center gap-2 transition-all"
        >
          <ArrowLeft className="w-4 h-4" />
          Back to Home
        </button>
      </div>

      {/* Receipt Metadata Card */}
      {data.receiptData && (data.receiptData.storeName || data.receiptData.total) && (
        <div className="mb-8 bg-[#f0fdf4] text-slate-900 p-4 rounded-xl border-b-4 border-slate-200 shadow-lg relative overflow-hidden font-mono max-w-md mx-auto transform -rotate-1">
          <div className="absolute top-0 left-0 w-full h-1 bg-slate-300/50"></div>
          <div className="flex justify-between items-start mb-3 border-b-2 border-dashed border-slate-300 pb-2">
            <div className="flex items-center gap-2">
              <div className="p-2 bg-slate-900 rounded-full text-white">
                <Receipt className="w-4 h-4" />
              </div>
              <div>
                <h4 className="font-bold uppercase text-sm tracking-widest">{data.receiptData.storeName || 'Unknown Store'}</h4>
                <div className="flex items-center gap-1 text-xs text-slate-500">
                  <Calendar className="w-3 h-3" />
                  <span>{data.receiptData.date || 'Today'}</span>
                </div>
              </div>
            </div>
            {data.receiptData.total && (
              <div className="text-right">
                <div className="text-2xl font-bold flex items-center justify-end">
                  <span className="text-sm text-slate-500 mr-1">Total</span>
                  {data.receiptData.total}
                </div>
              </div>
            )}
          </div>
          <div className="text-xs text-center text-slate-400 uppercase tracking-widest">Receipt Processed Successfully</div>
        </div>
      )}

      {/* Interactive Ingredient Visualizer */}
      <IngredientVisualizer ingredients={data.detectedIngredients} />

      {/* Controls Bar: Servings & Regen */}
      <div className="glass-panel rounded-xl p-4 mb-8 flex flex-col md:flex-row items-center justify-between gap-4">

        <div className="flex items-center gap-4 w-full md:w-auto">
          <div className="flex items-center gap-2 text-slate-400 text-sm font-bold uppercase tracking-wider">
            <Users className="w-4 h-4" /> Scale Servings
          </div>
          <div className="flex items-center gap-3 flex-1 md:flex-none">
            <input
              type="range"
              min="1"
              max="12"
              value={servings}
              onChange={handleServingsChange}
              className="w-32 accent-orange-500 h-1.5 bg-slate-700 rounded-lg appearance-none cursor-pointer"
            />
            <span className="w-8 text-center font-mono text-white font-bold">{servings}</span>
          </div>
        </div>

        <button
          onClick={onGenerateAlternatives}
          disabled={isRegenerating}
          className="w-full md:w-auto px-4 py-2 bg-slate-800 hover:bg-slate-700 border border-slate-600 rounded-lg text-sm font-medium text-slate-300 flex items-center justify-center gap-2 transition-all disabled:opacity-50"
        >
          <RefreshCw className={`w-4 h-4 ${isRegenerating ? 'animate-spin' : ''}`} />
          {isRegenerating ? 'Thinking...' : 'Try Different Recipes'}
        </button>
      </div>

      {/* Agent Reasoning */}
      <div className="mb-10 relative">
        <div className="absolute -left-4 top-0 bottom-0 w-1 bg-gradient-to-b from-orange-500 to-transparent rounded-full"></div>
        <Quote className="w-8 h-8 text-slate-700 absolute -top-4 -left-2 transform -translate-x-full opacity-50" />
        <p className="text-lg text-slate-200 italic font-light leading-relaxed pl-4">
          "{data.reasoning}"
        </p>
      </div>

      {/* Recipe Grid */}
      <div className="space-y-6">
        {data.recipes.map((recipe, idx) => {
          const base = recipe.baseServings || 2;
          const scaleFactor = servings / base;

          return (
            <RecipeCard
              key={recipe.id || idx}
              recipe={recipe}
              index={idx}
              servingsMultiplier={scaleFactor}
            />
          );
        })}
      </div>

      <div className="mt-12 text-center pb-12">
        <button
          onClick={onReset}
          className="px-8 py-3 rounded-full bg-slate-800 text-slate-300 hover:bg-slate-700 hover:text-white transition-all border border-slate-700 flex items-center gap-2 mx-auto shadow-lg shadow-slate-900/50"
        >
          <RotateCcw className="w-4 h-4" />
          Start Over (Clear History)
        </button>
      </div>
    </div>
  );
};

export default ResultsView;
