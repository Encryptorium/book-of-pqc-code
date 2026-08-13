# The Encryptorium Book of Post-Quantum Cryptography
# Chapter 30: Running a PQ migration program
# Section: "End-of-migration and classical deprecation (2035+)"
# https://book.encryptorium.com/part-5-migration-deployment/ch30-running-a-pq-migration-program/
#
# Generated from the chapter text. Edits here do not reach the book.
# Run: python3 chapter-code/ch30/03-report.py

# Block 3: pedagogical slice of migration_program.milestone_tracker.report (stdlib only).
from datetime import date

MILESTONES = [
    ("cbom_complete",                "2026-12-31", True),
    ("pqra_scored",                  "2027-06-30", True),
    ("owners_assigned",              "2025-12-31", False),
    ("public_vulnerable_migrated",   "2028-12-31", False),
]

def report(milestones, today):
    today_d = date.fromisoformat(today)
    parsed = [(name, date.fromisoformat(target), done)
              for name, target, done in milestones]
    total = len(parsed)
    completed = sum(1 for _, _, done in parsed if done)
    slipped = [name for name, d, done in parsed if (not done) and d < today_d]
    pct = (completed / total) if total > 0 else 0.0
    return {"total": total, "completed": completed,
            "percent": pct, "slipped": slipped}

r = report(MILESTONES, "2026-04-17")
print(f"{r['completed']}/{r['total']} complete ({r['percent'] * 100:.0f}%), "
      f"slipped={r['slipped']}")
# ==> 2/4 complete (50%), slipped=['owners_assigned']
