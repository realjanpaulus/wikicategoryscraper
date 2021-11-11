import argparse
import json
import logging
import sys
import time
from itertools import chain
from pathlib import Path

import wikipediaapi
from tqdm import tqdm


def extracting_section(
    unnecessary_sections: list, sections: list, level: int = 0
) -> str:
    """Extracts text from a list of sections and its subsections recursively.

    Parameters
    ----------
    unnecessary_sections : list
        List of strings with skippable sections
    sections : list
        List of sections of a Wikipedia article
    level : int, optional
        Current level, by default 0

    Returns
    -------
    str
        Combined sections but without the unnecessary sections
    """
    extracted_text = ""
    for section in sections:
        if section.title not in unnecessary_sections:
            extracted_text += section.text
            extracted_text += extracting_section(
                unnecessary_sections, section.sections, level + 1
            )
    return extracted_text


def generate_categories(
    wikipedia: wikipediaapi.Wikipedia,
    categories: dict,
    unnecessary_sections: list,
    max_articles: int = 200,
    min_article_length: int = 0,
    max_article_length: int = 10000,
) -> dict:
    """Iterates over a dictionary of Wikipedia categories and extracts articles per category until
        the max_articles parameter is reached. Each article has to contain at least 100 words or
        symbols and articles which contain more than 2000 words or symbols will be shortened.
        The name of the category, the shortened article and the length of the article are saved in
        a dictionary which is linked with the articles title.

    Parameters
    ----------
    wikipedia : wikipediaapi.Wikipedia
        Wikipedia class from the `wikipediaapi` module
    categories : dict
        Wikipedia category names with lists of subcategories as values
    unnecessary_sections : list
        List of strings with skippable sections
    max_articles : int, optional
        The maximum of articles per category, by default 200
    min_article_length : int, optional
        The minimum of characters for an article, by default 0
    max_article_length : int, optional
        The maximum of characters for an article, by default 10000

    Returns
    -------
    dict
        Article titles with a dictionary with the keys "category", "text" and "length" as value.
    """

    articles = {}

    for idx, (category_name, subcategories) in enumerate(categories.items()):
        article_counter = 0

        for subcategory in subcategories:
            if article_counter >= max_articles:
                break
            category = wikipedia.page(subcategory)

            for article in tqdm(
                category.categorymembers.values(), desc="Iterating over articles"
            ):
                if article_counter >= max_articles:
                    break
                # articles which aren't real articles but a list of articles will be skipped
                if article.ns == 0 and (
                    "Liste von" not in article.title and "Liste d" not in article.title
                ):
                    article_dict = get_article(
                        wikipedia,
                        article,
                        category_name,
                        unnecessary_sections,
                        min_article_length=min_article_length,
                        max_article_length=max_article_length,
                    )
                    if article_dict:
                        articles[article.title] = article_dict
                        article_counter += 1

        log_info = f"{idx+1} of {len(categories)} categories loaded."
        logging.info(f"\n\n{len(log_info)*'-'}\n{log_info}\n{len(log_info)*'-'}")
    return articles


def get_article(
    wikipedia: wikipediaapi.Wikipedia,
    article: wikipediaapi.WikipediaPage,
    category: str,
    unnecessary_sections: list,
    min_article_length: int = 0,
    max_article_length: int = 10000,
) -> dict:
    """Creates a dictionary with the title of the article as key and a dictionary with the keys
        "category", "text" and "length" as value.

    Example
    -------
    >>> get_article(wikipedia, 'Altersrente (id: ??, ns: 0)', 'Kategorie:Wirtschaft',
        ['Literatur', 'Weblinks', 'Einzelnachweis', 'Einzelnachweise', 'Siehe auch'])
    {"Altersrente":{category:"Kategorie:Wirtschaft", text:"...", len:1812}}

    Parameters
    ----------
    wikipedia : wikipediaapi.Wikipedia
        Wikipedia class from the `wikipediaapi` module
    article : wikipediaapi.WikipediaPage
        Page of the wikipedia article
    category : str
        Category of the article
    unnecessary_sections : list
        unnecessary_sections : list
        List of strings with skippable sections
    min_article_length : int, optional
        The minimum of characters for an article, by default 0
    max_article_length : int, optional
        The maximum of characters for an article, by default 10000

    Returns
    -------
    dict
        Article titles with a dictionary with the keys "category", "text" and "length" as value.
    """
    article_dict = {}

    # no anchored section articles in other articles
    if article.exists():
        reduced_article = article.summary + extracting_section(
            unnecessary_sections, article.sections
        )
        reduced_article = reduced_article[min_article_length:max_article_length]

        if reduced_article:
            article_dict["category"] = category
            article_dict["text"] = reduced_article
            article_dict["length"] = len(reduced_article)

    return article_dict


