"""
FHIR API discovery - first milestone of encounter analytics project.

Reads the public test server CapabilityStatement ONLY. It does not
download, create, or upload patient or encounter records.

Run:
    pip install -r requirements.txt
    python scripts/01_check_fhir_api.py
"""
from __future__ import annotations

import sys
import requests

BASE_URL = "https://hapi.fhir.org/baseR4"
TIMEOUT = 20


def main() -> int:
    url = f"{BASE_URL}/metadata"
    print("FHIR API Discovery")
    print(f"Endpoint: {url}")
    try:
        response = requests.get(
            url,
            headers={"Accept": "application/fhir+json"},
            timeout=TIMEOUT,
        )
        response.raise_for_status()
        data = response.json()
    except (requests.RequestException, ValueError) as exc:
        print(f"Connection / response error: {exc}", file=sys.stderr)
        return 1

    if data.get("resourceType") != "CapabilityStatement":
        print("Unexpected response: not a FHIR CapabilityStatement.", file=sys.stderr)
        return 1

    print(f"FHIR version: {data.get('fhirVersion', 'unknown')}")
    resource_types = sorted({
        resource.get("type", "")
        for rest in data.get("rest", [])
        for resource in rest.get("resource", [])
        if resource.get("type")
    })
    for name in ("Patient", "Encounter"):
        status = "supported" if name in resource_types else "not listed"
        print(f"{name}: {status}")
    if not all(name in resource_types for name in ("Patient", "Encounter")):
        print("Required resource types not confirmed.", file=sys.stderr)
        return 1

    print("\nConnection verified. Next: select a reproducible synthetic dataset.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
