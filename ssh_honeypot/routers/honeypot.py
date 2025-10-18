"""
Honeypot API endpoints
Handles SSH command processing and session management
"""

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import HTMLResponse

from ..models.schemas import CommandRequest, CommandResponse, SessionInfo
from ..services.honeypot_service import HoneypotService
from ..services.service_manager import get_honeypot_service
from ..utils.logging import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/api/v1", tags=["honeypot"])


@router.get("/", response_class=HTMLResponse)
async def root() -> str:
    """Serve the honeypot web interface"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>SSH Honeypot - Clean Architecture</title>
        <style>
            :root {
                --bg-color: #0a0a0a;
                --text-color: #00ff00;
                --accent-color: #ffff00;
                --border-color: #00ff00;
                --error-color: #ff0000;
                --success-color: #00ff00;
            }

            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }

            body {
                font-family: 'JetBrains Mono', 'Courier New', monospace;
                background: linear-gradient(135deg, #0a0a0a 0%, #1a1a1a 100%);
                color: var(--text-color);
                min-height: 100vh;
                overflow-x: hidden;
            }

            .header {
                background: linear-gradient(90deg, #00ff00 0%, #ffff00 100%);
                color: #000;
                padding: 1rem;
                text-align: center;
                box-shadow: 0 2px 10px rgba(0, 255, 0, 0.3);
            }

            .header h1 {
                font-size: 2rem;
                margin-bottom: 0.5rem;
            }

            .main-container {
                display: grid;
                grid-template-columns: 1fr 300px;
                gap: 1rem;
                padding: 1rem;
                height: calc(100vh - 120px);
            }

            .terminal-container {
                background: var(--bg-color);
                border: 1px solid var(--border-color);
                border-radius: 8px;
                overflow: hidden;
                box-shadow: 0 0 20px rgba(0, 255, 0, 0.2);
            }

            .terminal-header {
                background: linear-gradient(90deg, #1a1a1a 0%, #2a2a2a 100%);
                padding: 0.5rem 1rem;
                border-bottom: 1px solid var(--border-color);
                display: flex;
                justify-content: space-between;
                align-items: center;
            }

            .terminal-title {
                font-weight: bold;
                color: var(--accent-color);
            }

            .terminal-content {
                height: calc(100% - 60px);
                overflow-y: auto;
                padding: 1rem;
                background: #000;
            }

            .terminal-line {
                margin: 0.5rem 0;
                white-space: pre-wrap;
                word-wrap: break-word;
            }

            .prompt {
                color: var(--accent-color);
                font-weight: bold;
            }

            .command-input {
                background: transparent;
                border: none;
                color: var(--text-color);
                font-family: inherit;
                font-size: inherit;
                outline: none;
                width: calc(100% - 200px);
                margin-left: 0.5rem;
            }

            .input-line {
                display: flex;
                align-items: center;
                margin-top: 1rem;
            }

            .sidebar {
                background: rgba(0, 255, 0, 0.05);
                border: 1px solid var(--border-color);
                border-radius: 8px;
                padding: 1rem;
                overflow-y: auto;
            }

            .sidebar h3 {
                color: var(--accent-color);
                margin-bottom: 1rem;
                border-bottom: 1px solid var(--border-color);
                padding-bottom: 0.5rem;
            }

            .info-card {
                background: rgba(0, 255, 0, 0.1);
                border: 1px solid var(--border-color);
                border-radius: 4px;
                padding: 0.75rem;
                margin-bottom: 1rem;
            }

            .info-card h4 {
                color: var(--accent-color);
                margin-bottom: 0.5rem;
            }

            .command-list {
                list-style: none;
            }

            .command-list li {
                padding: 0.25rem 0;
                border-bottom: 1px solid rgba(0, 255, 0, 0.2);
            }

            .command-list li:last-child {
                border-bottom: none;
            }

            .error { color: var(--error-color); }
            .success { color: var(--success-color); }
            .warning { color: var(--accent-color); }

            @media (max-width: 768px) {
                .main-container {
                    grid-template-columns: 1fr;
                    grid-template-rows: 1fr auto;
                }

                .sidebar {
                    height: 200px;
                }
            }
        </style>
    </head>
    <body>
        <div class="header">
            <h1>🕸️ SSH Honeypot</h1>
            <p>Clean FastAPI Architecture - Interview Project</p>
        </div>

        <div class="main-container">
            <div class="terminal-container">
                <div class="terminal-header">
                    <div class="terminal-title">admin@honeypot:~$</div>
                </div>
                <div class="terminal-content" id="terminal">
                    <div class="terminal-line">
                        <span class="prompt">admin@honeypot:~$</span> Welcome to the SSH Honeypot!
                    </div>
                    <div class="terminal-line">
                        <span class="prompt">admin@honeypot:~$</span> Clean FastAPI architecture with proper separation of concerns.
                    </div>
                    <div class="terminal-line">
                        <span class="prompt">admin@honeypot:~$</span> Type 'help' for available commands or 'exit' to quit.
                    </div>
                </div>
                <div class="input-line">
                    <span class="prompt">admin@honeypot:~$</span>
                    <input type="text" id="commandInput" class="command-input" placeholder="Enter command..." autofocus>
                </div>
            </div>

            <div class="sidebar">
                <h3>Architecture</h3>
                <div class="info-card">
                    <h4>🏗️ Clean Structure</h4>
                    <p>FastAPI best practices with proper separation of concerns</p>
                </div>

                <div class="info-card">
                    <h4>🤖 AI Integration</h4>
                    <p>AI-powered responses with fallback mechanisms</p>
                </div>

                <div class="info-card">
                    <h4>🔒 Security First</h4>
                    <p>Fake commands only - safe for learning</p>
                </div>

                <h3>Available Commands</h3>
                <ul class="command-list">
                    <li><code>ls [path]</code> - List directory</li>
                    <li><code>cat /etc/passwd</code> - Show password file</li>
                    <li><code>who</code> - Show users</li>
                    <li><code>pwd</code> - Current directory</li>
                    <li><code>cd [path]</code> - Change directory</li>
                    <li><code>help</code> - Show help</li>
                    <li><code>exit</code> - Quit session</li>
                </ul>
            </div>
        </div>

        <script>
            const terminal = document.getElementById('terminal');
            const commandInput = document.getElementById('commandInput');
            let sessionId = null;

            function addOutput(text, className = '') {
                const output = document.createElement('div');
                output.className = `terminal-line ${className}`;
                output.innerHTML = `<span class="prompt">admin@honeypot:~$</span> ${text}`;
                terminal.appendChild(output);
                terminal.scrollTop = terminal.scrollHeight;
            }

            async function executeCommand(command) {
                if (command.trim() === '') return;

                // Add user input to terminal
                addOutput(command, 'user-input');

                if (command.toLowerCase() === 'exit' || command.toLowerCase() === 'quit') {
                    addOutput('Goodbye!', 'success');
                    commandInput.disabled = true;
                    return;
                }

                if (command.toLowerCase() === 'help') {
                    addOutput(`Available commands:
- ls [path]: List directory contents
- cat /etc/passwd: Show password file contents
- who: Show currently logged in users
- pwd: Show current working directory
- cd [path]: Change directory
- help: Show this help message
- exit: Quit the session`, 'success');
                    return;
                }

                try {
                    // Send command to API
                    const response = await fetch('/api/v1/command', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({
                            command: command,
                            session_id: sessionId
                        })
                    });

                    const data = await response.json();

                    if (response.ok) {
                        addOutput(data.response, 'success');
                        sessionId = data.session_id;
                    } else {
                        addOutput(data.detail || 'Error processing command', 'error');
                    }
                } catch (error) {
                    addOutput('Error: ' + error.message, 'error');
                }
            }

            commandInput.addEventListener('keypress', function(e) {
                if (e.key === 'Enter') {
                    const command = commandInput.value;
                    commandInput.value = '';
                    executeCommand(command);
                }
            });

            // Focus on input when clicking terminal
            terminal.addEventListener('click', function() {
                commandInput.focus();
            });
        </script>
    </body>
    </html>
    """


