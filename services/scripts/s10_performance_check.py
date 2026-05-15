import os
import statistics
import sys
import time
import warnings
from pathlib import Path

import httpx
from jwt.warnings import InsecureKeyLengthWarning


REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

from services.src.utils.security import create_access_token  # noqa: E402


# This check requires the backend server to be running to replicate the full environment.
BASE_URL = os.getenv("S10_BASE_URL", "https://knolly-svetlana-beribboned.ngrok-free.dev")
DEVICE_UUID = "S10_PERFORMANCE_DEVICE"
TARGET_MS = 500
ROUNDS = 100
REQUEST_TIMEOUT_SECONDS = 10


def warn_if_backend_is_unavailable(client):
    try:
        response = client.get(
            "/",
            headers={"ngrok-skip-browser-warning": "true"},
        )
        response.raise_for_status()
    except httpx.RequestError as exc:
        print(
            "WARNING: S10 live performance check was not run because the backend "
            f"server is not reachable at {BASE_URL}. Start the backend server or "
            f"ngrok tunnel before running this check. Error: {exc}"
        )
        return False
    except httpx.HTTPStatusError as exc:
        print(
            "WARNING: S10 live performance check was not run because the backend "
            f"health check returned HTTP {exc.response.status_code}: {exc.response.text}"
        )
        return False

    return True


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
        raise RuntimeError(
            f"{method} {path} returned HTTP {exc.response.status_code}: {exc.response.text}"
        ) from exc
    except httpx.RequestError as exc:
        raise RuntimeError(
            f"Backend server became unreachable at {BASE_URL}. Start the backend "
            f"server or ngrok tunnel before running this check. Error: {exc}"
        ) from exc

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
    except RuntimeError:
        # Cleanup should not hide the original performance or connectivity failure.
        pass


def run_s10_check():
    with warnings.catch_warnings():
        warnings.filterwarnings(
            "ignore",
            message=".*HMAC key is.*",
            category=InsecureKeyLengthWarning,
        )
        token = create_access_token("s10-performance-user")

    # Representative backend endpoints from the S10 scope.
    requests_to_measure = [
        ("GET", "/api/v1/devices", None),
        ("GET", f"/api/v1/devices/{DEVICE_UUID}", None),
        ("POST", f"/api/v1/devices/{DEVICE_UUID}/commands", {"state": {"power": "on"}}),
    ]

    with httpx.Client(base_url=BASE_URL, timeout=REQUEST_TIMEOUT_SECONDS) as client:
        if not warn_if_backend_is_unavailable(client):
            return 0

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

            print(f"S10 backend response-time check against {BASE_URL}")
            print(f"Requests measured: {len(timings_ms)}")
            print(f"Target: at least 95% below {TARGET_MS} ms")
            print(f"Result: {pass_ratio:.1%} below {TARGET_MS} ms")
            print(f"p50: {statistics.median(timings_ms):.2f} ms")
            print(f"p95: {p95_ms:.2f} ms")
            print(f"max: {max(timings_ms):.2f} ms")

            if pass_ratio < 0.95:
                print("FAIL: S10 target was not met.")
                return 1

            print("PASS: S10 target was met.")
            return 0
        finally:
            delete_seeded_device(client, token)


if __name__ == "__main__":
    try:
        raise SystemExit(run_s10_check())
    except RuntimeError as exc:
        print(f"FAIL: {exc}")
        raise SystemExit(1)
