import json
import os
import sys
import typer
from reviewer.generic import run_generic_review
from reviewer.structured import run_structured_review
from reviewer.reports import print_comparison
from reviewer.github import format_as_comment, format_generic_as_comment, post_to_github

app = typer.Typer()
review_app = typer.Typer()
app.add_typer(review_app, name="review")


def _read_diff(diff_path: str) -> str:
    with open(diff_path) as f:
        return f.read()


def _write_github_output(approved: bool) -> None:
    github_output = os.environ.get("GITHUB_OUTPUT", "")
    if github_output:
        with open(github_output, "a") as fh:
            fh.write(f"approved={str(approved).lower()}\n")


@review_app.command("generic")
def generic(
    diff: str = typer.Option(..., help="Path to diff file"),
    post_comment: bool = typer.Option(False, "--post-comment", help="Post result as GitHub PR comment"),
    pr_number: int = typer.Option(None, "--pr-number", help="GitHub PR number (required with --post-comment)"),
    github_output: bool = typer.Option(False, "--github-output", help="Write approved status to GITHUB_OUTPUT"),
):
    """Run generic review on a diff."""
    diff_content = _read_diff(diff)
    result = run_generic_review(diff_content)

    comment = format_generic_as_comment(result)
    typer.echo(comment)

    if post_comment and pr_number:
        post_to_github(comment, pr_number, "AI Review Generic")

    if github_output:
        try:
            data = json.loads(result)
            approved = data.get("approved", True)
        except Exception:
            approved = True
        _write_github_output(approved)


@review_app.command("structured")
def structured(
    diff: str = typer.Option(..., help="Path to diff file"),
    context_dir: str = typer.Option("app-example", help="Path to context directory"),
    pr_title: str = typer.Option(None, "--pr-title", help="PR title in Conventional Commits format"),
    post_comment: bool = typer.Option(False, "--post-comment", help="Post result as GitHub PR comment"),
    pr_number: int = typer.Option(None, "--pr-number", help="GitHub PR number (required with --post-comment)"),
    github_output: bool = typer.Option(False, "--github-output", help="Write approved status to GITHUB_OUTPUT"),
):
    """Run structured review on a diff."""
    diff_content = _read_diff(diff)
    result = run_structured_review(diff_content, context_dir, pr_title)

    comment = format_as_comment(result, title="AI Review Structured")
    typer.echo(comment)

    if post_comment and pr_number:
        post_to_github(comment, pr_number, "AI Review Structured")

    if github_output:
        try:
            data = json.loads(result)
            approved = data.get("approved", True)
        except Exception:
            approved = True
        _write_github_output(approved)


@review_app.command("compare")
def compare(
    diff: str = typer.Option(..., help="Path to diff file"),
    context_dir: str = typer.Option("app-example", help="Path to context directory"),
):
    """Run both reviews and print a comparison report."""
    diff_content = _read_diff(diff)
    generic_result = run_generic_review(diff_content)
    structured_result = run_structured_review(diff_content, context_dir)
    print_comparison(generic_result, structured_result)


@app.command("triage")
def triage(
    diff: str = typer.Option(..., help="Path to diff file"),
    pr_title: str = typer.Option(None, "--pr-title", help="PR title in Conventional Commits format"),
    output: str = typer.Option("text", help="Output format: text or github-output"),
):
    """Run triage and return which agents should be invoked."""
    from reviewer.triage import run_triage

    diff_content = _read_diff(diff)
    result = run_triage(diff_content, pr_title=pr_title)
    should_review = len(result.agents) > 0 or result.mode in ("generic", "structured")

    if output == "github-output":
        github_output = os.environ.get("GITHUB_OUTPUT", "")
        if github_output:
            with open(github_output, "a") as fh:
                fh.write(f"should_review={str(should_review).lower()}\n")
                fh.write(f"agents={json.dumps(result.agents)}\n")
                fh.write(f"mode={result.mode}\n")
    else:
        typer.echo(f"Source:  {result.source}")
        typer.echo(f"Mode:    {result.mode}")
        typer.echo(f"Agentes: {result.agents}")
        typer.echo(f"Motivo:  {result.reason}")


@app.command("format")
def format_comment(
    input_file: str = typer.Option(None, "--input", help="Path to structured JSON result file"),
    generic_file: str = typer.Option(None, "--generic", help="Path to generic review result file"),
    mode: str = typer.Option("auto", help="Review mode: generic, structured, or auto"),
):
    """Format a review result as a GitHub PR comment."""
    generic_result = None
    if generic_file:
        with open(generic_file) as f:
            generic_result = f.read()

    if mode == "generic":
        typer.echo(format_generic_as_comment(generic_result or ""))
        return

    if input_file:
        with open(input_file) as f:
            result = f.read()
    else:
        result = sys.stdin.read()

    if mode == "structured":
        typer.echo(format_as_comment(result, title="AI Review Structured"))
    else:
        typer.echo(format_as_comment(result, generic_result=generic_result, title="AI Review Structured"))
