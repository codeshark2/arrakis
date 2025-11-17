'use client';

import { useState, useEffect } from 'react';

interface AnalysisResult {
  sentiment: {
    tone: 'positive' | 'neutral' | 'negative';
    score: number;
    summary: string;
  };
  brand_mentions: {
    count: number;
    contexts: string[];
    summary: string;
  };
  website_coverage: {
    total_websites_crawled: number;
    unique_websites_found: number;
    coverage_percentage: number;
    coverage_quality: string;
    summary: string;
  };
  trust_score: {
    ai_recommendations: number;
    vs_others: number;
    summary: string;
  };
}

export default function AnalysisPage() {
  const [analysisResult, setAnalysisResult] = useState<AnalysisResult | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    // Get analysis results from sessionStorage (more secure)
    const storedResults = sessionStorage.getItem('analysisResults');

    if (storedResults) {
      try {
        const results = JSON.parse(storedResults);

        // Validate the parsed data structure
        if (!results || typeof results !== 'object') {
          throw new Error('Invalid data structure');
        }

        setAnalysisResult(results);
        setLoading(false);

        // Clear the stored data after loading (one-time use)
        // sessionStorage.removeItem('analysisResults');
      } catch (e) {
        setError('Failed to parse analysis results. Data may be corrupted.');
        setLoading(false);
      }
    } else {
      setError('No analysis results found. Please run an analysis first.');
      setLoading(false);
    }
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <svg className="animate-spin h-12 w-12 text-blue-600 mx-auto mb-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          <p className="text-gray-600">Loading analysis results...</p>
        </div>
      </div>
    );
  }

  if (error || !analysisResult) {
    return (
      <div className="max-w-6xl mx-auto">
        <div className="bg-red-50 border border-red-200 rounded-xl p-6 text-center">
          <svg className="w-12 h-12 text-red-600 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <h3 className="text-lg font-semibold text-red-800 mb-2">Analysis Error</h3>
          <p className="text-red-700 mb-4">{error || 'No analysis results available'}</p>
          <a
            href="/"
            className="inline-flex items-center px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
          >
            <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
            </svg>
            Back to Analysis
          </a>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto">
      {/* Page Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Analysis Results</h1>
        <p className="text-gray-600">Comprehensive insights from your prompt analysis</p>
      </div>

      {/* Main Analysis Tiles - 2x2 Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
        {/* Sentiment Analysis */}
        <div className="bg-white rounded-xl shadow-lg p-6 border-l-4 border-green-500">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-xl font-semibold text-gray-900">Sentiment Analysis</h3>
            <div className={`px-3 py-1 rounded-full text-sm font-medium ${
              analysisResult.sentiment.tone === 'positive' ? 'bg-green-100 text-green-800' :
              analysisResult.sentiment.tone === 'neutral' ? 'bg-yellow-100 text-yellow-800' :
              'bg-red-100 text-red-800'
            }`}>
              {analysisResult.sentiment.tone.charAt(0).toUpperCase() + analysisResult.sentiment.tone.slice(1)}
            </div>
          </div>
          <p className="text-gray-700">{analysisResult.sentiment.summary}</p>
        </div>

        {/* Brand Mention Tracking */}
        <div className="bg-white rounded-xl shadow-lg p-6 border-l-4 border-blue-500">
          <h3 className="text-xl font-semibold text-gray-900 mb-4">Brand Mention Tracking</h3>
          <div className="mb-4">
            <div className="text-3xl font-bold text-blue-600 mb-2">{analysisResult.brand_mentions.count}</div>
            <p className="text-sm text-gray-600">Total Mentions</p>
          </div>
          <div className="mb-4">
            <h4 className="text-sm font-medium text-gray-700 mb-2">Contexts:</h4>
            <div className="flex flex-wrap gap-2">
              {analysisResult.brand_mentions.contexts.map((context, index) => (
                <span key={index} className="px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded-full">
                  {context}
                </span>
              ))}
            </div>
          </div>
          <p className="text-gray-700">{analysisResult.brand_mentions.summary}</p>
        </div>

        {/* Website Coverage */}
        <div className="bg-white rounded-xl shadow-lg p-6 border-l-4 border-purple-500">
          <h3 className="text-xl font-semibold text-gray-900 mb-4">Website Coverage</h3>
          <div className="mb-4">
            <div className="text-3xl font-bold text-purple-600 mb-2">
              {analysisResult.website_coverage.coverage_percentage}
            </div>
            <p className="text-sm text-gray-600">Coverage Level</p>
          </div>
          <div className="mb-4">
            <h4 className="text-sm font-medium text-gray-700 mb-2">Coverage Details:</h4>
            <div className="grid grid-cols-2 gap-2 text-xs text-gray-600">
              <span>Total Websites: {analysisResult.website_coverage.total_websites_crawled}</span>
              <span>Unique Domains: {analysisResult.website_coverage.unique_websites_found}</span>
              <span>Quality: {analysisResult.website_coverage.coverage_quality}</span>
            </div>
          </div>
          <p className="text-gray-700">{analysisResult.website_coverage.summary}</p>
        </div>

        {/* Trust/Authority Score */}
        <div className="bg-white rounded-xl shadow-lg p-6 border-l-4 border-orange-500">
          <h3 className="text-xl font-semibold text-gray-900 mb-4">Trust/Authority Score</h3>
          <div className="grid grid-cols-2 gap-4 mb-4">
            <div className="text-center">
              <div className="text-2xl font-bold text-orange-600 mb-1">
                {Math.round(analysisResult.trust_score.ai_recommendations * 100)}
              </div>
              <p className="text-xs text-gray-600">Overall Trust</p>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-gray-600 mb-1">
                {Math.round(analysisResult.trust_score.vs_others * 100)}
              </div>
              <p className="text-xs text-gray-600">Brand Authority</p>
            </div>
          </div>
          <div className="mb-4">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm text-gray-600">Performance Metrics</span>
              <span className="text-sm font-medium text-gray-900">
                {Math.round((analysisResult.trust_score.ai_recommendations + analysisResult.trust_score.vs_others) * 50)}
              </span>
            </div>
            <div className="space-y-2">
              <div className="flex items-center justify-between text-xs">
                <span className="text-gray-600">Web Presence</span>
                <span className="text-gray-900 font-medium">
                  {Math.round(analysisResult.trust_score.vs_others * 100)}
                </span>
              </div>
              <div className="flex items-center justify-between text-xs">
                <span className="text-gray-600">Source Quality</span>
                <span className="text-gray-900 font-medium">
                  {Math.round(analysisResult.trust_score.ai_recommendations * 100)}
                </span>
              </div>
            </div>
          </div>
          <p className="text-gray-700">{analysisResult.trust_score.summary}</p>
        </div>
      </div>

      {/* Additional Analysis Section */}
      <div className="bg-white rounded-xl shadow-lg p-6">
        <h3 className="text-xl font-semibold text-gray-900 mb-4">Additional Insights</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="p-4 bg-gray-50 rounded-lg">
            <h4 className="font-medium text-gray-900 mb-2">Analysis Quality</h4>
            <p className="text-sm text-gray-600">Powered by AI-judge evaluation using GPT-4o</p>
          </div>
          <div className="p-4 bg-gray-50 rounded-lg">
            <h4 className="font-medium text-gray-900 mb-2">Data Sources</h4>
            <p className="text-sm text-gray-600">Comprehensive web crawling and AI analysis</p>
          </div>
          <div className="p-4 bg-gray-50 rounded-lg">
            <h4 className="font-medium text-gray-900 mb-2">Recommendations</h4>
            <p className="text-sm text-gray-600">Actionable insights for brand improvement</p>
          </div>
        </div>
      </div>

      {/* Back to Analysis Button */}
      <div className="mt-8 text-center">
        <a
          href="/"
          className="inline-flex items-center px-6 py-3 bg-blue-600 text-white font-semibold rounded-xl hover:bg-blue-700 transition-colors"
        >
          <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
          </svg>
          Analyze New Prompt
        </a>
      </div>
    </div>
  );
}
