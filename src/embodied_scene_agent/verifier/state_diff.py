"""Rule-based state differencing for v0."""

from __future__ import annotations

from embodied_scene_agent.memory.schema import SceneMemory
from embodied_scene_agent.planner.schema import PlannerOutput
from embodied_scene_agent.verifier.base import BaseVerifier
from embodied_scene_agent.verifier.schema import FailureType, VerificationResult


def _tags(mem: SceneMemory, oid: str) -> set[str]:
    if oid not in mem.objects:
        return set()
    return set(mem.objects[oid].state_tags)


def _drawer_is_open(mem: SceneMemory) -> bool:
    return "open" in _tags(mem, "drawer")


class StateDiffVerifier(BaseVerifier):
    """
    Checks simple tag transitions expected by mock skills.

    TODO: plug in learned verifier using `data/verifier_labels` format.
    """

    def verify(self, before: SceneMemory, after: SceneMemory, plan: PlannerOutput) -> VerificationResult:
        tgt = plan.target_object
        skill = plan.skill

        if tgt not in after.objects:
            return VerificationResult(
                success=False,
                failure_type=FailureType.TARGET_NOT_FOUND,
                should_replan=True,
                details=f"target {tgt} missing in after memory",
            )

        if tgt not in before.objects and tgt in after.objects:
            # newly appeared — acceptable for some sims; keep permissive
            pass

        b_tags = _tags(before, tgt)
        a_tags = _tags(after, tgt)

        if skill == "open":
            if "open" in a_tags:
                return VerificationResult(success=True, details="drawer opened")
            if "closed" in b_tags and b_tags == a_tags:
                return VerificationResult(
                    success=False,
                    failure_type=FailureType.STATE_UNCHANGED,
                    should_replan=True,
                    details="open had no effect",
                )
            return VerificationResult(
                success=False,
                failure_type=FailureType.UNKNOWN_FAILURE,
                should_replan=True,
                details="open verification inconclusive",
            )

        if skill == "grasp":
            oid = plan.target_object
            if oid not in after.objects:
                return VerificationResult(
                    success=False,
                    failure_type=FailureType.TARGET_NOT_FOUND,
                    should_replan=True,
                    details=f"grasp target {oid} missing after",
                )
            if "held" in _tags(after, oid):
                return VerificationResult(success=True, details=f"{oid} grasped")
            if _tags(before, oid) == _tags(after, oid):
                return VerificationResult(
                    success=False,
                    failure_type=FailureType.STATE_UNCHANGED,
                    should_replan=True,
                    details="grasp had no effect",
                )
            return VerificationResult(
                success=False,
                failure_type=FailureType.PRECONDITION_UNSATISFIED,
                should_replan=True,
                details="grasp failed",
            )

        if skill == "place":
            if not _drawer_is_open(before):
                return VerificationResult(
                    success=False,
                    failure_type=FailureType.PRECONDITION_UNSATISFIED,
                    should_replan=True,
                    details="drawer must be open before place",
                )
            if "held" not in _tags(before, "red_block"):
                return VerificationResult(
                    success=False,
                    failure_type=FailureType.PRECONDITION_UNSATISFIED,
                    should_replan=True,
                    details="object must be held before place",
                )
            if "in_drawer" in _tags(after, "red_block"):
                return VerificationResult(success=True, details="placed in drawer")
            if _tags(before, "red_block") == _tags(after, "red_block"):
                return VerificationResult(
                    success=False,
                    failure_type=FailureType.STATE_UNCHANGED,
                    should_replan=True,
                    details="place had no effect",
                )
            return VerificationResult(
                success=False,
                failure_type=FailureType.PRECONDITION_UNSATISFIED,
                should_replan=True,
                details="place not completed",
            )

        if skill in {"reach", "move_to", "close"}:
            return VerificationResult(success=True, details=f"noop-accept skill={skill}")

        if skill == "diagnostic_verifier_unknown":
            return VerificationResult(
                success=False,
                failure_type=FailureType.UNKNOWN_FAILURE,
                should_replan=True,
                details="diagnostic unknown skill branch",
            )

        return VerificationResult(
            success=False,
            failure_type=FailureType.UNKNOWN_FAILURE,
            should_replan=True,
            details=f"unhandled skill {skill}",
        )
