# `github-stats`

A workflow that generates various statistics about my GitHub activity in the form of SVGs. Check out the [original project (GitHub Stats Visualization)](https://github.com/jstrieb/github-stats) and [idiotWu's more updated fork](https://github.com/idiotWu/stats) that served as the basis for some of the changes I made.

![](https://raw.githubusercontent.com/uncenter/github-stats/main/github-stats-overview-dark.svg)
![](https://raw.githubusercontent.com/uncenter/github-stats/main/github-stats-languages-dark.svg)
![](https://raw.githubusercontent.com/uncenter/github-stats/main/github-stats-community-dark.svg)
![](https://raw.githubusercontent.com/uncenter/github-stats/main/github-stats-overview-light.svg)
![](https://raw.githubusercontent.com/uncenter/github-stats/main/github-stats-languages-light.svg)
![](https://raw.githubusercontent.com/uncenter/github-stats/main/github-stats-community-light.svg)

## Features

-   No distracting animations
-   Consistent styling and overall layout between the two generated images
-   No gaps between colors in the languages progress bar
-   Languages aligned in clean looking columns
-   Larger color circles for each language label
-   `EXCLUDE_PRIVATE_REPOS` option
-   Additional `community` image/card

## Options

For each of the following options, add a new secret with the name and value to your repository's secrets (under the `Settings` tab). Some of the values are added as secrets by default to prevent leaking information about private repositories. If you're not worried about that, you can change the values directly in the workflow itself - just replace `VARIABLE_NAME: ${{ secrets.VARIABLE_NAME }}` with the value you want, like `VARIABLE_NAME: true`. Any options which take "lists" of values should be set as comma seperated values inside a single string.

-   To exclude certain repos, set the variable `EXCLUDED` to `USERNAME/REPOSITORY,USERNAME/REPOSITORY2`.
-   To ignore certain languages, set the variable `EXCLUDED_LANGS` to `lang,lang2`. Languages are not case sensitive.
-   To show statistics only for "owned" repositories and not forks with contributions, set the variable called `EXCLUDE_FORKED_REPOS` to `true`.
-   To show statistics for only public repositories and not your privated ones, set the variable `EXCLUDE_PRIVATE_REPOS` to `true`.
-   To customize the output path, set the `GENERATED_IMAGE_NAME` variable. The default is `github-stats-{{ template }}-{{ theme }}.svg`, which will generate files like `github-stats-overview-dark.svg` and `github-stats-languages-light.svg`. Make sure to include the `.svg` extension and keep the `{{ template }}` and `{{ theme }}` variables (somewhere) in the name.
