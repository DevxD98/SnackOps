import { Clock, TrendingUp, Heart, BookOpen } from 'lucide-react';

interface Recipe {
  id: number;
  name: string;
  time: string;
  difficulty: string;
}

interface MealPlanResultsProps {
  mealPlan: {
    recipes: Recipe[];
  };
}

export function MealPlanResults({ mealPlan }: MealPlanResultsProps) {
  return (
    <div className="mt-8 space-y-6">
      <div className="flex items-center justify-between">
        <h3 className="text-2xl font-bold" style={{ color: '#5B532C' }}>
          Your Personalized Meal Plan
        </h3>
        <button
          className="flex items-center gap-2 px-4 py-2 rounded-lg transition-all font-medium"
          style={{
            backgroundColor: '#FFC50F',
            color: '#5B532C',
          }}
          onMouseEnter={(e) => {
            e.currentTarget.style.opacity = '0.9';
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.opacity = '1';
          }}
        >
          <Heart className="w-4 h-4" />
          Save Plan
        </button>
      </div>

      <div className="grid md:grid-cols-3 gap-6">
        {mealPlan.recipes.map((recipe, index) => (
          <div
            key={recipe.id}
            className="rounded-xl shadow-lg border-2 overflow-hidden transition-all hover:shadow-xl"
            style={{
              backgroundColor: '#FFFFFF',
              borderColor: '#D4CEBD',
            }}
          >
            <div className="h-48 relative" style={{ backgroundColor: '#E8DFC8' }}>
              <div className="absolute top-3 right-3 px-3 py-1 rounded-full text-xs font-bold shadow" style={{ backgroundColor: '#FFFFFF', color: '#628141' }}>
                Day {index + 1}
              </div>
            </div>

            <div className="p-5">
              <h4 className="text-lg font-bold mb-3" style={{ color: '#5B532C' }}>
                {recipe.name}
              </h4>

              <div className="flex items-center gap-4 mb-4 text-sm" style={{ color: '#8B8674' }}>
                <div className="flex items-center gap-1">
                  <Clock className="w-4 h-4" style={{ color: '#628141' }} />
                  <span>{recipe.time}</span>
                </div>
                <div className="flex items-center gap-1">
                  <TrendingUp className="w-4 h-4" style={{ color: '#FFC50F' }} />
                  <span>{recipe.difficulty}</span>
                </div>
              </div>

              <button
                className="w-full flex items-center justify-center gap-2 px-4 py-2 font-semibold rounded-lg transition-all"
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
                <BookOpen className="w-4 h-4" />
                View Recipe
              </button>
            </div>
          </div>
        ))}
      </div>

      <div className="border-2 rounded-xl p-6" style={{ backgroundColor: '#FAFAF7', borderColor: '#D4CEBD' }}>
        <h4 className="font-bold mb-2" style={{ color: '#5B532C' }}>
          Nutrition Summary
        </h4>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-4">
          <div className="rounded-lg p-3 border-2" style={{ backgroundColor: '#FFFFFF', borderColor: '#D4CEBD' }}>
            <p className="text-xs mb-1" style={{ color: '#8B8674' }}>
              Avg Calories
            </p>
            <p className="text-xl font-bold" style={{ color: '#628141' }}>
              520
            </p>
          </div>
          <div className="rounded-lg p-3 border-2" style={{ backgroundColor: '#FFFFFF', borderColor: '#D4CEBD' }}>
            <p className="text-xs mb-1" style={{ color: '#8B8674' }}>
              Protein
            </p>
            <p className="text-xl font-bold" style={{ color: '#628141' }}>
              32g
            </p>
          </div>
          <div className="rounded-lg p-3 border-2" style={{ backgroundColor: '#FFFFFF', borderColor: '#D4CEBD' }}>
            <p className="text-xs mb-1" style={{ color: '#8B8674' }}>
              Total Cost
            </p>
            <p className="text-xl font-bold" style={{ color: '#FFC50F' }}>
              $24
            </p>
          </div>
          <div className="rounded-lg p-3 border-2" style={{ backgroundColor: '#FFFFFF', borderColor: '#D4CEBD' }}>
            <p className="text-xs mb-1" style={{ color: '#8B8674' }}>
              Match Score
            </p>
            <p className="text-xl font-bold" style={{ color: '#628141' }}>
              94%
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