def parse_arguments():
    """Initialize argument parser and return arguments."""

    parser = argparse.ArgumentParser(
        prog="wikiscraper",
        description="Tool to create a corpus of Wikipedia articles based on Wikipedia categories.",
    )
    parser.add_argument(
        "path",
        type=str,
        help="Path to the JSON-File which contains the dictionary of the Wikipedia categories.",
    )
    parser.add_argument(
        "--lang", "-l", type=str, default="de", help="ISO2 lang string (default: 'de')."
    )
    parser.add_argument(
        "--max_articles",
        "-ma",
        type=int,
        default=1000,
        help="Sets the maximum of articles per category (default: 1000).",
    )
    parser.add_argument(
        "--max_article_length",
        "-max",
        type=int,
        default=10000,
        help="Maximum size of the article by characters (default: 10000).",
    )
    parser.add_argument(
        "--min_article_length",
        "-min",
        type=int,
        default=0,
        help="Minimum size of the article by characters (default: 0).",
    )
    parser.add_argument(
        "--output_format",
        "-of",
        type=str,
        choices=["csv", "json"],
        default="json",
        help="Format for the output (default: 'json').",
    )

    return parser.parse_args()


def main(args):

    start_time = time.time()

    wikipediaapi.log.setLevel(level=wikipediaapi.logging.WARNING)
    out_hdlr = wikipediaapi.logging.StreamHandler(sys.stderr)
    out_hdlr.setFormatter(wikipediaapi.logging.Formatter("%(asctime)s %(message)s"))
    out_hdlr.setLevel(wikipediaapi.logging.WARNING)
    wikipediaapi.log.addHandler(out_hdlr)

    # script logger
    logging.basicConfig(level=logging.INFO, filename="wikiscraper.log", filemode="w")
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    formatter = logging.Formatter("%(levelname)s: %(message)s")
    console.setFormatter(formatter)
    logging.getLogger("").addHandler(console)

    with Path(args.path).open("r", encoding="utf-8") as f:
        wikicategories = json.load(f)
        logging.info(f"Successfully loaded the categories from the JSON-File.")

    wikipedia = wikipediaapi.Wikipedia(
        args.lang, extract_format=wikipediaapi.ExtractFormat.WIKI
    )

    unnecessary_sections = [
        "Literatur",
        "Weblinks",
        "Einzelnachweis",
        "Einzelnachweise",
        "Siehe auch",
    ]

    categories = generate_categories(
        wikipedia,
        wikicategories,
        unnecessary_sections,
        max_articles=args.max_articles,
        min_article_length=args.min_article_length,
        max_article_length=args.max_article_length,
    )
    logging.info(
        "Successfully generated lists of the articles (time: "
        + f"{int((time.time() - start_time) / 60)} minutes)."
    )

    if args.output_format == "json":
        with open("articles.json", "w+") as f:
            json.dump(categories, f, ensure_ascii=False)
    elif args.output_format == "csv":
        import pandas as pd

        df = pd.DataFrame([v for k, v in categories.items()])
        df = df.rename(columns={"Unnamed: 0": "id"})
        df.to_csv("articles.csv", index=False)

    else:
        logging.info(
            f"Output format '{args.output_format}' is unknown. Can't save results."
        )

    logging.info(f"Successfully saved the articles.")
    logging.info(f"Total runtime: {(round(time.time() - start_time) / 60, 2)} minutes.")


if __name__ == "__main__":
    args = parse_arguments()
    main(args)
