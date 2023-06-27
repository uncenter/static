#!/usr/bin/python3

import asyncio
import os
import re
import aiohttp
import json

from github_stats import Stats

__DIRNAME__ = os.path.realpath(os.path.dirname(__file__))


def create_output_folder() -> None:
    if not os.path.isdir(os.path.join(os.path.join(__DIRNAME__, "generated"))):
        os.mkdir(os.path.join(__DIRNAME__, "generated"))


def replace_with_data(data, content):
    for key, value in data.items():
        content = re.sub("{{ " + key + " }}", value, content)
    return content


def get_inserted_styles():
    with open(os.path.join(__DIRNAME__, "templates/styles.json"), "r") as f:
        raw_styles = json.load(f)

    dark_styles = {}
    light_styles = {}
    for key, value in raw_styles.items():
        _selector = value.get("selector")
        _properties = value.get("properties")
        _both = (
            (_properties.get("both").items()) if _properties.get("both") != None else {}
        )
        _light = (
            (_properties.get("light").items())
            if _properties.get("light") != None
            else {}
        )
        _dark = (
            (_properties.get("dark").items()) if _properties.get("dark") != None else {}
        )
        if _selector != False:
            _both_properties = "".join([f"{prop}: {val};\n" for prop, val in _both])
            _light_properties = "".join([f"{prop}: {val};\n" for prop, val in _light])
            _dark_properties = "".join([f"{prop}: {val};\n" for prop, val in _dark])
            light_styles[key] = f"{_selector} {{{_both_properties}{_light_properties}}}"
            dark_styles[key] = f"{_selector} {{{_both_properties}{_dark_properties}}}"

        for prop, val in _light:
            light_styles[f"{key}.{prop}"] = val
        for prop, val in _dark:
            dark_styles[f"{key}.{prop}"] = val
        for prop, val in _both:
            light_styles[f"{key}.{prop}"] = val
            dark_styles[f"{key}.{prop}"] = val

    return {
        "light": {f"styles.{key}": value for key, value in light_styles.items()},
        "dark": {f"styles.{key}": value for key, value in dark_styles.items()},
    }


async def generate_overview(s: Stats) -> None:
    """
    Generate an SVG badge with summary statistics
    :param s: Represents user's GitHub statistics
    """
    with open(os.path.join(__DIRNAME__, "templates/overview.svg"), "r") as f:
        template = f.read()

    output = replace_with_data(
        {
            "name": await s.name,
            "stars": f"{await s.stargazers:,}",
            "forks": f"{await s.forks:,}",
            "contributions": f"{await s.total_contributions:,}",
            "lines_changed": f"{((await s.lines_changed)[0] + (await s.lines_changed)[1]):,}",
            "views": f"{await s.views:,}",
            "repos": f"{len(await s.repos):,}",
        },
        template,
    )

    create_output_folder()

    for theme in ["light", "dark"]:
        with open(
            os.path.join(__DIRNAME__, f"generated/github-stats-overview-{theme}.svg"),
            "w",
        ) as f:
            f.write(replace_with_data(get_inserted_styles()[theme], output))


async def generate_languages(s: Stats) -> None:
    """
    Generate an SVG badge with summary languages used
    :param s: Represents user's GitHub statistics
    """
    with open(os.path.join(__DIRNAME__, "templates/languages.svg"), "r") as f:
        template = f.read()

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

    output = replace_with_data(
        {
            "progress": progress,
            "lang_list": lang_list,
        },
        template,
    )

    create_output_folder()

    for theme in ["light", "dark"]:
        with open(
            os.path.join(__DIRNAME__, f"generated/github-stats-languages-{theme}.svg"),
            "w",
        ) as f:
            f.write(replace_with_data(get_inserted_styles()[theme], output))


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
