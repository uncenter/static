#!/usr/bin/python3

import aiohttp
import requests
import asyncio
import os
import pendulum
from typing import Dict, List, Optional, Set, Tuple, Any, cast


class Queries(object):
    def __init__(
        self,
        username: str,
        access_token: str,
        session: aiohttp.ClientSession,
        max_connections: int = 10,
    ):
        self.username = username
        self.access_token = access_token
        self.session = session
        self.semaphore = asyncio.Semaphore(max_connections)

    async def query(self, generated_query: str) -> Dict:
        """
        Args:
            generated_query (str): string query to be sent to the API

        Returns:
            Dict: decoded GraphQL JSON output
        """

        headers = {
            "Authorization": f"Bearer {self.access_token}",
        }
        try:
            async with self.semaphore:
                r_async = await self.session.post(
                    "https://api.github.com/graphql",
                    headers=headers,
                    json={"query": generated_query},
                )
            result = await r_async.json()
            if result is not None:
                return result
        except:
            print("aiohttp failed for GraphQL query")
            async with self.semaphore:
                r_requests = requests.post(
                    "https://api.github.com/graphql",
                    headers=headers,
                    json={"query": generated_query},
                )
                result = r_requests.json()
                if result is not None:
                    return result
        return dict()

    async def query_rest(self, path: str, params: Optional[Dict] = None) -> Dict:
        """
        Args:
            path (str): API path to query
            params (Optional[Dict], optional): Query parameters to be passed to the API. Defaults to None.

        Returns:
            Dict: deserialized REST JSON output
        """

        for _ in range(60):
            headers = {
                "Authorization": f"token {self.access_token}",
            }
            if params is None:
                params = dict()
            if path.startswith("/"):
                path = path[1:]
            try:
                async with self.semaphore:
                    r_async = await self.session.get(
                        f"https://api.github.com/{path}",
                        headers=headers,
                        params=tuple(params.items()),
                    )
                if r_async.status == 202:
                    print("A path returned 202. Retrying...")
                    await asyncio.sleep(2)
                    continue

                result = await r_async.json()
                if result is not None:
                    return result
            except:
                async with self.semaphore:
                    r_requests = requests.get(
                        f"https://api.github.com/{path}",
                        headers=headers,
                        params=tuple(params.items()),
                    )
                    if r_requests.status_code == 202:
                        print("A path returned 202. Retrying...")
                        await asyncio.sleep(2)
                        continue
                    elif r_requests.status_code == 200:
                        return r_requests.json()
        print("There were too many 202s. Data for this repository will be incomplete.")
        return dict()

    @staticmethod
    def overview(
        contrib_cursor: Optional[str] = None,
        owned_cursor: Optional[str] = None,
        options: Dict = dict(),
    ) -> str:
        """
        Returns a GraphQL query to get overall stats for a user

        Args:
            contrib_cursor (Optional[str], optional): cursor for contributions. Defaults to None.
            owned_cursor (Optional[str], optional): cursor for owned repositories. Defaults to None.
            options (Dict, optional): options for the query. Defaults to dict().
                exclude_private_repos (bool, optional): whether to exclude private repos. Defaults to False.

        Returns:
            str: GraphQL query
        """

        exclude_private_repos = options.get("exclude_private_repos", False)
        return f"""{{
    viewer {{
        login,
        name,
        createdAt,
        followers {{
            totalCount
        }},
        following {{
            totalCount
        }},
        sponsoring {{
            totalCount
        }},
        starredRepositories {{
            totalCount
        }},
        repositories(
            {"privacy: PUBLIC," if exclude_private_repos else ""}
            first: 100,
            orderBy: {{
                field: UPDATED_AT,
                direction: DESC
            }},
            isFork: false,
            ownerAffiliations: [OWNER, ORGANIZATION_MEMBER],
            after: {"null" if owned_cursor is None else '"'+ owned_cursor +'"'}
        ) {{
            pageInfo {{
                hasNextPage
                endCursor
            }}
            nodes {{
                nameWithOwner
                stargazers {{
                    totalCount
                }}
                forkCount
                languages(first: 10, orderBy: {{field: SIZE, direction: DESC}}) {{
                    edges {{
                        size
                        node {{
                            name
                            color
                        }}
                    }}
                }}
            }}
        }}
        repositoriesContributedTo(
            first: 100,
            includeUserRepositories: false,
            orderBy: {{
                field: UPDATED_AT,
                direction: DESC
            }},
            contributionTypes: [
                COMMIT,
                PULL_REQUEST,
                REPOSITORY,
                PULL_REQUEST_REVIEW
            ]
            after: {"null" if contrib_cursor is None else '"'+ contrib_cursor +'"'}
        ) {{
            pageInfo {{
                hasNextPage
                endCursor
            }}
            nodes {{
                nameWithOwner
                stargazers {{
                    totalCount
                }}
                forkCount
                languages(first: 10, orderBy: {{field: SIZE, direction: DESC}}) {{
                    edges {{
                        size
                        node {{
                            name
                            color
                        }}
                    }}
                }}
            }}
        }}
    }}
}}"""

    @staticmethod
    def contrib_years() -> str:
        """
        Returns a GraphQL query to get the years for which a user has contributions

        Returns:
            str: GraphQL query
        """

        return """
query {
    viewer {
        contributionsCollection {
            contributionYears
        }
    }
}
"""

    @staticmethod
    def contribs_by_year(year: str) -> str:
        """
        Args:
            year (str): year to query for

        Returns:
            str: portion of a GraphQL query with desired info for a given year
        """

        return f"""
    year{year}: contributionsCollection(
        from: "{year}-01-01T00:00:00Z",
        to: "{int(year) + 1}-01-01T00:00:00Z"
    ) {{
        contributionCalendar {{
            totalContributions
        }}
    }}
"""

    @classmethod
    def all_contribs(cls, years: List[str]) -> str:
        """
        Get contributions for all years

        Args:
            years (List[str]): list of years to get contributions for

        Returns:
            str: GraphQL query
        """

        by_years = "\n".join(map(cls.contribs_by_year, years))
        return f"""
query {{
    viewer {{
        {by_years}
    }}
}}
"""


