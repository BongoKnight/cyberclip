from textual_serve.server import Server
from pathlib import Path

path = Path(__file__).parent / "app.py"
server = Server("python.exe " + str(path.absolute()))
server.serve()