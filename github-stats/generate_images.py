#!/usr/bin/python3

import asyncio
import os
import re
import aiohttp

from github_stats import Stats

__DIRNAME__ = os.path.realpath(os.path.dirname(__file__))


def create_output_folder() -> None:
    if not os.path.isdir(os.path.join(os.path.join(__DIRNAME__, "generated"))):
        os.mkdir(os.path.join(__DIRNAME__, "generated"))


async def generate_overview(s: Stats) -> None:
    """
    Generate an SVG badge with summary statistics
    :param s: Represents user's GitHub statistics
    """
    with open(os.path.join(__DIRNAME__, "templates/overview.svg"), "r") as f:
        output = f.read()

    output = re.sub("{{ name }}", await s.name, output)
    output = re.sub("{{ stars }}", f"{await s.stargazers:,}", output)
    output = re.sub("{{ forks }}", f"{await s.forks:,}", output)
    output = re.sub("{{ contributions }}", f"{await s.total_contributions:,}", output)
    changed = (await s.lines_changed)[0] + (await s.lines_changed)[1]
    output = re.sub("{{ lines_changed }}", f"{changed:,}", output)
    output = re.sub("{{ views }}", f"{await s.views:,}", output)
    output = re.sub("{{ repos }}", f"{len(await s.repos):,}", output)

    create_output_folder()
    with open(
        os.path.join(__DIRNAME__, "generated/github-stats-overview.svg"), "w"
    ) as f:
        f.write(output)


async def generate_languages(s: Stats) -> None:
    """
    Generate an SVG badge with summary languages used
    :param s: Represents user's GitHub statistics
    """
    with open(os.path.join(__DIRNAME__, "templates/languages.svg"), "r") as f:
        output = f.read()

    progress = ""
    lang_list = ""
    sorted_languages = sorted(
        (await s.languages).items(), reverse=True, key=lambda t: t[1].get("size")
    )[:10]
    for lang, data in sorted_languages:
        color = data.get("color")
        color = color if color is not None else "#000000"
        progress += (
            f'<span style="background-color: {color};'
            f'width: {data.get("prop", 0):0.3f}%;" '
            f'class="progress-item"></span>'
        )
        lang_list += f"""
<li>
<svg xmlns="http://www.w3.org/2000/svg" class="octicon" style="fill:{color};" viewBox="0 0 16 16" width="16" height="16"><circle xmlns="http://www.w3.org/2000/svg" cx="8" cy="9" r="5" /></svg>
<span class="lang">{lang}</span>
<span class="percent">{data.get("prop", 0):0.2f}%</span>
</li>
"""

    output = re.sub(r"{{ progress }}", progress, output)
    output = re.sub(r"{{ lang_list }}", lang_list, output)

    create_output_folder()
    with open(
        os.path.join(__DIRNAME__, "generated/github-stats-languages.svg"), "w"
    ) as f:
        f.write(output)


async def main() -> None:
    access_token = os.getenv("ACCESS_TOKEN")
    if not access_token:
        raise Exception("A personal access token is required to proceed!")
    user = os.getenv("GITHUB_ACTOR")
    if user is None:
        raise RuntimeError("Environment variable GITHUB_ACTOR must be set.")
    exclude_repos = os.getenv("EXCLUDED")
    excluded_repos = (
        {x.strip() for x in exclude_repos.split(",")} if exclude_repos else None
    )
    exclude_langs = os.getenv("EXCLUDED_LANGS")
    excluded_langs = (
        {x.strip() for x in exclude_langs.split(",")} if exclude_langs else None
    )
    raw_exclude_forked_repos = os.getenv("EXCLUDE_FORKED_REPOS")
    exclude_forked_repos = (
        not not raw_exclude_forked_repos
        and raw_exclude_forked_repos.strip().lower() != "false"
    )
    raw_exclude_private_repos = os.getenv("EXCLUDE_PRIVATE_REPOS")
    exclude_private_repos = (
        not not raw_exclude_private_repos
        and raw_exclude_private_repos.strip().lower() != "false"
    )
    async with aiohttp.ClientSession() as session:
        s = Stats(
            user,
            access_token,
            session,
            exclude_repos=excluded_repos,
            exclude_langs=excluded_langs,
            exclude_forked_repos=exclude_forked_repos,
            exclude_private_repos=exclude_private_repos,
        )
        await asyncio.gather(generate_languages(s), generate_overview(s))


if __name__ == "__main__":
    asyncio.run(main())
