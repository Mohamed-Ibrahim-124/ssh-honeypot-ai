# SSH Honeypot with AI-Powered Terminal Emulation

A sophisticated SSH honeypot that uses AI to generate realistic terminal responses, designed to detect and analyze malicious activity. This project demonstrates modern Python development with FastAPI, AI integration, and cybersecurity principles.

## 🚀 Features

- **🤖 AI-Powered Responses**: Uses Hugging Face transformers to generate realistic Linux terminal outputs
- **🛡️ Threat Detection**: Real-time analysis of malicious commands and attack patterns
- **📊 Session Management**: Comprehensive tracking of attacker sessions and behavior
- **🔍 Analytics Dashboard**: Monitor threats, sessions, and attack statistics
- **⚡ Modern Architecture**: Clean FastAPI-based design with async programming
- **📝 Comprehensive Logging**: Structured logging for security analysis

## 🏗️ Architecture

```
ssh_honeypot/
├── main.py              # FastAPI application entry point
├── config.py            # Configuration management
├── core/
│   └── honeypot.py      # Core honeypot logic & threat analysis
├── services/
│   ├── ai_service.py    # LLM integration for realistic responses
│   ├── honeypot_service.py # Main business logic
│   ├── session_service.py  # Session management
│   └── service_manager.py  # Singleton service management
├── routers/
│   ├── honeypot.py      # SSH command endpoints
│   ├── analytics.py     # Threat analytics & reporting
│   └── health.py        # Health check endpoints
├── models/
│   └── schemas.py       # Pydantic data models
├── utils/
│   ├── helpers.py       # Utility functions
│   └── logging.py      # Logging configuration
├── tests/               # Test files
├── examples/            # Usage examples
├── docs/               # Documentation
├── scripts/            # Development scripts
└── logs/               # Log files (gitignored)
```

## 🛠️ Tech Stack

- **Backend**: FastAPI, Pydantic, Uvicorn
- **AI/ML**: Hugging Face Transformers (DialoGPT)
- **Database**: SQLite (easily configurable for PostgreSQL)
- **Logging**: Structured logging with configurable levels
- **Architecture**: Clean architecture with dependency injection

## 📋 Prerequisites

- Python 3.11+
- pip (Python package manager)
- Git

## 🚀 Quick Start

### 1. Clone the Repository
```bash
git clone https://github.com/Mohamed-Ibrahim-124/ssh-honeypot.git
cd ssh-honeypot
```

### 2. Create Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Configure Environment (Optional)
```bash
# Copy environment template
cp env.example .env

# Edit .env file with your settings
# AI_MODEL_NAME=microsoft/DialoGPT-small
# AI_MODEL_DEVICE=auto
# DEBUG=false
```

### 4. Install Dependencies
```bash
pip install -r requirements.txt
```

### 5. Run the Application
```bash
python run.py
```

The honeypot will be available at `http://localhost:8080`

## 📖 Usage

### Basic Commands
The honeypot responds to common Linux commands:

```bash
# List directory contents
$ ls
bin  etc  home  usr  var  Documents  Downloads

# Show current directory
$ pwd
/home/admin

# Display user information
$ who
admin    pts/0        2025-10-19 00:58 (127.0.0.1)

# Show system users
$ cat /etc/passwd
root:x:0:0:root:/root:/bin/bash
daemon:x:1:1:daemon:/usr/sbin:/usr/sbin/nologin
admin:x:1000:1000:admin:/home/admin:/bin/bash

# Unknown commands show realistic errors
$ unknown_command
bash: unknown_command: command not found
```

### API Endpoints

- `POST /api/v1/command` - Execute commands
- `GET /api/v1/sessions` - View active sessions
- `GET /api/v1/analytics/threats` - Threat analysis
- `GET /api/v1/analytics/stats` - Statistics
- `GET /health` - Health check

## 🔧 Configuration

Edit `ssh_honeypot/config.py` or use environment variables:

### Environment Variables
Copy `env.example` to `.env` and customize:

```bash
# AI Model Configuration
AI_MODEL_NAME=microsoft/DialoGPT-small
AI_MODEL_DEVICE=auto  # "cuda" for GPU, "cpu" for CPU
AI_MAX_TOKENS=100

# Server Configuration
HOST=0.0.0.0
PORT=8080
DEBUG=false

# Security Settings
ENABLE_CORS=true
LOG_LEVEL=INFO
```

