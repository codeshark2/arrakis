# Arrakis - Spice AI Signal Detection Platform

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![Next.js](https://img.shields.io/badge/Next.js-14+-black.svg)](https://nextjs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green.svg)](https://fastapi.tiangolo.com/)

## 🎯 About Arrakis

**Arrakis** is building the world's most advanced signal detection system for consumer brands, called **Spice**, powered by large language models. Our mission is to help customers understand how they are performing in the AI-driven marketplace.

Every day, thousands of AI-generated answers are produced across the web, and we need to analyze these answers for our customers and communicate actionable insights. This repository contains our prototype backend system and UI that powers this capability.

## 🚀 Project Overview

This prototype demonstrates Arrakis's core technology for:
- **Web Intelligence Gathering**: Automated search and analysis of AI-generated content
- **Signal Detection**: Identifying trends, sentiment, and performance indicators
- **Insight Generation**: Converting raw data into actionable business intelligence
- **Customer Dashboard**: Providing marketers with clear performance insights

## 🏗️ Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Frontend      │    │    Backend       │    │   External      │
│   (Next.js)     │◄──►│   (FastAPI)      │◄──►│   APIs          │
│                 │    │                  │    │                 │
│ • Dashboard     │    │ • Analytics      │    │ • Perplexity AI │
│ • Analysis      │    │ • Web Search     │    │ • Supabase      │
│ • Insights      │    │ • Data Storage   │    │                 │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

### Core Components

- **Frontend**: Modern React-based dashboard built with Next.js 14
- **Backend**: High-performance API server built with FastAPI
- **AI Integration**: Perplexity AI for intelligent web search and analysis
- **Data Storage**: Supabase for scalable data management
- **Real-time Analytics**: Live insights and performance metrics

## 🛠️ Technology Stack

### Backend
- **Python 3.12+** - Core application logic
- **FastAPI** - High-performance web framework
- **Perplexity AI** - Advanced web search and analysis
- **Supabase** - Database and real-time features
- **Pydantic** - Data validation and serialization

### Frontend
- **Next.js 14** - React framework with App Router
- **TypeScript** - Type-safe development
- **Tailwind CSS** - Utility-first styling
- **Lucide React** - Beautiful icons

## 📋 Prerequisites

- Python 3.12 or higher
- Node.js 18 or higher
- npm or yarn package manager
- Perplexity AI API key
- Supabase account and credentials

## 🚀 Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/codeshark2/arrakis.git
cd arrakis
```

### 2. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp env.sample .env
# Edit .env with your API keys and configuration
```

### 3. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Set up environment variables
cp env.local.sample .env.local
# Edit .env.local with your configuration
```

### 4. Database Setup

1. Create a Supabase project at [supabase.com](https://supabase.com)
2. Run the SQL schema from `backend/supabase/sql/000_complete_schema_safe.sql`
3. Update your `.env` file with Supabase credentials

### 5. Run the Application

#### Backend (Terminal 1)
```bash
cd backend
source venv/bin/activate  # or activate on Windows
python -m app.main
```

#### Frontend (Terminal 2)
```bash
cd frontend
npm run dev
```

The application will be available at:
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

## 🔑 Environment Variables

### Backend (.env)
```bash
# Perplexity AI
PERPLEXITY_API_KEY=your_perplexity_api_key

# Supabase
SUPABASE_URL=your_supabase_url
SUPABASE_ANON_KEY=your_supabase_anon_key
SUPABASE_SERVICE_ROLE_KEY=your_supabase_service_role_key

# Application
LOG_LEVEL=INFO
CORS_ORIGINS=http://localhost:3000
```

### Frontend (.env.local)
```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## 📊 Features

### Core Functionality
- **Prompt Analysis**: Submit natural language prompts for analysis
- **Web Intelligence**: Automated search across multiple sources
- **Insight Generation**: AI-powered analysis of search results
- **Performance Metrics**: Sentiment analysis, coverage metrics, and trust scores
- **Real-time Dashboard**: Live updates and performance monitoring

### Analysis Capabilities
- **Sentiment Analysis**: Understanding tone and sentiment of AI-generated content
- **Website Coverage**: Comprehensive analysis across multiple web sources
- **Trust Scoring**: Evaluating source credibility and authority
- **Trend Detection**: Identifying patterns and emerging signals

## 🧪 Testing

### Backend Tests
```bash
cd backend
source venv/bin/activate
pytest tests/ -v
```

### Frontend Tests
```bash
cd frontend
npm test
```

## 📁 Project Structure

```
arrakis/
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── api/            # API endpoints
│   │   ├── core/           # Configuration and middleware
│   │   ├── services/       # Business logic
│   │   └── supabase/       # Database integration
│   ├── requirements.txt     # Python dependencies
│   └── pyproject.toml      # Project configuration
├── frontend/                # Next.js frontend
│   ├── app/                # App Router pages
│   ├── components/         # Reusable components
│   └── package.json        # Node.js dependencies
└── README.md               # This file
```

## 🔧 Development

### Code Style
- **Backend**: Black formatter, Ruff linter
- **Frontend**: ESLint, Prettier
- **Git**: Conventional commits

### Adding New Features
1. Create feature branch: `git checkout -b feature/your-feature`
2. Implement changes with tests
3. Run linting and tests
4. Submit pull request

## 📈 Performance

- **Backend**: FastAPI with async support, sub-second response times
- **Frontend**: Next.js 14 with App Router, optimized bundle size
- **Database**: Supabase with real-time subscriptions
- **AI Integration**: Perplexity AI for high-quality search results

## 🤝 Contributing

We welcome contributions! Please see our contributing guidelines:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Documentation**: [API Docs](http://localhost:8000/docs) (when running)
- **Issues**: [GitHub Issues](https://github.com/codeshark2/arrakis/issues)
- **Discussions**: [GitHub Discussions](https://github.com/codeshark2/arrakis/discussions)

## 🚀 Roadmap

- [ ] Enhanced AI analysis capabilities
- [ ] Multi-language support
- [ ] Advanced reporting and analytics
- [ ] Enterprise features and integrations
- [ ] Mobile application
- [ ] API rate limiting and monitoring

---

**Built by Kshitij**

*Empowering brands with AI-driven insights through Spice - the world's most advanced signal detection system.*
