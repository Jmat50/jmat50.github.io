#!/usr/bin/env python3
"""Sync public GitHub repos into _data/projects.yml without overwriting manual entries."""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from ruamel.yaml import YAML

ROOT = Path(__file__).resolve().parents[2]
PROJECTS_FILE = ROOT / "_data" / "projects.yml"
GITHUB_USER = os.environ.get("GITHUB_USER", "jmat50")
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")
EXCLUDE_REPOS = {"jmat50.github.io"}

# Known live demos that are not stored in the repo homepage field.
DEMO_OVERRIDES = {
    "GameDudeSynth": "/GameDudeSynth/gamedude-player.html",
}


def api_get(url: str) -> list | dict:
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "jmat50-github-io-sync",
    }
    if GITHUB_TOKEN:
        headers["Authorization"] = f"Bearer {GITHUB_TOKEN}"

    request = Request(url, headers=headers)
    with urlopen(request) as response:
        return json.loads(response.read().decode("utf-8"))


def fetch_public_repos() -> list[dict]:
    repos: list[dict] = []
    page = 1

    while True:
        url = (
            f"https://api.github.com/users/{GITHUB_USER}/repos"
            f"?per_page=100&page={page}&type=owner&sort=updated"
        )
        batch = api_get(url)
        if not batch:
            break
        repos.extend(batch)
        if len(batch) < 100:
            break
        page += 1

    return [
        repo
        for repo in repos
        if not repo.get("fork")
        and not repo.get("archived")
        and not repo.get("private")
        and repo.get("name") not in EXCLUDE_REPOS
    ]


def normalize_repo_url(url: str) -> str:
    return url.rstrip("/").lower()


def default_description(repo: dict) -> str:
    description = (repo.get("description") or "").strip()
    if description:
        return description
    return f"Open-source project: {repo['name']}."


def default_tags(repo: dict) -> list[str]:
    topics = repo.get("topics") or []
    if topics:
        return [topic.lower() for topic in topics[:4]]

    tags: list[str] = []
    language = repo.get("language")
    if language:
        tags.append(language.lower())
    tags.append("open-source")
    return tags[:3]


def entry_from_repo(repo: dict) -> dict:
    entry: dict = {
        "name": repo["name"],
        "description": default_description(repo),
        "language": repo.get("language") or "Other",
        "repo": repo["html_url"],
    }

    demo = DEMO_OVERRIDES.get(repo["name"])
    if not demo:
        homepage = (repo.get("homepage") or "").strip()
        if homepage.startswith("http"):
            demo = homepage

    if demo:
        entry["demo"] = demo

    tags = default_tags(repo)
    if tags:
        entry["tags"] = tags

    return entry


def load_projects() -> list[dict]:
    yaml = YAML()
    yaml.preserve_quotes = True
    with PROJECTS_FILE.open(encoding="utf-8") as handle:
        data = yaml.load(handle)
    return data or []


def save_projects(projects: list[dict]) -> None:
    yaml = YAML()
    yaml.preserve_quotes = True
    yaml.default_flow_style = False
    yaml.indent(mapping=2, sequence=4, offset=2)

    with PROJECTS_FILE.open("w", encoding="utf-8") as handle:
        yaml.dump(projects, handle)


def sync_projects() -> bool:
    existing = load_projects()
    known_repos = {normalize_repo_url(project["repo"]) for project in existing}

    try:
        remote_repos = fetch_public_repos()
    except HTTPError as error:
        print(f"GitHub API request failed: {error}", file=sys.stderr)
        return False

    new_entries: list[dict] = []
    for repo in sorted(remote_repos, key=lambda item: item["name"].lower()):
        repo_url = normalize_repo_url(repo["html_url"])
        if repo_url in known_repos:
            continue
        new_entries.append(entry_from_repo(repo))
        known_repos.add(repo_url)
        print(f"Added project: {repo['name']}")

    if not new_entries:
        print("No new public repositories to add.")
        return False

    save_projects(existing + new_entries)
    print(f"Updated {PROJECTS_FILE} with {len(new_entries)} new project(s).")
    return True


if __name__ == "__main__":
    changed = sync_projects()
    sys.exit(0 if changed else 0)
