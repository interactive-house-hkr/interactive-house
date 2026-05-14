import statistics
import time

import httpx
import pytest

from services.src.utils.security import create_access_token


# This test requires the backend server to be running to replicate the full environment.
BASE_URL = "https://knolly-svetlana-beribboned.ngrok-free.dev"
DEVICE_UUID = "S10_PERFORMANCE_DEVICE"
TARGET_MS = 500
ROUNDS = 100
REQUEST_TIMEOUT_SECONDS = 10


def skip_if_backend_is_unavailable(client):
    try:
        response = client.get(
            "/",
            headers={"ngrok-skip-browser-warning": "true"},
        )
        response.raise_for_status()
    except httpx.RequestError as exc:
        pytest.skip(
            f"S10 live performance test skipped because the backend server is not reachable at "
            f"{BASE_URL}. Start the backend server or ngrok tunnel before running this test. "
            f"Error: {exc}"
        )
    except httpx.HTTPStatusError as exc:
        pytest.skip(
            f"S10 live performance test skipped because the backend health check returned "
            f"HTTP {exc.response.status_code}: {exc.response.text}"
        )


def send_request(client, method, path, body=None, token=None):
    headers = {
        "ngrok-skip-browser-warning": "true",
        "User-Agent": "interactive-house-s10-performance-check",
    }

    if token:
        headers["Authorization"] = f"Bearer {token}"

    start = time.perf_counter()

    try:
        response = client.request(
            method,
            path,
            json=body,
            headers=headers,
        )
        response.raise_for_status()
    except httpx.HTTPStatusError as exc:
        pytest.fail(
            f"{method} {path} returned HTTP {exc.response.status_code}: {exc.response.text}"
        )
    except httpx.RequestError as exc:
        pytest.skip(
            f"S10 live performance test skipped because the backend server became unreachable at "
            f"{BASE_URL}. Start the backend server or ngrok tunnel before running this test. "
            f"Error: {exc}"
        )

    return (time.perf_counter() - start) * 1000


def seed_rest_device(client):
    # The gateway route represents a REST device registering with the backend.
    # This keeps the measured command endpoint focused on backend accept/queue time,
    # not on waiting for a physical device to poll and execute the command.
    payload = {
        "devices": {
            "fan": {
                "device_uuid": DEVICE_UUID,
                "type": "fan",
                "transport": {"mode": "rest"},
                "capabilities": {
                    "power": {
                        "type": "boolean",
                        "writable": True,
                    }
                },
                "state": {"power": "off"},
                "status": {},
            }
        }
    }

    send_request(client, "POST", "/api/v1/device-gateway/connect", payload)


def delete_seeded_device(client, token):
    # Deleting the seeded device also deletes its pending command queue in device_store.
    try:
        send_request(client, "DELETE", f"/api/v1/devices/{DEVICE_UUID}", token=token)
    except pytest.fail.Exception:
        # Cleanup should not hide the original performance or connectivity failure.
        pass


@pytest.mark.filterwarnings("ignore:.*HMAC key is.*:jwt.warnings.InsecureKeyLengthWarning")
def test_s10_live_backend_responses_under_500ms_for_95_percent():
    token = create_access_token("s10-performance-user")

    # Representative backend endpoints from the S10 scope.
    requests_to_measure = [
        ("GET", "/api/v1/devices", None),
        ("GET", f"/api/v1/devices/{DEVICE_UUID}", None),
        ("POST", f"/api/v1/devices/{DEVICE_UUID}/commands", {"state": {"power": "on"}}),
    ]

    with httpx.Client(base_url=BASE_URL, timeout=REQUEST_TIMEOUT_SECONDS) as client:
        skip_if_backend_is_unavailable(client)
        seed_rest_device(client)

        try:
            timings_ms = []

            # Send repeated real HTTP requests so the result reflects normal backend API
            # response time against the running server.
            for _ in range(ROUNDS):
                for method, path, body in requests_to_measure:
                    timings_ms.append(send_request(client, method, path, body, token=token))

            timings_ms.sort()

            below_target = [ms for ms in timings_ms if ms < TARGET_MS]
            pass_ratio = len(below_target) / len(timings_ms)
            p95_index = int(len(timings_ms) * 0.95) - 1
            p95_ms = timings_ms[p95_index]

            # Keep useful performance numbers in the assertion message so failed CI/test
            # output can be referenced when evaluating S10.
            assert pass_ratio >= 0.95, (
                f"Only {pass_ratio:.1%} of backend responses were below {TARGET_MS} ms. "
                f"p50={statistics.median(timings_ms):.2f} ms, "
                f"p95={p95_ms:.2f} ms, "
                f"max={max(timings_ms):.2f} ms, "
                f"requests={len(timings_ms)}"
            )
        finally:
            delete_seeded_device(client, token)
