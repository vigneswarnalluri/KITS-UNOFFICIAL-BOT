# Contributing to KITS Bot

Thank you for your interest in contributing to the KITS Bot project! This document provides guidelines and information for contributors.

## 🤝 How to Contribute

### 1. Fork the Repository
- Click the "Fork" button on the GitHub repository page
- Clone your forked repository to your local machine

### 2. Create a Branch
```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/your-bug-fix
```

### 3. Make Your Changes
- Write clean, readable code
- Follow the existing code style
- Add comments where necessary
- Test your changes thoroughly

### 4. Commit Your Changes
```bash
git add .
git commit -m "Add: Brief description of your changes"
```

### 5. Push and Create Pull Request
```bash
git push origin feature/your-feature-name
```
Then create a pull request on GitHub.

## 📋 Code Style Guidelines

### Python Code Style
- Follow PEP 8 guidelines
- Use meaningful variable and function names
- Add docstrings to functions and classes
- Keep functions small and focused

### Example:
```python
def calculate_attendance(classes_attended: int, total_classes: int) -> float:
    """
    Calculate attendance percentage.
    
    Args:
        classes_attended: Number of classes attended
        total_classes: Total number of classes
        
    Returns:
        Attendance percentage as a float
    """
    if total_classes == 0:
        return 0.0
    return (classes_attended / total_classes) * 100
```

## 🧪 Testing

### Before Submitting
- Test your changes locally
- Ensure all existing tests pass
- Add tests for new functionality
- Check for any linting errors

### Running Tests
```bash
# Install test dependencies
pip install pytest pytest-cov

# Run tests
pytest

# Run with coverage
pytest --cov=.
```

## 📝 Pull Request Guidelines

### PR Title Format
- `Add: New feature description`
- `Fix: Bug description`
- `Update: Improvement description`
- `Remove: Feature removal description`

### PR Description Template
```markdown
## Description
Brief description of what this PR does.

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Tested locally
- [ ] Added tests for new functionality
- [ ] All existing tests pass

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] No sensitive data included
```

## 🐛 Bug Reports

When reporting bugs, please include:

1. **Description**: Clear description of the bug
2. **Steps to Reproduce**: Detailed steps to reproduce the issue
3. **Expected Behavior**: What should happen
4. **Actual Behavior**: What actually happens
5. **Environment**: OS, Python version, dependencies
6. **Logs**: Relevant error messages or logs

### Bug Report Template
```markdown
## Bug Description
[Clear description of the bug]

## Steps to Reproduce
1. Step one
2. Step two
3. Step three

## Expected Behavior
[What should happen]

## Actual Behavior
[What actually happens]

## Environment
- OS: [e.g., Windows 10, Ubuntu 20.04]
- Python Version: [e.g., 3.9.7]
- Bot Version: [e.g., v5.2]

## Logs
```
[Paste relevant logs here]
```
```

## 💡 Feature Requests

When requesting features, please include:

1. **Feature Description**: Clear description of the feature
2. **Use Case**: Why this feature would be useful
3. **Implementation Ideas**: Any ideas on how to implement it
4. **Alternatives**: Any alternative solutions considered

### Feature Request Template
```markdown
## Feature Description
[Clear description of the feature]

## Use Case
[Why this feature would be useful]

## Implementation Ideas
[Any ideas on how to implement it]

## Alternatives Considered
[Any alternative solutions]
```

## 🔒 Security

### Security Guidelines
- Never commit sensitive data (API keys, passwords, tokens)
- Use environment variables for configuration
- Follow secure coding practices
- Report security vulnerabilities privately

### Reporting Security Issues
If you discover a security vulnerability, please:
1. **DO NOT** create a public issue
2. Email the maintainers privately
3. Include detailed information about the vulnerability
4. Wait for acknowledgment before public disclosure

## 📚 Documentation

### Documentation Guidelines
- Update README.md for significant changes
- Add docstrings to new functions
- Update deployment guides if needed
- Include examples in documentation

### Documentation Types
- **Code Documentation**: Docstrings and comments
- **User Documentation**: README.md, DEPLOYMENT.md
- **API Documentation**: Function and class documentation
- **Troubleshooting**: Common issues and solutions

## 🏷️ Issue Labels

We use the following labels for issues:

- `bug`: Something isn't working
- `enhancement`: New feature or request
- `documentation`: Improvements to documentation
- `good first issue`: Good for newcomers
- `help wanted`: Extra attention is needed
- `question`: Further information is requested

## 🎯 Development Setup

### Prerequisites
- Python 3.8+
- Git
- Telegram Bot Token
- Telegram API credentials

### Setup Steps
1. Clone the repository
2. Create a virtual environment
3. Install dependencies
4. Set up environment variables
5. Run the bot locally

```bash
# Clone repository
git clone https://github.com/your-username/IARE-BOT-V5.2.git
cd IARE-BOT-V5.2

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp env.example .env
# Edit .env with your values

# Run the bot
python main.py
```

## 📞 Getting Help

### Community Support
- Create an issue for bugs or feature requests
- Join discussions in issues
- Check existing issues before creating new ones

### Contact Maintainers
- Use GitHub issues for public discussions
- Email for private security issues
- Telegram for urgent matters (if available)

## 🎉 Recognition

Contributors will be recognized in:
- README.md contributors section
- Release notes
- GitHub contributors page

Thank you for contributing to KITS Bot! 🚀