### Direct Configuration
Edit `ssh_honeypot/config.py` to customize:

```python
# AI Model Configuration
ai_model_name: str = "microsoft/DialoGPT-small"
ai_model_device: str = "auto"  # "cuda" for GPU, "cpu" for CPU
ai_max_tokens: int = 100

# Server Configuration
host: str = "0.0.0.0"
port: int = 8080
debug: bool = False

# Security Settings
enable_cors: bool = True
log_level: str = "INFO"
```

## 🤖 AI Integration

The honeypot uses Hugging Face's DialoGPT model to generate realistic terminal responses:

- **Few-shot prompting** teaches the model proper terminal output format
- **Contextual prompts** for different command types (ls, cat, who, etc.)
- **Response cleaning** extracts only terminal output
- **Fallback responses** ensure consistent behavior

## 🛡️ Security Features

- **Threat Detection**: Analyzes commands for malicious patterns
- **Session Tracking**: Monitors attacker behavior over time
- **IP Logging**: Tracks source IPs and geographic data
- **Rate Limiting**: Prevents abuse and DoS attacks
- **Structured Logging**: Comprehensive audit trail

## 📊 Analytics

Monitor threats and attacks through the analytics dashboard:

- **Active Sessions**: Real-time session monitoring
- **Threat Levels**: Low, Medium, High threat classification
- **Command Statistics**: Most common commands and patterns
- **Geographic Data**: Attack source locations
- **Time Analysis**: Attack patterns over time

## 📚 Examples and Scripts

### Examples Directory (`examples/`)
- `basic_usage.py` - Basic honeypot usage example
- `custom_config.py` - Custom configuration example
- `README.md` - Examples documentation

### Scripts Directory (`scripts/`)
- `dev.py` - Development utilities (testing, linting, security checks)

### Usage Examples
```bash
# Run basic example
python examples/basic_usage.py

# Run with custom configuration
python examples/custom_config.py

# Run development scripts
python scripts/dev.py test      # Run tests
python scripts/dev.py lint      # Run linting
python scripts/dev.py security  # Run security checks
python scripts/dev.py clean      # Clean project files
```

## 🧪 Testing

Test the honeypot with various commands:

```bash
# Test basic commands
curl -X POST "http://localhost:8080/api/v1/command" \
     -H "Content-Type: application/json" \
     -d '{"command": "ls", "session_id": "test_session"}'

# Test threat detection
curl -X POST "http://localhost:8080/api/v1/command" \
     -H "Content-Type: application/json" \
     -d '{"command": "rm -rf /", "session_id": "test_session"}'
```

## 🚀 Deployment

### Docker Deployment
```bash
# Build Docker image
docker build -t ssh-honeypot .

# Run container
docker run -p 8080:8080 ssh-honeypot
```

### Production Deployment
```bash
# Install production dependencies
pip install -r requirements.txt

# Run with production settings
uvicorn ssh_honeypot.main:app --host 0.0.0.0 --port 8080 --workers 4
```

## 📈 Performance

- **Response Time**: < 100ms for AI-generated responses
- **Memory Usage**: ~500MB with DialoGPT-small model
- **Concurrent Sessions**: Supports 100+ simultaneous sessions
- **Scalability**: Horizontal scaling with load balancer

## 🔒 Security Considerations

- **Isolation**: Runs in isolated environment
- **No Real Commands**: All responses are AI-generated or predefined
- **Input Validation**: All inputs are validated and sanitized
- **Logging**: Comprehensive audit trail for security analysis

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👨‍💻 Author

**Mohamed Ibrahim**
- GitHub: [@Mohamed-Ibrahim-124](https://github.com/Mohamed-Ibrahim-124)
- LinkedIn: [Your LinkedIn Profile]

## 🙏 Acknowledgments

- Hugging Face for the transformer models
- FastAPI team for the excellent web framework
- The cybersecurity community for inspiration and best practices

## 📚 Related Projects

- [RAG Agent](https://github.com/Mohamed-Ibrahim-124/RAG_Agent) - Simple RAG Agent using Streamlit
- [Text-to-Image Search](https://github.com/Mohamed-Ibrahim-124/Text-to-Image-Search) - ML-based image search system
- [Insurance Data Analysis](https://github.com/Mohamed-Ibrahim-124/Insurance-Data-Analysis) - Data analysis and prediction

---

⭐ **Star this repository if you found it helpful!**
