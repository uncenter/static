#!/usr/bin/python3

import asyncio
import os
import re
import aiohttp
import json
from dotenv import load_dotenv
from typing import Dict

from github_stats import Stats

load_dotenv()

__DIRNAME__ = os.path.realpath(os.path.dirname(__file__))
__TEMPLATE_DIR__ = os.path.join(__DIRNAME__, "templates")
__OUTPUT_DIR__ = os.path.join(__DIRNAME__, "generated")


def create_output_folder() -> None:
    """
    Create the output folder if it doesn't exist.
    """

    if not os.path.isdir(__OUTPUT_DIR__):
        os.mkdir(__OUTPUT_DIR__)


def replace_with_data(data: Dict[str, str], content: str) -> str:
    """
    Replace placeholder strings in a template with associated data.

    Args:
        data (dict[str, str]): A dictionary of placeholder strings and their associated data.
        content (str): The template content.

    Returns:
        str: The template content with the placeholder strings replaced.
    """

    for key, value in data.items():
        content = re.sub("{{ " + key + " }}", value, content)
    return content


def get_inserted_styles() -> Dict[str, Dict[str, str]]:
    """
    Convert template styles from JSON to CSS properties, themed for light and dark mode.

    Returns:
        dict[str, dict[str, str]]: A dictionary with two keys, "light" and "dark", each containing a dictionary of theme-specific CSS properties.
    """

    with open(os.path.join(__TEMPLATE_DIR__, "styles.json"), "r") as f:
        raw_styles = json.load(f)

    dark_styles = {}
    light_styles = {}
    for key, value in raw_styles.items():
        _selector = value.get("selector")
        _properties = value.get("properties")
        _both = (
            (_properties.get("both").items())
            if _properties.get("both") is not None
            else {}
        )
        _light = (
            (_properties.get("light").items())
            if _properties.get("light") is not None
            else {}
        )
        _dark = (
            (_properties.get("dark").items())
            if _properties.get("dark") is not None
            else {}
        )
        if _selector is not False:
            _both_properties = "".join([f"\t{prop}: {val};\n" for prop, val in _both])
            _light_properties = "".join([f"\t{prop}: {val};\n" for prop, val in _light])
            _dark_properties = "".join([f"\t{prop}: {val};\n" for prop, val in _dark])
            light_styles[
                key
            ] = f"{_selector} {{\n{_both_properties}{_light_properties}}}"
            dark_styles[key] = f"{_selector} {{\n{_both_properties}{_dark_properties}}}"

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


async def generate_overview(s: Stats, output_path: str) -> None:
    """
    Generate the overview image.

    Args:
        s (Stats): The Stats object.
    """

    with open(os.path.join(__TEMPLATE_DIR__, "overview.svg"), "r") as f:
        template = f.read()

    output = replace_with_data(
        {
            "name": await s.name,
            "stars": f"{await s.stargazers:,}",
            "forks": f"{await s.forks:,}",
            "contributions": f"{await s.total_contributions:,}",
            "lines_changed": f"{((await s.lines_changed)[0] + (await s.lines_changed)[1]):,}",
            "repos": f"{len(await s.repos):,}",
        },
        template,
    )

    create_output_folder()

    for theme in ["light", "dark"]:
        with open(
            os.path.join(
                __OUTPUT_DIR__, replace_with_data({"theme": theme}, output_path)
            ),
            "w",
        ) as f:
            f.write(replace_with_data(get_inserted_styles()[theme], output))