@router.post("/command", response_model=CommandResponse)
async def process_command(
    request: CommandRequest,
    honeypot_service: HoneypotService = Depends(get_honeypot_service),
) -> CommandResponse:
    """Process SSH command through honeypot"""
    try:
        result = await honeypot_service.process_command(
            command=request.command, session_id=request.session_id
        )
        return result
    except Exception as e:
        logger.error(f"Command processing failed: {e}")
        raise HTTPException(status_code=500, detail=str(e)) from None


@router.get("/sessions", response_model=list[SessionInfo])
async def get_sessions(
    honeypot_service: HoneypotService = Depends(get_honeypot_service),
) -> list[SessionInfo]:
    """Get all active sessions"""
    try:
        sessions = await honeypot_service.get_all_sessions()
        return sessions
    except Exception as e:
        logger.error(f"Failed to get sessions: {e}")
        raise HTTPException(status_code=500, detail=str(e)) from None


@router.get("/sessions/{session_id}", response_model=SessionInfo)
async def get_session(
    session_id: str, honeypot_service: HoneypotService = Depends(get_honeypot_service)
) -> SessionInfo:
    """Get specific session information"""
    try:
        session = await honeypot_service.get_session_info(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        return session
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get session {session_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e)) from None


@router.delete("/sessions/{session_id}")
async def close_session(
    session_id: str, honeypot_service: HoneypotService = Depends(get_honeypot_service)
) -> dict[str, str]:
    """Close a session"""
    try:
        success = await honeypot_service.close_session(session_id)
        if not success:
            raise HTTPException(status_code=404, detail="Session not found")
        return {"message": "Session closed successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to close session {session_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e)) from None
