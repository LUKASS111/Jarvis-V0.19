"""
Enhanced FastAPI Interface for Jarvis 1.0.0
Provides comprehensive REST API and WebSocket capabilities for real-time interaction.
"""

import asyncio
import json
import time
from datetime import datetime
from typing import Dict, List, Any, Optional
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import logging

# Setup logging
logger = logging.getLogger(__name__)

# Pydantic models for API
class ChatMessage(BaseModel):
    message: str
    model: Optional[str] = None
    include_context: bool = True

class MemoryEntry(BaseModel):
    content: str
    category: str = "general"
    importance: int = 5
    tags: List[str] = []
    metadata: Dict[str, Any] = {}

class SearchRequest(BaseModel):
    query: str
    category: Optional[str] = None
    limit: int = 10
    min_importance: int = 1

class SystemCommand(BaseModel):
    command: str
    parameters: Dict[str, Any] = {}

# WebSocket connection manager
class ConnectionManager:
    """Manages WebSocket connections for real-time communication."""
    
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.user_sessions: Dict[str, Dict[str, Any]] = {}
    
    async def connect(self, websocket: WebSocket, session_id: str):
        """Connect a new WebSocket client."""
        await websocket.accept()
        self.active_connections.append(websocket)
        self.user_sessions[session_id] = {
            'websocket': websocket,
            'connected_at': time.time(),
            'message_count': 0
        }
        logger.info(f"WebSocket connected: {session_id}")
    
    def disconnect(self, websocket: WebSocket, session_id: str):
        """Disconnect a WebSocket client."""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        if session_id in self.user_sessions:
            del self.user_sessions[session_id]
        logger.info(f"WebSocket disconnected: {session_id}")
    
    async def send_personal_message(self, message: Dict[str, Any], session_id: str):
        """Send message to specific client."""
        if session_id in self.user_sessions:
            websocket = self.user_sessions[session_id]['websocket']
            try:
                await websocket.send_text(json.dumps(message))
                self.user_sessions[session_id]['message_count'] += 1
            except Exception as e:
                logger.error(f"Error sending message to {session_id}: {e}")
    
    async def broadcast(self, message: Dict[str, Any]):
        """Broadcast message to all connected clients."""
        for connection in self.active_connections.copy():
            try:
                await connection.send_text(json.dumps(message))
            except Exception as e:
                logger.error(f"Error broadcasting message: {e}")
                if connection in self.active_connections:
                    self.active_connections.remove(connection)

