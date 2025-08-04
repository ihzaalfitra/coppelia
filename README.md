# Coppelia MVP

Multi-Entity Consensus AI System that prevents hallucination cascades through biological-inspired voting mechanisms.

## Quick Start

1. **Setup Environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Configure API Key:**
   ```bash
   cp .env.example .env
   # Edit .env and add your OpenAI API key
   ```

3. **Run Tests:**
   ```bash
   python -m pytest tests/ -v
   ```

## Architecture

- **Safety Validator**: Has veto power, ensures safe operations
- **Logic Checker**: Validates correctness and integration
- **Efficiency Monitor**: Assesses performance and resource usage

## Consensus Formula

```
Final Score = (Safety × 0.5) + (Logic × 0.35) + (Efficiency × 0.15)
```

## Development

Install development dependencies:
```bash
pip install -e ".[dev]"
```

Run code formatting:
```bash
black src/ tests/
```

Type checking:
```bash
mypy src/
```
