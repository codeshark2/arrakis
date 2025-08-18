# Arrakis - AI-Powered Brand Intelligence System

## 🚀 Overview

Arrakis is a comprehensive AI-powered brand intelligence system that provides deep research analysis using Perplexity AI's `sonar-deep-research` model. The system crawls 5 unique URLs and provides detailed analysis across 4 key dimensions with reasoning.

## ✨ Features

### **🎯 5-URL Deep Research Strategy**
- **Main Prompt**: Analyzes the primary query
- **4 Generated Queries**: Automatically generates relevant search queries covering:
  1. Brand performance and market position
  2. Customer sentiment and reviews  
  3. Competitive landscape and positioning
  4. Industry reputation and authority

### **🔍 4-Point Analysis with Reasoning**

#### 1. **Sentiment Analysis**
- Positive, neutral, or negative tone with percentages
- Detailed reasoning for sentiment classification
- Aggregated sentiment across all URLs

#### 2. **Brand Mention Tracking**
- Count of brand mentions per URL
- Context analysis (where/how brand is mentioned)
- Frequency and diversity metrics
- Reasoning for mention patterns

#### 3. **Competitor Analysis**
- Identification of competitors mentioned alongside the brand
- Favorability scores (-1.0 to 1.0) for each competitor
- Detailed reasoning for competitive positioning
- Aggregated competitor insights across URLs

#### 4. **Trust/Authority Score**
- AI recommendation score (0-100)
- Brand authority vs. others (0-100)
- Detailed reasoning for trust assessment
- Confidence level based on analysis depth

## 🏗️ System Architecture

### **Backend (FastAPI)**
```
backend/
├── app/
│   ├── api/
│   │   ├── deep_research_analytics.py    # NEW: Deep research endpoints
│   │   ├── dashboard.py                  # Dashboard data API
│   │   ├── analytics.py                  # Legacy analytics (for reference)
│   │   ├── runs.py                       # Run management
│   │   ├── brands.py                     # Brand management
│   │   ├── evidence.py                   # Evidence tracking
│   │   ├── prompts.py                    # Prompt management
│   │   └── health.py                     # Health checks
│   ├── services/
│   │   ├── deep_research_perplexity_client.py    # NEW: Deep research client
│   │   ├── deep_research_storage.py              # NEW: Database storage
│   │   ├── ai_analyzer.py                        # Legacy analyzer
│   │   ├── perplexity_client.py                  # Legacy client
│   │   ├── jobs.py                               # Job management
│   │   └── judge/                                # AI judge system
│   ├── core/                                     # Configuration & middleware
│   ├── schemas/                                  # Data models
│   └── supabase/                                 # Database client
├── supabase/sql/
│   └── 000_complete_schema_safe.sql             # Complete database schema
├── dev.py                                        # Main server startup
├── requirements.txt                               # Python dependencies
└── pyproject.toml                                # Project configuration
```

### **Frontend (Next.js)**
```
frontend/
├── app/
│   ├── page.tsx                                 # Home page with analysis form
│   ├── dashboard/page.tsx                       # NEW: Comprehensive dashboard
│   ├── analysis/page.tsx                        # Analysis results display
│   ├── layout.tsx                               # Layout with navigation
│   └── api/dashboard/route.ts                   # Frontend API route
├── components/
│   └── Navigation.tsx                           # NEW: Top navigation
├── package.json                                  # Node.js dependencies
└── tailwind.config.js                           # Styling configuration
```

## 🗄️ Database Schema

### **New Tables Created**

#### `deep_research_analysis`
- Main analysis results
- Aggregated metrics across all URLs
- Sentiment percentages and trust scores
- JSON storage for raw data

#### `url_analysis_results`
- Individual URL analysis
- Detailed reasoning for each analysis point
- Raw response data and usage statistics

#### `competitor_mentions`
- Aggregated competitor data
- Favorability scores and mention counts
- URLs where competitors were mentioned

## 🚀 Quick Start

