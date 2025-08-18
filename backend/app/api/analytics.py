"""Analytics API endpoints for Arrakis MVP."""

import logging
import uuid
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, List
from ..services.perplexity_client import PerplexityClient
from ..supabase.client import db
from ..core.config import settings

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/analytics", tags=["analytics"])

# Initialize Perplexity client only
perplexity_client = PerplexityClient()


class AnalyzeRequest(BaseModel):
    prompt: str


class AnalysisResponse(BaseModel):
    sentiment: Dict[str, Any]
    brand_mentions: Dict[str, Any]
    website_coverage: Dict[str, Any]
    trust_score: Dict[str, Any]
    analysis_id: str


@router.post("/analyze", response_model=AnalysisResponse)
async def analyze_prompt(request: AnalyzeRequest):
    """Analyze a prompt using Perplexity AI and store results in database."""
    try:
        logger.info(f"Starting analysis for prompt: {request.prompt}")
        
        # Extract brand name from prompt
        brand_name = _extract_brand_name(request.prompt)
        
        # Generate unique analysis ID
        analysis_id = str(uuid.uuid4())
        
        # Perform Perplexity AI analysis
        perplexity_result = await perplexity_client.search_and_analyze(
            prompt=request.prompt,
            target_websites=settings.pplx_target_sites  # Use config value (25)
        )
        
        # Store results in database
        await _store_analysis_results(analysis_id, brand_name, request.prompt, perplexity_result)
        
        # Extract the four parameters from Perplexity results
        analysis_result = _extract_four_parameters(perplexity_result, brand_name)
        
        logger.info(f"Analysis completed successfully for brand: {brand_name}")
        
        return AnalysisResponse(
            sentiment=analysis_result["sentiment"],
            brand_mentions=analysis_result["brand_mentions"],
            website_coverage=analysis_result["website_coverage"],
            trust_score=analysis_result["trust_score"],
            analysis_id=analysis_id
        )
        
    except Exception as e:
        logger.error(f"Analysis failed: {e}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


async def _store_analysis_results(analysis_id: str, brand_name: str, prompt: str, perplexity_result: Dict[str, Any]):
    """Store analysis results in the database."""
    try:
        # Calculate basic metrics from Perplexity results
        total_sources = perplexity_result.get('total_sources_analyzed', 0)
        crawled_content = perplexity_result.get('crawled_content', [])
        
        # Calculate sentiment using the same logic as the frontend response
        positive_count = 0
        negative_count = 0
        neutral_count = 0
        
        for content in crawled_content:
            # Check if Perplexity provided sentiment analysis
            if 'sentiment' in content:
                sentiment = content['sentiment'].lower()
                if 'positive' in sentiment or 'good' in sentiment or 'excellent' in sentiment:
                    positive_count += 1
                elif 'negative' in sentiment or 'bad' in sentiment or 'poor' in sentiment:
                    negative_count += 1
                else:
                    neutral_count += 1
            else:
                # If no sentiment data, analyze content text for keywords
                content_text = content.get('content', '').lower()
                positive_words = ['good', 'great', 'excellent', 'positive', 'successful', 'leading', 'innovative', 'strong']
                negative_words = ['bad', 'poor', 'negative', 'failing', 'weak', 'declining', 'struggling', 'problem']
                
                positive_matches = sum(1 for word in positive_words if word in content_text)
                negative_matches = sum(1 for word in negative_words if word in content_text)
                
                if positive_matches > negative_matches:
                    positive_count += 1
                elif negative_matches > positive_matches:
                    negative_count += 1
                else:
                    neutral_count += 1
        
        # Calculate meaningful metrics (no confusing percentages)
        total = max(total_sources, 1)
        
        # Determine overall sentiment tone
        if positive_count > negative_count and positive_count > neutral_count:
            overall_tone = 'positive'
        elif negative_count > positive_count and negative_count > neutral_count:
            overall_tone = 'negative'
        else:
            overall_tone = 'neutral'
        
        # Calculate meaningful trust score
        trust_score = min(100, max(0, (total_sources * 1.5) + (positive_count * 2)))
        
        # Store in deep_research_analysis table
        analysis_data = {
            "id": analysis_id,
            "brand_name": brand_name,
            "prompt_text": prompt,
            "total_urls_analyzed": total_sources,
            "overall_sentiment_tone": overall_tone,
            "positive_percentage": (positive_count / total) * 100,  # Keep for database compatibility
            "neutral_percentage": (neutral_count / total) * 100,   # Keep for database compatibility
            "negative_percentage": (negative_count / total) * 100, # Keep for database compatibility
            "total_mention_count": total_sources,
            "average_mentions_per_url": 1.0,
            "overall_trust_score": trust_score,
            "confidence_level": "high" if total_sources >= 30 else "medium" if total_sources >= 15 else "low",
            "model_used": "perplexity-ai",
            "total_tokens_used": perplexity_result.get('total_tokens_used', 0),
            "analysis_summary": perplexity_result.get('content', ''),
            "detailed_analyses": crawled_content,
            "crawled_urls": [content.get('source', '') for content in crawled_content]
        }
        
        # Insert into database
        await db.insert("deep_research_analysis", analysis_data)
        
        logger.info(f"Analysis results stored in database with ID: {analysis_id}")
        
    except Exception as e:
        logger.error(f"Failed to store analysis results: {e}")
        raise


def _extract_four_parameters(perplexity_result: Dict[str, Any], brand_name: str) -> Dict[str, Any]:
    """Extract the four key parameters from Perplexity results with meaningful metrics."""
    total_sources = perplexity_result.get('total_sources_analyzed', 0)
    crawled_content = perplexity_result.get('crawled_content', [])
    
    # Calculate sentiment from actual Perplexity content analysis
    positive_count = 0
    negative_count = 0
    neutral_count = 0
    
    for content in crawled_content:
        # Check if Perplexity provided sentiment analysis
        if 'sentiment' in content:
            sentiment = content['sentiment'].lower()
            if 'positive' in sentiment or 'good' in sentiment or 'excellent' in sentiment:
                positive_count += 1
            elif 'negative' in sentiment or 'bad' in sentiment or 'poor' in sentiment:
                negative_count += 1
            else:
                neutral_count += 1
        else:
            # If no sentiment data, analyze content text for keywords
            content_text = content.get('content', '').lower()
            positive_words = ['good', 'great', 'excellent', 'positive', 'successful', 'leading', 'innovative', 'strong']
            negative_words = ['bad', 'poor', 'negative', 'failing', 'weak', 'declining', 'struggling', 'problem']
            
            positive_matches = sum(1 for word in positive_words if word in content_text)
            negative_matches = sum(1 for word in negative_words if word in content_text)
            
            if positive_matches > negative_matches:
                positive_count += 1
            elif negative_matches > positive_matches:
                negative_count += 1
            else:
                neutral_count += 1
    
    total = max(total_sources, 1)
    
    # Calculate meaningful sentiment metrics (no percentages)
    sentiment_score = (positive_count / total) if total > 0 else 0.5
    
    # Determine overall sentiment tone
    if positive_count > negative_count and positive_count > neutral_count:
        overall_tone = 'positive'
    elif negative_count > positive_count and negative_count > neutral_count:
        overall_tone = 'negative'
    else:
        overall_tone = 'neutral'
    
    return {
        "sentiment": {
            "tone": overall_tone,
            "score": sentiment_score,  # 0-1 scale, no percentage
            "summary": f"Analysis of {total_sources} sources: {positive_count} positive, {neutral_count} neutral, {negative_count} negative mentions"
        },
        "brand_mentions": {
            "count": total_sources,
            "contexts": _extract_mention_contexts(crawled_content),
            "summary": f"Found {total_sources} sources mentioning {brand_name} across web search results"
        },
        "website_coverage": {
            "total_websites_crawled": total_sources,
            "unique_websites_found": len(set(content.get('source', '') for content in crawled_content)),
            "coverage_percentage": _calculate_meaningful_coverage(total_sources),  # New meaningful metric
            "coverage_quality": _determine_coverage_quality(total_sources),
            "summary": f"Analyzed {total_sources} websites with {len(set(content.get('source', '') for content in crawled_content))} unique domains"
        },
        "trust_score": {
            "ai_recommendations": _calculate_trust_score(total_sources, positive_count, total),
            "vs_others": _calculate_authority_score(total_sources, len(set(content.get('source', '') for content in crawled_content))),
            "summary": f"AI analysis indicates {brand_name} has {'strong' if positive_count > total/2 else 'moderate' if positive_count > total/4 else 'limited'} market presence based on {total_sources} analyzed sources"
        }
    }


def _extract_mention_contexts(crawled_content: List[Dict]) -> List[str]:
    """Extract meaningful mention contexts from crawled content."""
    contexts = []
    
    if not crawled_content:
        return ["Web search results", "Brand analysis", "Market research"]
    
    # Extract domains and content types as contexts
    for content in crawled_content[:5]:  # Limit to 5 contexts
        source = content.get('source', '')
        if source:
            # Extract domain as context
            import re
            domain_match = re.search(r'https?://(?:www\.)?([^/]+)', source)
            if domain_match:
                domain = domain_match.group(1)
                if domain not in contexts:
                    contexts.append(domain)
    
    # If no contexts found, return defaults
    if not contexts:
        contexts = ["Web search results", "Brand analysis", "Market research"]
    
    return contexts[:3]  # Limit to 3 contexts


def _calculate_meaningful_coverage(total_sources: int) -> str:
    """Calculate meaningful coverage metric instead of confusing percentages."""
    if total_sources >= 45:
        return "Comprehensive (45+ sites)"
    elif total_sources >= 35:
        return "Extensive (35-44 sites)"
    elif total_sources >= 25:
        return "Good (25-34 sites)"
    elif total_sources >= 15:
        return "Moderate (15-24 sites)"
    elif total_sources >= 8:
        return "Limited (8-14 sites)"
    else:
        return "Minimal (<8 sites)"


def _determine_coverage_quality(total_sources: int) -> str:
    """Determine coverage quality based on number of sources."""
    if total_sources >= 40:
        return "excellent"
    elif total_sources >= 30:
        return "very good"
    elif total_sources >= 20:
        return "good"
    elif total_sources >= 10:
        return "fair"
    else:
        return "poor"


def _calculate_trust_score(total_sources: int, positive_count: int, total: int) -> float:
    """Calculate trust score based on sources and sentiment (0-1 scale)."""
    # Base score from number of sources (0-0.4)
    source_score = min(0.4, total_sources / 50)
    
    # Sentiment score (0-0.6)
    sentiment_score = (positive_count / total) * 0.6 if total > 0 else 0.3
    
    return min(1.0, source_score + sentiment_score)


def _calculate_authority_score(total_sources: int, unique_domains: int) -> float:
    """Calculate authority score based on source diversity (0-1 scale)."""
    # Base score from unique domains (0-0.5)
    domain_score = min(0.5, unique_domains / 50)
    
    # Volume score from total sources (0-0.5)
    volume_score = min(0.5, total_sources / 50)
    
    return min(1.0, domain_score + volume_score)


def _extract_brand_name(prompt: str) -> str:
    """Extract brand name from prompt text."""
    prompt_lower = prompt.lower()
    
    # Common patterns for brand mentions
    patterns = [
        r"analyze (?:the\s+)?([A-Za-z\s]+?)(?:\s+is\s+doing|\s+performing|\s+visibility|\s+brand|\s+company|\.|,|$|\?)",
        r"([A-Za-z\s]+?) brand",
        r"([A-Za-z\s]+?) company",
        r"([A-Za-z\s]+?) visibility",
        r"([A-Za-z\s]+?) market presence",
        r"how is ([A-Za-z\s]+?) doing",
        r"what about ([A-Za-z\s]+?)",
        r"([A-Za-z\s]+?) performance",
        r"analyze ([A-Za-z\s]+?) in",
        r"([A-Za-z\s]+?) market position"
    ]
    
    for pattern in patterns:
        import re
        match = re.search(pattern, prompt_lower)
        if match:
            brand_name = match.group(1).strip()
            # Convert to proper case
            brand_name = ' '.join(word.capitalize() for word in brand_name.split())
            if len(brand_name) > 2:  # Avoid single letters
                logger.info(f"Extracted brand name: {brand_name}")
                return brand_name
    
    # If no pattern matches, try to find capitalized words that look like brand names
    words = prompt.split()
    for i, word in enumerate(words):
        if (word[0].isupper() and len(word) > 2 and 
            word.lower() not in ['analyze', 'brand', 'company', 'visibility', 'market', 'presence', 'performance']):
            # Look for adjacent capitalized words (compound brand names)
            brand_parts = [word]
            for j in range(i + 1, min(i + 3, len(words))):
                if words[j][0].isupper() and len(words[j]) > 2:
                    brand_parts.append(words[j])
                else:
                    break
            
            brand_name = ' '.join(brand_parts)
            logger.info(f"Extracted brand name from capitalized words: {brand_name}")
            return brand_name
    
    # Fallback: use first few words of prompt
    fallback_name = ' '.join(words[:3])[:30]
    logger.info(f"Using fallback brand name: {fallback_name}")
    return fallback_name
