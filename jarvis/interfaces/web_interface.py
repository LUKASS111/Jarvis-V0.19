"""
FastAPI Web Interface for Jarvis V0.19
Provides a modern web-based interface for the Jarvis AI system.
"""

from fastapi import FastAPI, HTTPException, UploadFile, File, Form, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import json
import os
import tempfile
import asyncio
from datetime import datetime
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Jarvis V0.19 Web Interface",
    description="Modern web interface for the Jarvis distributed AI system",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models for API
class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None
    model: Optional[str] = "auto"

class ChatResponse(BaseModel):
    response: str
    session_id: str
    timestamp: str
    model_used: str

class MemoryRequest(BaseModel):
    content: str
    category: Optional[str] = "general"
    tags: Optional[List[str]] = []

class MemoryResponse(BaseModel):
    memory_id: str
    content: str
    category: str
    tags: List[str]
    timestamp: str

class SearchRequest(BaseModel):
    query: str
    category: Optional[str] = None
    limit: Optional[int] = 10

class SystemStatus(BaseModel):
    health_score: int
    components: Dict[str, str]
    active_sessions: int
    total_memories: int
    supported_formats: List[str]
    timestamp: str

class FileProcessingResponse(BaseModel):
    file_name: str
    file_type: str
    processing_status: str
    summary: Dict[str, Any]
    content_preview: str

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

manager = ConnectionManager()

# Import Jarvis components
try:
    from jarvis.backend import get_jarvis_backend, shutdown_jarvis_backend
    from jarvis.memory.production_memory import get_production_memory
    from jarvis.utils.file_processors import process_file, get_supported_formats
    from jarvis.api.api_router import quick_chat, quick_remember, quick_recall
    BACKEND_AVAILABLE = True
except ImportError as e:
    logger.warning(f"Jarvis backend not available: {e}")
    BACKEND_AVAILABLE = False

# Initialize backend if available
jarvis_backend = None
if BACKEND_AVAILABLE:
    try:
        jarvis_backend = get_jarvis_backend()
        logger.info("Jarvis backend initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize Jarvis backend: {e}")
        BACKEND_AVAILABLE = False

# API Routes

