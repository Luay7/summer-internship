import io
from contextlib import redirect_stdout
from unittest.mock import patch

import requests

import checker


class FakeResponse:
    def __init__(self, status_code=200, text=""):
        self.status_code = status_code
        self.text = text

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        return False

    def raise_for_status(self):
        if self.status_code >= 400:
            error = requests.exceptions.HTTPError(f"HTTP {self.status_code}")
            error.response = self
            raise error


def capture(function, *args):
    output = io.StringIO()
    with redirect_stdout(output):
        function(*args)
    return output.getvalue()


def check_case(name, expected, function):
    try:
        actual = function()
        passed = expected in actual
    except Exception as error:
        actual = f"Unexpected exception: {error}"
        passed = False

    print(f"CASE: {name}")
    print(f"Expected: {expected}")
    print(f"Result: {'Passed' if passed else 'Failed'}")
    if not passed:
        print(f"Actual: {actual.strip()}")
    print("----------------------------------------")
    return passed


def head_retry_case(first_error, retry_result, expected, get_result=None):
    head_effects = [first_error, retry_result]
    get_patch = patch("checker.requests.get", return_value=FakeResponse(get_result)) if get_result is not None else patch("checker.requests.get")

    with patch("checker.requests.head", side_effect=head_effects), get_patch:
        return capture(checker.check_link, "http://test.local/link")


def get_retry_case(first_error, retry_result, expected):
    with patch("checker.requests.get", side_effect=[first_error, retry_result]):
        return capture(checker.verify_with_get, "http://test.local/link", "HEAD 403")


def main():
    timeout = requests.exceptions.Timeout("timeout")
    connection_error = requests.exceptions.ConnectionError("connection error")
    request_error = requests.exceptions.RequestException("request error")

    cases = [
        (
            "Initial page timeout",
            "[FATAL ERROR] The request timed out.",
            lambda: capture_with_patch("checker.requests.get", timeout, checker.fetch_page, "http://test.local"),
        ),
        (
            "Initial page HTTP 404",
            "HTTP Status: 404",
            lambda: capture_with_patch("checker.requests.get", FakeResponse(404), checker.fetch_page, "http://test.local/404"),
        ),
        (
            "Initial page connection error",
            "[FATAL ERROR] Failed to connect",
            lambda: capture_with_patch("checker.requests.get", connection_error, checker.fetch_page, "http://test.local"),
        ),
        (
            "Initial page unexpected request error",
            "[FATAL ERROR] An unexpected network error occurred.",
            lambda: capture_with_patch("checker.requests.get", request_error, checker.fetch_page, "http://test.local"),
        ),
        (
            "HEAD timeout then HEAD 200",
            "[OK]",
            lambda: head_retry_case(timeout, FakeResponse(200), "[OK]"),
        ),
        (
            "HEAD timeout then HEAD 404",
            "[DEAD]",
            lambda: head_retry_case(timeout, FakeResponse(404), "[DEAD]"),
        ),
        (
            "HEAD timeout then HEAD 503",
            "[UNAVAILABLE]",
            lambda: head_retry_case(timeout, FakeResponse(503), "[UNAVAILABLE]"),
        ),
        (
            "HEAD timeout then HEAD 429 then GET 200",
            "HEAD TIMEOUT -> HEAD 429 -> GET 200",
            lambda: head_retry_case(timeout, FakeResponse(429), "PROTECTED", 200),
        ),
        (
            "HEAD timeout twice",
            "[TIMEOUT]",
            lambda: head_retry_case(timeout, timeout, "[TIMEOUT]"),
        ),
        (
            "HEAD timeout then retry connection error",
            "HEAD TIMEOUT -> HEAD ERROR",
            lambda: head_retry_case(timeout, connection_error, "[ERROR]"),
        ),
        (
            "HEAD immediate connection error",
            "HEAD ERROR",
            lambda: capture_with_patch("checker.requests.head", connection_error, checker.check_link, "http://test.local/link"),
        ),
        (
            "GET timeout then GET 200",
            "GET TIMEOUT -> GET 200",
            lambda: get_retry_case(timeout, FakeResponse(200), "PROTECTED"),
        ),
        (
            "GET timeout then GET 404",
            "GET TIMEOUT -> GET 404",
            lambda: get_retry_case(timeout, FakeResponse(404), "DEAD"),
        ),
        (
            "GET timeout then GET 503",
            "GET TIMEOUT -> GET 503",
            lambda: get_retry_case(timeout, FakeResponse(503), "UNAVAILABLE"),
        ),
        (
            "GET timeout then GET 429",
            "GET TIMEOUT -> GET 429",
            lambda: get_retry_case(timeout, FakeResponse(429), "BLOCKED"),
        ),
        (
            "GET timeout twice",
            "GET TIMEOUT -> GET TIMEOUT",
            lambda: get_retry_case(timeout, timeout, "TIMEOUT"),
        ),
        (
            "GET timeout then retry connection error",
            "GET TIMEOUT -> GET ERROR",
            lambda: get_retry_case(timeout, connection_error, "BLOCKED"),
        ),
        (
            "GET immediate connection error",
            "HEAD 403 -> GET ERROR",
            lambda: capture_with_patch("checker.requests.get", connection_error, checker.verify_with_get, "http://test.local/link", "HEAD 403"),
        ),
    ]

    passed = 0
    for name, expected, function in cases:
        if check_case(name, expected, function):
            passed += 1

    print(f"BRANCH TEST SUMMARY: {passed}/{len(cases)} Passed")
    return 0 if passed == len(cases) else 1


def capture_with_patch(target, result, function, *args):
    if isinstance(result, BaseException):
        context = patch(target, side_effect=result)
    else:
        context = patch(target, return_value=result)

    with context:
        return capture(function, *args)


if __name__ == "__main__":
    raise SystemExit(main())


