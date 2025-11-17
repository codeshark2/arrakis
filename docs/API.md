# Arrakis API Documentation

## Overview

The Arrakis API provides AI-powered brand intelligence capabilities, allowing you to analyze brand visibility, sentiment, and market presence across web sources.

**Base URL**: `http://localhost:8000` (development) or `https://your-domain.com` (production)

**API Version**: 1.0.0

---

## Authentication

Currently, the API does not require authentication for basic operations. For production deployments, we recommend implementing API key authentication.

---

## Rate Limiting

- **Rate Limit**: 100 requests per 60 seconds per IP address
- **Headers**:
  - `X-RateLimit-Limit`: Maximum requests allowed
  - `X-RateLimit-Remaining`: Remaining requests in current window
  - `X-RateLimit-Reset`: Timestamp when rate limit resets

When rate limit is exceeded, you'll receive a `429 Too Many Requests` response.

---

## Endpoints

### Health Check

#### GET `/api/healthz`

Check if the API is healthy and running.

**Response** (200 OK):
```json
{
  "status": "healthy",
  "timestamp": "2025-11-17T18:00:00Z",
  "version": "1.0.0"
}
```

---

### Analytics

#### POST `/api/analytics/analyze`

Analyze a brand or prompt using AI-powered web intelligence.

**Request Body**:
```json
{
  "prompt": "Analyze Tesla brand visibility in the electric vehicle market"
}
```

**Request Parameters**:
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| prompt | string | Yes | The analysis prompt (max 2000 characters) |

**Response** (200 OK):
```json
{
  "sentiment": {
    "tone": "positive",
    "score": 0.75,
    "summary": "Analysis of 42 sources: 31 positive, 8 neutral, 3 negative mentions"
  },
  "brand_mentions": {
    "count": 42,
    "contexts": ["techcrunch.com", "theverge.com", "electrek.co"],
    "summary": "Found 42 sources mentioning Tesla across web search results"
  },
  "website_coverage": {
    "total_websites_crawled": 42,
    "unique_websites_found": 38,
    "coverage_percentage": "Extensive (35-44 sites)",
    "coverage_quality": "very good",
    "summary": "Analyzed 42 websites with 38 unique domains"
  },
  "trust_score": {
    "ai_recommendations": 0.82,
    "vs_others": 0.76,
    "summary": "AI analysis indicates Tesla has strong market presence based on 42 analyzed sources"
  },
  "analysis_id": "123e4567-e89b-12d3-a456-426614174000"
}
```

**Error Responses**:

- **400 Bad Request**: Invalid input
```json
{
  "detail": "Prompt cannot be empty"
}
```

- **429 Too Many Requests**: Rate limit exceeded
```json
{
  "detail": "Rate limit exceeded. Please try again later."
}
```

- **500 Internal Server Error**: Server error
```json
{
  "detail": "Analysis failed: <error message>"
}
```

---

### Dashboard

#### GET `/api/dashboard/stats`

Get aggregated dashboard statistics.

**Response** (200 OK):
```json
{
  "total_analyses": 150,
  "recent_analyses": [
    {
      "id": "123e4567-e89b-12d3-a456-426614174000",
      "brand_name": "Tesla",
      "created_at": "2025-11-17T18:00:00Z",
      "sentiment": "positive"
    }
  ]
}
```

---

## External Integration Guide

### Plug-and-Play Integration

The Arrakis API is designed to be easily integrated into your existing applications.

#### JavaScript/TypeScript

```typescript
// Using fetch API
async function analyzeBrand(prompt: string) {
  const response = await fetch('http://localhost:8000/api/analytics/analyze', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ prompt }),
  });

  if (!response.ok) {
    throw new Error(`API error: ${response.statusText}`);
  }

  return await response.json();
}

// Usage
const results = await analyzeBrand('Analyze Nike brand visibility');
console.log('Sentiment:', results.sentiment.tone);
console.log('Trust Score:', results.trust_score.ai_recommendations);
```

#### Python

```python
import requests
import json

def analyze_brand(prompt: str) -> dict:
    """Analyze brand using Arrakis API."""
    url = "http://localhost:8000/api/analytics/analyze"
    headers = {"Content-Type": "application/json"}
    data = {"prompt": prompt}

    response = requests.post(url, headers=headers, json=data)
    response.raise_for_status()

    return response.json()

# Usage
results = analyze_brand("Analyze Nike brand visibility")
print(f"Sentiment: {results['sentiment']['tone']}")
print(f"Trust Score: {results['trust_score']['ai_recommendations']}")
```

#### cURL

```bash
curl -X POST http://localhost:8000/api/analytics/analyze \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Analyze Nike brand visibility"}'
```

---

## Best Practices

### 1. Error Handling

Always implement proper error handling:

```typescript
try {
  const results = await analyzeBrand(prompt);
  // Process results
} catch (error) {
  if (error.response?.status === 429) {
    // Handle rate limiting
    console.error('Rate limit exceeded. Retry after:', error.response.headers['retry-after']);
  } else if (error.response?.status === 400) {
    // Handle invalid input
    console.error('Invalid input:', error.response.data.detail);
  } else {
    // Handle other errors
    console.error('Analysis failed:', error.message);
  }
}
```

### 2. Rate Limiting

Respect rate limits to avoid service disruptions:

```typescript
async function analyzeWithRateLimit(prompt: string) {
  const response = await fetch('http://localhost:8000/api/analytics/analyze', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ prompt }),
  });

  // Check rate limit headers
  const remaining = response.headers.get('X-RateLimit-Remaining');
  const resetTime = response.headers.get('X-RateLimit-Reset');

  if (parseInt(remaining) < 10) {
    console.warn(`Only ${remaining} requests remaining. Resets at ${resetTime}`);
  }

  return await response.json();
}
```

### 3. Timeout Handling

Set reasonable timeouts for API calls:

```typescript
const controller = new AbortController();
const timeoutId = setTimeout(() => controller.abort(), 30000); // 30 second timeout

try {
  const response = await fetch('http://localhost:8000/api/analytics/analyze', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ prompt }),
    signal: controller.signal,
  });
  clearTimeout(timeoutId);
  return await response.json();
} catch (error) {
  if (error.name === 'AbortError') {
    console.error('Request timed out');
  }
  throw error;
}
```

### 4. Input Validation

Validate inputs before sending to the API:

```typescript
function validatePrompt(prompt: string): void {
  if (!prompt || prompt.trim().length === 0) {
    throw new Error('Prompt cannot be empty');
  }
  if (prompt.length > 2000) {
    throw new Error('Prompt exceeds maximum length of 2000 characters');
  }
}
```

---

## WebSocket Support (Coming Soon)

Real-time analysis updates via WebSocket connection will be available in a future release.

---

## SDK Libraries (Coming Soon)

Official SDK libraries for popular programming languages:
- JavaScript/TypeScript
- Python
- Go
- Ruby

---

## Support

- **Documentation**: https://github.com/codeshark2/arrakis
- **Issues**: https://github.com/codeshark2/arrakis/issues
- **Email**: support@arrakis.example.com

---

## Changelog

### Version 1.0.0 (2025-11-17)
- Initial API release
- Analytics endpoint for brand analysis
- Rate limiting support
- Dashboard statistics endpoint
