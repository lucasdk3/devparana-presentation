import anyio
import sys
import typer
from reviewer.generic import run_generic_review
from reviewer.structured import run_structured_review
from reviewer.reports import print_comparison
from reviewer.github import format_as_comment

app = typer.Typer()
review_app = typer.Typer()
app.add_typer(review_app, name="review")


def _read_diff(diff_path: str) -> str:
    with open(diff_path) as f:
        return f.read()


@review_app.command("generic")
def generic(diff: str = typer.Option(..., help="Path to diff file")):
    """Run generic review on a diff."""
    diff_content = _read_diff(diff)
    result = anyio.run(run_generic_review, diff_content)
    typer.echo(result)


@review_app.command("structured")
def structured(
    diff: str = typer.Option(..., help="Path to diff file"),
    context_dir: str = typer.Option("app-example", help="Path to context directory"),
    pr_title: str = typer.Option(None, "--pr-title", help="PR title in Conventional Commits format"),
    format: str = typer.Option("json", help="Output format: json or github"),
):
    """Run structured review on a diff."""
    diff_content = _read_diff(diff)
    result = anyio.run(run_structured_review, diff_content, context_dir, pr_title)

    if format == "github":
        typer.echo(format_as_comment(result))
    else:
        typer.echo(result)


@review_app.command("compare")
def compare(
    diff: str = typer.Option(..., help="Path to diff file"),
    context_dir: str = typer.Option("app-example", help="Path to context directory"),
    format: str = typer.Option("text", help="Output format: text or github"),
):
    """Run both reviews and compare results."""
    diff_content = _read_diff(diff)

    async def run_both():
        generic_result = await run_generic_review(diff_content)
        structured_result = await run_structured_review(diff_content, context_dir)
        return generic_result, structured_result

    generic_result, structured_result = anyio.run(run_both)

    if format == "github":
        typer.echo(format_as_comment(structured_result, generic_result=generic_result))
    else:
        print_comparison(generic_result, structured_result)


@app.command("triage")
def triage(
    diff: str = typer.Option(..., help="Path to diff file"),
    pr_title: str = typer.Option(None, "--pr-title", help="PR title in Conventional Commits format"),
    output: str = typer.Option("text", help="Output format: text or github-output"),
):
    """Run triage and return which agents should be invoked."""
    import json, os
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
    input_file: str = typer.Option(None, "--input", help="Path to JSON result file (default: stdin)"),
    generic_file: str = typer.Option(None, "--generic", help="Path to generic review result file"),
):
    """Format a review JSON result as a GitHub PR comment."""
    if input_file:
        with open(input_file) as f:
            result = f.read()
    else:
        result = sys.stdin.read()

    generic_result = None
    if generic_file:
        with open(generic_file) as f:
            generic_result = f.read()

    typer.echo(format_as_comment(result, generic_result=generic_result))
