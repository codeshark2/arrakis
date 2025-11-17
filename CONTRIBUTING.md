# Contributing to Arrakis

Thank you for your interest in contributing to Arrakis! This document provides guidelines and instructions for contributing to the project.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [How to Contribute](#how-to-contribute)
- [Coding Standards](#coding-standards)
- [Testing Guidelines](#testing-guidelines)
- [Commit Message Guidelines](#commit-message-guidelines)
- [Pull Request Process](#pull-request-process)

## Code of Conduct

This project adheres to a Code of Conduct that all contributors are expected to follow. Please read [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) before contributing.

## Getting Started

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/your-username/arrakis.git
   cd arrakis
   ```
3. **Add the upstream repository**:
   ```bash
   git remote add upstream https://github.com/codeshark2/arrakis.git
   ```

## Development Setup

### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install development dependencies
pip install ruff black pytest pytest-cov

# Copy environment file
cp env.sample .env
# Edit .env with your configuration
```

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Copy environment file
cp env.local.sample .env.local
# Edit .env.local with your configuration
```

### Running Tests

```bash
# Backend tests
cd backend
pytest tests/ -v

# Frontend tests
cd frontend
npm test
```

### Running the Application

```bash
# Terminal 1: Backend
cd backend
source venv/bin/activate
python -m app.main

# Terminal 2: Frontend
cd frontend
npm run dev
```

## How to Contribute

### Reporting Bugs

Before creating bug reports, please check the existing issues to avoid duplicates. When creating a bug report, include:

- **Clear title and description**
- **Steps to reproduce**
- **Expected behavior**
- **Actual behavior**
- **Screenshots** (if applicable)
- **Environment details** (OS, Python/Node version, etc.)

### Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues. When creating an enhancement suggestion, include:

- **Clear title and description**
- **Use case and motivation**
- **Possible implementation approach**
- **Alternative solutions considered**

### Your First Code Contribution

Unsure where to begin? Look for issues tagged with:
- `good first issue` - Good for newcomers
- `help wanted` - Extra attention needed

## Coding Standards

### Python (Backend)

We use **Black** for code formatting and **Ruff** for linting.

```bash
# Format code
black app/

# Lint code
ruff check app/

# Type checking (optional)
mypy app/
```

**Style Guidelines**:
- Follow PEP 8
- Maximum line length: 88 characters (Black default)
- Use type hints for function signatures
- Write docstrings for all public functions and classes
- Use meaningful variable names

**Example**:
```python
def analyze_brand(prompt: str, max_sources: int = 50) -> dict:
    """
    Analyze brand visibility based on prompt.

    Args:
        prompt: Analysis prompt
        max_sources: Maximum number of sources to analyze

    Returns:
        Dictionary containing analysis results

    Raises:
        ValueError: If prompt is empty
    """
    if not prompt:
        raise ValueError("Prompt cannot be empty")
    # Implementation...
```

### TypeScript/JavaScript (Frontend)

We use **ESLint** and **Prettier** for code quality.

```bash
# Lint code
npm run lint

# Type check
npm run type-check
```

**Style Guidelines**:
- Use TypeScript for type safety
- Follow Airbnb style guide
- Use functional components with hooks
- Keep components small and focused
- Use meaningful component and variable names

**Example**:
```typescript
interface AnalysisResult {
  sentiment: SentimentData;
  brandMentions: BrandMentionsData;
}

export function AnalysisCard({ result }: { result: AnalysisResult }) {
  const [isExpanded, setIsExpanded] = useState(false);
  // Implementation...
}
```

## Testing Guidelines

### Backend Tests

- Write tests for all new features
- Aim for >80% code coverage
- Use pytest fixtures for setup
- Mock external API calls

```python
def test_analyze_endpoint_success(client, mock_perplexity):
    """Test successful analysis."""
    response = client.post(
        "/api/analytics/analyze",
        json={"prompt": "Analyze Tesla"}
    )
    assert response.status_code == 200
    assert "sentiment" in response.json()
```

### Frontend Tests

- Write tests for components and utilities
- Use React Testing Library
- Test user interactions
- Mock API calls

```typescript
it('submits analysis on button click', async () => {
  render(<HomePage />);
  const input = screen.getByPlaceholderText(/enter your prompt/i);
  const button = screen.getByRole('button', { name: /analyze/i });

  fireEvent.change(input, { target: { value: 'Test prompt' } });
  fireEvent.click(button);

  await waitFor(() => {
    expect(mockFetch).toHaveBeenCalled();
  });
});
```

## Commit Message Guidelines

We follow the [Conventional Commits](https://www.conventionalcommits.org/) specification.

### Format

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Types

- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

### Examples

```
feat(analytics): add sentiment analysis visualization

Implemented new chart component to display sentiment analysis
results with color-coded indicators.

Closes #123
```

```
fix(api): handle rate limiting errors correctly

Added proper error handling for 429 responses and exponential
backoff retry logic.

Fixes #456
```

## Pull Request Process

1. **Update your fork** with the latest upstream changes:
   ```bash
   git fetch upstream
   git rebase upstream/main
   ```

2. **Create a feature branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Make your changes** and commit them following the commit guidelines

4. **Run tests and linting**:
   ```bash
   # Backend
   cd backend
   pytest tests/
   ruff check app/
   black --check app/

   # Frontend
   cd frontend
   npm test
   npm run lint
   npm run type-check
   ```

5. **Push to your fork**:
   ```bash
   git push origin feature/your-feature-name
   ```

6. **Open a Pull Request** on GitHub with:
   - Clear title and description
   - Reference to related issues
   - Screenshots (for UI changes)
   - Test results

7. **Address review comments** and update your PR as needed

8. **Wait for approval** - PRs require at least one approval before merging

### PR Checklist

- [ ] Code follows project style guidelines
- [ ] Tests added/updated and passing
- [ ] Documentation updated (if needed)
- [ ] Commit messages follow guidelines
- [ ] No merge conflicts
- [ ] CI/CD pipeline passes

## Questions?

Feel free to:
- Open an issue for questions
- Join our discussions
- Reach out to maintainers

Thank you for contributing to Arrakis!
