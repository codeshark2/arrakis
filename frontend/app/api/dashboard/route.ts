import { NextRequest, NextResponse } from 'next/server';

// This would typically connect to your backend API
// For now, we'll create mock data structure that matches your database schema

export async function GET(request: NextRequest) {
  try {
    // In production, this would fetch from your backend API
    // const response = await fetch(`${process.env.BACKEND_URL}/api/dashboard`);
    // const data = await response.json();
    
    // For now, return mock data structure that matches your database
    const mockData = {
      totalAnalyses: 12,
      recentAnalyses: [
        {
          id: "1",
          brand_name: "Tesla",
          overall_sentiment_tone: "positive",
          overall_trust_score: 85,
          total_urls_analyzed: 5,
          created_at: "2024-01-15T10:30:00Z"
        },
        {
          id: "2",
          brand_name: "Apple",
          overall_sentiment_tone: "positive",
          overall_trust_score: 92,
          total_urls_analyzed: 5,
          created_at: "2024-01-14T15:45:00Z"
        },
        {
          id: "3",
          brand_name: "Nike",
          overall_sentiment_tone: "mixed",
          overall_trust_score: 78,
          total_urls_analyzed: 5,
          created_at: "2024-01-13T09:20:00Z"
        },
        {
          id: "4",
          brand_name: "Microsoft",
          overall_sentiment_tone: "positive",
          overall_trust_score: 88,
          total_urls_analyzed: 5,
          created_at: "2024-01-12T14:15:00Z"
        }
      ],
      sentimentBreakdown: {
        positive: 65,
        neutral: 20,
        negative: 10,
        mixed: 5
      },
      topBrands: [
        {
          brand_name: "Apple",
          average_trust_score: 92,
          total_analyses: 3
        },
        {
          brand_name: "Microsoft",
          average_trust_score: 88,
          total_analyses: 2
        },
        {
          brand_name: "Tesla",
          average_trust_score: 85,
          total_analyses: 2
        },
        {
          brand_name: "Nike",
          average_trust_score: 78,
          total_analyses: 2
        },
        {
          brand_name: "Google",
          average_trust_score: 82,
          total_analyses: 1
        }
      ],
      recentInsights: [
        {
          id: "1",
          brand_name: "Tesla",
          insight: "Strong positive sentiment around innovation and sustainability",
          created_at: "2024-01-15T10:30:00Z"
        },
        {
          id: "2",
          brand_name: "Apple",
          insight: "High trust score driven by product quality and customer satisfaction",
          created_at: "2024-01-14T15:45:00Z"
        }
      ]
    };

    return NextResponse.json(mockData);
    
  } catch (error) {
    console.error('Dashboard API error:', error);
    return NextResponse.json(
      { error: 'Failed to fetch dashboard data' },
      { status: 500 }
    );
  }
}
