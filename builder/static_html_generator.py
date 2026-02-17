"""
Auto-generates README.md files for each content directory by scanning for files.
Runs before Jekyll build in CI so GitHub Pages renders them as HTML.
"""

import os
from pathlib import Path
from datetime import datetime

REPO_ROOT = Path(__file__).resolve().parent.parent


def parse_date(date_str: str) -> datetime:
    """Parse YYYY-MM-DD into a datetime."""
    return datetime.strptime(date_str, "%Y-%m-%d")


def format_date(date_str: str) -> str:
    """Convert YYYY-MM-DD to 'Month Day, Year'."""
    return parse_date(date_str).strftime("%B %d, %Y").replace(" 0", " ")


def generate_exams():
    """Generate exams/README.md by scanning year subdirectories for PDFs."""
    exams_dir = REPO_ROOT / "exams"
    lines = [
        "# Exam Grades",
        "",
        "This folder contains grade reports for all exam sessions, organized by academic year.",
        "",
    ]

    # Get academic year directories sorted descending (newest first)
    year_dirs = sorted(
        [d for d in exams_dir.iterdir() if d.is_dir() and not d.name.startswith(".")],
        reverse=True,
    )

    for year_dir in year_dirs:
        pdfs = sorted(year_dir.glob("*.pdf"))
        if not pdfs:
            continue

        lines.append(f"## Academic Year {year_dir.name}")
        lines.append("")
        lines.append("| Exam Date | Grades |")
        lines.append("|-----------|--------|")

        for pdf in pdfs:
            # Filename format: YYYY-MM-DD_grades.pdf
            date_str = pdf.stem.split("_")[0]
            try:
                pretty_date = format_date(date_str)
            except ValueError:
                pretty_date = pdf.stem
            lines.append(f"| {pretty_date} | [PDF](./{year_dir.name}/{pdf.name}) |")

        lines.append("")

    lines.append("---")
    lines.append("")
    lines.append("[Back to Course Home](../README.md)")
    lines.append("")

    (exams_dir / "README.md").write_text("\n".join(lines), encoding="utf-8")
    print(f"Generated {exams_dir / 'README.md'}")


def generate_exercises():
    """Generate exercises/README.md by scanning for PDFs and pairing exercises with solutions."""
    exercises_dir = REPO_ROOT / "exercises"
    lines = [
        "# Exercises",
        "",
        "This folder contains exercise sets and their solutions for the Systems and Networking - Unit I course.",
        "",
        "## Exercise Sessions",
        "",
        "| Date | Exercises | Solutions |",
        "|------|-----------|-----------|",
    ]

    pdfs = sorted(exercises_dir.glob("*.pdf"))

    # Group by date prefix: {date_str: {type: filename}}
    sessions: dict[str, dict[str, str]] = {}
    for pdf in pdfs:
        parts = pdf.stem.split("_", 1)
        if len(parts) < 2:
            continue
        date_str = parts[0]
        rest = parts[1]

        sessions.setdefault(date_str, {})
        if "Solutions" in rest:
            sessions[date_str]["solutions"] = pdf.name
        else:
            sessions[date_str]["exercises"] = pdf.name

    for date_str in sorted(sessions.keys(), reverse=True):
        files = sessions[date_str]
        try:
            pretty_date = format_date(date_str)
        except ValueError:
            pretty_date = date_str

        ex = f"[PDF](./{files['exercises']})" if "exercises" in files else "--"
        sol = f"[PDF](./{files['solutions']})" if "solutions" in files else "--"
        lines.append(f"| {pretty_date} | {ex} | {sol} |")

    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("[Back to Course Home](../README.md)")
    lines.append("")

    (exercises_dir / "README.md").write_text("\n".join(lines), encoding="utf-8")
    print(f"Generated {exercises_dir / 'README.md'}")


def _is_numbered(name: str) -> bool:
    """Check if a filename starts with a number prefix like '01_' or '07-08_'."""
    return len(name) > 0 and name[0].isdigit()


def generate_lectures():
    """Generate lectures/slides/README.md by scanning for PDFs."""
    slides_dir = REPO_ROOT / "lectures" / "slides"

    pdfs = sorted(slides_dir.glob("*.pdf"))
    current = [p for p in pdfs if not _is_numbered(p.stem)]
    legacy = [p for p in pdfs if _is_numbered(p.stem)]

    lines = [
        "# Lecture Slides",
        "",
        "This folder contains all lecture slides for the Systems and Networking - Unit I course.",
        "",
        "## Course Material",
        "",
        "| Topic | Slides |",
        "|-------|--------|",
    ]

    for pdf in current:
        topic = pdf.stem.replace("_", " ")
        lines.append(f"| {topic} | [PDF](./{pdf.name}) |")

    if legacy:
        lines.append("")
        lines.append("## Legacy Slides (Previous Years)")
        lines.append("")
        lines.append("| Topic | Slides |")
        lines.append("|-------|--------|")
        for pdf in legacy:
            topic = pdf.stem.replace("_", " ")
            lines.append(f"| {topic} | [PDF](./{pdf.name}) |")

    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("[Back to Course Home](../../README.md)")
    lines.append("")

    (slides_dir / "README.md").write_text("\n".join(lines), encoding="utf-8")
    print(f"Generated {slides_dir / 'README.md'}")


if __name__ == "__main__":
    generate_exams()
    generate_exercises()
    generate_lectures()
    print("Done.")
