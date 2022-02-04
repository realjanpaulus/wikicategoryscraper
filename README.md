# wikicategoryscraper

Scrape Wikipedia pages by category. To scrape the desired categories, you have to create a json file in the `data` directory with the following format:

```
{
    "Bronzezeit": [
        "Kategorie:Bronzezeit_(Alter_Orient)",
        "Kategorie:Archäoastronomie_(Bronzezeit)"
    ],
}
```

The subcategories has to be chosen by hand. Use the name within the URL as value, e.g. for https://de.wikipedia.org/wiki/Kategorie:Bronzezeit_(Alter_Orient), use "Kategorie:Bronzezeit_(Alter_Orient)" (the underscore within the name is important!). Options to limit the number of articles or the minimum and maximum length of a single article can be found in the section **Usage**.

## Virtual Environment Setup

Create and activate the environment (the python version and the environment name can vary at will):

```sh
$ python3.9 -m venv .env
$ source .env/bin/activate
```

To install the project's dependencies, use the following:

```sh
$ pip install -r requirements.txt
```

Deactivate the environment:

```sh
$ deactivate
```

## Usage

```sh
usage: wikiscraper [-h] [--lang LANG] [--max_articles MAX_ARTICLES] [--max_article_length MAX_ARTICLE_LENGTH] [--min_article_length MIN_ARTICLE_LENGTH] [--output_format {csv,json}] path

Tool to create a corpus of Wikipedia articles based on Wikipedia categories.

positional arguments:
  path                  Path to the JSON-File which contains the dictionary of the Wikipedia categories.

optional arguments:
  -h, --help            show this help message and exit
  --lang LANG, -l LANG  ISO2 lang string (default: 'de').
  --max_articles MAX_ARTICLES, -ma MAX_ARTICLES
                        Sets the maximum of articles per category (default: 1000).
  --max_article_length MAX_ARTICLE_LENGTH, -max MAX_ARTICLE_LENGTH
                        Maximum size of the article by characters (default: 10000).
  --min_article_length MIN_ARTICLE_LENGTH, -min MIN_ARTICLE_LENGTH
                        Minimum size of the article by characters (default: 0).
  --output_format {csv,json}, -of {csv,json}
                        Format for the output (default: 'json').
```
