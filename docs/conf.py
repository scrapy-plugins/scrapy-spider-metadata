project = "scrapy-spider-metadata"
copyright = "2023, Zyte Group Ltd"
author = "Zyte Group Ltd"
release = "0.0.0"

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.intersphinx",
    "sphinx.ext.viewcode",
]

exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

html_theme = "sphinx_rtd_theme"

intersphinx_mapping = {
    "python": (
        "https://docs.python.org/3",
        None,
    ),
}
