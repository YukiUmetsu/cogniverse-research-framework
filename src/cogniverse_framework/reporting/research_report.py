from pathlib import Path


def write_research_markdown(path, result):

    path = Path(path)

    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    content = f"""# Research Report

Experiment: {result.get("experiment")}

Status: {result.get("status")}

## Evidence

{result}
"""

    path.write_text(content)

    return str(path)
