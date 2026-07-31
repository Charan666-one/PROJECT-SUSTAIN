"""
Send all due surveillance check-ins once, without a Celery broker.

Handy for dev/pilot (run from cron) or to test delivery:
    PYTHONPATH=backend python scripts/send_checkins.py
"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "backend"))

from app.services.followup.dispatch import send_due_checkins  # noqa: E402

if __name__ == "__main__":
    result = asyncio.run(send_due_checkins())
    print(f"Due check-ins processed: {result['processed']} | delivered: {result['delivered']}")
