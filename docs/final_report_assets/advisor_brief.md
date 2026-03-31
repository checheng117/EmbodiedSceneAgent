# Advisor brief (research framing)

## Claim

Explicit **3D object-level memory** as the interface for **verifiable** high-level robotics reasoning and recovery.

## Design

- Contracts reduce ambiguity between perception adapters and planning.
- Verifier taxonomy anchors replan strategies (rules + optional LLM JSON).

## Evidence status

- Ablations: E2 mock (symbolic): latest batch shows verifier_plus_replan task_completion=1.0, recovery_success_rate=0.6666666666666666 — **fixture/smoke**, not official CALVIN.
- Hybrid metrics: {"replan_parse_success_rate": 0.0, "validated_revision_rate": 0.0, "fallback_rate": 1.0, "repair_success_rate": 1.0, "unknown_failure_rate": 0.6, "unknown_skill_rate": 0.0, "alias_normalization_count": 0, "invalid_skill_count": 0}
- RLBench: import_fail (fixture bridge documented).

## Next milestones (honest)

1. CoppeliaSim-backed RLBench import → env_create → reset.
2. Frozen CALVIN eval split (if policy allows) — separate from fixtures.
3. Optional: richer hybrid stress batches to populate parse breakdown.
