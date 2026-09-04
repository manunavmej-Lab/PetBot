from __future__ import annotations

import json
import secrets
import socket
from dataclasses import dataclass, field
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from queue import SimpleQueue
from threading import Lock, Thread
from time import monotonic
from typing import Any
from urllib.parse import parse_qs, urlparse


@dataclass
class MobileDashboardState:
    """Copia segura de datos locales que la página móvil puede leer."""

    _status: dict[str, Any] = field(default_factory=dict)
    _camera_image: bytes | None = None
    _camera_sharing_until: float = 0.0
    _lock: Lock = field(default_factory=Lock)

    def update(self, status: dict[str, Any], camera_image: bytes | None) -> None:
        with self._lock:
            self._status = status
            self._camera_image = camera_image

    def status(self) -> dict[str, Any]:
        with self._lock:
            status = dict(self._status)
            status["camera_sharing"] = monotonic() < self._camera_sharing_until
            return status

    def camera_image(self) -> bytes | None:
        with self._lock:
            if monotonic() >= self._camera_sharing_until:
                return None
            return self._camera_image

    def enable_camera_sharing(self, seconds: int = 60) -> None:
        with self._lock:
            self._camera_sharing_until = monotonic() + seconds

    def disable_camera_sharing(self) -> None:
        with self._lock:
            self._camera_sharing_until = 0.0


class LocalMobileDashboard:
    def __init__(self, state: MobileDashboardState, actions: SimpleQueue[tuple[str, str]]) -> None:
        self._state = state
        self._actions = actions
        self._token = secrets.token_urlsafe(18)
        self._server = ThreadingHTTPServer(("0.0.0.0", 0), self._handler())
        self._thread = Thread(target=self._server.serve_forever, daemon=True)

    @property
    def url(self) -> str:
        return f"http://{_local_ip()}:{self._server.server_port}/?token={self._token}"

    def start(self) -> None:
        self._thread.start()

    def stop(self) -> None:
        self._server.shutdown()
        self._server.server_close()

    def _handler(self) -> type[BaseHTTPRequestHandler]:
        state = self._state
        actions = self._actions
        token = self._token

        class Handler(BaseHTTPRequestHandler):
            def do_GET(self) -> None:  # noqa: N802
                query = parse_qs(urlparse(self.path).query)
                if query.get("token", [""])[0] != token:
                    self.send_error(403, "Código de acceso inválido")
                    return
                path = urlparse(self.path).path
                if path == "/api/status":
                    self._send_json(state.status())
                elif path == "/camera.jpg":
                    image = state.camera_image()
                    if image is None:
                        self.send_error(503, "La cámara aún no ha enviado una imagen")
                    else:
                        self.send_response(200)
                        self.send_header("Content-Type", "image/jpeg")
                        self.send_header("Cache-Control", "no-store")
                        self.send_header("Content-Length", str(len(image)))
                        self.end_headers()
                        self.wfile.write(image)
                elif path == "/":
                    self._send_page()
                else:
                    self.send_error(404)

            def do_POST(self) -> None:  # noqa: N802
                query = parse_qs(urlparse(self.path).query)
                if query.get("token", [""])[0] != token or urlparse(self.path).path != "/api/action":
                    self.send_error(403, "Código de acceso inválido")
                    return
                size = int(self.headers.get("Content-Length", "0"))
                try:
                    payload = json.loads(self.rfile.read(size))
                    action = str(payload["action"])
                    text = str(payload.get("text", ""))
                except (ValueError, KeyError):
                    self.send_error(400, "Acción inválida")
                    return
                if action == "camera_start":
                    state.enable_camera_sharing()
                    self._send_json({"ok": True, "camera_sharing": True})
                    return
                if action == "camera_stop":
                    state.disable_camera_sharing()
                    self._send_json({"ok": True, "camera_sharing": False})
                    return
                if action not in {"jugar", "decir", "recuerda"} or (action in {"decir", "recuerda"} and not text.strip()):
                    self.send_error(400, "Acción no permitida")
                    return
                actions.put((action, text.strip()))
                self._send_json({"ok": True})

            def _send_json(self, payload: dict[str, Any]) -> None:
                content = json.dumps(payload).encode()
                self.send_response(200)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.send_header("Content-Length", str(len(content)))
                self.end_headers()
                self.wfile.write(content)

            def _send_page(self) -> None:
                page = _PAGE.encode()
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(page)))
                self.end_headers()
                self.wfile.write(page)

            def log_message(self, format: str, *args: object) -> None:
                return

        return Handler


def _local_ip() -> str:
    probe = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        probe.connect(("10.255.255.255", 1))
        return str(probe.getsockname()[0])
    except OSError:
        return "127.0.0.1"
    finally:
        probe.close()


_PAGE = """<!doctype html><html lang='es'><meta name='viewport' content='width=device-width, initial-scale=1'><title>Buvi</title><style>body{font-family:-apple-system,sans-serif;background:#fff;color:#111;margin:20px;max-width:640px}img{width:100%;background:#eee;border-radius:12px}button,input{font:inherit;padding:10px;margin:4px 0}#people{padding-left:20px}#camera{display:none}</style><h1 id='title'>Buvi</h1><button id='cameraButton' onclick='toggleCamera()'>Ver lo que ve Buvi (60 s)</button><img id='camera' alt='Vista temporal de cámara de Buvi'><h2>Estado</h2><div id='emotions'></div><h2>Personas conocidas</h2><ul id='people'></ul><button onclick="act('jugar')">Jugar con Buvi</button><h2>Hablar con Bulvi</h2><form onsubmit="say();return false"><input id='text' placeholder='Escribe a Buvi'><button>Enviar</button></form><h2>Guardar recuerdo</h2><form onsubmit="remember();return false"><input id='memory' placeholder='Ejemplo: Mi comida favorita es la pizza'><button>Guardar</button></form><script>const q=location.search;let viewing=false;async function load(){let s=await fetch('/api/status'+q).then(r=>r.json());title.textContent=s.pet_name;emotions.textContent=Object.entries(s.emotions).map(([k,v])=>k+': '+v).join(' · ');people.innerHTML=s.known_people.map(p=>'<li>'+p+'</li>').join('')||'<li>Nadie todavía</li>';if(viewing&&!s.camera_sharing){viewing=false;camera.style.display='none';cameraButton.textContent='Ver lo que ve Buvi (60 s)'}if(viewing)camera.src='/camera.jpg'+q+'&t='+Date.now()}async function act(action,text=''){return fetch('/api/action'+q,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({action,text})})}async function toggleCamera(){viewing=!viewing;await act(viewing?'camera_start':'camera_stop');camera.style.display=viewing?'block':'none';cameraButton.textContent=viewing?'Dejar de ver cámara':'Ver lo que ve Buvi (60 s)';if(viewing)load()}function say(){let x=text.value.trim();if(x){act('decir',x);text.value=''}}function remember(){let x=memory.value.trim();if(x){act('recuerda',x);memory.value=''}}load();setInterval(load,2000)</script></html>"""
