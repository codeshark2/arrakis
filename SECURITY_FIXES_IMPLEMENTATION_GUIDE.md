# Security Fixes Implementation Guide

## Overview
This guide provides code examples for implementing the critical security fixes needed for the Arrakis application.

---

## 1. FIX: Missing `execute_raw_sql()` Method

**File**: `/home/user/arrakis/backend/app/supabase/client.py`

**Problem**: The method is called in dashboard.py but never defined.

**Solution**: Add this method to the SupabaseClient class:

```python
async def execute_raw_sql(self, query: str, params: List[Any] = None) -> List[Dict[str, Any]]:
    """Execute a raw SQL query with parameterized parameters."""
    loop = asyncio.get_event_loop()
    try:
        result = await loop.run_in_executor(
            None,
            lambda: self.client.rpc('exec_sql', {
                'query': query,
                'params': params or []
            }).execute()
        )
        return result.data if result.data else []
    except Exception as e:
        raise Exception(f"Failed to execute SQL: {e}")
```

**Better Alternative**: Remove raw SQL entirely and use ORM queries instead.

---

## 2. FIX: Implement JWT Authentication

**File**: `/home/user/arrakis/backend/app/core/security.py` (NEW FILE)

```python
from datetime import datetime, timedelta
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthCredentials
from jose import JWTError, jwt
from pydantic import BaseModel
import os

# Configuration
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

security = HTTPBearer()

class TokenPayload(BaseModel):
    sub: str
    exp: datetime
    user_id: str
    role: str = "user"

class TokenData(BaseModel):
    user_id: str
    username: str
    role: str = "user"

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token."""
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    
    to_encode.update({"exp": expire})
    
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(credentials: HTTPAuthCredentials = Depends(security)) -> TokenData:
    """Validate and extract user from JWT token."""
    token = credentials.credentials
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        return TokenData(
            user_id=user_id,
            username=payload.get("username", ""),
            role=payload.get("role", "user")
        )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

async def get_admin_user(current_user: TokenData = Depends(get_current_user)) -> TokenData:
    """Verify user has admin role."""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions"
        )
    return current_user
```

**File**: `/home/user/arrakis/backend/app/api/analytics.py`

```python
# Add imports
from app.core.security import get_current_user, TokenData, create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES
from datetime import timedelta

# Modify endpoint
@router.post("/analyze", response_model=AnalysisResponse)
async def analyze_prompt(
    request: AnalyzeRequest,
    current_user: TokenData = Depends(get_current_user)  # Add this
):
    """Analyze a prompt using Perplexity AI and store results in database."""
    try:
        logger.info(f"Analysis request from user: {current_user.user_id}")
        # ... rest of the code
```

**File**: `/home/user/arrakis/backend/app/api/dashboard.py`

```python
# Add imports
from app.core.security import get_current_user, TokenData

# Modify endpoint
@router.get("/")
async def get_dashboard_data(
    current_user: TokenData = Depends(get_current_user)  # Add this
) -> Dict[str, Any]:
    """Get comprehensive dashboard data from deep research analysis."""
    try:
        logger.info(f"Dashboard accessed by user: {current_user.user_id}")
        # ... rest of the code
```

---

## 3. FIX: Add Input Validation

**File**: `/home/user/arrakis/backend/app/api/analytics.py`

```python
from pydantic import BaseModel, Field

class AnalyzeRequest(BaseModel):
    # OLD: prompt: str
    # NEW:
    prompt: str = Field(
        ...,
        min_length=1,
        max_length=10000,
        description="The prompt to analyze"
    )
```

**File**: `/home/user/arrakis/backend/app/api/dashboard.py`

```python
# For path parameters, create a validator
from pydantic import Field, validator
import re

class BrandQuery(BaseModel):
    brand_name: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Brand name to analyze"
    )
    
    @validator('brand_name')
    def validate_brand_name(cls, v):
        # Only allow alphanumeric, spaces, hyphens, and periods
        if not re.match(r'^[a-zA-Z0-9\s\-\.]+$', v):
            raise ValueError('Invalid characters in brand name')
        return v

# Update endpoint
@router.get("/brand/{brand_name}")
async def get_brand_dashboard(
    brand_name: str = Field(..., min_length=1, max_length=100),
    current_user: TokenData = Depends(get_current_user)
) -> Dict[str, Any]:
    # Add validation
    if not re.match(r'^[a-zA-Z0-9\s\-\.]+$', brand_name):
        raise HTTPException(status_code=400, detail="Invalid brand name")
    
    # ... rest of code
```

