"""
Custom dataset processing/generation functions should be added to this file
"""

import pandas as pd
import pathlib

__all__ = [
    'process_beer_review',
    'process_srm_data'
]

def process_beer_review(*, unpack_dir, kind='all', extract_dir='beer_review',
                        unpack=False, raw_dir=None, metadata=None):
    """
    Process beer reviews into (data, target, metadata) format. Since we plan to use Pandas
    for further processing, data will be a pandas dataframe. As Pandas will read that too.

    In this case, if we

    Parameters
    ----------
    unpack_dir:
        The directory the reviews have been unpacked into
    raw_dir:
        The directory the raw zip file
    kind: {'all'}
        This is an unsupervised learning example. There are no labels. We will only work
        with the whole dataset. (Optionally add train and test set later for experimenting.)
    extract_dir:
        Name of the directory of the unpacked zip file containing the raw data files.
    unpack: boolean
        If unpack is False, process data without bothering to unpack it. Requires raw_dir.

    Returns
    -------
    A tuple:
        (data, target, additional_metadata)

    """
    if metadata is None:
        metadata = {}

    if unpack:
        if unpack_dir:
            unpack_dir = pathlib.Path(unpack_dir)
            data_dir = unpack_dir / extract_dir
            data = pd.read_csv(data_dir/"beer_reviews.csv")
    else:
        if raw_dir:
            raw_dir = pathlib.Path(raw_dir)
            data = pd.read_csv(raw_dir/"beerreviews.zip")
        else:
            raise ValueError("raw_dir required")

    target = None

    return data, target, metadata

def process_srm_data(*, source_dir, kind='all', metadata=None):
    """
    Process beer reviews into (data, target, metadata) format. Since we plan to use Pandas
    for further processing, data will be a pandas dataframe. As Pandas will read that too.

    In this case, if we

    Parameters
    ----------
    source_dir:
        The directory the reviews have been put in (likely the raw data dir)
    raw_dir:
    kind: {'all'}
        This is an unsupervised learning example. There are no labels. We will only work
        with the whole dataset. (Optionally add train and test set later for experimenting.)


    Returns
    -------
    A tuple:
        (data, target, additional_metadata)

    """
    if metadata is None:
        metadata = {}

    if source_dir:
        source_dir = pathlib.Path(source_dir)

    srm_raw = pd.read_csv(source_dir / 'beer_styles.csv')
    schema_match = pd.read_csv(source_dir / 'beer_review_kaggle2srm_schema.csv')
    srm = schema_match.merge(srm_raw, how='left', right_on='Style Name', left_on='srm_style')

    srm2rgb = pd.read_csv(source_dir / 'srm2rgb.csv', header=None, sep=' ')
    srm2rgb.columns = ['srm_rgb','srm']
    data = srm.merge(srm2rgb, how='left', left_on=srm['SRM Mid'].apply(int), right_on='srm').drop(['srm'], axis =1)

    target = None

    return data, target, metadata

def process_wine_reviews(*, unpack_dir, kind='130k', extract_dir='wine_reviews',
                         metadata=None):
    """
    Process wine reviews into (data, target, metadata) format. Since we plan to use Pandas
    for further processing, data will be a pandas dataframe.

    Parameters
    ----------
    unpack_dir:
        The directory the reviews have been unpacked into
    kind: {'130k' , '150k'}
        This is an unsupervised learning example. There are no labels. We will only work
        with the whole dataset. There are two versions, the 130k version of 150k version.
    extract_dir:
        Name of the directory of the unpacked zip file containing the raw data files.


    Returns
    -------
    A tuple:
        (data, target, additional_metadata)

    """
    if metadata is None:
        metadata = {}

    unpack_dir = pathlib.Path(unpack_dir)
    data_dir = unpack_dir / extract_dir
    if kind == '130k':
        data = pd.read_csv(data_dir/"winemag-data-130k-v2.csv", index_col=0)
    elif kind == '150k':
        data = pd.read_csv(data_dir/"winemag-data_first150k.csv", index_col=0)
    else:
        raise ValueError(f'kind: {kind} must be one of "130k" or "150k"')

    target = None

    return data, target, metadata
