# Static

## `github-stats`

A workflow that generates various statistics about my GitHub activity in the form of SVGs. Check out the [original project (GitHub Stats Visualization)](https://github.com/jstrieb/github-stats) and [idiotWu's more updated fork](https://github.com/idiotWu/stats) that served as the basis for some of the changes I made.

![](https://raw.githubusercontent.com/uncenter/static/main/github-stats-overview-dark.svg)
![](https://raw.githubusercontent.com/uncenter/static/main/github-stats-languages-light.svg)
![](https://raw.githubusercontent.com/uncenter/static/main/github-stats-overview-light.svg)
![](https://raw.githubusercontent.com/uncenter/static/main/github-stats-languages-light.svg)

### Features

-   No distracting animations
-   Consistent styling and overall layout between the two generated images
-   No gaps between colors in the languages progress bar
-   Languages aligned in clean looking columns
-   Larger color circles for each language label
-   `EXCLUDE_PRIVATE_REPOS` option

### Options

-   For each of the following options, add a new secret with the name and value to your repository's secrets (under the `Settings` tab). Some of the values are added as secrets by default to prevent leaking information about private repositories. If you're not worried about that, you can change the values directly in the workflow itself - just replace `VARIABLE_NAME: ${{ secrets.VARIABLE_NAME }}` with the value you want, like `VARIABLE_NAME: true`.
-   For example, to exclude certain repos, add a new secret or value called `EXCLUDED` with a value of `USERNAME/REPOSITORY,USERNAME/REPOSITORY2`.
-   To ignore certain languages, add them (separated by commas) to a new secret called `EXCLUDED_LANGS`. For example, to exclude HTML and TeX you could set the value to `html,tex`.
-   To show statistics only for "owned" repositories and not forks with contributions, add an environment variable (under the `env` header in the [main workflow](https://github.com/uncenter/static/blob/main/.github/workflows/github-stats.yml)) called `EXCLUDE_FORKED_REPOS` with a value of `true`.
-   To show statistics for only public repositories and not your privated ones, add an environment variable (under the `env` header in the [main workflow](https://github.com/uncenter/static/blob/main/.github/workflows/github-stats.yml)) called `EXCLUDE_PRIVATE_REPOS` with a value of `true`.
