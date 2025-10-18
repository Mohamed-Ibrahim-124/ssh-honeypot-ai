# SSH Honeypot Examples

This directory contains example configurations and usage scenarios for the SSH Honeypot.

## Files

- `basic_usage.py` - Basic honeypot usage example
- `custom_config.py` - Custom configuration example
- `docker_example/` - Docker deployment examples
- `api_examples/` - API usage examples

## Quick Start Example

```python
from ssh_honeypot.main import app
import uvicorn

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)
```

## Custom Configuration

```python
from ssh_honeypot.config import settings

# Modify settings
settings.ai_model_name = "microsoft/DialoGPT-medium"
settings.debug = True
settings.log_level = "DEBUG"
```
