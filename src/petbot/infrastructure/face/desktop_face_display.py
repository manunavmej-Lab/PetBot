from __future__ import annotations

import os
import random
import tkinter as tk
from collections.abc import Callable
from queue import Empty, SimpleQueue

from petbot.domain.face.face_state import Expression, FaceState, Gaze, MouthState
from petbot.infrastructure.face import assets


class DesktopFaceDisplay:
    """Adaptador gráfico para Mac/PC; todas las animaciones usan Tk.after()."""

    WIDTH = 800
    HEIGHT = 480

    def __init__(self, title: str = "PETBOT — simulación") -> None:
        self._root = tk.Tk()
        self._root.title(title)
        self._root.resizable(False, False)
        if os.environ.get("PETBOT_FULLSCREEN") == "1":
            self._root.attributes("-fullscreen", True)
            self._root.overrideredirect(True)
            self._root.geometry(f"{self.WIDTH}x{self.HEIGHT}+0+0")
        self._canvas = tk.Canvas(self._root, width=self.WIDTH, height=self.HEIGHT, background=assets.BACKGROUND, highlightthickness=0)
        self._canvas.pack()
        self._state = FaceState()
        self._speaking_job: str | None = None
        self._actions: SimpleQueue[Callable[[], None]] = SimpleQueue()
        self._qr_photo: object | None = None
        self._qr_visible = False
        self._menu_visible = False
        self._menu_actions: dict[str, Callable[[], None]] = {}
        self._sleeping_menu_actions: dict[str, Callable[[], None]] = {}
        self._menu_buttons: list[tuple[tuple[int, int, int, int], Callable[[], None]]] = []
        self._info: tuple[str, list[str]] | None = None
        self._idle_blink_job: str | None = None
        self._idle_gaze_job: str | None = None
        self._canvas.bind("<Button-1>", self._on_touch)
        self._render()
        self._schedule_idle_blink()
        self._schedule_idle_gaze()

    def run(self) -> None:
        self._root.after(30, self._process_actions)
        self._root.mainloop()

    def close(self) -> None:
        self._root.destroy()

    def schedule(self, delay_ms: int, callback: Callable[[], None]) -> None:
        """Programa una acción de demo sin bloquear la interfaz."""
        self._root.after(delay_ms, callback)

    def enqueue(self, action: Callable[[], None]) -> None:
        """Permite solicitar cambios de cara desde otro hilo, como la consola."""
        self._actions.put(action)

    def show_mobile_qr(self, url: str) -> None:
        """Muestra un QR dentro de la pantalla para abrir el panel desde un móvil."""
        try:
            import qrcode
            from PIL import ImageTk
        except ImportError:
            return
        image = qrcode.make(url).resize((260, 260))
        self._qr_photo = ImageTk.PhotoImage(image)
        self._menu_visible = False
        self._info = None
        self._qr_visible = True
        self._render()

    def configure_touch_menu(self, actions: dict[str, Callable[[], None]], sleeping_actions: dict[str, Callable[[], None]] | None = None) -> None:
        self._menu_actions = actions
        self._sleeping_menu_actions = sleeping_actions or {}

    def show_info(self, title: str, lines: list[str]) -> None:
        self._menu_visible = False
        self._info = (title, lines)
        self._render()

    def _on_touch(self, event: tk.Event[tk.Misc]) -> None:
        if self._qr_visible:
            self._qr_visible = False
            self._render()
            return
        if self._info is not None:
            self._info = None
            self._render()
            return
        if self._menu_visible:
            for (left, top, right, bottom), action in self._menu_buttons:
                if left <= event.x <= right and top <= event.y <= bottom:
                    action()
                    if self._menu_visible:
                        self._menu_visible = False
                        self._render()
                    return
            self._menu_visible = False
            self._render()
            return
        if event.x >= self.WIDTH - 120 and event.y >= self.HEIGHT - 110:
            self._menu_visible = True
            self._render()

    def _process_actions(self) -> None:
        try:
            while True:
                self._actions.get_nowait()()
        except Empty:
            pass
        try:
            exists = self._root.winfo_exists()
        except tk.TclError:
            return
        if exists:
            self._root.after(30, self._process_actions)

    def _schedule_idle_blink(self) -> None:
        def blink_if_appropriate() -> None:
            if self._can_animate_idle():
                self.blink()
            self._schedule_idle_blink()

        self._idle_blink_job = self._root.after(random.randint(3_400, 6_800), blink_if_appropriate)

    def _schedule_idle_gaze(self) -> None:
        def glance_if_appropriate() -> None:
            if self._can_animate_idle() and random.random() < 0.7:
                direction = random.choice([Gaze.LEFT, Gaze.RIGHT])
                self.look_at(direction)
                self._root.after(random.randint(700, 1_400), self._return_gaze_to_center)
            self._schedule_idle_gaze()

        self._idle_gaze_job = self._root.after(random.randint(4_500, 8_000), glance_if_appropriate)

    def _return_gaze_to_center(self) -> None:
        if self._can_animate_idle():
            self.look_at(Gaze.CENTER)

    def _can_animate_idle(self) -> bool:
        return not self._menu_visible and self._info is None and not self._qr_visible and not self._state.sleeping

    def set_expression(self, expression: Expression) -> None:
        self._state = self._state.with_expression(expression)
        self._render()

    def blink(self) -> None:
        self._animate_eyes(left=True, right=True)

    def wink_left(self) -> None:
        self._animate_eyes(left=True, right=False)

    def wink_right(self) -> None:
        self._animate_eyes(left=False, right=True)

    def look_at(self, gaze: Gaze) -> None:
        self._state = FaceState(self._state.expression, gaze, self._state.mouth, self._state.eyes_closed, self._state.left_eye_closed, self._state.right_eye_closed, self._state.sleeping)
        self._render()

    def set_mouth_state(self, mouth: MouthState) -> None:
        self._state = FaceState(self._state.expression, self._state.gaze, mouth, self._state.eyes_closed, self._state.left_eye_closed, self._state.right_eye_closed, self._state.sleeping)
        self._render()

    def speak_animation(self, duration_ms: int = 1_000) -> None:
        if self._speaking_job is not None:
            self._root.after_cancel(self._speaking_job)
        remaining = duration_ms

        def animate() -> None:
            nonlocal remaining
            if remaining <= 0:
                self.set_mouth_state(MouthState.CLOSED)
                self._speaking_job = None
                return
            mouth = MouthState.OPEN if self._state.mouth is MouthState.CLOSED else MouthState.CLOSED
            self.set_mouth_state(mouth)
            remaining -= 160
            self._speaking_job = self._root.after(160, animate)

        animate()

    def sleep(self) -> None:
        self._state = FaceState(Expression.SLEEPY, self._state.gaze, MouthState.CLOSED, True, False, False, True)
        self._render()

    def wake(self) -> None:
        self._state = FaceState()
        self._render()

    def _animate_eyes(self, *, left: bool, right: bool) -> None:
        self._state = FaceState(self._state.expression, self._state.gaze, self._state.mouth, left and right, left, right, self._state.sleeping)
        self._render()
        self._root.after(180, self._open_eyes)

    def _open_eyes(self) -> None:
        self._state = FaceState(self._state.expression, self._state.gaze, self._state.mouth, False, False, False, self._state.sleeping)
        self._render()

    def _render(self) -> None:
        self._canvas.delete("all")
        if self._qr_visible:
            self._render_qr()
            return
        if self._info is not None:
            self._render_info()
            return
        if self._menu_visible:
            self._render_touch_menu()
            return
        self._canvas.create_text(400, 38, text=self._state.expression.value.upper(), fill=assets.TEXT_COLOR, font=("Helvetica", 16, "bold"))
        eye_y = 220
        offset = {Gaze.LEFT: -28, Gaze.CENTER: 0, Gaze.RIGHT: 28}[self._state.gaze]
        self._draw_buvi_eye(255, eye_y, offset, self._state.eyes_closed or self._state.left_eye_closed, mirrored=False)
        self._draw_buvi_eye(545, eye_y, offset, self._state.eyes_closed or self._state.right_eye_closed, mirrored=True)
        # Las fosas de Buvi se inclinan hacia el centro, no son óvalos horizontales.
        self._canvas.create_polygon(384, 252, 398, 256, 403, 264, 394, 266, 384, 260, fill=assets.PUPIL_COLOR, outline="", smooth=True)
        self._canvas.create_polygon(434, 252, 420, 256, 415, 264, 424, 266, 434, 260, fill=assets.PUPIL_COLOR, outline="", smooth=True)
        self._draw_mouth()
        self._canvas.create_oval(745, 426, 778, 459, fill="#ececec", outline="#a0a0a0")
        self._canvas.create_text(761, 442, text="⋮", fill="#555555", font=("Helvetica", 20, "bold"))

    def _render_touch_menu(self) -> None:
        self._canvas.create_rectangle(0, 0, self.WIDTH, self.HEIGHT, fill="#ffffff", outline="")
        self._canvas.create_text(400, 52, text="MENÚ DE BULVI", fill="#08090b", font=("Helvetica", 25, "bold"))
        entries = list((self._sleeping_menu_actions if self._state.sleeping else self._menu_actions).items())
        self._menu_buttons = []
        for index, (label, action) in enumerate(entries):
            column, row = index % 2, index // 2
            left, top = 85 + column * 335, 105 + row * 115
            right, bottom = left + 295, top + 82
            self._canvas.create_rectangle(left, top, right, bottom, fill="#b6345b", outline="#08090b", width=3)
            self._canvas.create_text((left + right) // 2, (top + bottom) // 2, text=label, fill="#ffffff", font=("Helvetica", 20, "bold"))
            self._menu_buttons.append(((left, top, right, bottom), action))
        self._canvas.create_text(400, 448, text="Toca fuera de un botón para cerrar.", fill="#555555", font=("Helvetica", 14))

    def _render_info(self) -> None:
        title, lines = self._info
        self._canvas.create_rectangle(0, 0, self.WIDTH, self.HEIGHT, fill="#ffffff", outline="")
        self._canvas.create_text(400, 60, text=title, fill="#08090b", font=("Helvetica", 25, "bold"))
        for index, line in enumerate(lines):
            self._canvas.create_text(400, 135 + index * 55, text=line, fill="#333333", font=("Helvetica", 19))
        self._canvas.create_text(400, 430, text="Toca la pantalla para volver con Bulvi.", fill="#555555", font=("Helvetica", 14))

    def _render_qr(self) -> None:
        self._canvas.create_rectangle(0, 0, self.WIDTH, self.HEIGHT, fill="#ffffff", outline="")
        self._canvas.create_text(400, 55, text="ABRIR PANEL MÓVIL", fill="#08090b", font=("Helvetica", 25, "bold"))
        if self._qr_photo is not None:
            self._canvas.create_image(400, 230, image=self._qr_photo)
        self._canvas.create_text(400, 400, text="Escanea desde la misma Wi‑Fi.", fill="#333333", font=("Helvetica", 17))
        self._canvas.create_text(400, 438, text="Toca la pantalla para volver con Bulvi.", fill="#555555", font=("Helvetica", 14))

    def _draw_buvi_eye(self, x: int, y: int, pupil_offset: int, closed: bool, *, mirrored: bool) -> None:
        """Ojo de Buvi: contorno asimétrico blanco, iris borgoña y brillo blanco."""
        if closed:
            self._canvas.create_line(x - 70, y + 20, x + 70, y + 30, fill=assets.FACE_COLOR, width=16, capstyle=tk.ROUND)
            return
        direction = -1 if mirrored else 1

        def point(horizontal: int, vertical: int) -> tuple[int, int]:
            return x + direction * horizontal, y + vertical

        # Contorno alto y algo inclinado, igual que los ojos de la referencia de Buvi.
        outer = [
            point(-78, -52), point(-63, -78), point(-42, -90), point(-16, -84),
            point(12, -52), point(23, -13), point(24, 51), point(-13, 61),
            point(-62, 50), point(-86, 33), point(-92, -8),
        ]
        self._canvas.create_polygon(outer, fill="#ffffff", outline="#08090b", width=7, smooth=True, splinesteps=18)
        # El borgoña nace en el borde interior y cubre algo más de media superficie.
        iris = [
            point(-44 + pupil_offset, 46), point(-43 + pupil_offset, 8), point(-30 + pupil_offset, -28),
            point(-14 + pupil_offset, -54), point(7 + pupil_offset, -61), point(20 + pupil_offset, -30), point(24 + pupil_offset, 2),
            point(21 + pupil_offset, 52), point(-14 + pupil_offset, 57),
        ]
        self._canvas.create_polygon(iris, fill="#b6345b", outline="", smooth=True, splinesteps=18)
        # Brillo en la mitad interior del ojo, centrado verticalmente.
        self._canvas.create_oval(*point(-4 + pupil_offset, -28), *point(17 + pupil_offset, 9), fill="#ffffff", outline="")

    def _draw_mouth(self) -> None:
        if self._state.mouth is MouthState.OPEN:
            self._canvas.create_oval(355, 335, 445, 390, fill=assets.PUPIL_COLOR, outline="")
        elif self._state.mouth is MouthState.FROWN or self._state.expression in {Expression.SAD, Expression.ANNOYED}:
            self._canvas.create_arc(345, 340, 455, 405, start=25, extent=130, style=tk.ARC, outline=assets.FACE_COLOR, width=12)
        else:
            self._draw_buvi_smile()

    def _draw_buvi_smile(self) -> None:
        """Sonrisa base de Buvi: amplia, borgoña, con colmillos y detalle inferior."""
        mouth = [
            (105, 320), (190, 346), (300, 342), (400, 370), (500, 342),
            (610, 346), (695, 320), (655, 375), (585, 418), (495, 442),
            (400, 450), (305, 442), (215, 418), (145, 375),
        ]
        self._canvas.create_polygon(mouth, fill="#b6345b", outline="#08090b", width=7, smooth=True, splinesteps=20)
        self._canvas.create_polygon(170, 336, 198, 344, 185, 367, fill="#ffffff", outline="#08090b", width=4, smooth=True)
        self._canvas.create_polygon(630, 336, 602, 344, 615, 367, fill="#ffffff", outline="#08090b", width=4, smooth=True)
        self._canvas.create_arc(285, 395, 515, 465, start=195, extent=150, style=tk.ARC, outline="#08090b", width=5)
