[![Build Status](https://travis-ci.org/acwooding/ReproAllTheThings.svg?branch=master)](https://travis-ci.org/acwooding/ReproAllTheThings)

[![Coverage Status](https://coveralls.io/repos/github/acwooding/ReproAllTheThings/badge.svg)](https://coveralls.io/github/acwooding/ReproAllTheThings)

ReproAllTheThings
==============================
_Author: John Healy, Amy Wooding_

Reproducing jc-healy's EmbedAllTheThings notebooks usint the Easydata framework.

GETTING STARTED
---------------

* Create and switch to the  virtual environment:
```
cd reproallthethings
make create_environment
conda activate reproallthethings
```
* Explore the notebooks in the `notebooks` directory

Project Organization
------------
* `LICENSE`
* `Makefile`
    * top-level makefile. Type `make` for a list of valid commands
* `Makefile.include`
    * Global includes for makefile routines. Included by `Makefile`
* `Makefile.env`
    * Command for maintaining reproducible conda environment. Included by `Makefile`
* `README.md`
    * this file
* `catalog`
  * Data catalog. This is where config information such as data sources
    and data transformations are saved
* `data`
    * Data directory. often symlinked to a filesystem with lots of space
    * `data/raw`
        * Raw (immutable) hash-verified downloads
    * `data/interim`
        * Extracted and interim data representations
    * `data/processed`
        * The final, canonical data sets for modeling.
* `docs`
    * A default Sphinx project; see sphinx-doc.org for details
* `models`
    * Trained and serialized models, model predictions, or model summaries
    * `models/trained`
        * Trained models
    * `models/output`
        * predictions and transformations from the trained models
* `notebooks`
    *  Jupyter notebooks. Naming convention is a number (for ordering),
    the creator's initials, and a short `-` delimited description,
    e.g. `1.0-jqp-initial-data-exploration`.
* `references`
    * Data dictionaries, manuals, papers, or other explanatory materials.
* `reports`
    * Generated analysis as HTML, PDF, LaTeX, etc.
    * `reports/figures`
        * Generated graphics and figures to be used in reporting
* `environment.yml`
    * The YAML file for reproducing the conda/pip environment
* `setup.py`
    * Turns contents of `src` into a
    pip-installable python module  (`pip install -e .`) so it can be
    imported in python code
* `src`
    * Source code for use in this project.
    * `src/__init__.py`
        * Makes src a Python module
    * `src/data`
        * Scripts to fetch or generate data. In particular:
        * `src/data/make_dataset.py`
            * Run with `python -m src.data.make_dataset fetch`
            or  `python -m src.data.make_dataset process`
    * `src/analysis`
        * Scripts to turn datasets into output products
* `tox.ini`
    * tox file with settings for running tox, including flake8 configuration; see tox.testrun.org
--------

<p><small>This project was built using <a target="_blank" href="https://github.com/hackalog/cookiecutter-easydata">cookiecutter-easydata</a>, an opinionated fork of [cookiecutter-data-science](https://github.com/drivendata/cookiecutter-data-science) aimed at making your data science workflow reproducible.</small></p>