### **1. Backend Setup**
```bash
cd backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp env.sample .env
# Edit .env with your API keys

# Run database migration
psql -h <host> -U <user> -d <db> -f supabase/sql/000_complete_schema_safe.sql

# Start the server
python3 dev.py
```

### **2. Frontend Setup**
```bash
cd frontend

# Install dependencies
npm install

# Set up environment variables
cp env.local.sample .env.local
# Edit .env.local with your backend URL

# Start development server
npm run dev
```

### **3. Access the System**
- **Frontend**: http://localhost:3000
- **Backend**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

## 🔌 API Endpoints

### **Deep Research Analytics (`/api/deep-research`)**

#### **Start Analysis**
```http
POST /api/deep-research/analyze
```
Starts comprehensive deep research analysis:
- Generates 4 additional relevant search queries
- Crawls 5 unique URLs (1 main + 4 generated)
- Performs deep research analysis on each URL
- Stores results in new database tables

#### **Check Status**
```http
GET /api/deep-research/status/{run_id}
```
Returns current status and progress (4 steps).

#### **Get Results**
```http
GET /api/deep-research/results/{run_id}
```
Returns complete analysis results once processing is complete.

### **Dashboard API (`/api/dashboard`)**
```http
GET /api/dashboard                    # Main dashboard data
GET /api/dashboard/brand/{brand_name} # Brand-specific data
```

## 💰 Cost Analysis

### **Perplexity API Costs (Estimated)**
- **sonar model**: ~$0.005 per query (5 queries = $0.025)
- **sonar-deep-research model**: ~$0.322 per analysis (5 analyses = $1.61)
- **Total per brand analysis**: ~$1.64

### **Cost vs. Value**
- **Traditional approach**: Basic search results, limited insights
- **Deep research approach**: 
  - Full content extraction (26K+ characters per URL)
  - Detailed reasoning for all analysis points
  - Structured data ready for database storage
  - Comprehensive competitive intelligence

## 🔄 User Flow

### **Complete Analysis Process**
```
1. User enters prompt on home page
2. System calls /api/deep-research/analyze
3. Background job starts with 4 steps:
   - Step 1: Start analysis
   - Step 2: Generate queries + crawl 5 URLs
   - Step 3: Store results in database
   - Step 4: Complete
4. Dashboard shows real-time progress
5. Results automatically appear when complete
6. Data stored in new deep research tables
```

### **What Happens Behind the Scenes**
- **Query Generation**: AI generates 4 relevant search queries
- **URL Crawling**: Top URL from each query gets analyzed
- **Deep Research**: sonar-deep-research model analyzes each URL
- **Data Storage**: All results stored in structured database tables
- **Real-time Updates**: Dashboard shows progress and results

## 🎨 Frontend Features

### **Dashboard Components**
- **Key Metrics Tiles**: Total analyses, sentiment percentages, trust scores
- **Recent Analyses**: Latest deep research results with sentiment indicators
- **Sentiment Overview**: Visual breakdown of sentiment types
- **Top Performing Brands**: Ranked by trust score
- **Real-time Progress**: Live updates for ongoing analysis

### **Navigation System**
- **Top navigation bar** with Arrakis branding
- **Active page highlighting** for better UX
- **Responsive design** for all device sizes
- **Smooth transitions** between pages

## 🔧 Configuration

### **Environment Variables**

#### **Backend (.env)**
```bash
# Supabase
SUPABASE_URL=your_supabase_url
SUPABASE_ANON_KEY=your_supabase_anon_key
SUPABASE_SERVICE_ROLE_KEY=your_service_role_key

# OpenAI
OPENAI_API_KEY=your_openai_api_key

# Perplexity AI
PERPLEXITY_API_KEY=your_perplexity_api_key
PPLX_TARGET_SITES=5  # Set to 5 for deep research system

# Application
APP_NAME=Arrakis
DEBUG=true
```

#### **Frontend (.env.local)**
```bash
NEXT_PUBLIC_BACKEND_URL=http://localhost:8000
NEXT_PUBLIC_APP_NAME=Arrakis
```

