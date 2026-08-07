#!/usr/bin/env python3
"""
bagback-cli / scripts/05_agile_pmo.py

GitHub Project Board V2 — creates Kanban board, 8 views, and custom fields
via GraphQL API. Uses gh CLI (no personal token needed).

Usage:
  python 05_agile_pmo.py --repo owner/repo --project-title "My Project" [--dry-run]
"""
import argparse
import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from lib import preflight

VIEWS = [
    {"name": "Kanban Board",           "layout": "BOARD_LAYOUT"},
    {"name": "Subsystems Breakdown",   "layout": "TABLE_LAYOUT"},
    {"name": "Priority Matrix",        "layout": "TABLE_LAYOUT"},
    {"name": "System Roadmap",         "layout": "ROADMAP_LAYOUT"},
    {"name": "Planning & Backlog",     "layout": "TABLE_LAYOUT"},
    {"name": "Feature Release",        "layout": "TABLE_LAYOUT"},
    {"name": "Bug Tracker",            "layout": "TABLE_LAYOUT"},
    {"name": "Sprints & Iterations",   "layout": "TABLE_LAYOUT"},
]

CUSTOM_FIELDS = [
    {"name": "Priority",    "type": "SINGLE_SELECT", "options": ["P0 - Critical", "P1 - High", "P2 - Medium", "P3 - Low"]},
    {"name": "Subsystem",   "type": "SINGLE_SELECT", "options": ["AI Pipeline", "3D Engine", "Audio", "API Server", "Database", "CI/CD", "Docs"]},
    {"name": "Story Points","type": "NUMBER"},
    {"name": "Target Date", "type": "DATE"},
]


def gh_graphql(query: str, variables: dict | None = None) -> dict:
    cmd = ["gh", "api", "graphql", "-f", f"query={query}"]
    if variables:
        for k, v in variables.items():
            cmd += ["-f", f"{k}={v}"]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"GraphQL error: {result.stderr}")
    return json.loads(result.stdout)


def get_owner_id(owner: str) -> str:
    q = """query($login: String!) { user(login: $login) { id } }"""
    data = gh_graphql(q, {"login": owner})
    return data["data"]["user"]["id"]


def create_project(owner_id: str, title: str) -> tuple[str, str]:
    q = """mutation($ownerId: ID!, $title: String!) {
      createProjectV2(input: {ownerId: $ownerId, title: $title}) {
        projectV2 { id number }
      }
    }"""
    data = gh_graphql(q, {"ownerId": owner_id, "title": title})
    p = data["data"]["createProjectV2"]["projectV2"]
    return p["id"], str(p["number"])


def get_project_id(owner: str, number: int) -> str:
    q = """query($owner: String!, $number: Int!) {
      user(login: $owner) {
        projectV2(number: $number) { id }
      }
    }"""
    result = subprocess.run(
        ["gh", "api", "graphql", "-f", f"query={q}", "-F", f"owner={owner}", "-F", f"number={number}"],
        capture_output=True, text=True
    )
    data = json.loads(result.stdout)
    return data["data"]["user"]["projectV2"]["id"]


def create_view(project_id: str, name: str, layout: str) -> None:
    q = """mutation($projectId: ID!, $name: String!, $layout: ProjectV2ViewLayout!) {
      createProjectV2View(input: {projectId: $projectId, name: $name, layout: $layout}) {
        projectV2View { id name }
      }
    }"""
    result = subprocess.run(
        ["gh", "api", "graphql",
         "-f", f"query={q}",
         "-f", f"projectId={project_id}",
         "-f", f"name={name}",
         "-f", f"layout={layout}"],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        print(f"  Warning: could not create view '{name}': {result.stderr[:100]}")
    else:
        print(f"  View created: {name}")


def create_custom_field(project_id: str, field: dict) -> None:
    if field["type"] == "NUMBER":
        q = """mutation($projectId: ID!, $name: String!, $type: ProjectV2CustomFieldType!) {
          createProjectV2Field(input: {projectId: $projectId, name: $name, dataType: $type}) {
            projectV2Field { ... on ProjectV2Field { id name } }
          }
        }"""
        result = subprocess.run(
            ["gh", "api", "graphql",
             "-f", f"query={q}",
             "-f", f"projectId={project_id}",
             "-f", f"name={field['name']}",
             "-f", f"type=NUMBER"],
            capture_output=True, text=True
        )
    elif field["type"] == "DATE":
        q = """mutation($projectId: ID!, $name: String!) {
          createProjectV2Field(input: {projectId: $projectId, name: $name, dataType: DATE}) {
            projectV2Field { ... on ProjectV2Field { id name } }
          }
        }"""
        result = subprocess.run(
            ["gh", "api", "graphql",
             "-f", f"query={q}",
             "-f", f"projectId={project_id}",
             "-f", f"name={field['name']}"],
            capture_output=True, text=True
        )
    elif field["type"] == "SINGLE_SELECT":
        options_gql = " ".join([f'{{name: "{o}"}}' for o in field.get("options", [])])
        q = f"""mutation {{
          createProjectV2Field(input: {{
            projectId: "{project_id}",
            name: "{field['name']}",
            dataType: SINGLE_SELECT,
            singleSelectOptions: [{options_gql}]
          }}) {{
            projectV2Field {{ ... on ProjectV2SingleSelectField {{ id name }} }}
          }}
        }}"""
        result = subprocess.run(
            ["gh", "api", "graphql", "-f", f"query={q}"],
            capture_output=True, text=True
        )
    else:
        return

    if result.returncode == 0:
        print(f"  Field created: {field['name']} ({field['type']})")
    else:
        print(f"  Warning: could not create field '{field['name']}'")


def setup_project_board(owner: str, title: str, dry_run: bool) -> None:
    if dry_run:
        print(f"  [DRY-RUN] Would create project: '{title}' for {owner}")
        print(f"  [DRY-RUN] Would create {len(VIEWS)} views:")
        for v in VIEWS:
            print(f"    - {v['name']} ({v['layout']})")
        print(f"  [DRY-RUN] Would create {len(CUSTOM_FIELDS)} custom fields:")
        for f in CUSTOM_FIELDS:
            print(f"    - {f['name']} ({f['type']})")
        return

    print(f"\n  Creating project board: '{title}'...")
    owner_id = get_owner_id(owner)
    project_id, project_number = create_project(owner_id, title)
    print(f"  Project created: #{project_number} (id={project_id})")

    print(f"\n  Creating {len(VIEWS)} views...")
    for view in VIEWS:
        create_view(project_id, view["name"], view["layout"])

    print(f"\n  Creating {len(CUSTOM_FIELDS)} custom fields...")
    for field in CUSTOM_FIELDS:
        create_custom_field(project_id, field)

    print(f"\n  Board URL: https://github.com/users/{owner}/projects/{project_number}")
    print("\n  ⚠  Manual step: Configure 'Group By' for each view in the GitHub UI.")
    print("     The GraphQL API does not expose groupBy mutations on Project V2 views.")


def main() -> None:
    parser = argparse.ArgumentParser(description="Agile PMO — GitHub Project Board setup")
    parser.add_argument("--owner", required=True, help="GitHub username")
    parser.add_argument("--project-title", default="Project Board", help="Board title")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    preflight.run_all(Path("."), require_gh_auth=True)
    setup_project_board(args.owner, args.project_title, args.dry_run)

    if args.dry_run:
        print("\n[DRY-RUN] No changes made.")


if __name__ == "__main__":
    main()