@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve the main web interface."""
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Jarvis V0.19 - AI Assistant</title>
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                color: #333;
            }
            
            .container {
                max-width: 1200px;
                margin: 0 auto;
                padding: 20px;
            }
            
            .header {
                text-align: center;
                color: white;
                margin-bottom: 30px;
            }
            
            .header h1 {
                font-size: 3rem;
                margin-bottom: 10px;
                text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
            }
            
            .header p {
                font-size: 1.2rem;
                opacity: 0.9;
            }
            
            .dashboard {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                gap: 20px;
                margin-bottom: 30px;
            }
            
            .card {
                background: white;
                border-radius: 15px;
                padding: 25px;
                box-shadow: 0 10px 25px rgba(0,0,0,0.1);
                transition: transform 0.3s ease, box-shadow 0.3s ease;
            }
            
            .card:hover {
                transform: translateY(-5px);
                box-shadow: 0 20px 40px rgba(0,0,0,0.15);
            }
            
            .card h3 {
                color: #5a67d8;
                margin-bottom: 15px;
                font-size: 1.3rem;
            }
            
            .chat-section {
                background: white;
                border-radius: 15px;
                padding: 25px;
                box-shadow: 0 10px 25px rgba(0,0,0,0.1);
                height: 500px;
                display: flex;
                flex-direction: column;
            }
            
            .chat-messages {
                flex: 1;
                overflow-y: auto;
                border: 1px solid #e2e8f0;
                border-radius: 10px;
                padding: 15px;
                margin-bottom: 15px;
                background: #f8fafc;
            }
            
            .message {
                margin-bottom: 15px;
                padding: 10px 15px;
                border-radius: 10px;
                max-width: 80%;
            }
            
            .user-message {
                background: #5a67d8;
                color: white;
                margin-left: auto;
            }
            
            .bot-message {
                background: #e2e8f0;
                color: #2d3748;
            }
            
            .input-group {
                display: flex;
                gap: 10px;
            }
            
            .input-group input {
                flex: 1;
                padding: 12px 15px;
                border: 2px solid #e2e8f0;
                border-radius: 10px;
                font-size: 1rem;
                transition: border-color 0.3s ease;
            }
            
            .input-group input:focus {
                outline: none;
                border-color: #5a67d8;
            }
            
            .btn {
                padding: 12px 20px;
                background: #5a67d8;
                color: white;
                border: none;
                border-radius: 10px;
                cursor: pointer;
                font-size: 1rem;
                transition: background 0.3s ease;
            }
            
            .btn:hover {
                background: #4c51bf;
            }
            
            .status-indicator {
                display: inline-block;
                width: 12px;
                height: 12px;
                border-radius: 50%;
                margin-right: 8px;
            }
            
            .status-online { background: #48bb78; }
            .status-offline { background: #f56565; }
            
            .feature-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                gap: 15px;
                margin-top: 20px;
            }
            
            .feature {
                background: #f8fafc;
                padding: 15px;
                border-radius: 10px;
                text-align: center;
                border: 2px solid #e2e8f0;
                transition: border-color 0.3s ease;
            }
            
            .feature:hover {
                border-color: #5a67d8;
            }
            
            .stats {
                display: flex;
                justify-content: space-around;
                text-align: center;
            }
            
            .stat-item h4 {
                font-size: 2rem;
                color: #5a67d8;
                margin-bottom: 5px;
            }
            
            .stat-item p {
                color: #718096;
                font-size: 0.9rem;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🤖 Jarvis V0.19</h1>
                <p>Advanced Distributed AI Assistant</p>
            </div>
            
            <div class="dashboard">
                <div class="card">
                    <h3>🔧 System Status</h3>
                    <div class="stats">
                        <div class="stat-item">
                            <h4 id="health-score">98</h4>
                            <p>Health Score</p>
                        </div>
                        <div class="stat-item">
                            <h4 id="active-sessions">0</h4>
                            <p>Active Sessions</p>
                        </div>
                    </div>
                    <p style="margin-top: 15px;">
                        <span class="status-indicator status-online" id="status-indicator"></span>
                        <span id="status-text">System Operational</span>
                    </p>
                </div>
                
                <div class="card">
                    <h3>📊 System Metrics</h3>
                    <div class="stats">
                        <div class="stat-item">
                            <h4 id="total-memories">0</h4>
                            <p>Stored Memories</p>
                        </div>
                        <div class="stat-item">
                            <h4 id="file-formats">10+</h4>
                            <p>File Formats</p>
                        </div>
                    </div>
                </div>
                
                <div class="card">
                    <h3>🚀 Quick Actions</h3>
                    <div class="feature-grid">
                        <div class="feature" onclick="showFileUpload()">
                            <h4>📁</h4>
                            <p>Process Files</p>
                        </div>
                        <div class="feature" onclick="showMemorySearch()">
                            <h4>🧠</h4>
                            <p>Search Memory</p>
                        </div>
                        <div class="feature" onclick="showSystemInfo()">
                            <h4>ℹ️</h4>
                            <p>System Info</p>
                        </div>
                        <div class="feature" onclick="openDocs()">
                            <h4>📚</h4>
                            <p>Documentation</p>
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="chat-section">
                <h3 style="margin-bottom: 15px;">💬 Chat with Jarvis</h3>
                <div class="chat-messages" id="chat-messages">
                    <div class="message bot-message">
                        Hello! I'm Jarvis, your AI assistant. How can I help you today?
                    </div>
                </div>
                <div class="input-group">
                    <input type="text" id="chat-input" placeholder="Type your message here..." onkeypress="handleKeyPress(event)">
                    <button class="btn" onclick="sendMessage()">Send</button>
                </div>
            </div>
        </div>
        
        <script>
            // WebSocket connection for real-time chat
            const ws = new WebSocket('ws://localhost:8000/ws');
            
            ws.onopen = function(event) {
                console.log('WebSocket connected');
                updateStatus(true);
            };
            
            ws.onclose = function(event) {
                console.log('WebSocket disconnected');
                updateStatus(false);
            };
            
            ws.onmessage = function(event) {
                const data = JSON.parse(event.data);
                addMessage(data.message, 'bot-message');
            };
            
            function updateStatus(online) {
                const indicator = document.getElementById('status-indicator');
                const text = document.getElementById('status-text');
                
                if (online) {
                    indicator.className = 'status-indicator status-online';
                    text.textContent = 'System Operational';
                } else {
                    indicator.className = 'status-indicator status-offline';
                    text.textContent = 'System Offline';
                }
            }
            
            function sendMessage() {
                const input = document.getElementById('chat-input');
                const message = input.value.trim();
                
                if (message) {
                    addMessage(message, 'user-message');
                    
                    // Send to backend
                    fetch('/api/chat', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({
                            message: message,
                            session_id: null
                        })
                    })
                    .then(response => response.json())
                    .then(data => {
                        addMessage(data.response, 'bot-message');
                    })
                    .catch(error => {
                        console.error('Error:', error);
                        addMessage('Sorry, I encountered an error. Please try again.', 'bot-message');
                    });
                    
                    input.value = '';
                }
            }
            
            function addMessage(text, className) {
                const messages = document.getElementById('chat-messages');
                const message = document.createElement('div');
                message.className = 'message ' + className;
                message.textContent = text;
                messages.appendChild(message);
                messages.scrollTop = messages.scrollHeight;
            }
            
            function handleKeyPress(event) {
                if (event.key === 'Enter') {
                    sendMessage();
                }
            }
            
            function showFileUpload() {
                alert('File upload feature coming soon!');
            }
            
            function showMemorySearch() {
                alert('Memory search feature coming soon!');
            }
            
            function showSystemInfo() {
                fetch('/api/status')
                .then(response => response.json())
                .then(data => {
                    alert('System Health: ' + data.health_score + '/100\\nActive Sessions: ' + data.active_sessions);
                });
            }
            
            function openDocs() {
                window.open('/api/docs', '_blank');
            }
            
            // Load initial system status
            fetch('/api/status')
            .then(response => response.json())
            .then(data => {
                document.getElementById('health-score').textContent = data.health_score;
                document.getElementById('active-sessions').textContent = data.active_sessions;
                document.getElementById('total-memories').textContent = data.total_memories;
                document.getElementById('file-formats').textContent = data.supported_formats.length;
            })
            .catch(error => {
                console.error('Error loading status:', error);
            });
        </script>
    </body>
    </html>
    """

