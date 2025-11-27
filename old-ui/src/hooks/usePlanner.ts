import { useState } from 'react';

interface MealPlanRequest {
    ingredients: string[];
    dietary_constraints: string[];
    calorie_target: number | null;
    meal_count: number;
}

export const usePlanner = () => {
    const [isLoading, setIsLoading] = useState(false);
    const [result, setResult] = useState<string | null>(null);
    const [error, setError] = useState<string | null>(null);

    const generateMealPlan = async (request: MealPlanRequest) => {
        setIsLoading(true);
        setError(null);
        setResult(null);

        try {
            const response = await fetch('http://localhost:8000/plan-meals', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(request),
            });

            if (!response.ok) {
                throw new Error('Failed to generate meal plan');
            }

            const data = await response.json();
            setResult(data.response);
        } catch (err) {
            console.error('Error generating meal plan:', err);
            setError('Failed to generate meal plan. Please check if the backend is running.');
        } finally {
            setIsLoading(false);
        }
    };

    return {
        isLoading,
        result,
        error,
        generateMealPlan,
    };
};
