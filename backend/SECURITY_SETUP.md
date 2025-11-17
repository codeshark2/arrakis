# Arrakis Security Setup Guide

This guide provides instructions for securing the Arrakis platform.

## 1. Database Security (Supabase)

### Row Level Security (RLS)

To properly secure your Supabase database, you need to enable Row Level Security and configure appropriate policies.

#### Enable RLS on Tables

Run these SQL commands in your Supabase SQL editor:

```sql
-- Enable RLS on all tables
ALTER TABLE deep_research_analysis ENABLE ROW LEVEL SECURITY;
ALTER TABLE url_analysis_results ENABLE ROW LEVEL SECURITY;
ALTER TABLE competitor_mentions ENABLE ROW LEVEL SECURITY;

-- Create a user_id column if not exists (for multi-tenant support)
-- ALTER TABLE deep_research_analysis ADD COLUMN user_id UUID REFERENCES auth.users(id);

-- Create RLS policies for authenticated users
-- Policy: Users can read all analyses (adjust based on your needs)
CREATE POLICY "Public read access" ON deep_research_analysis
  FOR SELECT USING (true);

-- Policy: Users can insert their own analyses
CREATE POLICY "Authenticated insert" ON deep_research_analysis
  FOR INSERT WITH CHECK (auth.role() = 'authenticated');

-- Policy: Users can only update their own analyses
-- CREATE POLICY "Users can update own analyses" ON deep_research_analysis
--   FOR UPDATE USING (auth.uid() = user_id);

-- Similar policies for other tables
CREATE POLICY "Public read url analysis" ON url_analysis_results
  FOR SELECT USING (true);

CREATE POLICY "Authenticated insert url analysis" ON url_analysis_results
  FOR INSERT WITH CHECK (auth.role() = 'authenticated');

CREATE POLICY "Public read competitor mentions" ON competitor_mentions
  FOR SELECT USING (true);

CREATE POLICY "Authenticated insert competitor mentions" ON competitor_mentions
  FOR INSERT WITH CHECK (auth.role() = 'authenticated');
```

### Switch from Service Key to Anon Key

**Current Issue:** The application uses `SUPABASE_SERVICE_KEY` which bypasses Row Level Security.

**Solution:**

1. Update your `.env` file:
   ```env
   # Replace this:
   SUPABASE_KEY=your_service_role_key_here

   # With this:
   SUPABASE_KEY=your_anon_key_here
   ```

2. Update `backend/app/core/config.py` if needed to use the anon key.

3. For operations that require elevated privileges, use the service key only in specific admin functions, not for all database operations.

## 2. API Key Configuration

### Generate API Keys

1. Generate a secure API key:
   ```bash
   python -c "import secrets; print(secrets.token_urlsafe(32))"
   ```

2. Add to your `.env` file:
   ```env
   ARRAKIS_API_KEY=<generated-key>
   ```

3. Share this key with frontend applications or API consumers.

### Protecting Endpoints

To protect an endpoint with API key authentication, use the dependency:

```python
from fastapi import Depends
from app.core.auth import verify_api_key_dependency

@router.post("/analyze", dependencies=[Depends(verify_api_key_dependency)])
async def analyze_prompt(request: AnalyzeRequest):
    # Your endpoint code
    pass
```

## 3. Environment Variables

### Required Environment Variables

Create a `.env` file in the `backend/` directory:

```env
# Supabase Configuration
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your_anon_key_here  # Use ANON key, not SERVICE key

# API Keys for External Services
PERPLEXITY_API_KEY=your_perplexity_api_key
OPENAI_API_KEY=your_openai_api_key  # Optional

# Application Configuration
DEBUG=false  # Set to false in production
PPLX_TARGET_SITES=25  # Number of sites to analyze

# API Authentication
ARRAKIS_API_KEY=<your-generated-api-key>

# CORS Configuration (comma-separated list)
CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

# Optional: For production logging
LOG_LEVEL=INFO
```

### Frontend Environment Variables

Create a `.env.local` file in the `frontend/` directory:

```env
# API Configuration
NEXT_PUBLIC_API_BASE=https://api.yourdomain.com

# API Key for authentication
NEXT_PUBLIC_API_KEY=<your-api-key>
```

## 4. CORS Configuration

Update `backend/app/core/config.py` to restrict CORS origins in production:

```python
cors_origins: list[str] = [
    "https://yourdomain.com",
    "https://www.yourdomain.com"
]
```

## 5. Rate Limiting

Rate limits are automatically enforced by the middleware:

- `/api/analytics/analyze`: 10 requests per minute per IP
- `/api/dashboard/*`: 60 requests per minute per IP

To modify rate limits, update `backend/app/core/security.py`:

```python
class RateLimitConfig:
    ANALYZE_ENDPOINT_LIMIT = 10  # Adjust as needed
    DASHBOARD_ENDPOINT_LIMIT = 60
```

## 6. Security Headers

Add security headers in production (configure in reverse proxy/CDN):

```
Content-Security-Policy: default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval'; style-src 'self' 'unsafe-inline';
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
X-XSS-Protection: 1; mode=block
Strict-Transport-Security: max-age=31536000; includeSubDomains
```

## 7. Production Deployment Checklist

Before deploying to production:

- [ ] Set `DEBUG=false` in environment variables
- [ ] Use HTTPS/TLS for all connections
- [ ] Switch from service key to anon key in Supabase config
- [ ] Enable Row Level Security on all database tables
- [ ] Configure production CORS origins
- [ ] Generate and configure strong API keys
- [ ] Set up proper logging and monitoring
- [ ] Configure rate limits based on expected traffic
- [ ] Enable security headers in reverse proxy/CDN
- [ ] Rotate all API keys and secrets
- [ ] Set up database backups
- [ ] Configure alerts for rate limit violations
- [ ] Review and test all security policies

## 8. Monitoring and Logging

### Security Event Logging

The application logs security events including:
- Rate limit violations
- Invalid API key attempts
- Failed authentication attempts
- Suspicious input patterns

Monitor logs for:
```bash
# Watch for security events
tail -f app.log | grep -E "Rate limit|Invalid API key|validation failed"
```

### Recommended Monitoring

Set up monitoring for:
1. Failed authentication attempts (> 10 per minute from same IP)
2. Rate limit violations (indicates potential DoS attack)
3. Unusual API usage patterns
4. Database query performance
5. External API costs (Perplexity AI)

## 9. Secrets Rotation

Regularly rotate sensitive credentials:

1. **API Keys**: Rotate every 90 days
   ```bash
   # Generate new key
   python -c "import secrets; print(secrets.token_urlsafe(32))"
   ```

2. **Database Credentials**: Rotate via Supabase dashboard

3. **External API Keys**: Rotate via provider dashboards

## 10. Incident Response

If you suspect a security breach:

1. Immediately rotate all API keys
2. Review application logs for suspicious activity
3. Check database for unauthorized access
4. Disable compromised accounts
5. Notify affected users if data was exposed
6. Document the incident and response

## Additional Resources

- [Supabase Row Level Security](https://supabase.com/docs/guides/auth/row-level-security)
- [FastAPI Security](https://fastapi.tiangolo.com/tutorial/security/)
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
