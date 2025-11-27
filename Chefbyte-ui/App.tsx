
import React, { useState, useEffect } from 'react';
import { AppState, UserPreferences, DietType, ChefResponse } from './types';
import Header from './components/Header';
import InputArea from './components/InputArea';
import PreferencesPanel from './components/PreferencesPanel';
import ProcessingView from './components/ProcessingView';
import ResultsView from './components/ResultsView';
import { generateMealPlan, generateAlternatives } from './services/apiService';
import { History } from 'lucide-react';

const App: React.FC = () => {
  const [appState, setAppState] = useState<AppState>('idle');
  const [preferences, setPreferences] = useState<UserPreferences>({
    diet: DietType.ANY,
    timeLimit: '45 minutes',
    calories: 600,
    servings: 2
  });

  // Persistent inventory history
  const [inventory, setInventory] = useState<string[]>([]);

  const [results, setResults] = useState<ChefResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isRegenerating, setIsRegenerating] = useState(false);

  // History management
  const [history, setHistory] = useState<ChefResponse[]>([]);
  const [showHistory, setShowHistory] = useState(false);

  // Load history from localStorage on mount
  useEffect(() => {
    const savedHistory = localStorage.getItem('chefbyte_history');
    if (savedHistory) {
      try {
        setHistory(JSON.parse(savedHistory));
      } catch (e) {
        console.error('Failed to load history:', e);
      }
    }
  }, []);

  // Save history to localStorage whenever it changes
  useEffect(() => {
    if (history.length > 0) {
      localStorage.setItem('chefbyte_history', JSON.stringify(history.slice(0, 20))); // Keep last 20
    }
  }, [history]);

  const handleAnalyze = async (mode: 'image' | 'text', data: string) => {
    setAppState('analyzing');
    setError(null);
    try {
      // Pass current inventory to the service
      const response = await generateMealPlan(mode, data, preferences, [], inventory);

      // Merge new ingredients with history, removing duplicates
      const newInventory = Array.from(new Set([...inventory, ...response.detectedIngredients]));
      setInventory(newInventory);

      // Update results with the merged inventory list so the UI shows everything
      const mergedResults = {
        ...response,
        detectedIngredients: newInventory
      };

      setResults(mergedResults);

      // Add to history
      setHistory(prev => [mergedResults, ...prev].slice(0, 20)); // Keep last 20

      // Simulate a small delay to let the animation finish
      setTimeout(() => {
        setAppState('results');
      }, 2000);
    } catch (err) {
      console.error(err);
      setError("ChefByte encountered an issue communicating with the kitchen. Please check your ingredients and try again.");
      setAppState('error');
    }
  };

  const handleGenerateAlternatives = async () => {
    if (!results) return;

    setIsRegenerating(true);
    const currentTitles = results.recipes.map(r => r.title);

    try {
      // We use the already merged list in results.detectedIngredients
      const newResponse = await generateAlternatives(
        results.detectedIngredients,
        preferences,
        currentTitles
      );

      // Preserve receipt data and original merged ingredients if new response misses them
      setResults(prev => prev ? {
        ...newResponse,
        detectedIngredients: prev.detectedIngredients, // Keep full history
        receiptData: prev.receiptData // Keep receipt data
      } : newResponse);

    } catch (err) {
      console.error("Failed to regenerate:", err);
    } finally {
      setIsRegenerating(false);
    }
  };

  // "Start Over" - clears everything
  const handleStartOver = () => {
    setAppState('idle');
    setResults(null);
    setError(null);
    setInventory([]);
  };

  // "Go Home" - returns to input but keeps inventory memory
  const handleGoHome = () => {
    setAppState('idle');
    setResults(null);
    setError(null);
    setShowHistory(false);
    // Inventory is preserved here
  };

  // Load a recipe from history
  const handleLoadHistory = (item: ChefResponse) => {
    setResults(item);
    setAppState('results');
    setShowHistory(false);
  };

  return (
    <div className="min-h-screen bg-[#0f172a] text-slate-200 overflow-x-hidden relative">

      {/* Background Ambient Effects */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none">
        <div className="absolute -top-24 -left-24 w-96 h-96 bg-orange-500/10 rounded-full blur-3xl animate-blob"></div>
        <div className="absolute top-1/4 right-0 w-80 h-80 bg-blue-500/10 rounded-full blur-3xl animate-blob animation-delay-2000"></div>
        <div className="absolute bottom-0 left-1/3 w-96 h-96 bg-purple-500/10 rounded-full blur-3xl animate-blob animation-delay-4000"></div>
        {/* Grid Pattern Overlay */}
        <div className="absolute inset-0 bg-[linear-gradient(rgba(255,255,255,0.02)_1px,transparent_1px),linear-gradient(90deg,rgba(255,255,255,0.02)_1px,transparent_1px)] bg-[size:4rem_4rem] [mask-image:radial-gradient(ellipse_60%_50%_at_50%_0%,#000_70%,transparent_100%)]"></div>
      </div>

      <div className="relative z-10 container mx-auto px-4 pb-20">
        <Header onGoHome={handleGoHome} />

        {/* History Sidebar */}
        {showHistory && (
          <>
            {/* Backdrop */}
            <div
              className="fixed inset-0 bg-black/50 backdrop-blur-sm z-30 animate-in fade-in"
              onClick={() => setShowHistory(false)}
            />

            {/* Sidebar Panel - Floating Card Style */}
            <div className="fixed left-4 top-24 bottom-auto max-h-[calc(100vh-8rem)] w-80 bg-slate-900/95 backdrop-blur-md border border-slate-700 rounded-2xl shadow-2xl z-40 animate-in slide-in-from-left duration-300 overflow-y-auto">
              <div className="p-6">
                <div className="flex items-center justify-between mb-6">
                  <h3 className="text-xl font-bold text-white flex items-center gap-2">
                    <History className="w-5 h-5 text-orange-400" />
                    Recipe History
                  </h3>
                  <button
                    onClick={() => setShowHistory(false)}
                    className="text-slate-400 hover:text-white transition-colors"
                  >
                    ✕
                  </button>
                </div>

                <div className="space-y-3">
                  {history.map((item, idx) => (
                    <button
                      key={idx}
                      onClick={() => handleLoadHistory(item)}
                      className="w-full text-left p-4 bg-slate-800/50 hover:bg-slate-800 border border-slate-700 rounded-lg transition-all group"
                    >
                      <div className="flex items-start justify-between mb-2">
                        <div className="text-sm font-medium text-white group-hover:text-orange-400 transition-colors">
                          {item.recipes.length} Recipes
                        </div>
                        <div className="text-xs text-slate-500">
                          {new Date().toLocaleDateString()}
                        </div>
                      </div>
                      <div className="text-xs text-slate-400">
                        {item.detectedIngredients.slice(0, 3).join(', ')}
                        {item.detectedIngredients.length > 3 && ` +${item.detectedIngredients.length - 3} more`}
                      </div>
                    </button>
                  ))}
                </div>
              </div>
            </div>
          </>
        )}

        <main className="mt-8">
          {appState === 'idle' && (
            <div className="animate-in fade-in zoom-in duration-500">
              <div className="text-center mb-10">
                <h2 className="text-4xl md:text-6xl font-bold text-white mb-4 tracking-tight">
                  Your Personal <span className="text-transparent bg-clip-text bg-gradient-to-r from-orange-400 to-red-500">AI Chef</span>
                </h2>
                <p className="text-slate-400 text-lg max-w-2xl mx-auto mb-2">
                  Upload a photo of your fridge, receipt, or paste your grocery list.
                  ChefByte will invent the perfect meal plan for you instantly.
                </p>
                {inventory.length > 0 && (
                  <div className="inline-flex items-center gap-2 px-4 py-1 rounded-full bg-emerald-900/30 border border-emerald-800 text-emerald-400 text-sm">
                    <span>🧠 {inventory.length} ingredients in memory</span>
                  </div>
                )}
              </div>

              {/* History Button */}
              {history.length > 0 && (
                <div className="fixed left-4 top-24 z-20">
                  <button
                    onClick={() => setShowHistory(!showHistory)}
                    className="px-4 py-3 bg-slate-800/90 backdrop-blur-sm hover:bg-slate-700 border border-slate-600 rounded-lg text-sm font-medium text-slate-300 flex items-center gap-2 transition-all shadow-lg"
                  >
                    <History className="w-4 h-4" />
                    History ({history.length})
                  </button>
                </div>
              )}

              <InputArea onAnalyze={handleAnalyze} isProcessing={false} />
              <PreferencesPanel prefs={preferences} setPrefs={setPreferences} />
            </div>
          )}

          {appState === 'analyzing' && (
            <ProcessingView />
          )}

          {appState === 'results' && results && (
            <ResultsView
              data={results}
              userPrefs={preferences}
              onReset={handleStartOver}
              onGenerateAlternatives={handleGenerateAlternatives}
              isRegenerating={isRegenerating}
              onBack={handleGoHome}
            />
          )}

          {appState === 'error' && (
            <div className="flex flex-col items-center justify-center py-20 animate-in fade-in">
              <div className="w-16 h-16 bg-red-500/10 rounded-full flex items-center justify-center mb-4 border border-red-500/20">
                <span className="text-3xl">⚠️</span>
              </div>
              <h3 className="text-xl font-bold text-white mb-2">System Error</h3>
              <p className="text-slate-400 mb-6 text-center max-w-md">{error}</p>
              <div className="flex gap-4">
                <button
                  onClick={handleGoHome}
                  className="px-6 py-2 bg-slate-800 hover:bg-slate-700 rounded-lg text-white transition-colors"
                >
                  Go Home
                </button>
              </div>
            </div>
          )}
        </main>
      </div>
    </div>
  );
};

export default App;
