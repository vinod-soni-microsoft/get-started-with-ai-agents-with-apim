# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE.md file in the project root for full license information.

import contextlib
import os

from azure.ai.projects.aio import AIProjectClient
from azure.identity import DefaultAzureCredential

import fastapi
from fastapi.staticfiles import StaticFiles
from fastapi import Request
from fastapi.responses import JSONResponse, HTMLResponse
from dotenv import load_dotenv

from logging_config import configure_logging

enable_trace = False
logger = None

@contextlib.asynccontextmanager
async def lifespan(app: fastapi.FastAPI):
    agent = None

    proj_endpoint = os.environ.get("AZURE_EXISTING_AIPROJECT_ENDPOINT")
    agent_id = os.environ.get("AZURE_EXISTING_AGENT_ID")
    try:
        ai_project = AIProjectClient(
            credential=DefaultAzureCredential(exclude_shared_token_cache_credential=True),
            endpoint=proj_endpoint,
            api_version = "2025-05-15-preview" # Evaluations yet not supported on stable (api_version="2025-05-01")
        )
        logger.info("Created AIProjectClient")

        if enable_trace:
            application_insights_connection_string = ""
            try:
                application_insights_connection_string = await ai_project.telemetry.get_connection_string()
            except Exception as e:
                e_string = str(e)
                logger.error("Failed to get Application Insights connection string, error: %s", e_string)
            if not application_insights_connection_string:
                logger.error("Application Insights was not enabled for this project.")
                logger.error("Enable it via the 'Tracing' tab in your AI Foundry project page.")
                exit()
            else:
                from azure.monitor.opentelemetry import configure_azure_monitor
                configure_azure_monitor(connection_string=application_insights_connection_string)
                app.state.application_insights_connection_string = application_insights_connection_string
                logger.info("Configured Application Insights for tracing.")

        if agent_id:
            try: 
                agent = await ai_project.agents.get_agent(agent_id)
                logger.info("Agent already exists, skipping creation")
                logger.info(f"Fetched agent, agent ID: {agent.id}")
                logger.info(f"Fetched agent, model name: {agent.model}")
            except Exception as e:
                logger.error(f"Error fetching agent: {e}", exc_info=True)

        if not agent:
            # Fallback to searching by name
            agent_name = os.environ["AZURE_AI_AGENT_NAME"]
            agent_list = ai_project.agents.list_agents()
            if agent_list:
                async for agent_object in agent_list:
                    if agent_object.name == agent_name:
                        agent = agent_object
                        logger.info(f"Found agent by name '{agent_name}', ID={agent_object.id}")
                        break

        if not agent:
            raise RuntimeError("No agent found. Ensure qunicorn.py created one or set AZURE_EXISTING_AGENT_ID.")

        app.state.ai_project = ai_project
        app.state.agent = agent
        
        yield

    except Exception as e:
        logger.error(f"Error during startup: {e}", exc_info=True)
        raise RuntimeError(f"Error during startup: {e}")

    finally:
        try:
            await ai_project.close()
            logger.info("Closed AIProjectClient")
        except Exception as e:
            logger.error("Error closing AIProjectClient", exc_info=True)


def create_app():
    if not os.getenv("RUNNING_IN_PRODUCTION"):
        load_dotenv(override=True)

    global logger
    logger = configure_logging(os.getenv("APP_LOG_FILE", ""))

    enable_trace_string = os.getenv("ENABLE_AZURE_MONITOR_TRACING", "")
    global enable_trace
    enable_trace = False
    if enable_trace_string == "":
        enable_trace = False
    else:
        enable_trace = str(enable_trace_string).lower() == "true"
    if enable_trace:
        logger.info("Tracing is enabled.")
        try:
            from azure.monitor.opentelemetry import configure_azure_monitor
        except ModuleNotFoundError:
            logger.error("Required libraries for tracing not installed.")
            logger.error("Please make sure azure-monitor-opentelemetry is installed.")
            exit()
    else:
        logger.info("Tracing is not enabled")

    directory = os.path.join(os.path.dirname(__file__), "static")
    app = fastapi.FastAPI(lifespan=lifespan)
    app.mount("/static", StaticFiles(directory=directory), name="static")
    
    # Mount React static files
    react_directory = os.path.join(os.path.dirname(__file__), "static/react")
    if os.path.exists(react_directory):
        app.mount("/assets", StaticFiles(directory=os.path.join(react_directory, "assets")), name="react-assets")

    from . import routes  # Import routes
    app.include_router(routes.router)

    # Serve React app for all other routes (SPA fallback)
    @app.get("/", response_class=HTMLResponse)
    @app.get("/{full_path:path}", response_class=HTMLResponse)
    async def serve_react_app(full_path: str = ""):
        """Serve the React app for all routes not handled by the API"""
        react_index_path = os.path.join(react_directory, "index.html")
        if os.path.exists(react_index_path):
            with open(react_index_path, "r", encoding="utf-8") as f:
                html_content = f.read()
            return HTMLResponse(content=html_content)
        else:
            # Fallback if React build doesn't exist
            return HTMLResponse(content="""
            <!DOCTYPE html>
            <html>
            <head>
                <title>AI Agents</title>
            </head>
            <body>
                <div id="react-root">
                    <h1>AI Agents API</h1>
                    <p>React frontend not built. Please run 'pnpm build' in the frontend directory.</p>
                    <p>API endpoints are available at:</p>
                    <ul>
                        <li><a href="/health">/health</a> - Health check</li>
                        <li><a href="/agent">/agent</a> - Agent details</li>
                        <li>/chat - Chat endpoint (POST)</li>
                        <li>/chat/history - Chat history (GET)</li>
                    </ul>
                </div>
            </body>
            </html>
            """)

    # Global exception handler for any unhandled exceptions
    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        logger.error("Unhandled exception occurred", exc_info=exc)
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal server error"}
        )
    
    return app
