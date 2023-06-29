# Static

## To-do

-   [ ] `community.svg` and `overview.svg` templates are identical except for table rows - figure out how to generate both from one template
-   [ ] Add new cards without adding a new function to `generate_images.py`?
-   [ ] Add environment variables for generated file names, headers, etc.

## `github-stats`

A workflow that generates various statistics about my GitHub activity in the form of SVGs. Check out the [original project (GitHub Stats Visualization)](https://github.com/jstrieb/github-stats) and [idiotWu's more updated fork](https://github.com/idiotWu/stats) that served as the basis for some of the changes I made.

![](https://raw.githubusercontent.com/uncenter/static/main/github-stats-overview-dark.svg)
![](https://raw.githubusercontent.com/uncenter/static/main/github-stats-languages-dark.svg)
![](https://raw.githubusercontent.com/uncenter/static/main/github-stats-community-dark.svg)
![](https://raw.githubusercontent.com/uncenter/static/main/github-stats-overview-light.svg)
![](https://raw.githubusercontent.com/uncenter/static/main/github-stats-languages-light.svg)
![](https://raw.githubusercontent.com/uncenter/static/main/github-stats-community-light.svg)

### Features

-   No distracting animations
-   Consistent styling and overall layout between the two generated images
-   No gaps between colors in the languages progress bar
-   Languages aligned in clean looking columns
-   Larger color circles for each language label
-   `EXCLUDE_PRIVATE_REPOS` option

### Displaying with media queries

```html
<picture>
    <source
        srcset="
            https://raw.githubusercontent.com/uncenter/static/main/github-stats-languages-dark.svg
        "
        media="(prefers-color-scheme: dark)"
    />
    <img
        src="https://raw.githubusercontent.com/uncenter/static/main/github-stats-languages-light.svg"
    />
</picture>
<picture>
    <source
        srcset="
            https://raw.githubusercontent.com/uncenter/static/main/github-stats-overview-dark.svg
        "
        media="(prefers-color-scheme: dark)"
    />
    <img
        src="https://raw.githubusercontent.com/uncenter/static/main/github-stats-overview-light.svg"
    />
</picture>
```

### Options

-   For each of the following options, add a new secret with the name and value to your repository's secrets (under the `Settings` tab). Some of the values are added as secrets by default to prevent leaking information about private repositories. If you're not worried about that, you can change the values directly in the workflow itself - just replace `VARIABLE_NAME: ${{ secrets.VARIABLE_NAME }}` with the value you want, like `VARIABLE_NAME: true`.
-   For example, to exclude certain repos, add a new secret or value called `EXCLUDED` with a value of `USERNAME/REPOSITORY,USERNAME/REPOSITORY2`.
-   To ignore certain languages, add them (separated by commas) to a new secret called `EXCLUDED_LANGS`. For example, to exclude HTML and TeX you could set the value to `html,tex`. Languages are not case sensitive.
-   To show statistics only for "owned" repositories and not forks with contributions, add an environment variable (under the `env` header in the [main workflow](https://github.com/uncenter/static/blob/main/.github/workflows/github-stats.yml)) called `EXCLUDE_FORKED_REPOS` with a value of `true`.
-   To show statistics for only public repositories and not your privated ones, add an environment variable (under the `env` header in the [main workflow](https://github.com/uncenter/static/blob/main/.github/workflows/github-stats.yml)) called `EXCLUDE_PRIVATE_REPOS` with a value of `true`.
-   To customize the output path, edit the `GENERATED_IMAGE_NAME` environment variable. The default is `github-stats-{{ template }}-{{ theme }}.svg`, which will generate files like `github-stats-overview-dark.svg` and `github-stats-languages-light.svg`. Make sure to include the `.svg` extension and keep the `{{ template }}` and `{{ theme }}` variables (somewhere) in the name.
