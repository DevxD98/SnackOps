import React, { useState, useRef } from 'react';
import { Upload, Image as ImageIcon, Loader2, AlertCircle } from 'lucide-react';
import { useVision } from '../hooks/useVision';

export const FridgePage: React.FC = () => {
    const { isAnalyzing, result, error, analyzeImage } = useVision();
    const [preview, setPreview] = useState<string | null>(null);
    const fileInputRef = useRef<HTMLInputElement>(null);

    const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
        const file = e.target.files?.[0];
        if (file) {
            handleFile(file);
        }
    };

    const handleFile = (file: File) => {
        // Create preview
        const reader = new FileReader();
        reader.onloadend = () => {
            setPreview(reader.result as string);
        };
        reader.readAsDataURL(file);

        // Analyze
        analyzeImage(file);
    };

    const handleDrop = (e: React.DragEvent) => {
        e.preventDefault();
        const file = e.dataTransfer.files?.[0];
        if (file && file.type.startsWith('image/')) {
            handleFile(file);
        }
    };

    return (
        <div className="space-y-8">
            <div className="flex items-center justify-between">
                <div>
                    <h2 className="text-2xl font-bold text-gray-800">Fridge Scanner</h2>
                    <p className="text-gray-500 mt-1">Upload a photo of your fridge or ingredients</p>
                </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                {/* Upload Area */}
                <div
                    className={`border-2 border-dashed rounded-2xl p-8 text-center transition-colors ${isAnalyzing ? 'border-orange-300 bg-orange-50' : 'border-gray-200 hover:border-orange-400 hover:bg-gray-50'
                        }`}
                    onDragOver={(e) => e.preventDefault()}
                    onDrop={handleDrop}
                >
                    <input
                        type="file"
                        ref={fileInputRef}
                        onChange={handleFileSelect}
                        accept="image/*"
                        className="hidden"
                    />

                    {preview ? (
                        <div className="relative rounded-xl overflow-hidden shadow-md">
                            <img src={preview} alt="Preview" className="w-full h-64 object-cover" />
                            <button
                                onClick={() => {
                                    setPreview(null);
                                    if (fileInputRef.current) fileInputRef.current.value = '';
                                }}
                                className="absolute top-2 right-2 bg-white/90 p-2 rounded-full hover:bg-white text-gray-700"
                            >
                                <Upload className="w-4 h-4" />
                            </button>
                        </div>
                    ) : (
                        <div
                            className="flex flex-col items-center justify-center h-64 cursor-pointer"
                            onClick={() => fileInputRef.current?.click()}
                        >
                            <div className="w-16 h-16 bg-orange-100 text-orange-500 rounded-full flex items-center justify-center mb-4">
                                <ImageIcon className="w-8 h-8" />
                            </div>
                            <h3 className="text-lg font-semibold text-gray-800 mb-2">Click to upload</h3>
                            <p className="text-gray-500 text-sm max-w-xs">
                                or drag and drop your image here. Supports JPG, PNG, WEBP.
                            </p>
                        </div>
                    )}
                </div>

                {/* Results Area */}
                <div className="bg-white rounded-2xl border border-gray-100 p-6 shadow-sm h-full min-h-[300px]">
                    <h3 className="text-lg font-semibold text-gray-800 mb-4">Analysis Results</h3>

                    {isAnalyzing ? (
                        <div className="flex flex-col items-center justify-center h-48 text-gray-500">
                            <Loader2 className="w-8 h-8 animate-spin text-orange-500 mb-3" />
                            <p>Analyzing ingredients...</p>
                        </div>
                    ) : error ? (
                        <div className="flex flex-col items-center justify-center h-48 text-red-500">
                            <AlertCircle className="w-8 h-8 mb-3" />
                            <p className="text-center">{error}</p>
                        </div>
                    ) : result ? (
                        <div className="prose prose-orange max-w-none">
                            <div className="whitespace-pre-wrap text-gray-700">{result}</div>
                        </div>
                    ) : (
                        <div className="flex flex-col items-center justify-center h-48 text-gray-400">
                            <p>Upload an image to see detected ingredients</p>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
};