---

## 4. FIX: Add Rate Limiting

**Install dependency**:
```bash
pip install slowapi
```

**File**: `/home/user/arrakis/backend/app/core/middleware.py`

```python
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi import Request
from fastapi.responses import JSONResponse

limiter = Limiter(key_func=get_remote_address)

def setup_rate_limiting(app):
    """Setup rate limiting middleware."""
    @app.exception_handler(RateLimitExceeded)
    async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
        return JSONResponse(
            status_code=429,
            content={"detail": "Rate limit exceeded. Try again later."}
        )
```

**File**: `/home/user/arrakis/backend/app/main.py`

```python
from slowapi import Limiter
from slowapi.util import get_remote_address
from .core.middleware import setup_rate_limiting

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

# Add this after CORS setup
setup_rate_limiting(app)
```

**File**: `/home/user/arrakis/backend/app/api/analytics.py`

```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@router.post("/analyze", response_model=AnalysisResponse)
@limiter.limit("5/minute")  # 5 requests per minute
async def analyze_prompt(
    request: Request,
    analyze_request: AnalyzeRequest,
    current_user: TokenData = Depends(get_current_user)
):
    """Analyze a prompt using Perplexity AI and store results in database."""
    # ... rest of code
```

---

## 5. FIX: Add CSRF Protection

**Install dependency**:
```bash
pip install fastapi-csrf-protect
```

**File**: `/home/user/arrakis/backend/app/core/security.py` (Add to existing file)

```python
from fastapi_csrf_protect import CsrfProtect
from pydantic import BaseModel

class CsrfSettings(BaseModel):
    autouse: bool = True

@CsrfProtect.load_config
def get_csrf_config():
    return CsrfSettings(autouse=True)
```

**File**: `/home/user/arrakis/backend/app/main.py`

```python
from fastapi_csrf_protect import CsrfProtect
from app.core.security import get_csrf_config

@CsrfProtect.load_config
def get_csrf_config():
    return {"secret": os.getenv("SECRET_KEY", "your-secret")}

# Add this before app creation
CsrfProtect.init_csrf(app)
```

**File**: `/home/user/arrakis/backend/app/api/analytics.py`

```python
from fastapi_csrf_protect import CsrfProtect
from fastapi import Request

@router.post("/analyze", response_model=AnalysisResponse)
async def analyze_prompt(
    request: Request,
    analyze_request: AnalyzeRequest,
    current_user: TokenData = Depends(get_current_user),
    csrf_protect: CsrfProtect = Depends()
):
    """Analyze a prompt - requires CSRF token."""
    await csrf_protect.validate_csrf(request)  # Validate CSRF
    # ... rest of code
```

---

## 6. FIX: Add Security Headers

**File**: `/home/user/arrakis/backend/app/core/middleware.py`

```python
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import FastAPI, Request

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        
        # Add security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Content-Security-Policy"] = "default-src 'self'"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        
        return response

def setup_middleware(app: FastAPI):
    """Configure all middleware."""
    app.add_middleware(SecurityHeadersMiddleware)
    app.add_middleware(LoggingMiddleware)
```

---

## 7. FIX: Restrict CORS

**File**: `/home/user/arrakis/backend/app/core/cors.py`

```python
def setup_cors(app):
    """Configure CORS middleware with security."""
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:3000"],  # Specific origins only
        allow_credentials=True,
        allow_methods=["GET", "POST"],  # Only needed methods
        allow_headers=["content-type"],  # Only needed headers
        expose_headers=["content-type"],
        max_age=3600,  # Cache preflight for 1 hour
    )
```

---

## 8. FIX: Frontend Response Validation

**File**: `/home/user/arrakis/frontend/package.json`

```json
{
  "dependencies": {
    "zod": "^4.0.17"
  }
}
```

**File**: `/home/user/arrakis/frontend/app/schemas/analysis.ts` (NEW FILE)

