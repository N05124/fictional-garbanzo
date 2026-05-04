import subprocess
import logging

log = logging.getLogger(__name__)

DEFAULT_SCRIPT  = "bash ./ssh-script.sh"
DEFAULT_TIMEOUT = 30  # seconds


def ssh(
    username: str,
    ip: str,
    script: str  = DEFAULT_SCRIPT,
    port: int    = 22,
    key_path: str = None,
) -> bool:
    """
    Open an SSH connection and execute a remote script.

    Args:
        username:  remote user
        ip:        target IP or hostname
        script:    command to run on remote (default: bash ./ssh-script.sh)
        port:      SSH port (default: 22)
        key_path:  path to private key file — uses ssh-agent if None

    Returns:
        True on success, False on failure

    Requirements:
        - Port 22 open on target, or explicit permit rule:
            sudo iptables -I INPUT -p tcp -s <your_ip> --dport 22 -j ACCEPT
        - Remote script ./ssh-script.sh must exist on target machine

    macOS pf note:
        To allow outbound SSH ensure pf is not blocking port 22:
            sudo pfctl -f /etc/pf.conf
    """
    cmd = ["ssh", "-p", str(port)]

    if key_path:
        cmd += ["-i", key_path]

    cmd += [
        "-o", "StrictHostKeyChecking=accept-new",  # auto-accept new host keys
        "-o", f"ConnectTimeout={DEFAULT_TIMEOUT}",
        f"{username}@{ip}",
        script,
    ]

    log.info(f"SSH → {username}@{ip}:{port} running: '{script}'")

    try:
        result = subprocess.run(
            cmd,
            check=True,
            capture_output=True,
            text=True,
            timeout=DEFAULT_TIMEOUT,
        )
        if result.stdout:
            log.info(f"stdout:\n{result.stdout.strip()}")
        if result.stderr:
            log.warning(f"stderr:\n{result.stderr.strip()}")
        return True

    except subprocess.CalledProcessError as e:
        log.error(f"SSH command failed (exit {e.returncode}):\n{e.stderr.strip()}")
    except subprocess.TimeoutExpired:
        log.error(f"SSH timed out after {DEFAULT_TIMEOUT}s")
    except FileNotFoundError:
        log.error("'ssh' binary not found — is OpenSSH installed?")

    return False


def get_local_username() -> str:
    """Return current OS username."""
    result = subprocess.run("whoami", capture_output=True, text=True)
    return result.stdout.strip()


def get_local_ip(interface: str = "en0") -> str:
    """Return IP of the given network interface (macOS default: en0)."""
    result = subprocess.run(
        ["ipconfig", "getifaddr", interface],
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()