## 📊 Data Output Structure

### **Analysis Summary**
```json
{
  "brand_name": "Tesla",
  "analysis_summary": {
    "total_urls_analyzed": 5,
    "overall_sentiment": {
      "tone": "positive",
      "positive_percentage": 65.2,
      "neutral_percentage": 25.8,
      "negative_percentage": 9.0
    },
    "brand_mentions": {
      "total_count": 47,
      "average_per_url": 9.4
    },
    "trust_authority": {
      "overall_score": 78.5,
      "confidence_level": "high"
    }
  }
}
```

### **Detailed URL Analysis**
```json
{
  "url": "https://example.com/article",
  "sentiment_analysis": {
    "overall_tone": "positive",
    "positive_percentage": 70.0,
    "reasoning": "Article emphasizes innovation and market leadership..."
  },
  "brand_mention_tracking": {
    "mention_count": 12,
    "contexts": ["innovation", "market position", "customer satisfaction"],
    "reasoning": "Brand mentioned frequently in positive contexts..."
  }
}
```

## 🚀 Development

### **Adding New Features**
1. **Backend**: Add new services in `app/services/`
2. **API**: Create new endpoints in `app/api/`
3. **Database**: Add new tables via migration scripts
4. **Frontend**: Create new components in `components/`

### **Testing**
```bash
# Backend tests
cd backend
python -m pytest

# Frontend tests
cd frontend
npm test
```

### **Building for Production**
```bash
# Backend
cd backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000

# Frontend
cd frontend
npm run build
npm start
```

## 🔒 Security & Performance

### **Security Features**
- **Input validation** on all forms
- **XSS protection** via Next.js
- **CSRF protection** built-in
- **Secure API calls** to backend

### **Performance Optimizations**
- **Background job processing** for analysis
- **Real-time progress updates** via polling
- **Efficient database queries** with proper indexing
- **Code splitting** via Next.js App Router

## 🐛 Troubleshooting

### **Common Issues**
1. **API Key Missing**: Ensure all API keys are set in `.env`
2. **Database Errors**: Verify migration script was applied
3. **Frontend Build Errors**: Ensure `lucide-react` is installed
4. **Analysis Failures**: Check Perplexity API quota and rate limits

### **Debug Information**
- Comprehensive logging throughout the system
- Real-time status updates in dashboard
- Detailed error messages and stack traces
- API documentation at `/docs` endpoint

## 📚 Dependencies

### **Backend (Python)**
- **FastAPI**: Web framework
- **OpenAI**: GPT-4o integration
- **Supabase**: Database and storage
- **Pydantic**: Data validation
- **Uvicorn**: ASGI server

### **Frontend (Node.js)**
- **Next.js 14**: React framework
- **TypeScript**: Type safety
- **Tailwind CSS**: Styling
- **Lucide React**: Icons

## 🔄 Updates & Maintenance

### **Regular Updates**
- Keep dependencies updated
- Monitor API quotas and costs
- Update database schema as needed
- Maintain responsive design standards

### **Performance Monitoring**
- Track analysis completion times
- Monitor API response times
- Optimize database queries
- Implement caching strategies

## 🎯 Future Enhancements

### **Planned Features**
- **Batch Processing**: Analyze multiple brands simultaneously
- **Historical Tracking**: Compare analysis over time
- **Alert System**: Notify on significant sentiment changes
- **Export Capabilities**: CSV/Excel report generation
- **User Authentication**: Multi-user support
- **API Rate Limiting**: Advanced quota management

---

## 🎉 Getting Started

1. **Clone the repository**
2. **Set up environment variables**
3. **Run database migration**
4. **Start backend server** (`python3 dev.py`)
5. **Start frontend server** (`npm run dev`)
6. **Access the system** at http://localhost:3000

**Welcome to Arrakis - Your AI-Powered Brand Intelligence Platform!** 🚀

For support or questions, check the API documentation at http://localhost:8000/docs when the backend is running.
