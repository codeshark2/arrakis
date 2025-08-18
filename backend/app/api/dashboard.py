"""Dashboard API endpoints for deep research analysis data."""

from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, List, Any
from ..supabase.client import db
from ..core.config import settings
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])

@router.get("/")
async def get_dashboard_data() -> Dict[str, Any]:
    """Get comprehensive dashboard data from deep research analysis."""
    try:
        logger.info("Fetching dashboard data from deep research analysis")
        
        # Get total analyses count
        total_analyses = await _get_total_analyses()
        
        # Get recent analyses
        recent_analyses = await _get_recent_analyses(limit=10)
        
        # Get sentiment breakdown
        sentiment_breakdown = await _get_sentiment_breakdown()
        
        # Get top performing brands
        top_brands = await _get_top_brands(limit=10)
        
        # Get recent insights
        recent_insights = await _get_recent_insights(limit=5)
        
        dashboard_data = {
            "totalAnalyses": total_analyses,
            "recentAnalyses": recent_analyses,
            "sentimentBreakdown": sentiment_breakdown,
            "topBrands": top_brands,
            "recentInsights": recent_insights
        }
        
        logger.info(f"Dashboard data fetched successfully: {total_analyses} analyses")
        return dashboard_data
        
    except Exception as e:
        logger.error(f"Error fetching dashboard data: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch dashboard data: {str(e)}")

async def _get_total_analyses() -> int:
    """Get total number of deep research analyses."""
    try:
        result = await db.execute_raw_sql(
            "SELECT COUNT(*) as count FROM deep_research_analysis"
        )
        return result[0]['count'] if result else 0
    except Exception as e:
        logger.error(f"Error getting total analyses: {e}")
        return 0

async def _get_recent_analyses(limit: int = 10) -> List[Dict[str, Any]]:
    """Get recent deep research analyses."""
    try:
        result = await db.execute_raw_sql(
            """
            SELECT 
                id,
                brand_name,
                overall_sentiment_tone,
                overall_trust_score,
                total_urls_analyzed,
                created_at
            FROM deep_research_analysis 
            ORDER BY created_at DESC 
            LIMIT $1
            """,
            [limit]
        )
        
        analyses = []
        for row in result:
            analyses.append({
                "id": str(row['id']),
                "brand_name": row['brand_name'],
                "overall_sentiment_tone": row['overall_sentiment_tone'],
                "overall_trust_score": float(row['overall_trust_score']),
                "total_urls_analyzed": row['total_urls_analyzed'],
                "created_at": row['created_at'].isoformat() if row['created_at'] else None
            })
        
        return analyses
        
    except Exception as e:
        logger.error(f"Error getting recent analyses: {e}")
        return []

async def _get_sentiment_breakdown() -> Dict[str, float]:
    """Get sentiment breakdown across all analyses."""
    try:
        result = await db.execute_raw_sql(
            """
            SELECT 
                overall_sentiment_tone,
                COUNT(*) as count,
                ROUND(
                    (COUNT(*) * 100.0 / (SELECT COUNT(*) FROM deep_research_analysis)), 
                    1
                ) as percentage
            FROM deep_research_analysis 
            GROUP BY overall_sentiment_tone
            """
        )
        
        # Initialize with zeros
        breakdown = {
            "positive": 0.0,
            "neutral": 0.0,
            "negative": 0.0,
            "mixed": 0.0
        }
        
        # Update with actual percentages
        for row in result:
            tone = row['overall_sentiment_tone']
            if tone in breakdown:
                breakdown[tone] = float(row['percentage'])
        
        return breakdown
        
    except Exception as e:
        logger.error(f"Error getting sentiment breakdown: {e}")
        return {"positive": 0.0, "neutral": 0.0, "negative": 0.0, "mixed": 0.0}

