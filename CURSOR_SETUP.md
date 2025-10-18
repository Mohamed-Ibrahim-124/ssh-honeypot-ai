# Cursor Global Settings Configuration

## Overview
This document explains how to configure Cursor globally for Python development with professional-grade code quality tools.

## Global Settings Location

### Windows
- **User Settings**: `%APPDATA%\Cursor\User\settings.json`
- **Keybindings**: `%APPDATA%\Cursor\User\keybindings.json`

### macOS
- **User Settings**: `~/Library/Application Support/Cursor/User/settings.json`
- **Keybindings**: `~/Library/Application Support/Cursor/User/keybindings.json`

### Linux
- **User Settings**: `~/.config/Cursor/User/settings.json`
- **Keybindings**: `~/.config/Cursor/User/keybindings.json`

## Recommended Global Settings

Add this to your global `settings.json`:

```json
{
    // Python Development
    "python.defaultInterpreterPath": "python",
    "python.terminal.activateEnvironment": true,
    "python.linting.enabled": true,
    "python.linting.mypyEnabled": true,
    "python.linting.banditEnabled": true,
    "python.linting.vultureEnabled": true,
    "python.linting.pylintEnabled": false,
    "python.linting.flake8Enabled": false,
    
    // Ruff Configuration (Updated for native server)
    "ruff.nativeServer": "on",
    "ruff.lineLength": 88,
    "ruff.lint.select": ["E", "F", "W", "I", "B", "C4", "UP", "SIM", "TCH", "TID", "Q", "RUF"],
    
    // Editor Behavior
    "editor.formatOnSave": true,
    "editor.codeActionsOnSave": {
        "source.organizeImports": "explicit",
        "source.fixAll.ruff": "explicit"
    },
    "editor.rulers": [88],
    "editor.wordWrap": "wordWrapColumn",
    "editor.wordWrapColumn": 88,
    
    // File Associations
    "files.associations": {
        "*.py": "python",
        "pyproject.toml": "toml",
        ".pre-commit-config.yaml": "yaml"
    },
    
    // Python Analysis
    "python.analysis.typeCheckingMode": "basic",
    "python.analysis.autoImportCompletions": true,
    "python.analysis.autoSearchPaths": true,
    
    // Terminal
    "terminal.integrated.defaultProfile.windows": "PowerShell",
    "python.terminal.executeInFileDir": false,
    
    // Exclude Patterns
    "files.exclude": {
        "**/__pycache__": true,
        "**/*.pyc": true,
        "**/.pytest_cache": true,
        "**/.mypy_cache": true,
        "**/.ruff_cache": true,
        "**/node_modules": true
    },
    
    "search.exclude": {
        "**/__pycache__": true,
        "**/*.pyc": true,
        "**/.pytest_cache": true,
        "**/.mypy_cache": true,
        "**/.ruff_cache": true,
        "**/node_modules": true
    },
    
    // Git
    "git.ignoreLimitWarning": true,
    
    // Cursor-specific
    "cursor.cpp.disabledLanguages": [],
    "cursor.general.enableCodeActions": true,
    "cursor.chat.enableCodeActions": true
}
```

## Required Extensions

Install these extensions globally in Cursor:

1. **Python** (`ms-python.python`)
2. **Ruff** (`charliermarsh.ruff`)
3. **Mypy Type Checker** (`ms-python.mypy-type-checker`)
4. **Python Docstring Generator** (`njpwerner.autodocstring`)
5. **Python Indent** (`KevinRose.vsc-python-indent`)
6. **Python Test Explorer** (`LittleFoxTeam.vscode-python-test-adapter`)

## Global Python Tools Installation

Install these tools globally on your system:

```bash
# Install globally (recommended for user)
pip install --user ruff mypy bandit vulture pre-commit black isort

# Or install system-wide (requires admin privileges)
pip install ruff mypy bandit vulture pre-commit black isort
```

## Global Configuration Files

### 1. Global pyproject.toml
Create `~/.config/pyproject.toml` (Linux/macOS) or `%APPDATA%\pyproject.toml` (Windows):

```toml
[tool.ruff]
target-version = "py38"
line-length = 88
select = ["E", "W", "F", "I", "B", "C4", "UP", "SIM", "TCH", "TID", "Q", "RUF"]
ignore = ["E501", "B008", "C901", "W191"]

[tool.ruff.per-file-ignores]
"__init__.py" = ["F401"]
"tests/**/*.py" = ["S101", "ARG", "FBT", "PLR2004"]

[tool.mypy]
python_version = "3.8"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
show_error_codes = true

[tool.bandit]
exclude_dirs = ["tests", "test_*", "__pycache__"]
skips = ["B101", "B601"]

[tool.vulture]
min_confidence = 80
```

### 2. Global .pre-commit-config.yaml
Create `~/.config/.pre-commit-config.yaml` (Linux/macOS) or `%APPDATA%\.pre-commit-config.yaml` (Windows):

```yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.1.6
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format
  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.7.1
    hooks:
      - id: mypy
  - repo: https://github.com/PyCQA/bandit
    rev: 1.7.5
    hooks:
      - id: bandit
        args: ['-r', '.']
  - repo: https://github.com/jendrikseipp/vulture
    rev: v2.10
    hooks:
      - id: vulture
```

## Setup Commands

Run these commands to set up everything:

```bash
# Install tools globally
pip install --user ruff mypy bandit vulture pre-commit black isort

# Install pre-commit hooks globally
pre-commit install --install-hooks

# Test the setup
pre-commit run --all-files
```

## Project-Specific Setup

For each new project, simply run:

```bash
# Copy global config to project (optional)
cp ~/.config/pyproject.toml ./pyproject.toml
cp ~/.config/.pre-commit-config.yaml ./.pre-commit-config.yaml

# Install project-specific hooks
pre-commit install
```

## Verification

Test your setup by creating a test file:

```python
# test_setup.py
def hello_world() -> str:
    return "Hello, World!"

if __name__ == "__main__":
    print(hello_world())
```

Then run:
```bash
ruff check test_setup.py
mypy test_setup.py
bandit test_setup.py
vulture test_setup.py
```

## Troubleshooting

### Common Issues

1. **Tools not found**: Ensure Python is in your PATH
2. **Permission errors**: Use `--user` flag with pip install
3. **Extension not working**: Restart Cursor after installing extensions
4. **Settings not applied**: Check file location and JSON syntax

### Reset to Defaults

To reset Cursor settings:
1. Close Cursor
2. Delete the settings.json file
3. Restart Cursor

## Benefits

✅ **Consistent code quality** across all projects  
✅ **Automatic formatting** on save  
✅ **Real-time linting** and error detection  
✅ **Security scanning** with Bandit  
✅ **Dead code detection** with Vulture  
✅ **Type checking** with Mypy  
✅ **Pre-commit hooks** for automated checks  
✅ **Professional development** environment
