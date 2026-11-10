"""
run_server.py
─────────────
Dual-Stack (IPv4 + IPv6) Server Launcher for Student Wellbeing Triage Engine.

Binds to both 0.0.0.0 (IPv4) and :: (IPv6) on Port 8000.
Ensures seamless browser compatibility on Windows (resolving both 'localhost' and '127.0.0.1').
"""

import sys
import socket
import logging
import uvicorn
from app.main import app
from app.config import LOG_LEVEL

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("server_runner")

def run():
    port = 8000
    sockets = []

    # 1. IPv4 Socket (127.0.0.1 / 0.0.0.0)
    try:
        s4 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s4.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s4.bind(('0.0.0.0', port))
        s4.listen(256)
        sockets.append(s4)
        logger.info("Bound IPv4 socket on 0.0.0.0:%d", port)
    except Exception as exc:
        logger.warning("Could not bind IPv4 socket: %s", exc)

    # 2. IPv6 Socket (::1 / ::)
    try:
        s6 = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
        s6.setsockopt(socket.IPPROTO_IPV6, socket.IPV6_V6ONLY, 1)
        s6.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s6.bind(('::', port))
        s6.listen(256)
        sockets.append(s6)
        logger.info("Bound IPv6 socket on [::]:%d", port)
    except Exception as exc:
        logger.warning("Could not bind IPv6 socket: %s", exc)

    config = uvicorn.Config(
        app,
        log_level=LOG_LEVEL.lower(),
        access_log=True,
    )
    server = uvicorn.Server(config)
    logger.info("FastAPI Server running cleanly on Port %d (Dual IPv4/IPv6)", port)
    logger.info("Access in browser at: http://localhost:%d", port)
    logger.info("Access API docs at: http://localhost:%d/docs", port)

    if sockets:
        server.run(sockets=sockets)
    else:
        uvicorn.run("app.main:app", host="0.0.0.0", port=port, log_level=LOG_LEVEL.lower())

if __name__ == "__main__":
    run()
