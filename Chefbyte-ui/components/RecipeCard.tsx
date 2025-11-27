
import React, { useState } from 'react';
import { Recipe } from '../types';
import { Clock, CheckCircle2, ChevronDown, ChevronUp, Gauge, Flame } from 'lucide-react';
import { RadialBarChart, RadialBar, ResponsiveContainer, Tooltip } from 'recharts';
import { scaleIngredientText } from '../utils';

interface RecipeCardProps {
  recipe: Recipe;
  index: number;
  servingsMultiplier: number;
}

const RecipeCard: React.FC<RecipeCardProps> = ({ recipe, index, servingsMultiplier }) => {
  const [expanded, setExpanded] = useState(false);

  // Scale nutrition
  const scaledCalories = Math.round(recipe.nutrition.calories * servingsMultiplier);
  const scaledCarbs = Math.round(parseInt(recipe.nutrition.carbs) * servingsMultiplier);
  const scaledProtein = Math.round(parseInt(recipe.nutrition.protein) * servingsMultiplier);
  const scaledFats = Math.round(parseInt(recipe.nutrition.fats) * servingsMultiplier);

  const nutritionData = [
    { name: 'Carbs', value: scaledCarbs, fill: '#60a5fa' },
    { name: 'Protein', value: scaledProtein, fill: '#34d399' },
    { name: 'Fats', value: scaledFats, fill: '#f472b6' },
  ];

  return (
    <div 
      className="glass-panel rounded-2xl overflow-hidden transition-all duration-500 hover:border-slate-600 group"
      style={{ animationDelay: `${index * 150}ms` }}
    >
      {/* Header */}
      <div 
        className="p-6 cursor-pointer bg-gradient-to-b from-slate-800/50 to-transparent"
        onClick={() => setExpanded(!expanded)}
      >
        <div className="flex justify-between items-start mb-3">
          <div className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full bg-orange-500/10 text-orange-400 text-xs font-bold border border-orange-500/20">
            <Gauge className="w-3 h-3" />
            {recipe.matchScore}% Match
          </div>
          <div className="text-slate-400">
            {expanded ? <ChevronUp className="w-5 h-5" /> : <ChevronDown className="w-5 h-5" />}
          </div>
        </div>
        
        <h3 className="text-xl md:text-2xl font-bold text-white mb-2 group-hover:text-orange-400 transition-colors">
          {recipe.title}
        </h3>
        <p className="text-slate-400 text-sm line-clamp-2">{recipe.description}</p>
        
        <div className="flex items-center gap-6 mt-4 text-sm font-medium text-slate-300">
          <div className="flex items-center gap-1.5">
            <Clock className="w-4 h-4 text-blue-400" />
            {recipe.time}
          </div>
          <div className="flex items-center gap-1.5">
            <Flame className="w-4 h-4 text-red-400" />
            <span className={servingsMultiplier !== 1 ? "text-orange-300 transition-colors" : ""}>
              {scaledCalories} kcal
            </span>
          </div>
          {servingsMultiplier !== 1 && (
            <div className="text-xs text-slate-500 font-normal">
              (Scaled {servingsMultiplier.toFixed(1)}x)
            </div>
          )}
        </div>
      </div>

      {/* Expanded Content */}
      {expanded && (
        <div className="border-t border-slate-800 animate-in fade-in slide-in-from-top-4 duration-300">
          <div className="grid md:grid-cols-3 gap-0">
            {/* Ingredients Column */}
            <div className="p-6 bg-slate-900/30 border-r border-slate-800/50">
              <h4 className="text-xs font-bold text-slate-500 uppercase tracking-wider mb-4">Ingredients</h4>
              <ul className="space-y-2">
                {recipe.ingredients.map((ing, i) => (
                  <li key={i} className="flex items-start gap-2 text-sm text-slate-300">
                    <CheckCircle2 className="w-4 h-4 text-emerald-500 shrink-0 mt-0.5" />
                    <span className={servingsMultiplier !== 1 ? "text-white transition-colors" : ""}>
                      {scaleIngredientText(ing, servingsMultiplier)}
                    </span>
                  </li>
                ))}
              </ul>
            </div>

            {/* Instructions Column */}
            <div className="p-6 md:col-span-2">
              <h4 className="text-xs font-bold text-slate-500 uppercase tracking-wider mb-4">Instructions</h4>
              <div className="space-y-6">
                {recipe.steps.map((step, i) => (
                  <div key={i} className="flex gap-4">
                    <div className="flex-shrink-0 w-6 h-6 rounded-full bg-slate-800 border border-slate-700 text-slate-400 text-xs flex items-center justify-center font-bold mt-0.5">
                      {i + 1}
                    </div>
                    <p className="text-slate-300 text-sm leading-relaxed">{step}</p>
                  </div>
                ))}
              </div>
              
              {/* Mini Chart */}
              <div className="mt-8 pt-6 border-t border-slate-800">
                <h4 className="text-xs font-bold text-slate-500 uppercase tracking-wider mb-4">Macros per Serving</h4>
                <div className="h-32 w-full flex items-center gap-8">
                   <div className="h-full aspect-square">
                    <ResponsiveContainer width="100%" height="100%">
                      <RadialBarChart innerRadius="40%" outerRadius="100%" data={nutritionData} startAngle={180} endAngle={0}>
                        <RadialBar background dataKey="value" cornerRadius={10} />
                        <Tooltip 
                          contentStyle={{ backgroundColor: '#1e293b', border: 'none', borderRadius: '8px', color: '#fff' }} 
                        />
                      </RadialBarChart>
                    </ResponsiveContainer>
                   </div>
                   <div className="space-y-2 text-sm">
                     <div className="flex items-center gap-2">
                       <div className="w-3 h-3 rounded-full bg-blue-400"></div>
                       <span className="text-slate-400">Carbs: <span className="text-white">{scaledCarbs}g</span></span>
                     </div>
                     <div className="flex items-center gap-2">
                       <div className="w-3 h-3 rounded-full bg-emerald-400"></div>
                       <span className="text-slate-400">Protein: <span className="text-white">{scaledProtein}g</span></span>
                     </div>
                     <div className="flex items-center gap-2">
                       <div className="w-3 h-3 rounded-full bg-pink-400"></div>
                       <span className="text-slate-400">Fats: <span className="text-white">{scaledFats}g</span></span>
                     </div>
                   </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default RecipeCard;
