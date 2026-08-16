from __future__ import annotations

import hashlib
import json
from collections import Counter
from datetime import UTC, datetime
from typing import Any

from .models import SiteConfig


def _canonical_hash(payload: Any) -> str:
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def build_evidence_bundle(config: SiteConfig, scenario: dict[str, Any]) -> dict[str, Any]:
    rows = scenario["rows"]
    reasons = Counter(reason for row in rows for reason in row["reason_codes"])
    constraints = Counter(item for row in rows for item in row["active_constraints"])
    return {
        "evidence_schema": "coolride-pq.evidence/1.0",
        "created_at": datetime.now(UTC).isoformat(),
        "site_id": config.site_id,
        "scenario_id": scenario["scenario_id"],
        "classification": "synthetic-engineering-reference",
        "config_sha256": _canonical_hash(config.__dict__),
        "scenario_sha256": _canonical_hash(scenario),
        "controller_version": "coolride-pq/0.1.0",
        "sample_count": len(rows),
        "time_step_minutes": scenario["time_step_minutes"],
        "first_timestamp": rows[0]["timestamp"],
        "last_timestamp": rows[-1]["timestamp"],
        "telemetry_quality": {"good": len(rows), "stale": 0, "bad": 0},
        "mode_counts": scenario["mode_counts"],
        "reason_code_counts": dict(sorted(reasons.items())),
        "constraint_counts": dict(sorted(constraints.items())),
        "metrics": scenario["metrics"],
        "limitations": [
            "No field calibration, utility network equivalent, or OEM protection model.",
            "PCC voltage and THD responses are synthetic and are not compliance results.",
            "Energy counterfactual does not include tariff, degradation, or forecast uncertainty.",
            "Control remains advisory and does not actuate equipment.",
        ],
    }
