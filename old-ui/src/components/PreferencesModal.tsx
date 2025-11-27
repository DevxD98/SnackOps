import { X, Check } from 'lucide-react';
import { useState } from 'react';

interface PreferencesModalProps {
  preferences: {
    dietaryRestrictions: string[];
    budget: string;
    cookingTime: string;
  };
  onClose: () => void;
  onSave: (preferences: any) => void;
}

export function PreferencesModal({ preferences, onClose, onSave }: PreferencesModalProps) {
  const [localPreferences, setLocalPreferences] = useState(preferences);

  const dietaryOptions = ['Vegetarian', 'Vegan', 'Gluten-Free', 'Dairy-Free', 'Keto', 'Paleo'];
  const budgetOptions = ['low', 'medium', 'high'];
  const timeOptions = ['quick', 'medium', 'long'];

  const toggleDietaryRestriction = (option: string) => {
    const current = localPreferences.dietaryRestrictions;
    if (current.includes(option)) {
      setLocalPreferences({
        ...localPreferences,
        dietaryRestrictions: current.filter((item) => item !== option),
      });
    } else {
      setLocalPreferences({
        ...localPreferences,
        dietaryRestrictions: [...current, option],
      });
    }
  };

  const handleSave = () => {
    onSave(localPreferences);
    onClose();
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="rounded-2xl shadow-2xl max-w-lg w-full max-h-[90vh] overflow-y-auto" style={{ backgroundColor: '#FFFFFF' }}>
        <div className="sticky top-0 px-6 py-4 flex items-center justify-between" style={{ backgroundColor: '#628141' }}>
          <h3 className="text-xl font-bold" style={{ color: '#F7F4EC' }}>
            Meal Preferences
          </h3>
          <button
            onClick={onClose}
            className="p-1 rounded-lg transition-colors"
            style={{ color: '#F7F4EC' }}
            onMouseEnter={(e) => {
              e.currentTarget.style.backgroundColor = 'rgba(0,0,0,0.1)';
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.backgroundColor = 'transparent';
            }}
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        <div className="p-6 space-y-6">
          <div>
            <label className="block text-sm font-bold mb-3" style={{ color: '#5B532C' }}>
              Dietary Restrictions
            </label>
            <div className="grid grid-cols-2 gap-2">
              {dietaryOptions.map((option) => (
                <button
                  key={option}
                  onClick={() => toggleDietaryRestriction(option)}
                  className="flex items-center justify-between px-4 py-2.5 rounded-lg border-2 transition-all font-medium"
                  style={{
                    backgroundColor: localPreferences.dietaryRestrictions.includes(option) ? '#F0F8E8' : '#FFFFFF',
                    borderColor: localPreferences.dietaryRestrictions.includes(option) ? '#628141' : '#D4CEBD',
                    color: localPreferences.dietaryRestrictions.includes(option) ? '#628141' : '#5B532C',
                  }}
                >
                  <span className="text-sm">{option}</span>
                  {localPreferences.dietaryRestrictions.includes(option) && (
                    <Check className="w-4 h-4" />
                  )}
                </button>
              ))}
            </div>
          </div>

          <div>
            <label className="block text-sm font-bold mb-3" style={{ color: '#5B532C' }}>
              Budget Level
            </label>
            <div className="grid grid-cols-3 gap-2">
              {budgetOptions.map((option) => (
                <button
                  key={option}
                  onClick={() => setLocalPreferences({ ...localPreferences, budget: option })}
                  className="px-4 py-2.5 rounded-lg border-2 transition-all font-medium capitalize"
                  style={{
                    backgroundColor: localPreferences.budget === option ? '#FFFAF0' : '#FFFFFF',
                    borderColor: localPreferences.budget === option ? '#FFC50F' : '#D4CEBD',
                    color: localPreferences.budget === option ? '#8B6914' : '#5B532C',
                  }}
                >
                  {option}
                </button>
              ))}
            </div>
          </div>

          <div>
            <label className="block text-sm font-bold mb-3" style={{ color: '#5B532C' }}>
              Cooking Time
            </label>
            <div className="grid grid-cols-3 gap-2">
              {timeOptions.map((option) => (
                <button
                  key={option}
                  onClick={() => setLocalPreferences({ ...localPreferences, cookingTime: option })}
                  className="px-4 py-2.5 rounded-lg border-2 transition-all font-medium"
                  style={{
                    backgroundColor: localPreferences.cookingTime === option ? '#FFFAF0' : '#FFFFFF',
                    borderColor: localPreferences.cookingTime === option ? '#FFC50F' : '#D4CEBD',
                    color: localPreferences.cookingTime === option ? '#8B6914' : '#5B532C',
                  }}
                >
                  {option === 'quick' ? '< 20 min' : option === 'medium' ? '20-40 min' : '> 40 min'}
                </button>
              ))}
            </div>
          </div>
        </div>

        <div className="sticky bottom-0 px-6 py-4 flex gap-3" style={{ backgroundColor: '#FAFAF7', borderTopColor: '#D4CEBD', borderTopWidth: '1px' }}>
          <button
            onClick={onClose}
            className="flex-1 px-4 py-2.5 border-2 font-semibold rounded-lg transition-colors"
            style={{
              backgroundColor: '#FFFFFF',
              borderColor: '#D4CEBD',
              color: '#5B532C',
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.backgroundColor = '#F7F4EC';
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.backgroundColor = '#FFFFFF';
            }}
          >
            Cancel
          </button>
          <button
            onClick={handleSave}
            className="flex-1 px-4 py-2.5 font-semibold rounded-lg shadow-lg transition-all"
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
            Save Preferences
          </button>
        </div>
      </div>
    </div>
  );
}
