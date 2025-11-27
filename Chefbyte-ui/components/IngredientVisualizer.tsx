
import React, { useState } from 'react';
import { Check, ShoppingCart, Info } from 'lucide-react';
import { getIngredientIcon } from '../utils';

interface IngredientVisualizerProps {
  ingredients: string[];
}

interface IngredientState {
  name: string;
  status: 'have' | 'need';
}

const IngredientVisualizer: React.FC<IngredientVisualizerProps> = ({ ingredients }) => {
  const [items, setItems] = useState<IngredientState[]>(
    ingredients.map(ing => ({ name: ing, status: 'have' }))
  );

  const toggleStatus = (index: number) => {
    const newItems = [...items];
    newItems[index].status = newItems[index].status === 'have' ? 'need' : 'have';
    setItems(newItems);
  };

  return (
    <div className="mb-8 animate-in fade-in slide-in-from-top-4 duration-500">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-slate-400 text-sm font-bold uppercase tracking-wider">Detected Inventory</h3>
        <div className="flex gap-3 text-xs">
          <div className="flex items-center gap-1.5 text-emerald-400">
            <div className="w-2 h-2 rounded-full bg-emerald-500"></div>
            In Stock
          </div>
          <div className="flex items-center gap-1.5 text-orange-400">
             <div className="w-2 h-2 rounded-full bg-orange-500"></div>
            To Buy
          </div>
        </div>
      </div>

      <div className="grid grid-cols-3 sm:grid-cols-4 md:grid-cols-6 gap-3">
        {items.map((item, idx) => {
          const Icon = getIngredientIcon(item.name);
          const isHave = item.status === 'have';

          return (
            <button
              key={idx}
              onClick={() => toggleStatus(idx)}
              className={`relative group flex flex-col items-center p-3 rounded-xl border transition-all duration-300 ${
                isHave 
                  ? 'bg-slate-800/50 border-slate-700 hover:border-emerald-500/50 hover:bg-emerald-900/10' 
                  : 'bg-orange-900/10 border-orange-500/30 hover:bg-orange-900/20'
              }`}
            >
              {/* Status Badge */}
              <div className={`absolute top-2 right-2 w-5 h-5 rounded-full flex items-center justify-center text-[10px] border ${
                isHave 
                  ? 'bg-emerald-500 text-emerald-950 border-emerald-400' 
                  : 'bg-orange-500 text-orange-950 border-orange-400'
              }`}>
                {isHave ? <Check className="w-3 h-3" /> : <ShoppingCart className="w-3 h-3" />}
              </div>

              {/* Icon */}
              <div className={`w-10 h-10 rounded-full flex items-center justify-center mb-2 transition-colors ${
                isHave ? 'bg-slate-700 text-slate-300' : 'bg-orange-500/20 text-orange-400'
              }`}>
                <Icon className="w-5 h-5" />
              </div>

              {/* Name */}
              <span className={`text-xs font-medium text-center leading-tight line-clamp-2 ${
                isHave ? 'text-slate-300' : 'text-orange-300'
              }`}>
                {item.name}
              </span>

              {/* Hover Tooltip Effect */}
              <div className="absolute inset-0 rounded-xl ring-2 ring-white/0 group-hover:ring-white/5 transition-all"></div>
            </button>
          );
        })}
      </div>
    </div>
  );
};

export default IngredientVisualizer;
