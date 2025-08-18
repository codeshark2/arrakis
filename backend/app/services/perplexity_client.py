"""Perplexity AI client for web search and crawling."""

import os
import logging
from typing import Dict, List, Any, Optional
from openai import OpenAI
from app.core.config import settings

logger = logging.getLogger(__name__)

class PerplexityClient:
    """Client for interacting with Perplexity AI API."""
    
    def __init__(self):
        """Initialize the Perplexity AI client."""
        if not settings.perplexity_api_key:
            logger.warning("Perplexity API key not configured")
            self.client = None
            return
            
        self.client = OpenAI(
            api_key=settings.perplexity_api_key,
            base_url="https://api.perplexity.ai"
        )
        logger.info("Perplexity AI client initialized successfully")
    
    async def search_and_analyze(self, prompt: str, target_websites: int = 50) -> Dict[str, Any]:
        """
        Perform comprehensive web search and analysis to reach target number of websites.
        
        Args:
            prompt: The search prompt
            target_websites: Target number of websites to crawl (default: 50)
        
        Returns:
            Dictionary containing aggregated search results and insights
        """
        if not self.client:
            return self._fallback_response(prompt)
        
        try:
            logger.info(f"Starting comprehensive Perplexity AI search for: {prompt}")
            logger.info(f"Target: {target_websites} websites")
            
            # Generate multiple search queries to get diverse results
            search_queries = self._generate_diverse_search_queries(prompt)
            logger.info(f"Generated {len(search_queries)} search queries")
            
            all_results = []
            total_websites = 0
            query_count = 0
            
            # Make multiple API calls to reach target website count
            for query in search_queries:
                if total_websites >= target_websites:
                    break
                    
                query_count += 1
                logger.info(f"Query {query_count}/{len(search_queries)}: {query[:100]}...")
                
                try:
                    # Make the API call
                    response = await self._make_perplexity_call(query)
                    
                    if response and 'choices' in response and response['choices']:
                        # Parse the response
                        parsed_result = self._parse_perplexity_response(response)
                        
                        if parsed_result['crawled_content']:
                            all_results.append(parsed_result)
                            total_websites += len(parsed_result['crawled_content'])
                            logger.info(f"Query {query_count} found {len(parsed_result['crawled_content'])} sources. Total: {total_websites}")
                        
                        # Add delay between queries to avoid rate limiting
                        if query_count < len(search_queries):
                            import asyncio
                            await asyncio.sleep(1)
                    
                except Exception as e:
                    logger.error(f"Error in query {query_count}: {e}")
                    continue
            
            # Aggregate all results
            aggregated_result = self._aggregate_results(all_results, target_websites)
            
            logger.info(f"Comprehensive search completed. Found {len(aggregated_result['crawled_content'])} total sources")
            return aggregated_result
            
        except Exception as e:
            logger.error(f"Perplexity API call failed: {e}")
            return self._fallback_response(prompt)
    
    def _generate_diverse_search_queries(self, base_prompt: str) -> List[str]:
        """
        Generate diverse search queries to get comprehensive coverage.
        
        Args:
            base_prompt: The original prompt
            
        Returns:
            List of diverse search queries
        """
        # Extract key terms from the prompt
        prompt_lower = base_prompt.lower()
        
        # Base queries
        queries = [
            base_prompt,
            f"{base_prompt} latest news and updates",
            f"{base_prompt} industry analysis and trends",
            f"{base_prompt} market research and statistics",
            f"{base_prompt} expert opinions and reviews",
            f"{base_prompt} competitive analysis",
            f"{base_prompt} customer feedback and reviews",
            f"{base_prompt} financial performance and metrics",
            f"{base_prompt} technology and innovation",
            f"{base_prompt} regulatory and compliance",
            f"{base_prompt} social media presence",
            f"{base_prompt} press releases and announcements",
            f"{base_prompt} academic research and studies",
            f"{base_prompt} industry reports and whitepapers",
            f"{base_prompt} case studies and success stories"
        ]
        
        # Add company-specific queries if company name is detected
        if any(word in prompt_lower for word in ['tesla', 'apple', 'google', 'microsoft', 'amazon']):
            company_queries = [
                f"{base_prompt} company overview and history",
                f"{base_prompt} leadership team and management",
                f"{base_prompt} products and services portfolio",
                f"{base_prompt} global presence and expansion",
                f"{base_prompt} sustainability and corporate responsibility"
            ]
            queries.extend(company_queries)
        
        # Limit to reasonable number of queries to avoid excessive API calls
        return queries[:20]
    
    async def _make_perplexity_call(self, query: str) -> Optional[Dict[str, Any]]:
        """
        Make a single API call to Perplexity AI.
        
        Args:
            query: The search query
            
        Returns:
            API response or None if failed
        """
        try:
            # Use sonar model for web search capabilities
            # Based on latest Perplexity docs: https://docs.perplexity.ai/getting-started/overview
            # Correct model names: sonar, sonar-reasoning, sonar-deep-research
            response = self.client.chat.completions.create(
                model="sonar",  # Lightweight search model with grounding
                messages=[
                    {
                        "role": "user",
                        "content": query
                    }
                ],
                max_tokens=2000,
                temperature=0.1,  # Low temperature for consistent analysis
                # Remove unsupported parameters - Perplexity handles web search automatically
                # when using online models like sonar
            )
            
            return response.model_dump()
            
        except Exception as e:
            logger.error(f"Perplexity API call failed: {e}")
            return None
    
    def _parse_perplexity_response(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parse the Perplexity API response.
        
        Args:
            response: Raw API response
            
        Returns:
            Parsed and structured data
        """
        try:
            # Extract the main content
            content = ""
            if 'choices' in response and response['choices']:
                content = response['choices'][0].get('message', {}).get('content', '')
            
            # Extract citations (URLs)
            citations = response.get('citations', [])
            
            # Extract usage information
            usage = response.get('usage', {})
            
            # Generate crawled content from citations
            crawled_content = self._format_citations_as_content(citations)
            
            # Extract insights from content
            insights = self._extract_insights_from_content(content)
            
            return {
                'content': content,
                'citations': citations,
                'usage': usage,
                'crawled_content': crawled_content,
                'insights': insights
            }
            
        except Exception as e:
            logger.error(f"Error parsing Perplexity response: {e}")
            return self._fallback_response("")
    
    def _format_citations_as_content(self, citations: List[str]) -> List[Dict[str, Any]]:
        """
        Format citations as crawled content structure.
        
        Args:
            citations: List of URLs from Perplexity
            
        Returns:
            List of crawled content objects
        """
        crawled_content = []
        
        for i, url in enumerate(citations):
            # Extract domain from URL
            try:
                from urllib.parse import urlparse
                parsed_url = urlparse(url)
                domain = parsed_url.netloc
                source = domain.replace('www.', '')
            except:
                source = "unknown"
            
            crawled_content.append({
                'title': f"Source {i+1} from {source}",
                'url': url,
                'snippet': f"Content from {source} - {url}",
                'source': source,
                'relevance_score': 0.8 - (i * 0.1),  # Decreasing relevance for later sources
                'rank': i + 1
            })
        
        return crawled_content
    
    def _extract_insights_from_content(self, content: str) -> Dict[str, Any]:
        """
        Extract insights from the content.
        
        Args:
            content: The main content from Perplexity
            
        Returns:
            Dictionary of extracted insights
        """
        insights = {
            'sentiment': {
                'label': 'neutral',
                'score': 0.5
            },
            'visibility': {
                'visibility_percent': 50,
                'visible': True
            },
            'key_topics': [],
            'competitors': []
        }
        
        # Simple sentiment analysis based on content
        positive_words = ['good', 'great', 'excellent', 'positive', 'success', 'growth', 'improve']
        negative_words = ['bad', 'poor', 'negative', 'decline', 'problem', 'issue', 'concern']
        
        content_lower = content.lower()
        positive_count = sum(1 for word in positive_words if word in content_lower)
        negative_count = sum(1 for word in negative_words if word in content_lower)
        
        if positive_count > negative_count:
            insights['sentiment']['label'] = 'positive'
            insights['sentiment']['score'] = 0.7
        elif negative_count > positive_count:
            insights['sentiment']['label'] = 'negative'
            insights['sentiment']['score'] = 0.3
        
        return insights
    
    def _aggregate_results(self, all_results: List[Dict[str, Any]], target_websites: int) -> Dict[str, Any]:
        """
        Aggregate results from multiple queries.
        
        Args:
            all_results: List of results from different queries
            target_websites: Target number of websites
            
        Returns:
            Aggregated result
        """
        # Combine all crawled content
        all_crawled_content = []
        all_citations = []
        all_usage = {'total_tokens': 0, 'prompt_tokens': 0, 'completion_tokens': 0}
        
        for result in all_results:
            if 'crawled_content' in result:
                all_crawled_content.extend(result['crawled_content'])
            if 'citations' in result:
                all_citations.extend(result['citations'])
            if 'usage' in result:
                for key in all_usage:
                    all_usage[key] += result['usage'].get(key, 0)
        
        # Remove duplicates based on URL
        seen_urls = set()
        unique_crawled_content = []
        
        for content in all_crawled_content:
            if content['url'] not in seen_urls:
                seen_urls.add(content['url'])
                unique_crawled_content.append(content)
        
        # Limit to target number of websites
        if len(unique_crawled_content) > target_websites:
            unique_crawled_content = unique_crawled_content[:target_websites]
        
        # Re-rank the content
        for i, content in enumerate(unique_crawled_content):
            content['rank'] = i + 1
            content['relevance_score'] = max(0.1, 1.0 - (i * 0.02))  # Gradual decrease in relevance
        
        # Generate comprehensive insights
        comprehensive_insights = self._generate_comprehensive_insights(unique_crawled_content)
        
        return {
            'content': f"Comprehensive analysis based on {len(unique_crawled_content)} web sources",
            'citations': list(set(all_citations)),  # Remove duplicate URLs
            'usage': all_usage,
            'crawled_content': unique_crawled_content,
            'insights': comprehensive_insights,
            'search_queries': [f"Query {i+1}" for i in range(len(all_results))],
            'total_sources_analyzed': len(unique_crawled_content)
        }
    
    def _generate_comprehensive_insights(self, crawled_content: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generate comprehensive insights from aggregated crawled content.
        
        Args:
            crawled_content: List of crawled content objects
            
        Returns:
            Comprehensive insights
        """
        # Analyze source diversity
        sources = [content['source'] for content in crawled_content]
        unique_sources = list(set(sources))
        
        # Calculate average relevance
        avg_relevance = sum(content['relevance_score'] for content in crawled_content) / len(crawled_content) if crawled_content else 0
        
        insights = {
            'sentiment': {
                'label': 'comprehensive',
                'score': avg_relevance
            },
            'visibility': {
                'visibility_percent': min(100, len(crawled_content) * 2),  # Scale visibility based on source count
                'visible': len(crawled_content) > 0
            },
            'source_diversity': {
                'total_sources': len(crawled_content),
                'unique_domains': len(unique_sources),
                'diversity_score': len(unique_sources) / len(crawled_content) if crawled_content else 0
            },
            'coverage_quality': {
                'comprehensive': len(crawled_content) >= 100,
                'moderate': 50 <= len(crawled_content) < 100,
                'limited': len(crawled_content) < 50
            }
        }
        
        return insights
    
    def _fallback_response(self, prompt: str) -> Dict[str, Any]:
        """Provide fallback response when Perplexity API is not available."""
        return {
            'content': f"Analysis of: {prompt}",
            'citations': [],
            'usage': {'total_tokens': 0, 'prompt_tokens': 0, 'completion_tokens': 0},
            'crawled_content': [],
            'insights': {
                'sentiment': {'label': 'neutral', 'score': 0.5},
                'visibility': {'visibility_percent': 0, 'visible': False}
            },
            'search_queries': [prompt],
            'total_sources_analyzed': 0
        }
