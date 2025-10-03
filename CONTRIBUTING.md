# Contributing to FlashVideoBot

Thank you for your interest in contributing to FlashVideoBot! We welcome contributions from everyone.

## 🤝 How to Contribute

### Reporting Issues
- Use GitHub Issues to report bugs or request features
- Search existing issues before creating new ones
- Provide clear descriptions and steps to reproduce bugs
- Include system information (OS, Python version, etc.)

### Development Setup

1. **Fork and Clone**
   ```bash
   git clone https://github.com/YourUsername/FlashVideoBot.git
   cd FlashVideoBot
   ```

2. **Set up Environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Test Installation**
   ```bash
   python quickstart.py
   ```

### Making Changes

1. **Create a Branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Follow Code Style**
   - Use meaningful variable and function names
   - Add docstrings to all functions and classes
   - Follow PEP 8 style guidelines
   - Keep functions focused and under 50 lines when possible

3. **Write Tests**
   - Add tests for new functionality
   - Run existing tests to ensure nothing breaks
   - Use the `test_examples.py` as a starting point

4. **Update Documentation**
   - Update README.md if adding new features
   - Add docstrings and comments for complex code
   - Update configuration examples if needed

### Submitting Changes

1. **Commit Messages**
   ```
   feat: add support for custom video templates
   fix: resolve image caching issue
   docs: update installation instructions
   refactor: improve video creation performance
   test: add unit tests for news fetcher
   ```

2. **Push and Create PR**
   ```bash
   git push origin feature/your-feature-name
   ```
   - Create a Pull Request on GitHub
   - Provide a clear description of changes
   - Link related issues

## 🎯 Contribution Areas

### High Priority
- **Performance Optimization**: Improve video generation speed
- **Error Handling**: Better error messages and recovery
- **Documentation**: More examples and tutorials
- **Testing**: Increase test coverage

### Medium Priority
- **New Features**: Additional video effects and transitions
- **API Integration**: Support for more news sources
- **Configuration**: More customization options
- **Internationalization**: Multi-language support

### Good First Issues
- **Bug Fixes**: Small, well-defined issues
- **Documentation**: Fix typos, improve clarity
- **Code Quality**: Refactoring and cleanup
- **Examples**: Add more usage examples

## 📝 Code Guidelines

### Python Style
```python
# Good: Clear, descriptive names
async def fetch_latest_news(self) -> List[Article]:
    """Fetch the latest news articles from configured sources."""
    pass

# Good: Proper error handling
try:
    result = await api_call()
except APIError as e:
    logger.error(f"API call failed: {e}")
    return fallback_result()
```

### Documentation
```python
def create_video(self, article: Dict[str, Any], images: List[str]) -> Optional[str]:
    """
    Create a video from an article and images.
    
    Args:
        article: Article data with title, content, etc.
        images: List of image file paths
        
    Returns:
        Path to created video file, or None if creation failed
        
    Raises:
        VideoCreationError: If video processing fails
    """
```

### Configuration
- Use type hints for all function parameters and returns
- Add configuration options to `config.yaml` with sensible defaults
- Validate configuration values and provide helpful error messages

## 🧪 Testing

### Running Tests
```bash
# Run all tests
python test_examples.py

# Test specific component
python -c "from test_examples import test_news_fetcher; test_news_fetcher()"

# Quick integration test
python quickstart.py
```

### Writing Tests
```python
async def test_news_fetcher():
    """Test news fetching functionality."""
    config = ConfigManager().get_config()
    fetcher = NewsFetcher(config)
    
    articles = await fetcher.fetch_latest_news()
    assert len(articles) > 0
    assert 'title' in articles[0]
    assert 'content' in articles[0]
```

## 🔄 Review Process

1. **Automated Checks**: Code passes basic linting and tests
2. **Manual Review**: Maintainer reviews code quality and design
3. **Testing**: Changes are tested in different environments
4. **Documentation**: Changes are documented appropriately
5. **Merge**: Changes are merged into main branch

## 🆘 Getting Help

- **GitHub Discussions**: For questions and ideas
- **GitHub Issues**: For bugs and feature requests
- **Documentation**: Check README.md and code comments
- **Examples**: See `quickstart.py` and `test_examples.py`

## 📋 Checklist for Contributors

Before submitting a PR, ensure:

- [ ] Code follows project style guidelines
- [ ] All tests pass
- [ ] New features have tests
- [ ] Documentation is updated
- [ ] Commit messages are clear
- [ ] No sensitive information (API keys) in code
- [ ] Dependencies are justified and minimal

## 🏆 Recognition

Contributors will be:
- Listed in the project README
- Thanked in release notes
- Given credit for their specific contributions

## 📜 License

By contributing to FlashVideoBot, you agree that your contributions will be licensed under the MIT License.

---

**Thank you for helping make FlashVideoBot better!** 🚀