from petbot.domain.face.face_state import Expression, FaceState, Gaze


def test_expression_transition_preserves_gaze() -> None:
    state = FaceState(gaze=Gaze.LEFT)

    changed = state.with_expression(Expression.HAPPY)

    assert changed.expression is Expression.HAPPY
    assert changed.gaze is Gaze.LEFT


def test_sleepy_expression_marks_face_as_sleeping() -> None:
    state = FaceState().with_expression(Expression.SLEEPY)

    assert state.sleeping
