# Contributing to Smart JPEG Renamer

Thank you for considering contributing to Smart JPEG Renamer! This document provides guidelines and information for contributors.

## Development Setup

1. Fork and clone the repository
2. Create a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Set up pre-commit hooks (if available)

## Code Style

- Follow PEP 8 guidelines
- Use type hints for function parameters and return values
- Write docstrings for all functions and classes
- Keep functions focused and under 50 lines when possible
- Use meaningful variable names

## Testing

Before submitting a PR:

1. Run all tests:
   ```bash
   python3 tests/test_naming.py
   python3 tests/test_schema.py
   ```

2. Test the app manually:
   ```bash
   streamlit run app.py
   ```

3. Verify with different scenarios:
   - Small batch (1-5 images)
   - Medium batch (10-20 images)
   - Large batch (50+ images)
   - Images with/without EXIF data
   - All casing styles
   - OCR enabled/disabled

## Project Structure

```
src/
├── ai_client.py      # Gemini API integration
├── caching.py        # Result caching
├── exif_utils.py     # EXIF data handling
├── naming.py         # Filename sanitization
├── ocr_utils.py      # OCR functionality
├── ui.py             # Streamlit components
└── zip_export.py     # Export utilities
```

## Adding Features

### New AI Provider

To add support for a new AI provider (e.g., OpenAI, Anthropic):

1. Create a new client class in `src/ai_client.py`
2. Implement the same interface as `GeminiClient`
3. Add provider selection in settings sidebar
4. Update documentation

### New Export Format

To add a new export format:

1. Add function to `src/zip_export.py`
2. Add button in `src/ui.py`
3. Wire up in `app.py`
4. Update README

### New Naming Rule

To add a new filename transformation:

1. Add function to `src/naming.py`
2. Add tests in `tests/test_naming.py`
3. Add UI control in settings sidebar
4. Update documentation

## Pull Request Process

1. Create a feature branch:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. Make your changes with clear commit messages:
   ```bash
   git commit -m "Add: description of feature"
   ```

3. Push to your fork:
   ```bash
   git push origin feature/your-feature-name
   ```

4. Open a Pull Request with:
   - Clear description of changes
   - Screenshots (if UI changes)
   - Test results
   - Documentation updates

## Bug Reports

When reporting bugs, include:

- Python version
- Operating system
- Streamlit version
- Steps to reproduce
- Error messages/logs
- Screenshots (if applicable)

## Feature Requests

For feature requests, describe:

- Use case / problem to solve
- Proposed solution
- Alternative solutions considered
- Additional context

## Code of Conduct

- Be respectful and inclusive
- Provide constructive feedback
- Focus on what is best for the project
- Show empathy towards others

## Questions?

- Open an issue for general questions
- Check existing issues/PRs first
- Provide context and examples

Thank you for contributing! 🎉

