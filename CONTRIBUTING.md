# Contributing to Claude Market System

Thank you for your interest in contributing! This document provides guidelines for contributing to this project.

## Getting Started

1. Fork the repository
2. Clone your fork: `git clone https://github.com/YOUR_USERNAME/claude-market-system.git`
3. Create a virtual environment: `python -m venv venv && source venv/bin/activate`
4. Install dependencies: `pip install -r requirements.txt`
5. Create a feature branch: `git checkout -b feature/your-feature-name`

## Development Workflow

### Running Tests

```bash
# Test individual components
python signals/run_signals.py
python scanner/demo_scanner.py
python analyst/test_financials.py

# Test with limited scope
python run_analysis.py --signals-only
```

### Code Style

- Follow PEP 8 style guidelines
- Use meaningful variable and function names
- Add docstrings to functions and classes
- Keep functions focused and modular

### Commit Messages

Use clear, descriptive commit messages:

```
Add momentum factor to L2 scanner

- Implement EMA crossover detection
- Add 3-month return calculation
- Update tests for new factor
```

## Types of Contributions

### 1. Adding New Signals (L1)

Create a new signal file in `signals/`:

```python
# signals/new_signal.py
def calculate_new_signal_score() -> dict:
    """
    Calculate new signal score (0-100).
    
    Returns:
        dict: {
            'score': float (0-100),
            'signal_name': str,
            'timestamp': str,
            # Additional metrics...
        }
    """
    # Implementation
    pass
```

Then add to `signals/run_signals.py`.

### 2. Adding New Factors (L2)

Create a new factor file in `scanner/factors/`:

```python
# scanner/factors/new_factor.py
def calculate_new_factor_score(ticker: str, data: pd.DataFrame) -> dict:
    """
    Calculate new factor score for a ticker.
    
    Args:
        ticker: Stock ticker symbol
        data: DataFrame with OHLCV data
        
    Returns:
        dict: {
            'ticker': str,
            'score': float (0-100),
            'factor_name': str,
            # Additional metrics...
        }
    """
    # Implementation
    pass
```

### 3. Improving Dashboard

- Add new visualizations to existing pages
- Create new dashboard pages
- Improve UI/UX
- Add interactivity

### 4. Documentation

- Improve README clarity
- Add code comments
- Create tutorials
- Add examples

### 5. Bug Fixes

- Report bugs via GitHub Issues
- Include reproduction steps
- Provide error messages
- Submit fixes via Pull Request

## Pull Request Process

1. **Update Documentation**: If your change affects usage, update README.md
2. **Test Thoroughly**: Ensure your changes don't break existing functionality
3. **One Feature Per PR**: Keep pull requests focused on a single feature or fix
4. **Describe Changes**: Provide a clear description of what changed and why
5. **Reference Issues**: If fixing a bug, reference the issue number

### PR Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Performance improvement

## Testing
How has this been tested?

## Checklist
- [ ] Code follows project style guidelines
- [ ] Documentation updated
- [ ] Tests pass
- [ ] No breaking changes (or documented if necessary)
```

## Code Review Process

- Maintainers will review PRs as time permits
- Be patient and responsive to feedback
- Make requested changes in new commits
- Once approved, maintainers will merge

## Areas for Contribution

### High Priority

- [ ] Add more macro signals to L1
- [ ] Implement real short interest data for L2
- [ ] Add sector/industry analysis
- [ ] Improve error handling and logging
- [ ] Add unit tests
- [ ] Performance optimizations

### Medium Priority

- [ ] Add more scanner factors
- [ ] Implement backtesting framework
- [ ] Add alert/notification system
- [ ] Create Jupyter notebook examples
- [ ] Add data export features

### Nice to Have

- [ ] Mobile-friendly dashboard
- [ ] Historical performance tracking
- [ ] Integration with other data sources
- [ ] Alternative AI models (GPT-4, etc.)
- [ ] Docker containerization

## Questions?

Feel free to open an issue with the `question` label if you need help or clarification.

## Code of Conduct

- Be respectful and inclusive
- Provide constructive feedback
- Help others learn and grow
- Focus on what's best for the project

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
