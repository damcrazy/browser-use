from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from langchain_openai import AzureChatOpenAI
from browser_use import Agent
import asyncio
from dotenv import load_dotenv
import json
import base64
from PIL import Image
import io
import os
from pydantic import SecretStr
import logging
from browser_use.logging_config import setup_logging
from langchain_openai import ChatOpenAI
# Configure logging
setup_logging()
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Validate Azure OpenAI configuration
azure_endpoint = os.getenv("AZURE_ENDPOINT")
azure_api_key = os.getenv("AZURE_OPENAI_API_KEY")

if not azure_endpoint or not azure_api_key:
    raise ValueError(
        "Azure OpenAI configuration missing. Please set AZURE_ENDPOINT and AZURE_OPENAI_API_KEY in your .env file"
    )

app = FastAPI()

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Store active WebSocket connections
active_connections = []

@app.get("/", response_class=HTMLResponse)
async def get():
    with open("static/index.html") as f:
        return f.read()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    logger.info("New WebSocket connection request")
    await websocket.accept()
    logger.info("WebSocket connection accepted")
    active_connections.append(websocket)
    
    # try:
        # Create a custom Agent class that sends screenshots to clients
    class StreamingAgent(Agent):
            async def take_screenshot(self):
                page = await self.browser_context.get_current_page()
                screenshot = await page.screenshot()
                # Convert screenshot to base64
                img = Image.open(io.BytesIO(screenshot))
                buffered = io.BytesIO()
                img.save(buffered, format="PNG")
                img_str = base64.b64encode(buffered.getvalue()).decode()
                
                # Send to all connected clients
                for connection in active_connections:
                    try:
                        await connection.send_json({
                            "type": "screenshot",
                            "data": img_str
                        })
                        logger.debug("Screenshot sent successfully")
                    except Exception as e:
                        logger.error(f"Error sending screenshot: {e}")
                        active_connections.remove(connection)
                
                # No need to call parent's take_screenshot

        # Create and run the agent with Azure OpenAI configuration
    agent = StreamingAgent(
            task="Compare the price of gpt-4 and DeepSeek-V3",
            llm=AzureChatOpenAI(
                model="gpt-4o",
                api_version="2024-08-01-preview",
                azure_endpoint=azure_endpoint,
                api_key=SecretStr(azure_api_key or "")
            ),
        )
        
    await agent.run()
        
    # except WebSocketDisconnect:
    #     logger.info("WebSocket disconnected")
    # except Exception as e:
    #     logger.error(f"Error in WebSocket connection: {e}")
    #     await websocket.send_json({
    #         "type": "error",
    #         "message": str(e)
    #     })
    # finally:
    #     if websocket in active_connections:
    #         active_connections.remove(websocket)
    #     logger.info(f"Active connections: {len(active_connections)}")

if __name__ == "__main__":
    import uvicorn
    import socket
    import sys

    def find_available_port(start_port=8000, max_port=8999):
        for port in range(start_port, max_port + 1):
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.bind(('0.0.0.0', port))
                    return port
            except OSError:
                continue
        raise RuntimeError(f"No available ports found between {start_port} and {max_port}")

    try:
        port = find_available_port()
        print(f"Starting server on port {port}")
        uvicorn.run(
            "server:app",
            host="0.0.0.0",
            port=port,
            reload=True,
            log_level="debug"
        )
    except Exception as e:
        print(f"Error starting server: {e}")
        print("Try running with administrator privileges or choose a different port")
        sys.exit(1)
