"""Seed five realistic, idempotent CRM meeting records for local demos."""

from __future__ import annotations

import os
from datetime import datetime, time, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

from mechman_bot.storage import BotStore

IST = ZoneInfo("Asia/Kolkata")

SAMPLES = [
    {
        "name": "Asha Shah",
        "phone": "919876500001",
        "email": "asha.shah@example.com",
        "company": "Shah Precision Works",
        "designation": "Production Manager",
        "city": "Vadodara",
        "interest": "Fusion 360 CAM",
        "purpose": "Evaluate CAM programming for three-axis milling",
        "meeting_mode": "Video call",
        "status": "confirmed",
        "lead_stage": "qualified",
        "assigned_to": "Kiran",
    },
    {
        "name": "Dev Mehta",
        "phone": "919876500002",
        "email": "dev.mehta@example.com",
        "company": "Delta Tooling",
        "designation": "Director",
        "city": "Ahmedabad",
        "interest": "PowerMill",
        "purpose": "Review five-axis toolpath optimization",
        "meeting_mode": "WhatsApp call",
        "status": "scheduled",
        "lead_stage": "proposal",
        "assigned_to": "Sagar",
    },
    {
        "name": "Isha Patel",
        "phone": "919876500003",
        "email": "isha.patel@example.com",
        "company": "Patel Engineering",
        "designation": "Design Engineer",
        "city": "Anand",
        "interest": "Autodesk training",
        "purpose": "Plan a CAM training program for six engineers",
        "meeting_mode": "On-site meeting",
        "status": "requested",
        "lead_stage": "new",
        "assigned_to": "Kiran",
    },
    {
        "name": "Rohan Desai",
        "phone": "919876500004",
        "email": "rohan.desai@example.com",
        "company": "Desai Components",
        "designation": "Operations Head",
        "city": "Surat",
        "interest": "Post processor",
        "purpose": "Discuss a custom post processor for a Mazak machine",
        "meeting_mode": "Video call",
        "status": "completed",
        "lead_stage": "won",
        "assigned_to": "Sagar",
    },
    {
        "name": "Neha Joshi",
        "phone": "919876500005",
        "email": "neha.joshi@example.com",
        "company": "NJ Manufacturing",
        "designation": "Purchase Manager",
        "city": "Rajkot",
        "interest": "Autodesk licensing",
        "purpose": "Compare annual licensing and implementation options",
        "meeting_mode": "Phone call",
        "status": "cancelled",
        "lead_stage": "lost",
        "assigned_to": "Kiran",
    },
]


def _next_business_days(count: int) -> list[datetime]:
    result: list[datetime] = []
    day = datetime.now(IST).date() + timedelta(days=1)
    while len(result) < count:
        if day.weekday() != 6:
            result.append(datetime.combine(day, time(10, 0), tzinfo=IST))
        day += timedelta(days=1)
    return result


def seed(database: str | Path) -> tuple[int, int]:
    store = BotStore(database)
    created = 0
    skipped = 0
    starts = _next_business_days(len(SAMPLES))
    try:
        for sample, start_at in zip(SAMPLES, starts, strict=True):
            if any(
                row["phone"] == sample["phone"]
                for row in store.list_meetings(query=sample["phone"])
            ):
                skipped += 1
                continue
            end_at = start_at + timedelta(hours=1)
            meeting_id = store.create_meeting(
                {
                    **sample,
                    "source": "sample_seed",
                    "start_at": start_at.isoformat(),
                    "end_at": end_at.isoformat(),
                    "preferred_date": start_at.date().isoformat(),
                    "preferred_time": start_at.strftime("%H:%M"),
                    "notes": "Sample record for dashboard QA and demonstrations.",
                }
            )
            store.update_meeting(
                meeting_id,
                {
                    "status": sample["status"],
                    "lead_stage": sample["lead_stage"],
                    "assigned_to": sample["assigned_to"],
                },
                changed_by="sample_seed",
            )
            created += 1
    finally:
        store.close()
    return created, skipped


if __name__ == "__main__":
    target = Path(os.environ.get("BOT_DATABASE", "data/mechman-bot.db"))
    added, existing = seed(target)
    print(f"Sample data ready: {added} created, {existing} already present in {target}")
