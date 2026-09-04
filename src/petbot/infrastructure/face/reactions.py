from __future__ import annotations

from petbot.domain.face.face_state import Expression, Gaze
from petbot.infrastructure.face.desktop_face_display import DesktopFaceDisplay


class DesktopFaceReactions:
    """Traduce interacciones del cerebro a reacciones visuales de escritorio."""

    def __init__(self, display: DesktopFaceDisplay) -> None:
        self._display = display

    def on_start(self) -> None:
        self._display.set_expression(Expression.NEUTRAL)

    def on_play(self) -> None:
        self._display.enqueue(self._show_play_reaction)

    def on_expression(self, expression: Expression) -> None:
        self._display.enqueue(lambda: self._show_expression(expression))

    def on_autonomous_expression(self, expression: Expression) -> None:
        """Estado de fondo: permanece hasta que la autonomía decida otro."""
        self._display.enqueue(lambda: self._display.set_expression(expression))

    def on_blink(self) -> None:
        self._display.enqueue(self._display.blink)

    def close(self) -> None:
        self._display.enqueue(self._display.close)

    def _show_play_reaction(self) -> None:
        self._display.set_expression(Expression.EXCITED)
        self._display.blink()
        self._display.look_at(Gaze.LEFT)
        self._display.speak_animation(800)
        self._display.schedule(1_500, self._return_to_neutral)

    def _show_expression(self, expression: Expression) -> None:
        self._display.set_expression(expression)
        if expression is not Expression.NEUTRAL:
            self._display.schedule(2_000, lambda: self._display.set_expression(Expression.NEUTRAL))

    def _return_to_neutral(self) -> None:
        self._display.look_at(Gaze.CENTER)
        self._display.set_expression(Expression.HAPPY)
        self._display.schedule(900, lambda: self._display.set_expression(Expression.NEUTRAL))