async def generate_languages(s: Stats, output_path: str) -> None:
    """
    Generate the languages image.

    Args:
        s (Stats): The Stats object.
    """

    with open(os.path.join(__TEMPLATE_DIR__, "languages.svg"), "r") as f:
        template = f.read()

    progress = ""
    lang_list = ""
    sorted_languages = sorted(
        (await s.languages).items(), reverse=True, key=lambda t: t[1].get("size")
    )[:8]
    for lang, data in sorted_languages:
        color = data.get("color")
        color = color if color is not None else "#000000"
        progress += f'<span style="background-color: {color}; width: {data.get("prop", 0):0.3f}%;"></span>'
        lang_list += f"""<li>
<svg xmlns="http://www.w3.org/2000/svg" class="octicon" style="fill:{color};" viewBox="0 0 16 16" width="16" height="16"><circle xmlns="http://www.w3.org/2000/svg" cx="8" cy="9" r="5" /></svg>
<span class="lang">{lang}</span>
<span class="percent">{data.get("prop", 0):0.2f}%</span>
</li>"""

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
            os.path.join(
                __OUTPUT_DIR__, replace_with_data({"theme": theme}, output_path)
            ),
            "w",
        ) as f:
            f.write(replace_with_data(get_inserted_styles()[theme], output))


async def generate_community(s: Stats, output_path: str) -> None:
    """
    Generate the community image.

    Args:
        s (Stats): The Stats object.
    """

    with open(os.path.join(__TEMPLATE_DIR__, "community.svg"), "r") as f:
        template = f.read()

    output = replace_with_data(
        {
            "joined": await s.joined,
            "followers": f"{await s.followers:,}",
            "following": f"{await s.following:,}",
            "stars": f"{await s.starred_repos:,}",
            "sponsoring": f"{await s.sponsoring:,}",
        },
        template,
    )

    create_output_folder()

    for theme in ["light", "dark"]:
        with open(
            os.path.join(
                __OUTPUT_DIR__, replace_with_data({"theme": theme}, output_path)
            ),
            "w",
        ) as f:
            f.write(replace_with_data(get_inserted_styles()[theme], output))


async def main() -> None:
    def string_to_list(string) -> list:
        """
        Convert a comma-separated string to a list of strings

        Args:
            string (str): A comma-separated string

        Returns:
            list: A list of strings
        """

        return [x.strip() for x in string.split(",")] if string else []

    def truthy(value, default=False) -> bool:
        """
        Convert an unknown value to a boolean

        Args:
            value (str, int, bool): An unknown value

        Returns:
            bool: The boolean representation of the value
        """

        if type(value) == str:
            return value.strip().lower() in ["true", "1", "yes", "y"]
        elif type(value) == int:
            return value == 1
        elif type(value) == bool:
            return value
        return default

    access_token = os.getenv("ACCESS_TOKEN")
    if not access_token:
        raise Exception("A personal access token is required to proceed!")
    user = os.getenv("GITHUB_ACTOR")
    if user is None:
        raise RuntimeError("Environment variable GITHUB_ACTOR must be set.")
    excluded_repos = string_to_list(os.getenv("EXCLUDED"))
    excluded_langs = string_to_list(os.getenv("EXCLUDED_LANGS"))
    exclude_forked_repos = truthy(os.getenv("EXCLUDE_FORKED_REPOS"), True)
    exclude_private_repos = truthy(os.getenv("EXCLUDE_PRIVATE_REPOS"), True)
    generated_image_path = os.getenv("GENERATED_IMAGE_PATH")
    if generated_image_path is None:
        raise RuntimeError("Environment variable GENERATED_IMAGE_PATH must be set.")
    else:
        generated_image_path = generated_image_path.strip()
        if generated_image_path.endswith(".svg") is False:
            raise RuntimeError(
                "Environment variable GENERATED_IMAGE_PATH must end with .svg"
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
        await asyncio.gather(
            generate_languages(
                s,
                replace_with_data(
                    {
                        "template": "languages",
                    },
                    generated_image_path,
                ),
            ),
            generate_overview(
                s,
                replace_with_data(
                    {
                        "template": "overview",
                    },
                    generated_image_path,
                ),
            ),
            generate_community(
                s, replace_with_data({"template": "community"}, generated_image_path)
            ),
        )


if __name__ == "__main__":
    asyncio.run(main())
