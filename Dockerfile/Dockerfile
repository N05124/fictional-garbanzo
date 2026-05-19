FROM python:3.12-slim

# -----------------------------
# Core environment settings
# -----------------------------
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    JUPYTER_TOKEN=mytoken123 \
    XDG_CACHE_HOME=/workspace/.cache \
    XDG_CONFIG_HOME=/workspace/.config \
    XDG_DATA_HOME=/workspace/.local

# -----------------------------
# System dependencies
# -----------------------------
RUN apt-get update && apt-get install -y \
    build-essential \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# -----------------------------
# Create user
# -----------------------------
RUN useradd -ms /bin/bash jupyter

# -----------------------------
# Workspace setup
# -----------------------------
WORKDIR /workspace

RUN mkdir -p /workspace/.local /workspace/.config /workspace/.cache && \
    chown -R jupyter:jupyter /workspace

# -----------------------------
# Install Python deps
# -----------------------------
COPY requirements.txt .

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# -----------------------------
# Switch to non-root user
# -----------------------------
USER jupyter

EXPOSE 8888

# -----------------------------
# Startup command
# -----------------------------
CMD sh -c '\
URL="http://localhost:8888/lab?token=$JUPYTER_TOKEN"; \
echo ""; \
echo "=================================================="; \
echo " JupyterLab ready"; \
echo ""; \
echo " $URL"; \
echo ""; \
echo "=================================================="; \
echo ""; \
exec jupyter lab \
  --ip=0.0.0.0 \
  --port=8888 \
  --no-browser \
  --ServerApp.token="$JUPYTER_TOKEN" \
  --ServerApp.root_dir=/workspace \
  --ServerApp.terminals_enabled=True \
  --ServerApp.allow_remote_access=True'