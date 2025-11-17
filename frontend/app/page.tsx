'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';

// API configuration from environment
const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE || 'http://localhost:8000';
const API_KEY = process.env.NEXT_PUBLIC_API_KEY;

// Input validation constants
const MAX_PROMPT_LENGTH = 2000;

export default function HomePage() {
  const [prompt, setPrompt] = useState('');
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const router = useRouter();

  const validatePrompt = (text: string): string | null => {
    if (!text.trim()) {
      return 'Prompt cannot be empty';
    }
    if (text.length > MAX_PROMPT_LENGTH) {
      return `Prompt exceeds maximum length of ${MAX_PROMPT_LENGTH} characters`;
    }
    return null;
  };

  const handleAnalyze = async () => {
    // Clear previous error
    setError(null);

    // Validate input
    const validationError = validatePrompt(prompt);
    if (validationError) {
      setError(validationError);
      return;
    }

    setIsAnalyzing(true);

    try {
      // Build headers
      const headers: HeadersInit = {
        'Content-Type': 'application/json',
      };

      // Add API key if configured
      if (API_KEY) {
        headers['X-API-Key'] = API_KEY;
      }

      // Call the analytics API
      const response = await fetch(`${API_BASE_URL}/api/analytics/analyze`, {
        method: 'POST',
        headers,
        body: JSON.stringify({ prompt: prompt.trim() }),
      });
      
      if (response.ok) {
        const results = await response.json();

        // Validate response data before storing
        if (!results || typeof results !== 'object') {
          throw new Error('Invalid response from server');
        }

        // Store results in sessionStorage (more secure than localStorage)
        // Use sessionStorage to auto-clear on tab close
        sessionStorage.setItem('analysisResults', JSON.stringify(results));

        // Redirect to analysis page
        router.push('/analysis');
      } else if (response.status === 429) {
        setError('Rate limit exceeded. Please wait a moment and try again.');
      } else if (response.status === 401) {
        setError('Authentication failed. Please check your API key configuration.');
      } else {
        const errorData = await response.json().catch(() => ({}));
        setError(errorData.detail || 'Analysis failed. Please try again.');
      }
    } catch (error) {
      console.error('Analysis failed:', error);
      setError('Unable to connect to the server. Please check your connection and try again.');
    } finally {
      setIsAnalyzing(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto">
      {/* Hero Section */}
      <div className="text-center mb-12">
        <h1 className="text-4xl font-bold text-gray-900 mb-4">
          AI-Powered Brand Intelligence
        </h1>
        <p className="text-xl text-gray-600">
          Analyze prompts and get instant insights about brand sentiment, mentions, competitors, and trust scores.
        </p>
      </div>

      {/* Input Section */}
      <div className="bg-white rounded-2xl shadow-lg p-8 mb-8">
        <div className="max-w-3xl mx-auto">
          <h2 className="text-2xl font-semibold text-gray-900 mb-6 text-center">
            What would you like to analyze?
          </h2>
          
          <div className="space-y-4">
            {error && (
              <div className="p-4 bg-red-50 border border-red-200 rounded-xl text-red-700">
                {error}
              </div>
            )}

            <div className="relative">
              <textarea
                value={prompt}
                onChange={(e) => {
                  setPrompt(e.target.value);
                  setError(null); // Clear error on input change
                }}
                placeholder="Enter your prompt here... For example: 'Analyze customer sentiment about our new product launch'"
                className="w-full h-32 p-4 border border-gray-300 rounded-xl resize-none focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent text-gray-900 placeholder-gray-500"
                disabled={isAnalyzing}
                maxLength={MAX_PROMPT_LENGTH}
              />
              <div className="absolute bottom-2 right-2 text-sm text-gray-400">
                {prompt.length}/{MAX_PROMPT_LENGTH}
              </div>
            </div>
            
            <div className="flex justify-center">
              <button
                onClick={handleAnalyze}
                disabled={!prompt.trim() || isAnalyzing}
                className="px-8 py-3 bg-blue-600 text-white font-semibold rounded-xl hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center space-x-2"
              >
                {isAnalyzing ? (
                  <>
                    <svg className="animate-spin h-5 w-5" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    <span>Analyzing...</span>
                  </>
                ) : (
                  <>
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                    </svg>
                    <span>Analyze</span>
                  </>
                )}
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Preview of Analysis Tiles */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
        <div className="bg-white rounded-xl shadow-md p-6 border-l-4 border-green-500">
          <h3 className="text-lg font-semibold text-gray-900 mb-2">Sentiment Analysis</h3>
          <p className="text-gray-600">Positive, neutral, or negative tone about the brand</p>
        </div>
        
        <div className="bg-white rounded-xl shadow-md p-6 border-l-4 border-blue-500">
          <h3 className="text-lg font-semibold text-gray-900 mb-2">Brand Mention Tracking</h3>
          <p className="text-gray-600">How often is the brand mentioned? In what contexts?</p>
        </div>
        
        <div className="bg-white rounded-xl shadow-md p-6 border-l-4 border-purple-500">
          <h3 className="text-lg font-semibold text-gray-900 mb-2">Website Coverage</h3>
          <p className="text-gray-600">How many unique websites mention the brand out of 50 crawled</p>
        </div>
        
        <div className="bg-white rounded-xl shadow-md p-6 border-l-4 border-orange-500">
          <h3 className="text-lg font-semibold text-gray-900 mb-2">Trust/Authority Score</h3>
          <p className="text-gray-600">How often AI recommends the brand vs others</p>
        </div>
      </div>
    </div>
  );
}
