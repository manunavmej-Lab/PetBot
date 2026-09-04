import json
from queue import SimpleQueue
from urllib.parse import urlparse
from urllib.request import Request, urlopen

from petbot.infrastructure.mobile.local_dashboard import LocalMobileDashboard, MobileDashboardState


def test_camera_image_is_private_until_temporarily_enabled() -> None:
    state = MobileDashboardState()
    state.update({"pet_name": "Buvi"}, b"image")

    assert state.camera_image() is None
    state.enable_camera_sharing()
    assert state.camera_image() == b"image"
    state.disable_camera_sharing()
    assert state.camera_image() is None


def test_mobile_can_queue_a_free_form_memory() -> None:
    actions: SimpleQueue[tuple[str, str]] = SimpleQueue()
    dashboard = LocalMobileDashboard(MobileDashboardState(), actions)
    dashboard.start()
    parsed = urlparse(dashboard.url)
    request = Request(
        f"http://127.0.0.1:{parsed.port}/api/action?{parsed.query}",
        data=json.dumps({"action": "recuerda", "text": "Mi comida favorita es la pizza"}).encode(),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urlopen(request) as response:
            assert response.status == 200
        assert actions.get_nowait() == ("recuerda", "Mi comida favorita es la pizza")
    finally:
        dashboard.stop()
