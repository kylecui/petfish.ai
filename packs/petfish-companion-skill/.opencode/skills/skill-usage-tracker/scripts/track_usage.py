#!/usr/bin/env python3
"""PEtFiSh Skill Usage Tracker — 记录和分析skill使用情况。

Usage:
    uv run scripts/track_usage.py --skill <name> --action activate --target .
    uv run scripts/track_usage.py --skill <name> --action feedback --feedback helpful --target .
    uv run scripts/track_usage.py --action report --target .
    uv run scripts/track_usage.py --action report --target . --json
"""

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path


USAGE_FILENAME = "skill-usage.json"

# Platform directories to search for usage file
PLATFORM_DIRS = [".opencode", ".claude", ".cursor", ".github", ".windsurf", ".agents"]


def find_usage_file(target: str) -> Path:
    """Find or determine the usage file path."""
    target_path = Path(target).resolve()

    # Check existing platform dirs
    for pd in PLATFORM_DIRS:
        candidate = target_path / pd / USAGE_FILENAME
        if candidate.exists():
            return candidate

    # Default to .opencode/
    default_dir = target_path / ".opencode"
    default_dir.mkdir(parents=True, exist_ok=True)
    return default_dir / USAGE_FILENAME


def load_usage(filepath: Path) -> dict:
    """Load usage data from file."""
    if filepath.exists():
        try:
            return json.loads(filepath.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            # Backup corrupt file before overwriting
            ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
            backup = filepath.with_suffix(f".json.corrupt.{ts}")
            try:
                filepath.rename(backup)
                print(
                    f"Warning: corrupt {filepath.name} backed up to {backup.name}",
                    file=sys.stderr,
                )
            except OSError:
                pass
        except OSError:
            pass

    return {
        "project": str(filepath.parent.parent),
        "platform": filepath.parent.name.lstrip("."),
        "created": datetime.now(timezone.utc).isoformat(),
        "updated": datetime.now(timezone.utc).isoformat(),
        "skills": {},
    }


def save_usage(filepath: Path, data: dict):
    """Save usage data to file."""
    data["updated"] = datetime.now(timezone.utc).isoformat()
    filepath.parent.mkdir(parents=True, exist_ok=True)
    filepath.write_text(
        json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )


def record_activation(
    data: dict,
    skill_name: str,
    session_id: str | None = None,
    topic_id: str | None = None,
    agent_id: str | None = None,
) -> dict:
    """Record a skill activation event."""
    now = datetime.now(timezone.utc).isoformat()

    if skill_name not in data["skills"]:
        data["skills"][skill_name] = {
            "activations": 0,
            "last_used": now,
            "first_used": now,
            "sessions": 1,
            "feedback": {"helpful": 0, "not_helpful": 0},
        }

    entry = data["skills"][skill_name]
    entry["activations"] += 1
    entry["last_used"] = now

    # Add context fields if provided
    if session_id:
        entry["session_id"] = session_id
    if topic_id:
        entry["topic_id"] = topic_id
    if agent_id:
        entry["agent_id"] = agent_id

    return data


def record_session(
    data: dict,
    skill_name: str,
    session_id: str | None = None,
    topic_id: str | None = None,
    agent_id: str | None = None,
) -> dict:
    """Record a new session for a skill."""
    if skill_name in data["skills"]:
        data["skills"][skill_name]["sessions"] += 1
        # Add context fields if provided
        if session_id:
            data["skills"][skill_name]["session_id"] = session_id
        if topic_id:
            data["skills"][skill_name]["topic_id"] = topic_id
        if agent_id:
            data["skills"][skill_name]["agent_id"] = agent_id
    return data


def record_feedback(
    data: dict,
    skill_name: str,
    feedback_type: str,
    session_id: str | None = None,
    topic_id: str | None = None,
    agent_id: str | None = None,
) -> dict:
    """Record user feedback for a skill."""
    if skill_name not in data["skills"]:
        # Can't give feedback for unused skill
        return data

    if feedback_type in ("helpful", "not_helpful"):
        data["skills"][skill_name]["feedback"][feedback_type] += 1
        # Add context fields if provided
        if session_id:
            data["skills"][skill_name]["session_id"] = session_id
        if topic_id:
            data["skills"][skill_name]["topic_id"] = topic_id
        if agent_id:
            data["skills"][skill_name]["agent_id"] = agent_id

    return data


def generate_report(data: dict, as_json: bool = False) -> str | dict:
    """Generate usage report."""
    skills = data.get("skills", {})

    if not skills:
        if as_json:
            return {
                "project": data.get("project", "unknown"),
                "total_activations": 0,
                "total_skills": 0,
                "skills": [],
            }
        return "No usage data recorded yet."

    # Calculate metrics
    total_activations = sum(s["activations"] for s in skills.values())
    now = datetime.now(timezone.utc)

    skill_stats = []
    for name, info in skills.items():
        activations = info["activations"]
        helpful = info["feedback"]["helpful"]
        not_helpful = info["feedback"]["not_helpful"]
        total_feedback = helpful + not_helpful
        satisfaction = (helpful / total_feedback * 100) if total_feedback > 0 else None

        # Parse last_used for dormancy
        try:
            last_used = datetime.fromisoformat(info["last_used"].replace("Z", "+00:00"))
            days_since = (now - last_used).days
        except (ValueError, KeyError):
            days_since = -1

        share = (activations / total_activations * 100) if total_activations > 0 else 0

        skill_stats.append(
            {
                "name": name,
                "activations": activations,
                "sessions": info.get("sessions", 0),
                "share": round(share, 1),
                "days_since_use": days_since,
                "satisfaction": round(satisfaction, 1)
                if satisfaction is not None
                else None,
                "feedback_count": total_feedback,
                "dormant": days_since >= 7,
            }
        )

    # Sort by activations descending
    skill_stats.sort(key=lambda x: x["activations"], reverse=True)

    # Derived metrics
    installed_count = len(skill_stats)
    dormant_count = sum(1 for s in skill_stats if s["dormant"])
    used_count = sum(1 for s in skill_stats if s["activations"] > 0)
    coverage = (used_count / installed_count * 100) if installed_count > 0 else 0

    total_helpful = sum(
        s.get("feedback_count", 0) for s in skill_stats if s["satisfaction"] is not None
    )
    avg_satisfaction = None
    if total_helpful > 0:
        weighted = sum(
            s["satisfaction"] * s["feedback_count"]
            for s in skill_stats
            if s["satisfaction"] is not None and s["feedback_count"] > 0
        )
        avg_satisfaction = round(weighted / total_helpful, 1)

    report_data = {
        "project": data.get("project", "unknown"),
        "period": {
            "from": data.get("created", "unknown"),
            "to": data.get("updated", "unknown"),
        },
        "total_activations": total_activations,
        "total_skills": installed_count,
        "coverage": round(coverage, 1),
        "dormant_count": dormant_count,
        "avg_satisfaction": avg_satisfaction,
        "skills": skill_stats,
    }

    if as_json:
        return report_data

    return format_text_report(report_data)


def format_text_report(report: dict) -> str:
    """Format report as text."""
    lines = []
    lines.append("")
    lines.append("┌──────────────────────────────────────────┐")
    lines.append("│  ><(((^>  Skill Usage Report             │")
    lines.append("├──────────────────────────────────────────┤")

    proj = report["project"]
    if len(proj) > 36:
        proj = "..." + proj[-33:]
    lines.append(f"│  Project: {proj:<31}│")
    lines.append(f"│  Total activations: {report['total_activations']:<21}│")
    lines.append(
        f"│  Coverage: {report['coverage']}% ({report['total_skills']} skills){' ' * (21 - len(str(report['coverage'])) - len(str(report['total_skills'])))}│"
    )
    lines.append("│                                          │")

    # Top skills
    lines.append("│  Top Skills:                             │")
    for i, s in enumerate(report["skills"][:5]):
        rank = f"{i + 1}."
        name = s["name"]
        if len(name) > 22:
            name = name[:19] + "..."
        acts = str(s["activations"])
        share = f"({s['share']}%)"
        entry = f"    {rank} {name:<23} {acts:>3} {share}"
        lines.append(f"│{entry:<41}│")

    # Dormant skills
    dormant = [s for s in report["skills"] if s["dormant"]]
    if dormant:
        lines.append("│                                          │")
        lines.append("│  Dormant Skills (7+ days):               │")
        for s in dormant[:5]:
            name = s["name"]
            if len(name) > 32:
                name = name[:29] + "..."
            lines.append(f"│    ⚪ {name:<35}│")

    # Satisfaction
    if report["avg_satisfaction"] is not None:
        lines.append("│                                          │")
        sat = report["avg_satisfaction"]
        lines.append(f"│  Satisfaction: {sat}% helpful{' ' * (18 - len(str(sat)))}│")

    lines.append("└──────────────────────────────────────────┘")
    lines.append("")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="PEtFiSh Skill Usage Tracker — 记录和分析skill使用情况",
        epilog="Example: uv run scripts/track_usage.py --action report --target .",
    )
    parser.add_argument(
        "--action",
        required=True,
        choices=["activate", "session", "feedback", "report", "reset"],
        help="Action to perform",
    )
    parser.add_argument(
        "--skill", help="Skill name (required for activate/session/feedback)"
    )
    parser.add_argument(
        "--feedback",
        choices=["helpful", "not_helpful"],
        help="Feedback type (required for feedback action)",
    )
    parser.add_argument("--target", default=".", help="Project directory (default: .)")
    parser.add_argument(
        "--json", action="store_true", dest="as_json", help="Output as JSON"
    )
    parser.add_argument(
        "--session-id", type=str, default=None, help="Session identifier"
    )
    parser.add_argument(
        "--topic-id", type=str, default=None, help="Active topic identifier"
    )
    parser.add_argument("--agent-id", type=str, default=None, help="Agent identifier")

    args = parser.parse_args()

    # Validate arguments
    if args.action in ("activate", "session", "feedback") and not args.skill:
        parser.error(f"--skill is required for action '{args.action}'")
    if args.action == "feedback" and not args.feedback:
        parser.error("--feedback is required for action 'feedback'")

    target = os.path.abspath(args.target)
    if not os.path.isdir(target):
        print(f"Error: '{target}' is not a directory", file=sys.stderr)
        sys.exit(1)

    usage_file = find_usage_file(target)
    data = load_usage(usage_file)

    if args.action == "activate":
        data = record_activation(
            data, args.skill, args.session_id, args.topic_id, args.agent_id
        )
        save_usage(usage_file, data)
        if args.as_json:
            print(
                json.dumps(
                    {"status": "ok", "skill": args.skill, "action": "activate"},
                    indent=2,
                )
            )
        else:
            print(f"✅ Recorded activation: {args.skill}")

    elif args.action == "session":
        data = record_session(
            data, args.skill, args.session_id, args.topic_id, args.agent_id
        )
        save_usage(usage_file, data)
        if args.as_json:
            print(
                json.dumps(
                    {"status": "ok", "skill": args.skill, "action": "session"}, indent=2
                )
            )
        else:
            print(f"✅ Recorded session: {args.skill}")

    elif args.action == "feedback":
        data = record_feedback(
            data,
            args.skill,
            args.feedback,
            args.session_id,
            args.topic_id,
            args.agent_id,
        )
        save_usage(usage_file, data)
        if args.as_json:
            print(
                json.dumps(
                    {
                        "status": "ok",
                        "skill": args.skill,
                        "action": "feedback",
                        "type": args.feedback,
                    },
                    indent=2,
                )
            )
        else:
            icon = "👍" if args.feedback == "helpful" else "👎"
            print(f"{icon} Recorded feedback: {args.skill} → {args.feedback}")

    elif args.action == "report":
        report = generate_report(data, as_json=args.as_json)
        if args.as_json:
            print(json.dumps(report, indent=2, ensure_ascii=False))
        else:
            print(report)

    elif args.action == "reset":
        if usage_file.exists():
            usage_file.unlink()
            print(f"🗑️ Usage data reset: {usage_file}")
        else:
            print("No usage data to reset.")


if __name__ == "__main__":
    main()
