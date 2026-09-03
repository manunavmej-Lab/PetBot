from __future__ import annotations

from petbot.domain.face.face_state import Expression, Gaze
from petbot.infrastructure.face.desktop_face_display import DesktopFaceDisplay


def main() -> None:
    face = DesktopFaceDisplay()
    face.set_expression(Expression.HAPPY)
    face.schedule(600, face.blink)
    face.schedule(1_200, lambda: face.look_at(Gaze.LEFT))
    face.schedule(1_800, face.wink_right)
    face.schedule(2_400, face.speak_animation)
    face.schedule(3_800, lambda: face.set_expression(Expression.SURPRISED))
    face.run()


if __name__ == "__main__":
    main()
