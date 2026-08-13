# The Encryptorium Book of Post-Quantum Cryptography
# Chapter 30: Running a PQ migration program
# Section: "First-wave deployment (2028-2031)"
# https://book.encryptorium.com/part-5-migration-deployment/ch30-running-a-pq-migration-program/
#
# Generated from the chapter text. Edits here do not reach the book.
# Run: python3 chapter-code/ch30/02-check.py

# Block 2: pedagogical slice of migration_program.phase_gate.check (stdlib only).
PHASE_EXIT_CRITERIA = {
    "discovery": (
        "cbom_complete", "pqra_scored", "owners_assigned",
    ),
    "first-wave": (
        "public_vulnerable_migrated", "jwt_signing_migrated",
        "rollback_drill_completed",
    ),
    "broad-rollout": (
        "remaining_vulnerable_migrated",
        "composite_client_adoption_above_threshold",
        "work_stream_reports_green",
    ),
    "end-of-migration": (
        "classical_retired", "pq_only_mode",
        "post_migration_review_signed",
    ),
}

def check(phase, record):
    if phase not in PHASE_EXIT_CRITERIA:
        raise ValueError(f"unknown phase: {phase!r}")
    criteria = PHASE_EXIT_CRITERIA[phase]
    missing = tuple(c for c in criteria if record.get(c) is not True)
    return {"phase": phase, "passed": len(missing) == 0, "missing": missing}

record = {
    "public_vulnerable_migrated": True,
    "jwt_signing_migrated": True,
    "rollback_drill_completed": False,
}
result = check("first-wave", record)
print(f"{result['phase']}: passed={result['passed']}, missing={list(result['missing'])}")
# ==> first-wave: passed=False, missing=['rollback_drill_completed']