# Create FastAPI app
app = FastAPI(
    title="Jarvis 1.0.0 Enhanced API",
    description="Comprehensive AI Assistant API with real-time capabilities",
    version="1.0.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize connection manager
manager = ConnectionManager()

# Initialize Jarvis components
try:
    from jarvis.core.main import JarvisAgent
    from jarvis.llm.llm_interface import get_llm_interface
    from jarvis.memory.memory_manager import get_memory_manager
    from jarvis.monitoring.performance_optimizer import get_performance_monitor
    from jarvis.utils.file_processors import process_file, get_supported_formats
    
    jarvis_agent = JarvisAgent()
    jarvis_agent.initialize()
    llm_interface = get_llm_interface()
    memory_manager = get_memory_manager()
    performance_monitor = get_performance_monitor()
    
except Exception as e:
    logger.error(f"Error initializing Jarvis components: {e}")
    jarvis_agent = None
    llm_interface = None
    memory_manager = None
    performance_monitor = None

@app.get("/", response_class=HTMLResponse)
async def read_root():
    """Serve the main web interface."""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Jarvis 1.0.0 - Enhanced AI Assistant</title>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                height: 100vh;
                display: flex;
                flex-direction: column;
            }
            
            .header {
                background: rgba(255, 255, 255, 0.1);
                backdrop-filter: blur(10px);
                padding: 1rem 2rem;
                color: white;
                box-shadow: 0 2px 20px rgba(0,0,0,0.1);
            }
            
            .header h1 {
                font-size: 2rem;
                font-weight: 300;
            }
            
            .subtitle {
                opacity: 0.8;
                margin-top: 0.5rem;
            }
            
            .main-container {
                flex: 1;
                display: flex;
                padding: 2rem;
                gap: 2rem;
                overflow: hidden;
            }
            
            .chat-container {
                flex: 2;
                background: rgba(255, 255, 255, 0.95);
                border-radius: 15px;
                display: flex;
                flex-direction: column;
                box-shadow: 0 8px 32px rgba(0,0,0,0.1);
            }
            
            .sidebar {
                flex: 1;
                background: rgba(255, 255, 255, 0.9);
                border-radius: 15px;
                padding: 1.5rem;
                box-shadow: 0 8px 32px rgba(0,0,0,0.1);
                overflow-y: auto;
            }
            
            .chat-messages {
                flex: 1;
                padding: 1.5rem;
                overflow-y: auto;
                display: flex;
                flex-direction: column;
                gap: 1rem;
            }
            
            .message {
                max-width: 80%;
                padding: 0.75rem 1rem;
                border-radius: 18px;
                word-wrap: break-word;
            }
            
            .user-message {
                background: linear-gradient(135deg, #667eea, #764ba2);
                color: white;
                align-self: flex-end;
            }
            
            .bot-message {
                background: #f1f3f4;
                color: #333;
                align-self: flex-start;
            }
            
            .input-container {
                padding: 1.5rem;
                border-top: 1px solid #e0e0e0;
                display: flex;
                gap: 1rem;
            }
            
            #messageInput {
                flex: 1;
                padding: 0.75rem 1rem;
                border: 2px solid #e0e0e0;
                border-radius: 25px;
                outline: none;
                font-size: 1rem;
                transition: border-color 0.3s;
            }
            
            #messageInput:focus {
                border-color: #667eea;
            }
            
            #sendButton {
                padding: 0.75rem 1.5rem;
                background: linear-gradient(135deg, #667eea, #764ba2);
                color: white;
                border: none;
                border-radius: 25px;
                cursor: pointer;
                font-weight: 500;
                transition: transform 0.2s;
            }
            
            #sendButton:hover {
                transform: translateY(-2px);
            }
            
            .status-section {
                background: #f8f9fa;
                border-radius: 10px;
                padding: 1rem;
                margin-bottom: 1.5rem;
            }
            
            .status-item {
                display: flex;
                justify-content: space-between;
                margin: 0.5rem 0;
                font-size: 0.9rem;
            }
            
            .status-label {
                font-weight: 500;
                color: #666;
            }
            
            .status-value {
                color: #333;
            }
            
            .file-upload {
                margin-top: 1rem;
                padding: 1rem;
                border: 2px dashed #ddd;
                border-radius: 10px;
                text-align: center;
                cursor: pointer;
                transition: background-color 0.3s;
            }
            
            .file-upload:hover {
                background-color: #f8f9fa;
            }
            
            .health-score {
                font-size: 1.5rem;
                font-weight: bold;
                color: #4caf50;
            }
            
            .connection-status {
                padding: 0.5rem;
                border-radius: 5px;
                font-size: 0.8rem;
                font-weight: bold;
            }
            
            .connected {
                background: #4caf50;
                color: white;
            }
            
            .disconnected {
                background: #f44336;
                color: white;
            }
            
            @media (max-width: 768px) {
                .main-container {
                    flex-direction: column;
                    padding: 1rem;
                }
                
                .sidebar {
                    order: -1;
                    max-height: 200px;
                }
            }
        </style>
    </head>
    <body>
        <div class="header">
            <h1>🤖 Jarvis 1.0.0</h1>
            <div class="subtitle">Enhanced AI Assistant with Real-time Capabilities</div>
        </div>
        
        <div class="main-container">
            <div class="chat-container">
                <div class="chat-messages" id="chatMessages">
                    <div class="message bot-message">
                        👋 Hello! I'm Jarvis 1.0.0 with enhanced capabilities. I can help you with:
                        <br>• Intelligent conversations with context awareness
                        <br>• File processing (13+ formats supported)
                        <br>• Memory management and search
                        <br>• System monitoring and optimization
                        <br>• Real-time performance analytics
                        <br><br>How can I assist you today?
                    </div>
                </div>
                <div class="input-container">
                    <input type="text" id="messageInput" placeholder="Type your message here..." />
                    <button id="sendButton">Send</button>
                </div>
            </div>
            
            <div class="sidebar">
                <div class="status-section">
                    <h3>🔗 Connection Status</h3>
                    <div id="connectionStatus" class="connection-status disconnected">Disconnected</div>
                </div>
                
                <div class="status-section">
                    <h3>⚡ System Health</h3>
                    <div class="status-item">
                        <span class="status-label">Overall Health:</span>
                        <span class="status-value health-score" id="healthScore">--</span>
                    </div>
                    <div class="status-item">
                        <span class="status-label">Memory Entries:</span>
                        <span class="status-value" id="memoryEntries">--</span>
                    </div>
                    <div class="status-item">
                        <span class="status-label">Active Model:</span>
                        <span class="status-value" id="activeModel">--</span>
                    </div>
                </div>
                
                <div class="status-section">
                    <h3>📁 File Processing</h3>
                    <div class="status-item">
                        <span class="status-label">Supported Formats:</span>
                        <span class="status-value" id="supportedFormats">--</span>
                    </div>
                    
                    <div class="file-upload" onclick="document.getElementById('fileInput').click()">
                        📎 Click to upload file
                        <input type="file" id="fileInput" style="display: none;" />
                    </div>
                </div>
                
                <div class="status-section">
                    <h3>🔧 Quick Actions</h3>
                    <button onclick="refreshStatus()" style="width: 100%; padding: 0.5rem; margin: 0.25rem 0; border: none; border-radius: 5px; background: #667eea; color: white; cursor: pointer;">
                        🔄 Refresh Status
                    </button>
                    <button onclick="clearChat()" style="width: 100%; padding: 0.5rem; margin: 0.25rem 0; border: none; border-radius: 5px; background: #f44336; color: white; cursor: pointer;">
                        🗑️ Clear Chat
                    </button>
                </div>
            </div>
        </div>
        
        <script>
            let ws = null;
            let sessionId = Date.now().toString();
            
            function connectWebSocket() {
                const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
                ws = new WebSocket(`${protocol}//${window.location.host}/ws/${sessionId}`);
                
                ws.onopen = function() {
                    updateConnectionStatus(true);
                    refreshStatus();
                };
                
                ws.onmessage = function(event) {
                    const data = JSON.parse(event.data);
                    handleWebSocketMessage(data);
                };
                
                ws.onclose = function() {
                    updateConnectionStatus(false);
                    setTimeout(connectWebSocket, 3000); // Reconnect after 3 seconds
                };
                
                ws.onerror = function(error) {
                    console.error('WebSocket error:', error);
                    updateConnectionStatus(false);
                };
            }
            
            function updateConnectionStatus(connected) {
                const statusElement = document.getElementById('connectionStatus');
                if (connected) {
                    statusElement.textContent = 'Connected';
                    statusElement.className = 'connection-status connected';
                } else {
                    statusElement.textContent = 'Disconnected';
                    statusElement.className = 'connection-status disconnected';
                }
            }
            
            function handleWebSocketMessage(data) {
                if (data.type === 'chat_response') {
                    addMessage(data.content, 'bot');
                } else if (data.type === 'status_update') {
                    updateSystemStatus(data.data);
                } else if (data.type === 'file_processed') {
                    addMessage(`File processed successfully: ${data.filename}`, 'bot');
                }
            }
            
            function sendMessage() {
                const input = document.getElementById('messageInput');
                const message = input.value.trim();
                
                if (message && ws && ws.readyState === WebSocket.OPEN) {
                    addMessage(message, 'user');
                    ws.send(JSON.stringify({
                        type: 'chat_message',
                        content: message
                    }));
                    input.value = '';
                }
            }
            
            function addMessage(content, sender) {
                const messagesContainer = document.getElementById('chatMessages');
                const messageDiv = document.createElement('div');
                messageDiv.className = `message ${sender}-message`;
                messageDiv.textContent = content;
                messagesContainer.appendChild(messageDiv);
                messagesContainer.scrollTop = messagesContainer.scrollHeight;
            }
            
            function updateSystemStatus(data) {
                if (data.health) {
                    document.getElementById('healthScore').textContent = data.health + '%';
                }
                if (data.memory_entries) {
                    document.getElementById('memoryEntries').textContent = data.memory_entries;
                }
                if (data.active_model) {
                    document.getElementById('activeModel').textContent = data.active_model;
                }
                if (data.supported_formats) {
                    document.getElementById('supportedFormats').textContent = data.supported_formats;
                }
            }
            
            function refreshStatus() {
                if (ws && ws.readyState === WebSocket.OPEN) {
                    ws.send(JSON.stringify({
                        type: 'get_status'
                    }));
                }
            }
            
            function clearChat() {
                document.getElementById('chatMessages').innerHTML = `
                    <div class="message bot-message">
                        Chat cleared. How can I help you?
                    </div>
                `;
            }
            
            // Event listeners
            document.getElementById('messageInput').addEventListener('keypress', function(e) {
                if (e.key === 'Enter') {
                    sendMessage();
                }
            });
            
            document.getElementById('sendButton').addEventListener('click', sendMessage);
            
            document.getElementById('fileInput').addEventListener('change', function(e) {
                const file = e.target.files[0];
                if (file) {
                    uploadFile(file);
                }
            });
            
            function uploadFile(file) {
                const formData = new FormData();
                formData.append('file', file);
                
                fetch('/api/files/upload', {
                    method: 'POST',
                    body: formData
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        addMessage(`File "${file.name}" uploaded and processed successfully!`, 'bot');
                    } else {
                        addMessage(`Error uploading file: ${data.error}`, 'bot');
                    }
                })
                .catch(error => {
                    addMessage(`Upload error: ${error.message}`, 'bot');
                });
            }
            
            // Initialize WebSocket connection
            connectWebSocket();
        </script>
    </body>
    </html>
    """

# API Routes

@app.get("/api/health")
async def health_check():
    """Get comprehensive system health information."""
    try:
        if jarvis_agent:
            health = jarvis_agent.health_check()
            return health
        else:
            return {"error": "Jarvis agent not available"}
    except Exception as e:
        logger.error(f"Health check error: {e}")
        return {"error": str(e)}

@app.get("/api/capabilities")
async def get_capabilities():
    """Get system capabilities information."""
    try:
        if jarvis_agent:
            capabilities = jarvis_agent.get_capabilities()
            return capabilities
        else:
            return {"error": "Jarvis agent not available"}
    except Exception as e:
        logger.error(f"Capabilities error: {e}")
        return {"error": str(e)}

@app.post("/api/chat")
async def chat_endpoint(message: ChatMessage):
    """Process chat message and return response."""
    try:
        if not llm_interface:
            raise HTTPException(status_code=503, detail="LLM interface not available")
        
        # Generate response
        if message.include_context:
            response = llm_interface.generate_with_context(
                message.message, 
                context_messages=5,
                model=message.model
            )
        else:
            response = llm_interface.generate_response(
                message.message,
                model=message.model
            )
        
        return {
            "response": response,
            "model": llm_interface.get_current_model(),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Chat endpoint error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/memory/store")
async def store_memory(entry: MemoryEntry):
    """Store new memory entry."""
    try:
        if not memory_manager:
            raise HTTPException(status_code=503, detail="Memory manager not available")
        
        entry_id = memory_manager.store(
            content=entry.content,
            category=entry.category,
            importance=entry.importance,
            tags=entry.tags,
            metadata=entry.metadata
        )
        
        return {
            "success": True,
            "entry_id": entry_id,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Memory store error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/memory/search")
async def search_memory(request: SearchRequest):
    """Search memory entries."""
    try:
        if not memory_manager:
            raise HTTPException(status_code=503, detail="Memory manager not available")
        
        results = memory_manager.search(
            query=request.query,
            category=request.category,
            limit=request.limit,
            min_importance=request.min_importance
        )
        
        return {
            "results": [
                {
                    "entry": {
                        "id": result.entry.id,
                        "content": result.entry.content,
                        "category": result.entry.category,
                        "importance": result.entry.importance,
                        "tags": result.entry.tags,
                        "timestamp": result.entry.timestamp
                    },
                    "relevance_score": result.relevance_score,
                    "match_type": result.match_type
                } for result in results
            ],
            "total_results": len(results),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Memory search error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/memory/statistics")
async def get_memory_statistics():
    """Get memory system statistics."""
    try:
        if not memory_manager:
            raise HTTPException(status_code=503, detail="Memory manager not available")
        
        stats = memory_manager.get_statistics()
        return stats
        
    except Exception as e:
        logger.error(f"Memory statistics error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/files/upload")
async def upload_file(file: UploadFile = File(...)):
    """Upload and process file."""
    try:
        # Save uploaded file temporarily
        import tempfile
        with tempfile.NamedTemporaryFile(delete=False, suffix=f"_{file.filename}") as temp_file:
            content = await file.read()
            temp_file.write(content)
            temp_file_path = temp_file.name
        
        # Process the file
        result = process_file(temp_file_path, output_format='memory')
        
        # Store in memory if available
        if memory_manager and result:
            entry_id = memory_manager.store(
                content=result.get('content', ''),
                category='uploaded_file',
                importance=6,
                tags=['uploaded', 'file_processing'],
                metadata={
                    'filename': file.filename,
                    'file_size': len(content),
                    'content_type': file.content_type,
                    'processing_result': result
                }
            )
        
        # Clean up temp file
        import os
        os.unlink(temp_file_path)
        
        return {
            "success": True,
            "filename": file.filename,
            "size": len(content),
            "processing_result": result,
            "memory_entry_id": entry_id if memory_manager else None,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"File upload error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/files/formats")
async def get_supported_formats():
    """Get list of supported file formats."""
    try:
        formats = get_supported_formats()
        return {
            "supported_formats": formats,
            "total_formats": len(formats)
        }
    except Exception as e:
        logger.error(f"Formats error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/performance")
async def get_performance_metrics():
    """Get current performance metrics."""
    try:
        if not performance_monitor:
            raise HTTPException(status_code=503, detail="Performance monitor not available")
        
        current_metrics = performance_monitor.get_performance_summary()
        health = performance_monitor.assess_system_health()
        
        return {
            "current_metrics": current_metrics,
            "system_health": health.to_dict() if hasattr(health, 'to_dict') else health,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Performance metrics error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/system/command")
async def execute_system_command(command: SystemCommand):
    """Execute system command."""
    try:
        if not jarvis_agent:
            raise HTTPException(status_code=503, detail="Jarvis agent not available")
        
        # Process the command through Jarvis agent
        result = jarvis_agent.process_input(command.command)
        
        return {
            "success": True,
            "result": result,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"System command error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# WebSocket endpoint
@app.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    """WebSocket endpoint for real-time communication."""
    await manager.connect(websocket, session_id)
    
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            
            if message.get('type') == 'chat_message':
                # Process chat message
                content = message.get('content', '')
                if content and llm_interface:
                    try:
                        response = llm_interface.generate_with_context(content, context_messages=3)
                        await manager.send_personal_message({
                            'type': 'chat_response',
                            'content': response,
                            'timestamp': datetime.now().isoformat()
                        }, session_id)
                    except Exception as e:
                        await manager.send_personal_message({
                            'type': 'error',
                            'content': f"Error processing message: {str(e)}",
                            'timestamp': datetime.now().isoformat()
                        }, session_id)
            
            elif message.get('type') == 'get_status':
                # Send system status
                try:
                    status_data = {}
                    
                    if jarvis_agent:
                        health = jarvis_agent.health_check()
                        status_data['health'] = health.get('overall', {}).get('health_percentage', 0)
                    
                    if memory_manager:
                        memory_stats = memory_manager.get_statistics()
                        status_data['memory_entries'] = memory_stats.get('total_entries', 0)
                    
                    if llm_interface:
                        llm_stats = llm_interface.get_statistics()
                        status_data['active_model'] = llm_stats.get('current_model', 'Unknown')
                    
                    formats = get_supported_formats()
                    status_data['supported_formats'] = len(formats)
                    
                    await manager.send_personal_message({
                        'type': 'status_update',
                        'data': status_data,
                        'timestamp': datetime.now().isoformat()
                    }, session_id)
                    
                except Exception as e:
                    await manager.send_personal_message({
                        'type': 'error',
                        'content': f"Error getting status: {str(e)}",
                        'timestamp': datetime.now().isoformat()
                    }, session_id)
                    
    except WebSocketDisconnect:
        manager.disconnect(websocket, session_id)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(websocket, session_id)

# Startup event
@app.on_event("startup")
async def startup_event():
    """Initialize services on startup."""
    logger.info("Jarvis 1.0.0 Enhanced API starting up...")
    
    # Broadcast startup message to all connections
    await manager.broadcast({
        'type': 'system_message',
        'content': 'Jarvis 1.0.0 Enhanced API is now online!',
        'timestamp': datetime.now().isoformat()
    })

# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Clean up on shutdown."""
    logger.info("Jarvis 1.0.0 Enhanced API shutting down...")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)