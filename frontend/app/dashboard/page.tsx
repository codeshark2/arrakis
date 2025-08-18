'use client';

import { useState, useEffect } from 'react';
import { 
  TrendingUp, 
  MessageSquare, 
  Users, 
  Shield, 
  BarChart3, 
  Globe,
  Activity,
  Target,
  Zap,
  Eye
} from 'lucide-react';

interface DashboardData {
  totalAnalyses: number;
  recentAnalyses: Array<{
    id: string;
    brand_name: string;
    overall_sentiment_tone: string;
    overall_trust_score: number;
    total_urls_analyzed: number;
    created_at: string;
  }>;
  sentimentBreakdown: {
    positive: number;
    neutral: number;
    negative: number;
    mixed: number;
  };
  topBrands: Array<{
    brand_name: string;
    average_trust_score: number;
    total_analyses: number;
  }>;
  recentInsights: Array<{
    id: string;
    brand_name: string;
    insight: string;
    created_at: string;
  }>;
}

export default function DashboardPage() {
  const [dashboardData, setDashboardData] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      const response = await fetch('/api/dashboard');
      if (!response.ok) {
        throw new Error('Failed to fetch dashboard data');
      }
      const data = await response.json();
      setDashboardData(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading dashboard...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="text-red-500 text-6xl mb-4">⚠️</div>
          <h2 className="text-2xl font-bold text-gray-900 mb-2">Error Loading Dashboard</h2>
          <p className="text-gray-600 mb-4">{error}</p>
          <button 
            onClick={fetchDashboardData}
            className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors"
          >
            Try Again
          </button>
        </div>
      </div>
    );
  }

  if (!dashboardData) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <p className="text-gray-600">No dashboard data available</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">Arrakis Dashboard</h1>
              <p className="text-gray-600">AI-Powered Brand Intelligence System</p>
            </div>
            <div className="flex items-center space-x-4">
              <button 
                onClick={fetchDashboardData}
                className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors flex items-center space-x-2"
              >
                <Activity className="h-4 w-4" />
                <span>Refresh</span>
              </button>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Key Metrics Tiles */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <MetricTile
            title="Total Analyses"
            value={dashboardData.totalAnalyses}
            icon={BarChart3}
            color="blue"
            description="Deep research analyses completed"
          />
          <MetricTile
            title="Positive Sentiment"
            value={`${dashboardData.sentimentBreakdown.positive}%`}
            icon={TrendingUp}
            color="green"
            description="Average positive sentiment across brands"
          />
          <MetricTile
            title="Trust Score"
            value={`${Math.round(dashboardData.topBrands.reduce((acc, brand) => acc + brand.average_trust_score, 0) / Math.max(dashboardData.topBrands.length, 1))}/100`}
            icon={Shield}
            color="purple"
            description="Average brand trust score"
          />
          <MetricTile
            title="Active Brands"
            value={dashboardData.topBrands.length}
            icon={Target}
            color="orange"
            description="Brands analyzed in system"
          />
        </div>

        {/* Main Content Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Recent Analyses */}
          <div className="lg:col-span-2">
            <div className="bg-white rounded-lg shadow-sm border">
              <div className="px-6 py-4 border-b border-gray-200">
                <h3 className="text-lg font-semibold text-gray-900 flex items-center">
                  <Zap className="h-5 w-5 mr-2 text-blue-600" />
                  Recent Deep Research Analyses
                </h3>
              </div>
              <div className="p-6">
                {dashboardData.recentAnalyses.length === 0 ? (
                  <div className="text-center py-8 text-gray-500">
                    <BarChart3 className="h-12 w-12 mx-auto mb-4 text-gray-300" />
                    <p>No analyses completed yet</p>
                    <p className="text-sm">Start your first brand analysis to see results here</p>
                  </div>
                ) : (
                  <div className="space-y-4">
                    {dashboardData.recentAnalyses.map((analysis) => (
                      <div key={analysis.id} className="border border-gray-200 rounded-lg p-4 hover:bg-gray-50 transition-colors">
                        <div className="flex justify-between items-start">
                          <div>
                            <h4 className="font-semibold text-gray-900">{analysis.brand_name}</h4>
                            <p className="text-sm text-gray-600">
                              {analysis.total_urls_analyzed} URLs analyzed
                            </p>
                          </div>
                          <div className="text-right">
                            <div className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${
                              analysis.overall_sentiment_tone === 'positive' ? 'bg-green-100 text-green-800' :
                              analysis.overall_sentiment_tone === 'negative' ? 'bg-red-100 text-red-800' :
                              analysis.overall_sentiment_tone === 'mixed' ? 'bg-yellow-100 text-yellow-800' :
                              'bg-gray-100 text-gray-800'
                            }`}>
                              {analysis.overall_sentiment_tone}
                            </div>
                            <div className="mt-1 text-sm text-gray-600">
                              Trust: {analysis.overall_trust_score}/100
                            </div>
                          </div>
                        </div>
                        <div className="mt-2 text-xs text-gray-500">
                          {new Date(analysis.created_at).toLocaleDateString()}
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* Sentiment Breakdown */}
          <div className="lg:col-span-1">
            <div className="bg-white rounded-lg shadow-sm border">
              <div className="px-6 py-4 border-b border-gray-200">
                <h3 className="text-lg font-semibold text-gray-900 flex items-center">
                  <TrendingUp className="h-5 w-5 mr-2 text-green-600" />
                  Sentiment Overview
                </h3>
              </div>
              <div className="p-6">
                <div className="space-y-4">
                  <SentimentBar label="Positive" percentage={dashboardData.sentimentBreakdown.positive} color="green" />
                  <SentimentBar label="Neutral" percentage={dashboardData.sentimentBreakdown.neutral} color="gray" />
                  <SentimentBar label="Negative" percentage={dashboardData.sentimentBreakdown.negative} color="red" />
                  <SentimentBar label="Mixed" percentage={dashboardData.sentimentBreakdown.mixed} color="yellow" />
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Top Brands */}
        <div className="mt-8">
          <div className="bg-white rounded-lg shadow-sm border">
            <div className="px-6 py-4 border-b border-gray-200">
              <h3 className="text-lg font-semibold text-gray-900 flex items-center">
                <Target className="h-5 w-5 mr-2 text-orange-600" />
                Top Performing Brands
              </h3>
            </div>
            <div className="p-6">
              {dashboardData.topBrands.length === 0 ? (
                <div className="text-center py-8 text-gray-500">
                  <Target className="h-12 w-12 mx-auto mb-4 text-gray-300" />
                  <p>No brand data available</p>
                </div>
              ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {dashboardData.topBrands.map((brand, index) => (
                    <div key={brand.brand_name} className="border border-gray-200 rounded-lg p-4">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center">
                          <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center mr-3">
                            <span className="text-blue-600 font-semibold text-sm">{index + 1}</span>
                          </div>
                          <div>
                            <h4 className="font-semibold text-gray-900">{brand.brand_name}</h4>
                            <p className="text-sm text-gray-600">{brand.total_analyses} analyses</p>
                          </div>
                        </div>
                        <div className="text-right">
                          <div className="text-2xl font-bold text-blue-600">
                            {Math.round(brand.average_trust_score)}
                          </div>
                          <div className="text-xs text-gray-500">trust score</div>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

// Metric Tile Component
function MetricTile({ 
  title, 
  value, 
  icon: Icon, 
  color, 
  description 
}: { 
  title: string; 
  value: string | number; 
  icon: any; 
  color: string; 
  description: string; 
}) {
  const colorClasses = {
    blue: 'bg-blue-500',
    green: 'bg-green-500',
    purple: 'bg-purple-500',
    orange: 'bg-orange-500',
    red: 'bg-red-500',
    yellow: 'bg-yellow-500'
  };

  return (
    <div className="bg-white rounded-lg shadow-sm border p-6 hover:shadow-md transition-shadow">
      <div className="flex items-center">
        <div className={`${colorClasses[color as keyof typeof colorClasses]} p-3 rounded-lg`}>
          <Icon className="h-6 w-6 text-white" />
        </div>
        <div className="ml-4">
          <p className="text-sm font-medium text-gray-600">{title}</p>
          <p className="text-2xl font-semibold text-gray-900">{value}</p>
        </div>
      </div>
      <p className="mt-2 text-sm text-gray-500">{description}</p>
    </div>
  );
}

// Sentiment Bar Component
function SentimentBar({ 
  label, 
  percentage, 
  color 
}: { 
  label: string; 
  percentage: number; 
  color: string; 
}) {
  const colorClasses = {
    green: 'bg-green-500',
    gray: 'bg-gray-500',
    red: 'bg-red-500',
    yellow: 'bg-yellow-500'
  };

  return (
    <div>
      <div className="flex justify-between text-sm mb-1">
        <span className="text-gray-600">{label}</span>
        <span className="font-medium text-gray-900">{percentage}%</span>
      </div>
      <div className="w-full bg-gray-200 rounded-full h-2">
        <div 
          className={`${colorClasses[color as keyof typeof colorClasses]} h-2 rounded-full transition-all duration-300`}
          style={{ width: `${percentage}%` }}
        ></div>
      </div>
    </div>
  );
}
