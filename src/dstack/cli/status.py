import os
import sys
from argparse import Namespace
from itertools import groupby
from typing import List

from git import InvalidGitRepositoryError
from rich.console import Console
from rich.table import Table

from dstack.backend import load_backend, Backend, Run, RequestStatus
from dstack.cli.common import pretty_date
from dstack.config import ConfigError
from dstack.jobs import JobStatus
from dstack.repo import load_repo_data

_status_colors = {
    JobStatus.SUBMITTED: "yellow",
    JobStatus.DOWNLOADING: "yellow",
    JobStatus.RUNNING: "dark_sea_green4",
    JobStatus.UPLOADING: "dark_sea_green4",
    JobStatus.DONE: "gray74",
    JobStatus.FAILED: "red",
    JobStatus.STOPPED: "grey58",
    JobStatus.STOPPING: "yellow",
    JobStatus.ABORTING: "yellow",
    JobStatus.ABORTED: "grey58",
}


def _status_color(run: Run, val: str, run_column: bool, status_column: bool):
    if status_column and _has_request_status(run, [RequestStatus.TERMINATED, RequestStatus.NO_CAPACITY]):
        color = "dark_orange"
    else:
        color = _status_colors.get(run.status)
    return f"[{'bold ' if run_column else ''}{color}]{val}[/]" if color is not None else val


def _has_request_status(run, statuses: List[RequestStatus]):
    return run.status.is_unfinished() and any(filter(lambda s: s.status in statuses, run.request_heads or []))


def status_func(args: Namespace):
    try:
        backend = load_backend()
        print_runs(args, backend)
    except ConfigError:
        sys.exit(f"Call 'dstack config' first")
    except InvalidGitRepositoryError:
        sys.exit(f"{os.getcwd()} is not a Git repo")


def pretty_print_status(run: Run) -> str:
    status_color = _status_colors.get(run.status)
    status = run.status.value
    status = status[:1].upper() + status[1:]
    s = f"[{status_color}]{status}[/]"
    if _has_request_status(run, [RequestStatus.TERMINATED]):
        s += "\n[red]Request(s) terminated[/]"
    elif _has_request_status(run, [RequestStatus.NO_CAPACITY]):
        s += " \n[dark_orange]No capacity[/]"
    return s


def print_runs(args: Namespace, backend: Backend):
    repo_data = load_repo_data()
    job_heads = backend.list_job_heads(repo_data.repo_user_name, repo_data.repo_name, args.run_name)
    runs = backend.get_runs(repo_data.repo_user_name, repo_data.repo_name, job_heads)
    if not args.all:
        unfinished = any(run.status.is_unfinished() for run in runs)
        if unfinished:
            runs = list(filter(lambda r: r.status.is_unfinished(), runs))
        else:
            runs = runs[:1]
    runs = reversed(runs)

    runs_by_name = [(run_name, list(run)) for run_name, run in groupby(runs, lambda run: run.run_name)]
    console = Console()
    table = Table(box=None)
    table.add_column("RUN", style="bold", no_wrap=True)
    table.add_column("TARGET", style="grey58", width=12)
    table.add_column("STATUS", no_wrap=True)
    table.add_column("APPS", justify="center", style="green", no_wrap=True)
    table.add_column("ARTIFACTS", style="grey58", width=12)
    table.add_column("SUBMITTED", style="grey58", no_wrap=True)
    table.add_column("TAG", style="bold yellow", no_wrap=True)

    for run_name, runs in runs_by_name:
        for i in range(len(runs)):
            run = runs[i]
            submitted_at = pretty_date(round(run.submitted_at / 1000))
            table.add_row(
                _status_color(run, run_name, True, False),
                _status_color(run, run.workflow_name or run.provider_name, False, False),
                pretty_print_status(run),
                _status_color(run, _app_heads(run.app_heads, run.status.name), False, False),
                _status_color(run, '\n'.join([a.artifact_path for a in run.artifact_heads or []]), False, False),
                _status_color(run, submitted_at, False, False),
                _status_color(run, f"{run.tag_name}" if run.tag_name else "", False, False))
    console.print(table)


def get_workflow_runs(args: Namespace, backend: Backend):
    workflows_by_id = {}
    repo_data = load_repo_data()
    job_heads = backend.list_job_heads(repo_data.repo_user_name, repo_data.repo_name, args.run_name)
    unfinished = False
    for job_head in job_heads:
        if job_head.status.is_unfinished():
            unfinished = True
        workflow_id = ','.join([job_head.run_name, job_head.workflow_name or ''])
        if workflow_id not in workflows_by_id:
            workflow = {
                "run_name": job_head.run_name,
                "workflow_name": job_head.workflow_name,
                "provider_name": job_head.provider_name,
                "artifacts": job_head.artifacts or [],
                "status": job_head.status,
                "submitted_at": job_head.submitted_at,
                "tag_name": job_head.tag_name
            }
            workflows_by_id[workflow_id] = workflow
        else:
            workflow = workflows_by_id[workflow_id]
            workflow["submitted_at"] = min(workflow["submitted_at"], job_head.submitted_at)
            if job_head.artifacts:
                workflow["artifacts"].extend(job_head.artifacts)
            if job_head.status.is_unfinished():
                # TODO: implement max(status1, status2)
                workflow["status"] = job_head.status

    workflows = list(workflows_by_id.values())
    workflows = sorted(workflows, key=lambda j: j["submitted_at"], reverse=True)
    if not args.all:
        if unfinished:
            workflows = list(filter(lambda w: w["status"].is_unfinished(), workflows))
    for workflow in workflows:
        workflow["status"] = workflow["status"].value
    return reversed(workflows)


def pretty_duration_and_submitted_at(submitted_at, started_at=None, finished_at=None):
    if started_at is not None and finished_at is not None:
        _finished_at_milli = round(finished_at / 1000)
        duration_milli = _finished_at_milli - round(started_at / 1000)
        hours, remainder = divmod(duration_milli, 3600)
        minutes, seconds = divmod(remainder, 60)
        duration_str = ""
        if int(hours) > 0:
            duration_str += "{} hours".format(int(hours))
        if int(minutes) > 0:
            if int(hours) > 0:
                duration_str += " "
            duration_str += "{} mins".format(int(minutes))
        if int(hours) == 0 and int(minutes) == 0:
            duration_str = "{} secs".format(int(seconds))
    else:
        duration_str = "<none>"
    submitted_at_str = pretty_date(round(submitted_at / 1000)) if submitted_at is not None else ""
    return duration_str, submitted_at_str


def _app_heads(apps, status):
    if status == "RUNNING" and apps is not None and len(apps) > 0:
        # return "✔"
        return "\n".join(map(lambda app: app.get("app_name"), apps))
    else:
        return ""


def register_parsers(main_subparsers):
    parser = main_subparsers.add_parser("status", help="Show status of runs")

    parser.add_argument("run_name", metavar="RUN", type=str, nargs="?", help="A name of a run")
    parser.add_argument("-a", "--all",
                        help="Show status for all runs. "
                             "By default, it shows only status for unfinished runs, or the last finished.",
                        action="store_true")

    parser.set_defaults(func=status_func)