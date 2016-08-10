IM Logs processing
=============

For the past three years, I have backed up all my IM logs. At the time, I didn't
really know why. I thought that maybe one day I would want to read something
again. Well, my logs have 150Mb now and I probably won't be reading through it
any time soon.

But this year I did two courses on Coursera, Machine Learning and Natural
Language Processing, that started to make me think. Maybe I could build some
tools to help me analyze my logs and process some meaningfull information out of
them. What information is that? I don't know yet. But it's a work in progress.

Roadmap
-------
1. Process the logs of various IM programs
   * Process Digsby logs
   * Process Trillian logs
   * Process Pidgin logs
   * Process Whatsapp emailed chats
   * Process Facebook takeout data
   * Process Hangouts takeout data
2. Store the logs as efficiently as possible
3. Make pretty graphs out of evolution of most popular contacts
4. Most common words
5. Figure out clusters in my contacts
6. To infinity and beyond

Instructions 
------------
Facebook messages from the takeout data should be prettified. The HTML output is
more consistent then and easier to parse. 

Project Organization
------------

    ├── LICENSE
    ├── Makefile           <- Makefile with commands like `make data` or `make train`
    ├── README.md          <- The top-level README for developers using this project.
    ├── data
    │   ├── external       <- Data from third party sources.
    │   ├── interim        <- Intermediate data that has been transformed.
    │   ├── processed      <- The final, canonical data sets for modeling.
    │   └── raw            <- The original, immutable data dump.
    │
    ├── docs               <- A default Sphinx project; see sphinx-doc.org for details
    │
    ├── models             <- Trained and serialized models, model predictions, or model summaries
    │
    ├── notebooks          <- Jupyter notebooks. Naming convention is a number (for ordering),
    │                         the creator's initials, and a short `-` delimited description, e.g.
    │                         `1.0-jqp-initial-data-exploration`.
    │
    ├── references         <- Data dictionaries, manuals, and all other explanatory materials.
    │
    ├── reports            <- Generated analysis as HTML, PDF, LaTeX, etc.
    │   └── figures        <- Generated graphics and figures to be used in reporting
    │
    ├── requirements.txt   <- The requirements file for reproducing the analysis environment, e.g.
    │                         generated with `pip freeze > requirements.txt`
    │
    ├── src                <- Source code for use in this project.
    │   ├── __init__.py    <- Makes src a Python module
    │   │
    │   ├── data           <- Scripts to download or generate data
    │   │   └── make_dataset.py
    │   │
    │   ├── features       <- Scripts to turn raw data into features for modeling
    │   │   └── build_features.py
    │   │
    │   ├── models         <- Scripts to train models and then use trained models to make
    │   │   │                 predictions
    │   │   ├── predict_model.py
    │   │   └── train_model.py
    │   │
    │   └── visualization  <- Scripts to create exploratory and results oriented visualizations
    │       └── visualize.py
    │
    └── tox.ini            <- tox file with settings for running tox; see tox.testrun.org
