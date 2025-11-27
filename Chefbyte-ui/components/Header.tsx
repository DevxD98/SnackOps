
import React from 'react';
import { Bot, ChefHat } from 'lucide-react';

interface HeaderProps {
  onGoHome?: () => void;
}

const Header: React.FC<HeaderProps> = ({ onGoHome }) => {
  return (
    <header className="w-full py-6 px-4 md:px-8 flex items-center justify-between relative z-10">
      <div 
        onClick={onGoHome} 
        className={`flex items-center gap-3 group ${onGoHome ? 'cursor-pointer' : 'cursor-default'}`}
        title="Go to Home"
      >
        <div className="relative">
          <div className="absolute -inset-1 bg-gradient-to-r from-orange-500 to-red-600 rounded-full blur opacity-40 group-hover:opacity-75 transition duration-500"></div>
          <div className="relative bg-slate-900 p-2 rounded-full border border-slate-700">
            <ChefHat className="w-8 h-8 text-orange-500 transition-transform group-hover:scale-110 duration-300" />
          </div>
        </div>
        <div>
          <h1 className="text-2xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-white to-slate-400 tracking-tight">
            ChefByte
          </h1>
          <div className="flex items-center gap-1">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse"></span>
            <p className="text-xs text-emerald-500 font-medium tracking-wide uppercase">System Online</p>
          </div>
        </div>
      </div>
      
      <div className="hidden md:flex items-center gap-4">
        <div className="flex items-center gap-2 px-4 py-1.5 rounded-full bg-slate-800/50 border border-slate-700 text-slate-400 text-sm">
          <Bot className="w-4 h-4" />
          <span>AI Agent v2.5</span>
        </div>
      </div>
    </header>
  );
};

export default Header;
