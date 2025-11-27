import React, { useState } from 'react';
import { Calendar, ChefHat, Loader2, AlertCircle, Plus, X } from 'lucide-react';
import { usePlanner } from '../hooks/usePlanner';

export const PlannerPage: React.FC = () => {
    const { isLoading, result, error, generateMealPlan } = usePlanner();

    const [ingredients, setIngredients] = useState<string[]>([]);
    const [currentIngredient, setCurrentIngredient] = useState('');
    const [calories, setCalories] = useState<string>('2000');
    const [meals, setMeals] = useState<number>(3);
    const [dietary, setDietary] = useState<string[]>([]);

    const dietaryOptions = ['Vegetarian', 'Vegan', 'Gluten-Free', 'Keto', 'Paleo', 'Halal'];

    const addIngredient = (e: React.FormEvent) => {
        e.preventDefault();
        if (currentIngredient.trim()) {
            setIngredients([...ingredients, currentIngredient.trim()]);
            setCurrentIngredient('');
        }
    };

    const removeIngredient = (index: number) => {
        setIngredients(ingredients.filter((_, i) => i !== index));
    };

    const toggleDietary = (option: string) => {
        if (dietary.includes(option)) {
            setDietary(dietary.filter(d => d !== option));
        } else {
            setDietary([...dietary, option]);
        }
    };

    const handleSubmit = () => {
        if (ingredients.length === 0) return;

        generateMealPlan({
            ingredients,
            dietary_constraints: dietary,
            calorie_target: calories ? parseInt(calories) : null,
            meal_count: meals,
        });
    };

    return (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            {/* Configuration Panel */}
            <div className="lg:col-span-1 space-y-6">
                <div className="bg-white rounded-2xl p-6 shadow-sm border border-gray-100 space-y-6">
                    <div>
                        <h3 className="text-lg font-semibold text-gray-800 mb-4 flex items-center gap-2">
                            <ChefHat className="w-5 h-5 text-orange-500" />
                            Ingredients
                        </h3>
                        <form onSubmit={addIngredient} className="flex gap-2 mb-3">
                            <input
                                type="text"
                                value={currentIngredient}
                                onChange={(e) => setCurrentIngredient(e.target.value)}
                                placeholder="Add ingredient..."
                                className="flex-1 p-2 rounded-lg border border-gray-200 focus:outline-none focus:ring-2 focus:ring-orange-500"
                            />
                            <button
                                type="submit"
                                className="p-2 bg-orange-100 text-orange-600 rounded-lg hover:bg-orange-200"
                            >
                                <Plus className="w-5 h-5" />
                            </button>
                        </form>
                        <div className="flex flex-wrap gap-2">
                            {ingredients.map((ing, i) => (
                                <span key={i} className="bg-gray-100 text-gray-700 px-3 py-1 rounded-full text-sm flex items-center gap-1">
                                    {ing}
                                    <button onClick={() => removeIngredient(i)} className="hover:text-red-500">
                                        <X className="w-3 h-3" />
                                    </button>
                                </span>
                            ))}
                            {ingredients.length === 0 && (
                                <p className="text-sm text-gray-400 italic">No ingredients added yet</p>
                            )}
                        </div>
                    </div>

                    <div className="border-t border-gray-100 pt-6">
                        <h3 className="text-lg font-semibold text-gray-800 mb-4">Preferences</h3>

                        <div className="space-y-4">
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">Daily Calories</label>
                                <input
                                    type="number"
                                    value={calories}
                                    onChange={(e) => setCalories(e.target.value)}
                                    className="w-full p-2 rounded-lg border border-gray-200 focus:outline-none focus:ring-2 focus:ring-orange-500"
                                />
                            </div>

                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">Meals per Day: {meals}</label>
                                <input
                                    type="range"
                                    min="1"
                                    max="5"
                                    value={meals}
                                    onChange={(e) => setMeals(parseInt(e.target.value))}
                                    className="w-full accent-orange-500"
                                />
                                <div className="flex justify-between text-xs text-gray-400">
                                    <span>1</span>
                                    <span>5</span>
                                </div>
                            </div>

                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-2">Dietary</label>
                                <div className="flex flex-wrap gap-2">
                                    {dietaryOptions.map((option) => (
                                        <button
                                            key={option}
                                            onClick={() => toggleDietary(option)}
                                            className={`px-3 py-1 rounded-lg text-sm border transition-colors ${dietary.includes(option)
                                                    ? 'bg-orange-500 text-white border-orange-500'
                                                    : 'bg-white text-gray-600 border-gray-200 hover:border-orange-300'
                                                }`}
                                        >
                                            {option}
                                        </button>
                                    ))}
                                </div>
                            </div>
                        </div>
                    </div>

                    <button
                        onClick={handleSubmit}
                        disabled={isLoading || ingredients.length === 0}
                        className="w-full py-3 bg-orange-500 text-white rounded-xl font-semibold hover:bg-orange-600 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center justify-center gap-2"
                    >
                        {isLoading ? <Loader2 className="w-5 h-5 animate-spin" /> : <Calendar className="w-5 h-5" />}
                        Generate Plan
                    </button>
                </div>
            </div>

            {/* Results Panel */}
            <div className="lg:col-span-2">
                <div className="bg-white rounded-2xl border border-gray-100 p-8 shadow-sm min-h-[600px]">
                    <h2 className="text-2xl font-bold text-gray-800 mb-6">Your Meal Plan</h2>

                    {isLoading ? (
                        <div className="flex flex-col items-center justify-center h-96 text-gray-500">
                            <Loader2 className="w-12 h-12 animate-spin text-orange-500 mb-4" />
                            <p className="text-lg">ChefByte is crafting your menu...</p>
                        </div>
                    ) : error ? (
                        <div className="flex flex-col items-center justify-center h-96 text-red-500">
                            <AlertCircle className="w-12 h-12 mb-4" />
                            <p className="text-lg">{error}</p>
                        </div>
                    ) : result ? (
                        <div className="prose prose-orange max-w-none">
                            <div className="whitespace-pre-wrap text-gray-700">{result}</div>
                        </div>
                    ) : (
                        <div className="flex flex-col items-center justify-center h-96 text-gray-400">
                            <ChefHat className="w-16 h-16 mb-4 opacity-20" />
                            <p className="text-lg">Add ingredients and preferences to generate a plan</p>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
};
