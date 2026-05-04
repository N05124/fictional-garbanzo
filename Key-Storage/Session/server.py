import os
import socket
import logging
import subprocess
import requests
from flask import Flask, request, jsonify, send_from_directory

log = logging.getLogger(__name__)

STATIC_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)) if '__file__' in dir() else os.getcwd(), "static")
app = Flask(__name__, static_folder=STATIC_DIR, static_url_path="/static")

DEFAULT_PORT    = 8080
DEFAULT_TIMEOUT = 10

# ---------------------------------------------------------------------------
# Frontend routes
# ---------------------------------------------------------------------------

@app.route("/")
def index():
    """Serve the frontend."""
    return send_from_directory(STATIC_DIR, "index.html")

# ---------------------------------------------------------------------------
# API routes
# ---------------------------------------------------------------------------

@app.route("/landing", methods=["POST"])
def landing():
    """Receive handshake from send_link."""
    data = request.get_json(silent=True)
    if not data or "key_hash" not in data:
        return jsonify({"error": "missing key_hash"}), 400
    log.info(f"Landing zone hit — key_hash: {data['key_hash']}")
    return jsonify({"status": "ready"}), 200

@app.route("/receive", methods=["POST"])
def receive():
    """Receive encrypted credential payload."""
    data = request.get_json(silent=True)
    if not data or "encrypted" not in data:
        return jsonify({"error": "missing encrypted payload"}), 400
    log.info("Credential received.")
    # todo: pass to validate_credentials + store_credentials
    return jsonify({"status": "received"}), 200

@app.route("/status", methods=["GET"])
def status():
    """Health check endpoint polled by the frontend."""
    return jsonify({"status": "online", "ip": get_local_ip()}), 200

# ---------------------------------------------------------------------------
# Transmit (client side)
# ---------------------------------------------------------------------------

def transmit(client_pkg: dict) -> bool:
    endpoint  = client_pkg.get("endpoint")
    encrypted = client_pkg.get("key")

    if not endpoint or not encrypted:
        log.error("transmit: missing 'endpoint' or 'key'")
        return False

    payload = {
        "encrypted": encrypted.hex() if isinstance(encrypted, bytes) else encrypted
    }

    try:
        response = requests.post(
            f"{endpoint}/receive",
            json=payload,
            timeout=DEFAULT_TIMEOUT,
        )
        response.raise_for_status()
        log.info(f"Credential transmitted — status {response.status_code}")
        return True

    except requests.exceptions.ConnectionError:
        log.error(f"transmit: could not reach {endpoint}")
    except requests.exceptions.Timeout:
        log.error(f"transmit: timed out after {DEFAULT_TIMEOUT}s")
    except requests.exceptions.HTTPError as e:
        log.error(f"transmit: server error: {e}")

    return False

# ---------------------------------------------------------------------------
# Server setup
# ---------------------------------------------------------------------------

def get_local_ip() -> str:
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        return s.getsockname()[0]
    finally:
        s.close()

def setup(ip: str) -> None:
    script = os.environ.get("SETUP_SCRIPT")
    if script:
        subprocess.run([script, ip], check=True)
    else:
        log.info("No SETUP_SCRIPT env var set — skipping external setup")

def start_server(host: str = "0.0.0.0", port: int = DEFAULT_PORT) -> None:
    log.info(f"Starting server on {host}:{port}")
    app.run(host=host, port=port)

def remote_browser(ip: str) -> None:
    confirm = input(f"Start server at {ip}:{DEFAULT_PORT}? [y/n]: ").strip().lower()
    if confirm != "y":
        print("Cancelled.")
        return
    setup(ip)
    start_server()

# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    local_ip = get_local_ip()
    print(f"Server will be available at: http://{local_ip}:{DEFAULT_PORT}")
    remote_browser(local_ip)
    