import { useState } from 'react';
import { Header } from './components/Header';
import { InputSection } from './components/InputSection';
import { MealPlanResults } from './components/MealPlanResults';
import { PreferencesModal } from './components/PreferencesModal';

function App() {
  const [showPreferences, setShowPreferences] = useState(false);
  const [preferences, setPreferences] = useState({
    dietaryRestrictions: [] as string[],
    budget: 'medium',
    cookingTime: 'medium',
  });
  const [mealPlan, setMealPlan] = useState(null);

  return (
    <div className="min-h-screen" style={{ backgroundColor: '#F7F4EC' }}>
      <Header onOpenPreferences={() => setShowPreferences(true)} />

      <main className="container mx-auto px-4 py-8 max-w-6xl">
        <InputSection
          preferences={preferences}
          onGenerateMealPlan={setMealPlan}
        />

        {mealPlan && <MealPlanResults mealPlan={mealPlan} />}
      </main>

      {showPreferences && (
        <PreferencesModal
          preferences={preferences}
          onClose={() => setShowPreferences(false)}
          onSave={setPreferences}
        />
      )}
    </div>
  );
}

export default App;
