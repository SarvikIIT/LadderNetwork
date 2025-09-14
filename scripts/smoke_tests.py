#!/usr/bin/env python3
import json
import sys
from urllib import request, error

BASE_URL = "http://127.0.0.1:5000"


def post_json(path: str, payload: dict):
    data = json.dumps(payload).encode("utf-8")
    req = request.Request(
        BASE_URL + path,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with request.urlopen(req, timeout=15) as resp:
            code = resp.getcode()
            body = json.loads(resp.read().decode("utf-8"))
            return code, body
    except error.HTTPError as e:
        try:
            body = json.loads(e.read().decode("utf-8"))
        except Exception:
            body = {"error": str(e)}
        return e.code, body
    except Exception as e:
        return None, {"error": str(e)}


TESTS = [
    # name, payload, should_pass, expect_contains (for error text)
    ("RC", {"numerator": [1, 1], "denominator": [0, 1]}, True, None),
    ("LC", {"numerator": [3, 4, 1], "denominator": [0, 2, 1]}, True, None),
    ("Const", {"numerator": [1], "denominator": [1]}, True, None),
    ("Inductor", {"numerator": [0, 1], "denominator": [1]}, True, None),
    ("Capacitor", {"numerator": [1], "denominator": [0, 1]}, True, None),
    (
        "EvenOnlyQuadraticRequired",
        {"numerator": [3, 0, 4, 0, 1], "denominator": [0, 0, 2, 0, 1]},
        False,
        "requires quadratic",
    ),
]


def main() -> int:
    all_ok = True
    for name, payload, should_pass, expect_contains in TESTS:
        code, out = post_json("/api/process", payload)
        if should_pass:
            ok = code == 200 and isinstance(out, dict) and out.get("success") is True and out.get("image")
        else:
            msg = (out or {}).get("error", "").lower()
            ok = code == 400 and (expect_contains in msg if expect_contains else True)
        print(f"{name}: {'OK' if ok else 'FAIL'} -> code={code}, error={out.get('error') if isinstance(out, dict) else out}")
        all_ok = all_ok and ok
    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main())