@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Handle chat requests."""
    if not BACKEND_AVAILABLE:
        raise HTTPException(status_code=503, detail="Backend service not available")
    
    try:
        # Use the quick_chat function from the backend
        response = quick_chat(request.message)
        
        return ChatResponse(
            response=response,
            session_id=request.session_id or "default",
            timestamp=datetime.now().isoformat(),
            model_used=request.model or "auto"
        )
    except Exception as e:
        logger.error(f"Chat error: {e}")
        raise HTTPException(status_code=500, detail=f"Chat processing failed: {str(e)}")

@app.post("/api/memory", response_model=MemoryResponse)
async def store_memory(request: MemoryRequest):
    """Store information in memory."""
    if not BACKEND_AVAILABLE:
        raise HTTPException(status_code=503, detail="Backend service not available")
    
    try:
        # Store memory using the backend
        memory_id = quick_remember(request.content, request.category)
        
        return MemoryResponse(
            memory_id=str(memory_id),
            content=request.content,
            category=request.category,
            tags=request.tags,
            timestamp=datetime.now().isoformat()
        )
    except Exception as e:
        logger.error(f"Memory storage error: {e}")
        raise HTTPException(status_code=500, detail=f"Memory storage failed: {str(e)}")

@app.post("/api/search")
async def search_memory(request: SearchRequest):
    """Search stored memories."""
    if not BACKEND_AVAILABLE:
        raise HTTPException(status_code=503, detail="Backend service not available")
    
    try:
        # Search memories using the backend
        results = quick_recall(request.query, request.limit)
        
        return {
            "query": request.query,
            "results": results,
            "count": len(results),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Memory search error: {e}")
        raise HTTPException(status_code=500, detail=f"Memory search failed: {str(e)}")

@app.post("/api/upload", response_model=FileProcessingResponse)
async def upload_file(file: UploadFile = File(...)):
    """Upload and process a file."""
    try:
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as tmp_file:
            content = await file.read()
            tmp_file.write(content)
            tmp_file_path = tmp_file.name
        
        try:
            # Process the file
            result = process_file(tmp_file_path, 'memory')
            
            return FileProcessingResponse(
                file_name=file.filename,
                file_type=result['metadata']['file_extension'],
                processing_status="success",
                summary=result['summary'],
                content_preview=result['content'][:500] + "..." if len(result['content']) > 500 else result['content']
            )
        finally:
            # Clean up temporary file
            os.unlink(tmp_file_path)
            
    except Exception as e:
        logger.error(f"File processing error: {e}")
        raise HTTPException(status_code=500, detail=f"File processing failed: {str(e)}")

@app.get("/api/status", response_model=SystemStatus)
async def get_system_status():
    """Get current system status."""
    try:
        if BACKEND_AVAILABLE and jarvis_backend:
            # Get status from backend
            status = jarvis_backend.get_system_status()
            
            return SystemStatus(
                health_score=status.get('system_metrics', {}).get('health_score', 98),
                components={
                    "backend": "operational" if BACKEND_AVAILABLE else "offline",
                    "memory": "operational",
                    "file_processing": "operational",
                    "security": "operational"
                },
                active_sessions=status.get('sessions', {}).get('active', 0),
                total_memories=status.get('subsystems', {}).get('memory', {}).get('total_memories', 0),
                supported_formats=get_supported_formats() if BACKEND_AVAILABLE else [],
                timestamp=datetime.now().isoformat()
            )
        else:
            # Fallback status
            return SystemStatus(
                health_score=50,
                components={"backend": "offline"},
                active_sessions=0,
                total_memories=0,
                supported_formats=[],
                timestamp=datetime.now().isoformat()
            )
    except Exception as e:
        logger.error(f"Status check error: {e}")
        raise HTTPException(status_code=500, detail=f"Status check failed: {str(e)}")

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time communication."""
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            # Process the message
            if BACKEND_AVAILABLE:
                try:
                    response = quick_chat(message_data.get('message', ''))
                    await manager.send_personal_message(
                        json.dumps({"message": response}),
                        websocket
                    )
                except Exception as e:
                    await manager.send_personal_message(
                        json.dumps({"message": f"Error: {str(e)}"}),
                        websocket
                    )
            else:
                await manager.send_personal_message(
                    json.dumps({"message": "Backend service not available"}),
                    websocket
                )
    except WebSocketDisconnect:
        manager.disconnect(websocket)

@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy" if BACKEND_AVAILABLE else "degraded",
        "timestamp": datetime.now().isoformat(),
        "backend_available": BACKEND_AVAILABLE,
        "version": "1.0.0"
    }

# Startup and shutdown events
@app.on_event("startup")
async def startup_event():
    """Initialize services on startup."""
    logger.info("Starting Jarvis Web Interface...")
    if BACKEND_AVAILABLE:
        logger.info("Backend services initialized successfully")
    else:
        logger.warning("Backend services not available - running in limited mode")

@app.on_event("shutdown")
async def shutdown_event():
    """Clean up on shutdown."""
    logger.info("Shutting down Jarvis Web Interface...")
    if BACKEND_AVAILABLE:
        try:
            shutdown_jarvis_backend()
            logger.info("Backend services shut down successfully")
        except Exception as e:
            logger.error(f"Error shutting down backend: {e}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "web_interface:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )