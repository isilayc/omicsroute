"""Exercise the public planning contract locally or against a deployed URL.

Local: python tests/vercel_migration/test_http_flow.py
Live:  python tests/vercel_migration/test_http_flow.py https://omicsroute.vercel.app
Local mode needs httpx in addition to the API dependencies.
"""
import sys
from pathlib import Path
from time import perf_counter

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))


def verify(client):
    def request(method, path, **kwargs):
        started = perf_counter()
        response = client.request(method, path, **kwargs)
        response.raise_for_status()
        assert "application/json" in response.headers.get("content-type", ""), path
        print(f"PASS {method} {path} ({perf_counter() - started:.3f}s)")
        return response.json()

    assert request("GET", "/health")["status"] == "ok"
    samples = request("GET", "/v1/sample-types")["sample_types"]
    assert "Eukaryotic genome" in samples
    for sample in samples:
        params = {"sample_type": sample}
        assert request("GET", "/v1/data-states", params=params)["data_states"]
        request("GET", "/v1/sequencing-options", params=params)

    for state in ("raw_reads", "genome_assembly"):
        context = {
            "sample_type": "Eukaryotic genome",
            "data_state": state,
            "sequencing": "Illumina" if state == "raw_reads" else None,
            "read_type": "Paired-end" if state == "raw_reads" else None,
        }
        goals = request("POST", "/v1/goals", json=context)["goals"]
        goal = "Organism identification / closest reference match"
        assert any(g["id"] == goal and g["selectable"] for g in goals)
        context["goal"] = goal
        strategies = request("POST", "/v1/strategies", json=context)["strategies"]
        assert strategies
        context["workflow_id"] = strategies[0]["id"]
        context["compute_profile"] = {"enabled": False}
        result = request("POST", "/v1/workflow/inspect", json=context)
        assert result["workflow"]["steps"]
        assert result["exports"]["json"]["content"]
        assert result["exports"]["markdown"]["content"]
    print("PASS sample selection -> goals -> strategies -> workflow -> exports")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        import httpx
        with httpx.Client(base_url=sys.argv[1].rstrip("/"), timeout=60) as client:
            verify(client)
    else:
        from fastapi.testclient import TestClient
        from api.main import app
        with TestClient(app) as client:
            verify(client)