class Stats(object):
    """
    Retrieve and store statistics about GitHub usage.
    """

    def __init__(
        self,
        username: str,
        access_token: str,
        session: aiohttp.ClientSession,
        exclude_repos: Optional[Set] = None,
        exclude_langs: Optional[Set] = None,
        exclude_forked_repos: bool = False,
        exclude_private_repos: bool = False,
    ):
        self.username = username
        self._exclude_forked_repos = exclude_forked_repos
        self._exclude_private_repos = exclude_private_repos
        self._exclude_repos = set() if exclude_repos is None else exclude_repos
        self._exclude_langs = set() if exclude_langs is None else exclude_langs
        self.queries = Queries(username, access_token, session)

        self._name: Optional[str] = None
        self._joined: Optional[str] = None
        self._followers: Optional[int] = None
        self._following: Optional[int] = None
        self._sponsoring: Optional[int] = None
        self._starred_repos: Optional[int] = None
        self._stargazers: Optional[int] = None
        self._forks: Optional[int] = None
        self._total_contributions: Optional[int] = None
        self._languages: Optional[Dict[str, Any]] = None
        self._repos: Optional[Set[str]] = None
        self._lines_changed: Optional[Tuple[int, int]] = None

    async def get_stats(self) -> None:
        """
        Get statistics about GitHub usage.
        """

        self._stargazers = 0
        self._forks = 0
        self._languages = dict()
        self._repos = set()

        next_owned = None
        next_contrib = None
        while True:
            raw_results = await self.queries.query(
                Queries.overview(
                    owned_cursor=next_owned,
                    contrib_cursor=next_contrib,
                    options={
                        "exclude_private_repos": self._exclude_private_repos,
                    },
                )
            )
            raw_results = raw_results if raw_results is not None else {}

            self._name = raw_results.get("data", {}).get("viewer", {}).get("name", None)
            if self._name is None:
                self._name = (
                    raw_results.get("data", {})
                    .get("viewer", {})
                    .get("login", "No Name")
                )

            created_at = (
                raw_results.get("data", {}).get("viewer", {}).get("createdAt", None)
            )
            if created_at is not None:
                self._joined = pendulum.parse(created_at).diff_for_humans()
            else:
                self._joined = "Unknown"

            self._followers = (
                raw_results.get("data", {})
                .get("viewer", {})
                .get("followers", {})
                .get("totalCount", 0)
            )
            self._following = (
                raw_results.get("data", {})
                .get("viewer", {})
                .get("following", {})
                .get("totalCount", 0)
            )
            self._sponsoring = (
                raw_results.get("data", {})
                .get("viewer", {})
                .get("sponsoring", {})
                .get("totalCount", 0)
            )
            self._starred_repos = (
                raw_results.get("data", {})
                .get("viewer", {})
                .get("starredRepositories", {})
                .get("totalCount", 0)
            )

            contrib_repos = (
                raw_results.get("data", {})
                .get("viewer", {})
                .get("repositoriesContributedTo", {})
            )
            owned_repos = (
                raw_results.get("data", {}).get("viewer", {}).get("repositories", {})
            )

            repos = owned_repos.get("nodes", [])
            if not self._exclude_forked_repos:
                repos += contrib_repos.get("nodes", [])

            for repo in repos:
                if repo is None:
                    continue
                name = repo.get("nameWithOwner")
                if name in self._repos or name in self._exclude_repos:
                    continue
                self._repos.add(name)
                self._stargazers += repo.get("stargazers").get("totalCount", 0)
                self._forks += repo.get("forkCount", 0)

                for lang in repo.get("languages", {}).get("edges", []):
                    name = lang.get("node", {}).get("name", "Other")
                    languages = await self.languages
                    if name.lower() in {x.lower() for x in self._exclude_langs}:
                        continue
                    if name in languages:
                        languages[name]["size"] += lang.get("size", 0)
                        languages[name]["occurrences"] += 1
                    else:
                        languages[name] = {
                            "size": lang.get("size", 0),
                            "occurrences": 1,
                            "color": lang.get("node", {}).get("color"),
                        }

            if owned_repos.get("pageInfo", {}).get(
                "hasNextPage", False
            ) or contrib_repos.get("pageInfo", {}).get("hasNextPage", False):
                next_owned = owned_repos.get("pageInfo", {}).get(
                    "endCursor", next_owned
                )
                next_contrib = contrib_repos.get("pageInfo", {}).get(
                    "endCursor", next_contrib
                )
            else:
                break

        langs_total = sum([v.get("size", 0) for v in self._languages.values()])
        for k, v in self._languages.items():
            v["prop"] = 100 * (v.get("size", 0) / langs_total)

    @property
    async def name(self) -> str:
        """
        Returns:
            str: GitHub user's name
        """

        if self._name is not None:
            return self._name
        await self.get_stats()
        assert self._name is not None
        return self._name

    @property
    async def joined(self) -> str:
        """
        Returns:
            str: GitHub user's join date (relative)
        """

        if self._joined is not None:
            return self._joined
        await self.get_stats()
        assert self._joined is not None
        return self._joined

    @property
    async def followers(self) -> int:
        """
        Returns:
            int: total number of followers
        """

        if self._followers is not None:
            return self._followers
        await self.get_stats()
        assert self._followers is not None
        return self._followers

    @property
    async def following(self) -> int:
        """
        Returns:
            int: total number of users followed by the user
        """

        if self._following is not None:
            return self._following
        await self.get_stats()
        assert self._following is not None
        return self._following

    @property
    async def sponsoring(self) -> int:
        """
        Returns:
            int: total number of users and organizations sponsored by the user
        """

        if self._sponsoring is not None:
            return self._sponsoring
        await self.get_stats()
        assert self._sponsoring is not None
        return self._sponsoring

    @property
    async def starred_repos(self) -> int:
        """
        Returns:
            int: total number of repos starred by the user
        """

        if self._starred_repos is not None:
            return self._starred_repos
        await self.get_stats()
        assert self._starred_repos is not None
        return self._starred_repos

    @property
    async def stargazers(self) -> int:
        """
        Returns:
            int: total number of stargazers on user's repos
        """

        if self._stargazers is not None:
            return self._stargazers
        await self.get_stats()
        assert self._stargazers is not None
        return self._stargazers

    @property
    async def forks(self) -> int:
        """
        Returns:
            int: total number of forks on user's repos
        """

        if self._forks is not None:
            return self._forks
        await self.get_stats()
        assert self._forks is not None
        return self._forks

    @property
    async def languages(self) -> Dict:
        """
        Returns:
            Dict: summary of languages used by the user
        """

        if self._languages is not None:
            return self._languages
        await self.get_stats()
        assert self._languages is not None
        return self._languages

    @property
    async def languages_proportional(self) -> Dict:
        """
        Returns:
            Dict: summary of languages used by the user, with proportional usage
        """

        if self._languages is None:
            await self.get_stats()
            assert self._languages is not None

        return {k: v.get("prop", 0) for (k, v) in self._languages.items()}

    @property
    async def repos(self) -> Set[str]:
        """
        Returns:
            Set[str]: list of names of user's repos
        """

        if self._repos is not None:
            return self._repos
        await self.get_stats()
        assert self._repos is not None
        return self._repos

    @property
    async def total_contributions(self) -> int:
        """
        Returns:
            int: count of user's total contributions as defined by GitHub
        """

        if self._total_contributions is not None:
            return self._total_contributions

        self._total_contributions = 0
        years = (
            (await self.queries.query(Queries.contrib_years()))
            .get("data", {})
            .get("viewer", {})
            .get("contributionsCollection", {})
            .get("contributionYears", [])
        )
        by_year = (
            (await self.queries.query(Queries.all_contribs(years)))
            .get("data", {})
            .get("viewer", {})
            .values()
        )
        for year in by_year:
            self._total_contributions += year.get("contributionCalendar", {}).get(
                "totalContributions", 0
            )
        return cast(int, self._total_contributions)

    @property
    async def lines_changed(self) -> Tuple[int, int]:
        """
        Returns:
            Tuple[int, int]: count of lines added and deleted by the user (Tuple[additions, deletions])
        """

        if self._lines_changed is not None:
            return self._lines_changed
        additions = 0
        deletions = 0
        for repo in await self.repos:
            r = await self.queries.query_rest(f"/repos/{repo}/stats/contributors")
            for author_obj in r:
                if not isinstance(author_obj, dict) or not isinstance(
                    author_obj.get("author", {}), dict
                ):
                    continue
                author = author_obj.get("author", {}).get("login", "")
                if author != self.username:
                    continue

                for week in author_obj.get("weeks", []):
                    additions += week.get("a", 0)
                    deletions += week.get("d", 0)

        self._lines_changed = (additions, deletions)
        return self._lines_changed


async def main() -> None:
    access_token = os.getenv("ACCESS_TOKEN")
    user = os.getenv("GITHUB_ACTOR")
    if access_token is None or user is None:
        raise RuntimeError(
            "ACCESS_TOKEN and GITHUB_ACTOR environment variables cannot be None!"
        )
    async with aiohttp.ClientSession() as session:
        s = Stats(user, access_token, session)


if __name__ == "__main__":
    asyncio.run(main())
