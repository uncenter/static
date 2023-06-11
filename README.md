# Static

## `github-stats`

A workflow that generates various statistics about my GitHub activity in the form of SVGs (in the [`/generated`](/generated) directory). Check out the [original project (GitHub Stats Visualization)](https://github.com/jstrieb/github-stats) and [idiotWu's more updated fork](https://github.com/idiotWu/stats) that this was inspired by.

![](https://raw.githubusercontent.com/uncenter/static/main/github-stats-overview.svg#gh-dark-mode-only)
![](https://raw.githubusercontent.com/uncenter/static/main/github-stats-languages.svg#gh-dark-mode-only)
![](https://raw.githubusercontent.com/uncenter/static/main/github-stats-overview.svg#gh-light-mode-only)
![](https://raw.githubusercontent.com/uncenter/static/main/github-stats-languages.svg#gh-light-mode-only)

### Features

-   No distracting animations
-   Consistent styling between the two generated images
-   No gaps between colors in the languages progress bar
-   Languages aligned in clean looking columns
-   Larger color circles for each language label
-   `EXCLUDE_PRIVATE_REPOS` option

### Options

-   To ignore certain repos, add them (in owner/name format, e.g. `USERNAME/REPOSITORY`) separated by commas to a new secret called `EXCLUDED`.
-   To ignore certain languages, add them (separated by commas) to a new secret called `EXCLUDED_LANGS`. For example, to exclude HTML and TeX you could set the value to `html,tex`.
-   To show statistics only for "owned" repositories and not forks with contributions, add an environment variable (under the `env` header in the [main workflow](https://github.com/uncenter/static/blob/main/.github/workflows/github-stats.yml)) called `EXCLUDE_FORKED_REPOS` with a value of `true`.
-   To show statistics for only public repositories and not your privated ones, add an environment variable (under the `env` header in the [main workflow](https://github.com/uncenter/static/blob/main/.github/workflows/github-stats.yml)) called `EXCLUDE_PRIVATE_REPOS` with a value of `true`.
-   These other values are added as secrets by default to prevent leaking information about private repositories. If you're not worried about that, you can change the values directly in the workflow itself - just replace `VARIABLE_NAME: ${{ secrets.VARIABLE_NAME }}` with the value you want, like `VARIABLE_NAME: true`.
