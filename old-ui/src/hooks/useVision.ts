import { useState } from 'react';

export const useVision = () => {
    const [isAnalyzing, setIsAnalyzing] = useState(false);
    const [result, setResult] = useState<string | null>(null);
    const [error, setError] = useState<string | null>(null);

    const analyzeImage = async (file: File) => {
        setIsAnalyzing(true);
        setError(null);
        setResult(null);

        const formData = new FormData();
        formData.append('file', file);

        try {
            const response = await fetch('http://localhost:8000/analyze-image', {
                method: 'POST',
                body: formData,
            });

            if (!response.ok) {
                throw new Error('Failed to analyze image');
            }

            const data = await response.json();
            setResult(data.response);
        } catch (err) {
            console.error('Error analyzing image:', err);
            setError('Failed to analyze image. Please check if the backend is running.');
        } finally {
            setIsAnalyzing(false);
        }
    };

    return {
        isAnalyzing,
        result,
        error,
        analyzeImage,
    };
};
