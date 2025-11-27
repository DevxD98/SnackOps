import { useState } from 'react';
import { Camera, List, Upload, Sparkles } from 'lucide-react';

interface InputSectionProps {
  preferences: {
    dietaryRestrictions: string[];
    budget: string;
    cookingTime: string;
  };
  onGenerateMealPlan: (plan: any) => void;
}

export function InputSection({ preferences, onGenerateMealPlan }: InputSectionProps) {
  const [activeTab, setActiveTab] = useState<'text' | 'photo' | 'receipt'>('text');
  const [ingredients, setIngredients] = useState('');
  const [isGenerating, setIsGenerating] = useState(false);

  const handleGenerate = async () => {
    setIsGenerating(true);
    setTimeout(() => {
      onGenerateMealPlan({
        recipes: [
          { id: 1, name: 'Mediterranean Pasta', time: '25 min', difficulty: 'Easy' },
          { id: 2, name: 'Garlic Herb Chicken', time: '35 min', difficulty: 'Medium' },
          { id: 3, name: 'Quick Veggie Stir-fry', time: '15 min', difficulty: 'Easy' },
        ],
      });
      setIsGenerating(false);
    }, 1500);
  };

  return (
    <div className="rounded-2xl shadow-xl border-2 overflow-hidden" style={{ backgroundColor: '#FFFFFF', borderColor: '#D4CEBD' }}>
      <div className="px-6 py-5" style={{ backgroundColor: '#628141' }}>
        <h2 className="text-xl font-bold mb-2" style={{ color: '#F7F4EC' }}>
          What's in your kitchen?
        </h2>
        <p className="text-sm" style={{ color: '#E8DFC8' }}>
          Share your ingredients and let AI create perfect meals
        </p>
      </div>

      <div className="p-6">
        <div className="flex gap-2 mb-6" style={{ borderBottomColor: '#E8DFC8', borderBottomWidth: '1px' }}>
          <button
            onClick={() => setActiveTab('text')}
            className="flex items-center gap-2 px-4 py-3 font-medium transition-all"
            style={{
              color: activeTab === 'text' ? '#628141' : '#8B8674',
              borderBottomWidth: activeTab === 'text' ? '2px' : '0px',
              borderBottomColor: '#628141',
            }}
          >
            <List className="w-4 h-4" />
            Type Ingredients
          </button>
          <button
            onClick={() => setActiveTab('photo')}
            className="flex items-center gap-2 px-4 py-3 font-medium transition-all"
            style={{
              color: activeTab === 'photo' ? '#628141' : '#8B8674',
              borderBottomWidth: activeTab === 'photo' ? '2px' : '0px',
              borderBottomColor: '#628141',
            }}
          >
            <Camera className="w-4 h-4" />
            Fridge Photo
          </button>
          <button
            onClick={() => setActiveTab('receipt')}
            className="flex items-center gap-2 px-4 py-3 font-medium transition-all"
            style={{
              color: activeTab === 'receipt' ? '#628141' : '#8B8674',
              borderBottomWidth: activeTab === 'receipt' ? '2px' : '0px',
              borderBottomColor: '#628141',
            }}
          >
            <Upload className="w-4 h-4" />
            Upload Receipt
          </button>
        </div>

        {activeTab === 'text' && (
          <div className="space-y-4">
            <textarea
              value={ingredients}
              onChange={(e) => setIngredients(e.target.value)}
              placeholder="e.g., tomatoes, basil, garlic, olive oil, pasta, chicken breast..."
              className="w-full h-32 px-4 py-3 border-2 rounded-lg outline-none resize-none transition-all"
              style={{
                borderColor: '#D4CEBD',
                color: '#5B532C',
              }}
              onFocus={(e) => {
                e.currentTarget.style.borderColor = '#FFC50F';
                e.currentTarget.style.boxShadow = '0 0 0 2px rgba(255, 197, 15, 0.1)';
              }}
              onBlur={(e) => {
                e.currentTarget.style.borderColor = '#D4CEBD';
                e.currentTarget.style.boxShadow = 'none';
              }}
            />
          </div>
        )}

        {activeTab === 'photo' && (
          <div className="border-2 border-dashed rounded-lg p-8 text-center cursor-pointer" style={{ borderColor: '#D4CEBD', backgroundColor: '#FAFAF7' }}>
            <Camera className="w-12 h-12 mx-auto mb-3" style={{ color: '#A89A88' }} />
            <p className="font-medium mb-1" style={{ color: '#5B532C' }}>
              Take or upload a photo of your fridge
            </p>
            <p className="text-sm" style={{ color: '#8B8674' }}>
              AI will identify your ingredients automatically
            </p>
          </div>
        )}

        {activeTab === 'receipt' && (
          <div className="border-2 border-dashed rounded-lg p-8 text-center cursor-pointer" style={{ borderColor: '#D4CEBD', backgroundColor: '#FAFAF7' }}>
            <Upload className="w-12 h-12 mx-auto mb-3" style={{ color: '#A89A88' }} />
            <p className="font-medium mb-1" style={{ color: '#5B532C' }}>
              Upload your grocery receipt
            </p>
            <p className="text-sm" style={{ color: '#8B8674' }}>
              We'll extract your purchased items
            </p>
          </div>
        )}

        <div className="mt-6 flex items-center justify-between pt-4" style={{ borderTopColor: '#E8DFC8', borderTopWidth: '1px' }}>
          <div className="text-sm" style={{ color: '#8B8674' }}>
            <span className="font-medium" style={{ color: '#5B532C' }}>
              Budget:
            </span>{' '}
            {preferences.budget} •
            <span className="font-medium ml-2" style={{ color: '#5B532C' }}>
              Time:
            </span>{' '}
            {preferences.cookingTime}
            {preferences.dietaryRestrictions.length > 0 && (
              <>
                {' • '}
                <span className="font-medium" style={{ color: '#5B532C' }}>
                  Diet:
                </span>{' '}
                {preferences.dietaryRestrictions.join(', ')}
              </>
            )}
          </div>

          <button
            onClick={handleGenerate}
            disabled={isGenerating}
            className="flex items-center gap-2 px-6 py-3 font-semibold rounded-lg shadow-lg transition-all disabled:opacity-50 disabled:cursor-not-allowed"
            style={{
              backgroundColor: '#628141',
              color: '#F7F4EC',
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.backgroundColor = '#526238';
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.backgroundColor = '#628141';
            }}
          >
            {isGenerating ? (
              <>
                <div className="w-4 h-4 border-2 rounded-full animate-spin" style={{ borderColor: '#F7F4EC', borderTopColor: 'transparent' }} />
                Generating...
              </>
            ) : (
              <>
                <Sparkles className="w-4 h-4" />
                Generate Meal Plan
              </>
            )}
          </button>
        </div>
      </div>
    </div>
  );
}
