from flask import jsonify


def ok(data=None, status=200):
    return jsonify({"ok": True, "data": data}), status


def fail(message: str, status=400, code: str | None = None):
    payload = {"ok": False, "error": {"message": message}}
    if code:
        payload["error"]["code"] = code
    return jsonify(payload), status