async def _get_top_brands(limit: int = 10) -> List[Dict[str, Any]]:
    """Get top performing brands by trust score."""
    try:
        result = await db.execute_raw_sql(
            """
            SELECT 
                brand_name,
                ROUND(AVG(overall_trust_score), 1) as average_trust_score,
                COUNT(*) as total_analyses
            FROM deep_research_analysis 
            GROUP BY brand_name 
            HAVING COUNT(*) > 0
            ORDER BY average_trust_score DESC 
            LIMIT $1
            """,
            [limit]
        )
        
        brands = []
        for row in result:
            brands.append({
                "brand_name": row['brand_name'],
                "average_trust_score": float(row['average_trust_score']),
                "total_analyses": row['total_analyses']
            })
        
        return brands
        
    except Exception as e:
        logger.error(f"Error getting top brands: {e}")
        return []

async def _get_recent_insights(limit: int = 5) -> List[Dict[str, Any]]:
    """Get recent insights from deep research analysis."""
    try:
        result = await db.execute_raw_sql(
            """
            SELECT 
                id,
                brand_name,
                analysis_summary->>'overall_sentiment_tone' as sentiment_tone,
                overall_trust_score,
                created_at
            FROM deep_research_analysis 
            ORDER BY created_at DESC 
            LIMIT $1
            """,
            [limit]
        )
        
        insights = []
        for row in result:
            # Generate insight based on sentiment and trust score
            sentiment = row['sentiment_tone'] or 'neutral'
            trust_score = float(row['overall_trust_score']) if row['overall_trust_score'] else 0
            
            if sentiment == 'positive' and trust_score > 80:
                insight = f"Strong positive sentiment with high trust score of {trust_score}"
            elif sentiment == 'positive':
                insight = f"Positive sentiment with trust score of {trust_score}"
            elif sentiment == 'negative':
                insight = f"Negative sentiment detected, trust score of {trust_score}"
            elif sentiment == 'mixed':
                insight = f"Mixed sentiment with trust score of {trust_score}"
            else:
                insight = f"Neutral sentiment with trust score of {trust_score}"
            
            insights.append({
                "id": str(row['id']),
                "brand_name": row['brand_name'],
                "insight": insight,
                "created_at": row['created_at'].isoformat() if row['created_at'] else None
            })
        
        return insights
        
    except Exception as e:
        logger.error(f"Error getting recent insights: {e}")
        return []

@router.get("/brand/{brand_name}")
async def get_brand_dashboard(brand_name: str) -> Dict[str, Any]:
    """Get dashboard data for a specific brand."""
    try:
        logger.info(f"Fetching dashboard data for brand: {brand_name}")
        
        # Get brand-specific analyses
        brand_analyses = await _get_brand_analyses(brand_name)
        
        # Get brand sentiment trend
        sentiment_trend = await _get_brand_sentiment_trend(brand_name)
        
        # Get brand competitors
        competitors = await _get_brand_competitors(brand_name)
        
        # Get brand URL analysis details
        url_details = await _get_brand_url_details(brand_name)
        
        brand_data = {
            "brand_name": brand_name,
            "analyses": brand_analyses,
            "sentiment_trend": sentiment_trend,
            "competitors": competitors,
            "url_details": url_details
        }
        
        return brand_data
        
    except Exception as e:
        logger.error(f"Error fetching brand dashboard data: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch brand data: {str(e)}")

