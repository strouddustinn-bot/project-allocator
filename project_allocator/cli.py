from __future__ import annotations

import argparse
import platform
import sqlite3
from pathlib import Path

from . import __version__
from .db import connect, list_latest, record_result, save_evaluation, save_project
from .decision import Evaluation, evaluate
from .economics import all_scenarios
from .intake import interactive_project, save_interactive_project
from .models import Project
from .serde import load_project


DEFAULT_DB = ".pursuit/project_allocator.db"
DEFAULT_PROJECT_DIR = ".pursuit/projects"


def money(value: float) -> str:
    return f"${value:,.2f}"


def _ensure_parent(path: str | Path) -> None:
    Path(path).expanduser().parent.mkdir(parents=True, exist_ok=True)


def _print_evaluation(project: Project, result: Evaluation) -> None:
    print("=" * 76)
    print(f"PROJECT: {project.name}")
    print(f"DECISION: {result.decision.value}")
    print(f"SUMMARY SCORE: {result.score}/100")
    print(f"EVIDENCE CONFIDENCE: {result.confidence.value}")
    print("-" * 76)

    if result.reasons:
        print("WHY:")
        for reason in result.reasons:
            print(f"  - {reason}")

    if result.blockers:
        print("BLOCKERS:")
        for blocker in result.blockers:
            print(f"  - {blocker}")

    print("\nECONOMICS:")
    for scenario in all_scenarios(project):
        print(
            f"  {scenario.name.upper():5} | upside {money(scenario.upside):>12} | "
            f"p={scenario.probability:.0%} | net EV {money(scenario.net_expected_value):>12}"
        )

    if project.competing_project:
        print(f"\nDIRECT COMPETITOR FOR RESOURCES: {project.competing_project}")
    print(f"OPPORTUNITY COST VALUE: {money(project.opportunity_cost_value)}")

    print("\nAUTHORIZED NEXT INVESTMENT:")
    print(f"  Cash:  {money(result.authorized_cash)}")
    print(f"  Hours: {result.authorized_hours:g}")

    print("\nNEXT ACTION:")
    print(f"  {result.next_action}")

    if project.proposed_experiment:
        experiment = project.proposed_experiment
        print("\nEXPERIMENT:")
        print(f"  Hypothesis: {experiment.hypothesis}")
        print(f"  Action:     {experiment.action}")
        print(f"  Pass:       {experiment.pass_condition}")
        print(f"  Fail:       {experiment.fail_condition}")
        print(f"  Hard cap:   {money(experiment.max_cash)} + {experiment.max_hours:g} hours")

    print("=" * 76)


def _evaluate_and_persist(project: Project, db_path: str) -> Evaluation:
    result = evaluate(project)
    _ensure_parent(db_path)
    conn = connect(db_path)
    try:
        save_project(conn, project)
        save_evaluation(conn, project.name, result)
    finally:
        conn.close()
    return result


def cmd_evaluate(args):
    project = load_project(args.file)
    result = _evaluate_and_persist(project, args.db)
    _print_evaluation(project, result)


def cmd_intake(args):
    project = interactive_project()
    path = save_interactive_project(project, args.project_dir)
    result = _evaluate_and_persist(project, args.db)
    print(f"\nSaved project snapshot: {path}")
    print(f"Saved decision history:  {args.db}\n")
    _print_evaluation(project, result)


def cmd_init(args):
    _ensure_parent(args.db)
    Path(args.project_dir).mkdir(parents=True, exist_ok=True)
    conn = connect(args.db)
    conn.close()
    print("Project Allocator initialized.")
    print(f"Database: {args.db}")
    print(f"Projects: {args.project_dir}")
    print("Next: pursuit intake")


def cmd_doctor(args):
    problems: list[str] = []
    db_path = Path(args.db).expanduser()
    project_dir = Path(args.project_dir).expanduser()

    try:
        db_path.parent.mkdir(parents=True, exist_ok=True)
        conn = connect(db_path)
        conn.execute("SELECT 1").fetchone()
        conn.close()
    except Exception as exc:
        problems.append(f"SQLite/database path failed: {exc}")

    try:
        project_dir.mkdir(parents=True, exist_ok=True)
        probe = project_dir / ".write-test"
        probe.write_text("ok", encoding="utf-8")
        probe.unlink()
    except Exception as exc:
        problems.append(f"Project directory is not writable: {exc}")

    print(f"Project Allocator {__version__}")
    print(f"Python: {platform.python_version()}")
    print(f"SQLite: {sqlite3.sqlite_version}")
    print(f"Database: {db_path}")
    print(f"Project snapshots: {project_dir}")

    if problems:
        print("\nSTATUS: FAIL")
        for problem in problems:
            print(f"  - {problem}")
        raise SystemExit(1)

    print("\nSTATUS: READY")
    print("USER GATE 1: run `pursuit intake` and enter the first real project.")


def cmd_list(args):
    _ensure_parent(args.db)
    conn = connect(args.db)
    try:
        rows = list_latest(conn)
    finally:
        conn.close()
    if not rows:
        print("No evaluated projects.")
        return
    print(f"{'PROJECT':32} {'DECISION':12} {'SCORE':>5} {'CONFIDENCE':12}")
    print("-" * 68)
    for row in rows:
        print(f"{row['project_name'][:32]:32} {row['decision']:12} {row['score']:>5} {row['confidence']:12}")


def cmd_result(args):
    _ensure_parent(args.db)
    conn = connect(args.db)
    try:
        record_result(
            conn,
            project_name=args.project,
            outcome=args.outcome,
            actual_cash=args.cash,
            actual_hours=args.hours,
            notes=args.notes,
        )
    finally:
        conn.close()
    print(f"Recorded result for {args.project}: {args.outcome}")


def build_parser():
    parser = argparse.ArgumentParser(
        prog="pursuit",
        description="Evidence-driven project capital allocation engine",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    parser.add_argument("--db", default=DEFAULT_DB, help=f"SQLite database path (default: {DEFAULT_DB})")
    parser.add_argument(
        "--project-dir",
        default=DEFAULT_PROJECT_DIR,
        help=f"Project snapshot directory (default: {DEFAULT_PROJECT_DIR})",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    init = sub.add_parser("init", help="Initialize local Project Allocator state")
    init.set_defaults(func=cmd_init)

    doctor = sub.add_parser("doctor", help="Verify the local installation is ready")
    doctor.set_defaults(func=cmd_doctor)

    intake = sub.add_parser("intake", help="Interactively capture and evaluate a real project")
    intake.set_defaults(func=cmd_intake)

    evaluate_parser = sub.add_parser("evaluate", help="Evaluate a project JSON file")
    evaluate_parser.add_argument("file")
    evaluate_parser.set_defaults(func=cmd_evaluate)

    list_parser = sub.add_parser("list", help="List latest project evaluations")
    list_parser.set_defaults(func=cmd_list)

    result_parser = sub.add_parser("result", help="Record a real-world experiment/project result")
    result_parser.add_argument("project")
    result_parser.add_argument("outcome")
    result_parser.add_argument("--cash", type=float, default=0.0)
    result_parser.add_argument("--hours", type=float, default=0.0)
    result_parser.add_argument("--notes", default="")
    result_parser.set_defaults(func=cmd_result)

    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
