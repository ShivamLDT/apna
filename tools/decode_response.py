"""
Decode and compare responses from /clientnodes (Endpoints page) and /restore_nodes (Restore page).
Optionally call POST /restore with action=fetch to verify restore data (e.g. GDrive backups).

Usage:
  python tools/decode_response.py <base_url> <access_token> [--plain]
  python tools/decode_response.py <base_url> <access_token> --restore [agent_name]
      [--restore-action fetch|browse|restore] [--restore-payload <json|@file>]

  --plain           Use Bearer token only (no handshake/decrypt). Use when server returns plain JSON.
  --restore         Call POST /restore and decode response (default agent: DESKTOP-F1DRACU).
  --restore-action  Override restore action (default: fetch). Examples: fetch, browse, restore.
  --restore-payload JSON string or @path to a JSON file to use as the restore body.

Example:
  python tools/decode_response.py http://127.0.0.1:53335 <your_access_token>
  python tools/decode_response.py http://127.0.0.1:53335 <your_access_token> --restore
  python tools/decode_response.py http://127.0.0.1:53335 <your_access_token> --restore DESKTOP-F1DRACU
  python tools/decode_response.py http://127.0.0.1:53335 <your_access_token> --restore \
    --restore-action restore --restore-payload @tools/restore_payload.json

RCA (Root Cause Analysis) – why Restore page showed Offline while Endpoints showed Online:
  1. Different data sources: /clientnodes iterates over all nodes in clientnodes (from clientnodes_x).
     /restore_nodes only returns nodes from job records (fetch_nodes_as_json) that are in agent_activation_keys.
  2. Online check input: Both call is_less_than_2_minutes(). /clientnodes passes match["ipAddress"] (raw).
     /restore_nodes was passing _normalize_ip_url(x.get("ipAddress")) – a different string when stored
     value had no scheme (e.g. 10.109.164.78:7777), so is_client_online() could get different results.
  3. URL without scheme: is_client_online() uses urlparse(); for "10.109.164.78:7777" (no http://)
     hostname was None, so the check failed. /clientnodes could still show Online if stored value
     had "http://"; /restore_nodes normalized to "http://" but then is_less_than_2_minutes() exception
     path uses clientnodes_x[timestamp] – key mismatch if keys are raw ip:port.
  Fixes applied: (1) is_client_online() now handles URL without scheme (host:port). (2) restore_nodes
  now passes the same raw ipAddress string as clientnodes for the online check, then uses normalized
  URL only in the response payload.
"""
import argparse
import base64
import json
import os
import sys

from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError


def main():
    parser = argparse.ArgumentParser(description="Decode encrypted API responses.")
    parser.add_argument("base_url")
    parser.add_argument("access_token")
    parser.add_argument("--plain", action="store_true")
    parser.add_argument("--restore", nargs="?", const="")
    parser.add_argument("--restore-action", dest="restore_action")
    parser.add_argument("--restore-payload", dest="restore_payload")
    args = parser.parse_args()

    plain_mode = args.plain
    do_restore = args.restore is not None
    restore_agent = args.restore or "DESKTOP-F1DRACU"
    restore_action = args.restore_action
    restore_payload_arg = args.restore_payload

    base_url = args.base_url.rstrip("/")
    token = args.access_token

    def http_json(method, url, body=None, headers=None, timeout=10):
        data = None
        if body is not None:
            data = json.dumps(body).encode("utf-8")
        req = Request(url, data=data, method=method.upper())
        for k, v in (headers or {}).items():
            req.add_header(k, v)
        if body is not None:
            req.add_header("Content-Type", "application/json")
        try:
            with urlopen(req, timeout=timeout) as resp:
                raw = resp.read()
                return resp.status, raw
        except HTTPError as e:
            return e.code, e.read()
        except URLError as e:
            raise RuntimeError(f"Request failed: {e}") from e

    if plain_mode:
        headers = {"Authorization": f"Bearer {token}", "Accept": "application/json"}
        print("(using --plain: Bearer token only, no handshake)")
    else:
        try:
            from cryptography.hazmat.primitives import serialization
            from cryptography.hazmat.primitives.asymmetric import padding
            from cryptography.hazmat.primitives.ciphers.aead import AESGCM
        except ImportError:
            print("cryptography not installed. Use --plain to call endpoints with Bearer token only.")
            sys.exit(1)
        status, raw = http_json("GET", f"{base_url}/handshake", timeout=10)
        if status >= 400:
            raise RuntimeError(f"/handshake failed: {status} {raw[:200]!r}")
        handshake = json.loads(raw.decode("utf-8"))
        key_id = handshake["key_id"]
        pub_pem = handshake["pub_pem"].encode()
        pub_key = serialization.load_pem_public_key(pub_pem)
        aes_key = os.urandom(32)
        enc_aes = pub_key.encrypt(aes_key, padding.PKCS1v15())
        enc_aes_b64 = base64.b64encode(enc_aes).decode()
        status, raw = http_json(
            "POST",
            f"{base_url}/handshake/confirm",
            body={"key_id": key_id, "enc_aes_b64": enc_aes_b64},
            timeout=10,
        )
        if status >= 400:
            raise RuntimeError(f"/handshake/confirm failed: {status} {raw[:200]!r}")
        headers = {"X-Key-Id": key_id, "Authorization": f"Bearer {token}"}

    decoded = {}
    for path in ("/clientnodes", "/restore_nodes"):
        status, raw = http_json("GET", f"{base_url}{path}", headers=headers, timeout=30)
        print(f"\n{path} status={status}")
        try:
            data = json.loads(raw.decode("utf-8"))
        except Exception:
            print("non-json response:", raw[:500])
            continue

        if not plain_mode and isinstance(data, dict) and "iv" in data and "ct" in data:
            iv = base64.b64decode(data["iv"])
            ct = base64.b64decode(data["ct"])
            plain = AESGCM(aes_key).decrypt(iv, ct, None)
            data = json.loads(plain.decode())
            print("decrypted:", plain.decode())
        else:
            print("plain:", json.dumps(data, indent=2))

        lst = data.get("result", data) if isinstance(data, dict) else data
        if isinstance(lst, list):
            decoded[path] = {item.get("agent"): item.get("lastConnected") for item in lst if item.get("agent")}
        else:
            decoded[path] = {}

    if decoded.get("/clientnodes") is not None and decoded.get("/restore_nodes") is not None:
        print("\n--- lastConnected comparison (RCA) ---")
        all_agents = set(decoded["/clientnodes"]) | set(decoded["/restore_nodes"])
        for agent in sorted(all_agents):
            cn = decoded["/clientnodes"].get(agent)
            rn = decoded["/restore_nodes"].get(agent)
            diff = "DIFF" if cn != rn else "same"
            print(f"  {agent}: clientnodes={cn!r}  restore_nodes={rn!r}  [{diff}]")

    if do_restore:
        # POST /restore with action=fetch/restore; optionally override payload
        restore_payload = None
        if restore_payload_arg:
            try:
                payload_text = restore_payload_arg
                if payload_text.startswith("@"):
                    with open(payload_text[1:], "r", encoding="utf-8") as f:
                        payload_text = f.read()
                restore_payload = json.loads(payload_text)
            except Exception as e:
                raise RuntimeError(f"Invalid --restore-payload: {e}") from e
        if restore_payload is None:
            restore_payload = {
                "action": "fetch",
                "agentName": restore_agent,
                "startDate": "01/01/2026, 12:00:00 AM",
                "endDate": "31/01/2026, 11:59:59 PM",
                "storageType": "GDRIVE",
            }
        if restore_action:
            restore_payload["action"] = restore_action
        restore_payload.setdefault("agentName", restore_agent)
        restore_payload.setdefault("targetAgentName", restore_payload.get("agentName", restore_agent))
        body_to_send = restore_payload
        if not plain_mode:
            try:
                from cryptography.hazmat.primitives.ciphers.aead import AESGCM
                iv = os.urandom(12)
                ct = AESGCM(aes_key).encrypt(iv, json.dumps(restore_payload).encode("utf-8"), None)
                body_to_send = {"iv": base64.b64encode(iv).decode(), "ct": base64.b64encode(ct).decode()}
            except Exception as e:
                print(f"(restore request not encrypted: {e})")
        status, raw = http_json("POST", f"{base_url}/restore", body=body_to_send, headers=headers, timeout=30)
        print(f"\n/restore (fetch) status={status}")
        try:
            text = raw.decode("utf-8", errors="replace")
            data = json.loads(text)
        except Exception:
            raw_preview = (raw[:1000].decode("utf-8", errors="replace") if raw else "(empty)")
            print("response (raw):", raw_preview)
            data = None
        if data is not None:
            if not plain_mode and isinstance(data, dict) and "iv" in data and "ct" in data:
                try:
                    iv = base64.b64decode(data["iv"])
                    ct = base64.b64decode(data["ct"])
                    plain = AESGCM(aes_key).decrypt(iv, ct, None)
                    plain_text = plain.decode()
                    print("decrypted:", plain_text)
                    try:
                        data = json.loads(plain_text)
                    except json.JSONDecodeError:
                        data = None
                        if status >= 400:
                            print("  -> (decrypted body is not JSON; likely error message above)")
                except Exception as e:
                    print("decrypt failed:", e, "raw keys:", list(data.keys()))
                    data = None
            else:
                print("plain:", json.dumps(data, indent=2))
            if data is not None:
                if isinstance(data, list):
                    print(f"  -> {len(data)} restore point(s)")
                elif isinstance(data, dict) and "error" in data:
                    print("  -> error:", data.get("error"))
                elif status >= 400:
                    print("  -> server error response:", data)


if __name__ == "__main__":
    main()