async def _get_brand_analyses(brand_name: str) -> List[Dict[str, Any]]:
    """Get all analyses for a specific brand."""
    try:
        result = await db.execute_raw_sql(
            """
            SELECT 
                id,
                overall_sentiment_tone,
                overall_trust_score,
                total_urls_analyzed,
                positive_percentage,
                neutral_percentage,
                negative_percentage,
                total_mention_count,
                created_at
            FROM deep_research_analysis 
            WHERE brand_name = $1
            ORDER BY created_at DESC
            """,
            [brand_name]
        )
        
        analyses = []
        for row in result:
            analyses.append({
                "id": str(row['id']),
                "sentiment_tone": row['overall_sentiment_tone'],
                "trust_score": float(row['overall_trust_score']),
                "urls_analyzed": row['total_urls_analyzed'],
                "sentiment_breakdown": {
                    "positive": float(row['positive_percentage']),
                    "neutral": float(row['neutral_percentage']),
                    "negative": float(row['negative_percentage'])
                },
                "mention_count": row['total_mention_count'],
                "created_at": row['created_at'].isoformat() if row['created_at'] else None
            })
        
        return analyses
        
    except Exception as e:
        logger.error(f"Error getting brand analyses: {e}")
        return []

async def _get_brand_sentiment_trend(brand_name: str) -> List[Dict[str, Any]]:
    """Get sentiment trend over time for a brand."""
    try:
        result = await db.execute_raw_sql(
            """
            SELECT 
                DATE(created_at) as date,
                overall_sentiment_tone,
                positive_percentage,
                neutral_percentage,
                negative_percentage
            FROM deep_research_analysis 
            WHERE brand_name = $1
            ORDER BY created_at ASC
            """,
            [brand_name]
        )
        
        trend = []
        for row in result:
            trend.append({
                "date": row['date'].isoformat() if row['date'] else None,
                "sentiment_tone": row['overall_sentiment_tone'],
                "sentiment_breakdown": {
                    "positive": float(row['positive_percentage']),
                    "neutral": float(row['neutral_percentage']),
                    "negative": float(row['negative_percentage'])
                }
            })
        
        return trend
        
    except Exception as e:
        logger.error(f"Error getting brand sentiment trend: {e}")
        return []

async def _get_brand_competitors(brand_name: str) -> List[Dict[str, Any]]:
    """Get competitors mentioned alongside a brand."""
    try:
        result = await db.execute_raw_sql(
            """
            SELECT 
                cm.competitor_name,
                cm.total_mentions,
                cm.average_favorability_score,
                cm.mention_urls
            FROM competitor_mentions cm
            JOIN deep_research_analysis dra ON cm.deep_research_analysis_id = dra.id
            WHERE dra.brand_name = $1
            ORDER BY cm.total_mentions DESC
            """,
            [brand_name]
        )
        
        competitors = []
        for row in result:
            competitors.append({
                "name": row['competitor_name'],
                "total_mentions": row['total_mentions'],
                "favorability_score": float(row['average_favorability_score']),
                "mention_urls": row['mention_urls'] or []
            })
        
        return competitors
        
    except Exception as e:
        logger.error(f"Error getting brand competitors: {e}")
        return []

async def _get_brand_url_details(brand_name: str) -> List[Dict[str, Any]]:
    """Get detailed URL analysis for a brand."""
    try:
        result = await db.execute_raw_sql(
            """
            SELECT 
                uar.url,
                uar.title,
                uar.sentiment_tone,
                uar.mention_count,
                uar.ai_recommendation_score,
                uar.sentiment_reasoning,
                uar.mention_reasoning,
                uar.trust_reasoning
            FROM url_analysis_results uar
            JOIN deep_research_analysis dra ON uar.deep_research_analysis_id = dra.id
            WHERE dra.brand_name = $1
            ORDER BY uar.created_at DESC
            """,
            [brand_name]
        )
        
        url_details = []
        for row in result:
            url_details.append({
                "url": row['url'],
                "title": row['title'],
                "sentiment_tone": row['sentiment_tone'],
                "mention_count": row['mention_count'],
                "ai_recommendation_score": float(row['ai_recommendation_score']),
                "sentiment_reasoning": row['sentiment_reasoning'],
                "mention_reasoning": row['mention_reasoning'],
                "trust_reasoning": row['trust_reasoning']
            })
        
        return url_details
        
    except Exception as e:
        logger.error(f"Error getting brand URL details: {e}")
        return []