```typescript
import { z } from 'zod';

export const AnalysisResponseSchema = z.object({
  sentiment: z.object({
    tone: z.enum(['positive', 'neutral', 'negative']),
    score: z.number().min(0).max(1),
    summary: z.string().max(500)
  }),
  brand_mentions: z.object({
    count: z.number(),
    contexts: z.array(z.string()),
    summary: z.string().max(1000)
  }),
  website_coverage: z.object({
    total_websites_crawled: z.number(),
    unique_websites_found: z.number(),
    coverage_percentage: z.string(),
    coverage_quality: z.string(),
    summary: z.string().max(1000)
  }),
  trust_score: z.object({
    ai_recommendations: z.number(),
    vs_others: z.number(),
    summary: z.string().max(1000)
  })
});

export type AnalysisResponse = z.infer<typeof AnalysisResponseSchema>;
```

**File**: `/home/user/arrakis/frontend/app/page.tsx`

```typescript
import { AnalysisResponseSchema } from '@/app/schemas/analysis';

const handleAnalyze = async () => {
    if (!prompt.trim()) return;
    
    setIsAnalyzing(true);
    
    try {
      const response = await fetch('http://localhost:8000/api/analytics/analyze', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`  // Add auth token
        },
        body: JSON.stringify({ prompt }),
      });
      
      if (response.ok) {
        const data = await response.json();
        
        // Validate response
        const results = AnalysisResponseSchema.parse(data);
        
        // Use sessionStorage instead of localStorage
        sessionStorage.setItem('analysisResults', JSON.stringify(results));
        router.push('/analysis');
      } else {
        console.error('Analysis failed:', response.statusText);
        alert('Analysis failed. Please try again.');
      }
    } catch (error) {
      console.error('Analysis failed:', error);
      alert('Analysis failed. Please try again.');
    } finally {
      setIsAnalyzing(false);
    }
  };
```

---

## 9. FIX: Environment Configuration

**File**: `/home/user/arrakis/backend/.env.sample` (Update)

```env
# Authentication
SECRET_KEY=your-secret-key-change-in-production
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Supabase Configuration
SUPABASE_URL=your_supabase_url_here
SUPABASE_SERVICE_KEY=your_supabase_service_key_here

# Perplexity AI Configuration
PERPLEXITY_API_KEY=your_perplexity_api_key_here

# Application Configuration
APP_NAME=Arrakis MVP
DEBUG=false
ENVIRONMENT=development

# CORS Origins (comma-separated)
CORS_ORIGINS=http://localhost:3000

# Logging
LOG_LEVEL=INFO
```

---

## 10. FIX: Disable Debug Mode in Production

**File**: `/home/user/arrakis/backend/app/main.py`

```python
# OLD:
app = FastAPI(
    title=settings.app_name,
    description="AI-Powered Brand Intelligence System",
    version="1.0.0",
    debug=settings.debug  # DANGEROUS
)

# NEW:
app = FastAPI(
    title=settings.app_name,
    description="AI-Powered Brand Intelligence System",
    version="1.0.0",
    debug=False if os.getenv("ENVIRONMENT") == "production" else settings.debug,
    docs_url="/docs" if settings.debug else None,  # Disable docs in production
    redoc_url="/redoc" if settings.debug else None
)
```

---

## Implementation Checklist

- [ ] Add JWT authentication module
- [ ] Update analytics endpoint with auth
- [ ] Update dashboard endpoint with auth
- [ ] Add input validation with Pydantic Field
- [ ] Install and configure SlowAPI rate limiting
- [ ] Add rate limiting decorators to endpoints
- [ ] Add security headers middleware
- [ ] Update CORS configuration
- [ ] Create Zod schemas for frontend
- [ ] Update frontend pages with validation
- [ ] Switch from localStorage to sessionStorage
- [ ] Update environment files
- [ ] Test all endpoints with authentication
- [ ] Test rate limiting
- [ ] Test CORS with different origins
- [ ] Security review and penetration testing

---

## Testing Commands

```bash
# Test authentication
curl -X POST http://localhost:8000/api/analytics/analyze \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer invalid-token" \
  -d '{"prompt": "test"}'
# Should return 401 Unauthorized

# Test rate limiting
for i in {1..10}; do
  curl -X POST http://localhost:8000/api/analytics/analyze \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer $TOKEN" \
    -d '{"prompt": "test"}'
done
# Should return 429 Too Many Requests after limit

# Test CSRF
curl -X POST http://localhost:8000/api/analytics/analyze \
  -H "Content-Type: application/json" \
  -d '{"prompt": "test"}'
# Should require CSRF token
```

---

**For detailed explanation of each fix, see `SECURITY_ANALYSIS.md`**
