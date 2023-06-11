# Static

## `github-stats`

A workflow that generates various statistics about my GitHub activity in the form of SVGs (in the [`/generated`](/generated) directory). Check out the [original project (GitHub Stats Visualization)](https://github.com/jstrieb/github-stats) and [idiotWu's more updated fork](https://github.com/idiotWu/stats) that this was inspired by.

![](https://raw.githubusercontent.com/uncenter/static/github-stats/overview.svg#gh-dark-mode-only)
![](https://raw.githubusercontent.com/uncenter/static/github-stats/languages.svg#gh-dark-mode-only)
![](https://raw.githubusercontent.com/uncenter/static/github-stats/overview.svg#gh-light-mode-only)
![](https://raw.githubusercontent.com/uncenter/static/github-stats/languages.svg#gh-light-mode-only)

### Features

-   No distracting animations
-   Consistent styling between the two generated images
-   No gaps between colors in the languages progress bar
-   Languages aligned in clean looking columns
-   Larger color circles for each language label
-   `EXCLUDE_PRIVATE_REPOS` option

### Installation

<!-- TODO: Add details and screenshots -->

1. Create a personal access token (not the default GitHub Actions token) using the instructions [here](https://docs.github.com/en/github/authenticating-to-github/creating-a-personal-access-token). This personal access token must have permissions: `read:user` and `repo`. Copy the access token when it is generated and save it somewhere secure - if you lose it, you will have to regenerate the token.
2. Clone or download the related files (`.github/workflows/github-stats.yml`, `templates/`, `.gitattributes`, `.gitignore`, `generate_images.py`, `github_stats.py`, `requirements.txt`) and add them to a repository of your own.
3. Go to the "Secrets" page of your copy of the repository: click the "Settings" tab of the newly-created repository, expand the "Secrets and variables" section on the left, and click "Actions".
4. Create a new secret with the name `ACCESS_TOKEN` and paste your copied personal access token as the value.
5. It is possible to change the type of statistics reported by adding other repository secrets.
    - To ignore certain repos, add them (in owner/name format, e.g. `USERNAME/REPOSITORY`) separated by commas to a new secret called `EXCLUDED`.
    - To ignore certain languages, add them (separated by commas) to a new secret called `EXCLUDED_LANGS`. For example, to exclude HTML and TeX you could set the value to `html,tex`.
    - To show statistics only for "owned" repositories and not forks with contributions, add an environment variable (under the `env` header in the [main workflow](https://github.com/uncenter/static/blob/main/.github/workflows/github-stats.yml)) called `EXCLUDE_FORKED_REPOS` with a value of `true`.
    - To show statistics for only public repositories and not your privated ones, add an environment variable (under the `env` header in the [main workflow](https://github.com/uncenter/static/blob/main/.github/workflows/github-stats.yml)) called `EXCLUDE_PRIVATE_REPOS` with a value of `true`.
    - These other values are added as secrets by default to prevent leaking information about private repositories. If you're not worried about that, you can change the values directly in the workflow itself - just replace `VARIABLE_NAME: ${{ secrets.VARIABLE_NAME }}` with the value you want, like `VARIABLE_NAME: true`.
6. Go to the "Actions" tab, click "Generate github-stats images..." on the left, and press "Run Workflow" on the right side of the screen to generate images for the first time.
    - The images will be automatically regenerated every 24 hours, but they can be regenerated manually by running the workflow this way.
7. Take a look at the images that have been created in the [`generated`](generated) folder.
8. To add your statistics to your GitHub Profile README, copy and paste the following lines of code into your markdown content. Replace `USERNAME` with your GitHub username and `REPOSITORY` with the name of your new repository.

```md
![](https://raw.githubusercontent.com/USERNAME/REPOSITORY/github-stats/overview.svg#gh-dark-mode-only)
![](https://raw.githubusercontent.com/USERNAME/REPOSITORY/github-stats/languages.svg#gh-dark-mode-only)
![](https://raw.githubusercontent.com/USERNAME/REPOSITORY/github-stats/overview.svg#gh-light-mode-only)
![](https://raw.githubusercontent.com/USERNAME/REPOSITORY/github-stats/languages.svg#gh-light-mode-only)
```
