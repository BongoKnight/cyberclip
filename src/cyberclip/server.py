from textual_serve.server import Server
from pathlib import Path

path = Path(__file__).parent / "app.py"
server = Server(f"python {Path(__file__).parent / "app.py"}", host="0.0.0.0")
server.serve()