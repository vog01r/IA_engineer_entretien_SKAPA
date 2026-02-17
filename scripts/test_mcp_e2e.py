"""Test E2E du serveur MCP SKAPA — transport streamable-http.

Lance le serveur HTTP, envoie des requêtes JSON-RPC 2.0 (initialize, tools/list, tools/call)
et vérifie que les réponses sont conformes au protocole MCP (tool standard ChatGPT/Claude).

Usage:
    python scripts/test_mcp_e2e.py

Nécessite : PYTHONPATH à la racine du projet, dépendances installées (mcp, requests).
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import time
from pathlib import Path

import urllib.request
import urllib.error

# Racine du projet
ROOT = Path(__file__).resolve().parent.parent
# Port dédié au test (éviter conflit avec API 8000, MCP manuel 8001)
MCP_PORT = 18080 + (os.getpid() % 100)


def _post(url: str, body: dict, session_id: str | None = None) -> tuple[dict, dict]:
    """Envoie une requête POST JSON-RPC. Retourne (corps JSON, headers de réponse)."""
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
    if session_id:
        headers["Mcp-Session-Id"] = session_id
    data = json.dumps(body).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers=headers, method="POST")
    with urllib.request.urlopen(req, timeout=30) as resp:
        body_out = json.loads(resp.read().decode())
        # Récupérer les headers (urllib met tout en minuscules)
        resp_headers = {k.lower(): v for k, v in resp.headers.items()}
        return body_out, resp_headers


def _wait_for_server(base_url: str, max_attempts: int = 30) -> bool:
    """Attend que le serveur réponde (initialize) avec 200."""
    last_err = None
    for _ in range(max_attempts):
        try:
            init_req = {
                "jsonrpc": "2.0",
                "id": 0,
                "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {},
                    "clientInfo": {"name": "test-e2e", "version": "1.0"},
                },
            }
            _post(base_url, init_req)
            return True
        except Exception as e:
            last_err = e
            time.sleep(0.5)
    if last_err is not None:
        print("  Dernière erreur:", last_err)
    return False


def run_e2e() -> bool:
    """Lance le serveur MCP en HTTP, exécute les requêtes MCP standard, vérifie les réponses."""
    base_url = f"http://127.0.0.1:{MCP_PORT}/mcp"
    env = os.environ.copy()
    env["PORT"] = str(MCP_PORT)
    env["PYTHONPATH"] = str(ROOT)

    proc = subprocess.Popen(
        [sys.executable, "-m", "backend.services.mcp.run_http"],
        cwd=str(ROOT),
        env=env,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.PIPE,
    )
    try:
        if not _wait_for_server(base_url):
            try:
                _, stderr = proc.communicate(timeout=2)
                if stderr:
                    print("Stderr serveur:", stderr.decode(errors="replace")[:500])
            except subprocess.TimeoutExpired:
                proc.kill()
            print("ERREUR: Le serveur MCP n'a pas répondu à temps.")
            return False

        # 1) initialize (handshake MCP standard) — obligatoire avant tools/list et tools/call
        init_req = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "test-e2e", "version": "1.0"},
            },
        }
        init_resp, init_headers = _post(base_url, init_req)
        if "result" not in init_resp:
            print("ERREUR: initialize sans result:", json.dumps(init_resp, indent=2))
            return False
        session_id = init_headers.get("mcp-session-id")
        if not session_id:
            print("ERREUR: initialize doit retourner l'en-tête mcp-session-id")
            return False
        print("  initialize: OK (session établie)")

        # 2) tools/list — au moins 3 tools (exigence projet), on en a 4
        list_req = {"jsonrpc": "2.0", "id": 2, "method": "tools/list"}
        list_resp, _ = _post(base_url, list_req, session_id=session_id)
        if "result" not in list_resp or "tools" not in list_resp["result"]:
            print("ERREUR: tools/list sans result.tools:", json.dumps(list_resp, indent=2))
            return False
        tools = list_resp["result"]["tools"]
        names = [t.get("name") for t in tools]
        required = {"get_weather", "search_knowledge", "conversation_history"}
        if not required.issubset(set(names)):
            print("ERREUR: tools/list doit contenir au moins get_weather, search_knowledge, conversation_history. Reçu:", names)
            return False
        for t in tools:
            if "inputSchema" not in t:
                print("ERREUR: Chaque tool doit avoir inputSchema (MCP standard). Tool sans schema:", t.get("name"))
                return False
        print("  tools/list: OK (4 tools, inputSchema présents)")

        # 3) tools/call — get_weather
        call_req = {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {
                "name": "get_weather",
                "arguments": {"latitude": 48.8566, "longitude": 2.3522},
            },
        }
        call_resp, _ = _post(base_url, call_req, session_id=session_id)
        if "result" not in call_resp:
            print("ERREUR: tools/call sans result:", json.dumps(call_resp, indent=2))
            return False
        result = call_resp["result"]
        # MCP spec: result.content = [ { "type": "text", "text": "..." } ]
        if "content" not in result or not isinstance(result["content"], list):
            print("ERREUR: result doit contenir content (liste). Reçu:", result)
            return False
        if len(result["content"]) < 1:
            print("ERREUR: result.content ne doit pas être vide.")
            return False
        first = result["content"][0]
        if first.get("type") != "text" or "text" not in first:
            print("ERREUR: result.content[0] doit être { type: 'text', text: '...' }. Reçu:", first)
            return False
        text = first["text"]
        if not text or not isinstance(text, str):
            print("ERREUR: result.content[0].text doit être une chaîne non vide.")
            return False
        print("  tools/call get_weather: OK (content[].type=text, text présent)")

        print("\nTous les tests E2E MCP sont passés.")
        return True
    finally:
        proc.terminate()
        proc.wait(timeout=5)


def main() -> int:
    print("Test E2E MCP (streamable-http) — SKAPA")
    print("Port", MCP_PORT, "— démarrage du serveur...")
    ok = run_e2e()
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
