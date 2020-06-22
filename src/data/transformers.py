
import sys
import pathlib
import os
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from vectorizers import cast_tokens_to_strings
from .datasets import Dataset
from ..log import logger
from ..utils import custom_join

__all__ = [
    'available_transformers'
]

_MODULE = sys.modules[__name__]
_MODULE_DIR = pathlib.Path(os.path.dirname(os.path.abspath(__file__)))

def available_transformers(keys_only=True):
    """Valid transformation functions

    This function simply returns a dict of known
    tranformer algorithms strings and their corresponding
    function call

    It exists to allow for a description of the mapping for
    each of the valid strings as a docstring

    The valid algorithm names, and the function they map to, are:

    ============                ====================================
    string                      Transformer Function
    ============                ====================================
    train_test_split            train_test_split_xform
    pivot                       pivot
    index_to_date_time          index_to_date_time
    add_srm_to_reviews          add_srm_to_reviews
    groupby_style_to_reviewers  groupby_style_to_reviewers
    sklearn_transform           sklearn_transform
    groupby_beer_to_reviewers   groupby_beer_to_reviewers
    groupby_breweries           groupby_breweries
    groupby_breweries_by_style  groupby_breweries_by_style
    ============                ====================================

    Parameters
    ----------
    keys_only: boolean
        If True, return only keys. Otherwise, return a dictionary mapping keys to algorithms
    """
    _TRANSFORMERS = {
        "add_srm_to_reviews": add_srm_to_reviews,
        "groupby_beer_to_reviewers": groupby_beer_to_reviewers,
        "groupby_breweries": groupby_breweries,
        "groupby_breweries_by_style": groupby_breweries_by_style,
        "groupby_style_to_reviewers": groupby_style_to_reviewers,
        "index_to_date_time": index_to_date_time,
        "pivot": pivot,
        "sklearn_transform": sklearn_transform,
        "train_test_split": split_dataset_test_train,
    }

    if keys_only:
        return list(_TRANSFORMERS.keys())
    return _TRANSFORMERS


def sklearn_transformers(keys_only=True):
    """Valid sklearn-style transformers

    This function simply returns a dict of known
    tranformer algorithms strings and their corresponding
    function call

    It exists to allow for a description of the mapping for
    each of the valid strings as a docstring

    The valid algorithm names, and the function they map to, are:

    ============                ====================================
    string                      Transformer Function
    ============                ====================================
    CountVectorizer             sklearn.feature_extraction.text.CountVectorizer
    TfidfVectorizer             sklearn.feature_extraction.text.TfidfVectorizer
    ============                ====================================

    Parameters
    ----------
    keys_only: boolean
        If True, return only keys. Otherwise, return a dictionary mapping keys to algorithms
    """
    _SK_TRANSFORMERS = {
        "CountVectorizer": CountVectorizer,
        "TfidfVectorizer": TfidfVectorizer,
    }

    if keys_only:
        return list(_SK_TRANSFORMERS.keys())
    return _SK_TRANSFORMERS


def split_dataset_test_train(dset,
                             dump_path=None, dump_metadata=True,
                             force=True, create_dirs=True,
                             **split_opts):
    """Transformer that performs a train/test split.

    This transformer passes `dset` intact, but creates and dumps two new
    datasets as a side effect: {dset.name}_test and {dset.name}_train

    Parameters
    ----------
    dump_metadata: boolean
        If True, also dump a standalone copy of the metadata.
        Useful for checking metadata without reading
        in the (potentially large) dataset itself
    dump_path: path. (default: `processed_data_path`)
        Directory where data will be dumped.
    force: boolean
        If False, raise an exception if any dunp files already exists
        If True, overwrite any existing files
    create_dirs: boolean
        If True, `dump_path` will be created (if necessary)
    **split_opts:
        Remaining options will be passed to `train_test_split`

    """
    new_ds = {}
    for kind in ['train', 'test']:
        dset_name = f"{dset.name}_{kind}"
        dset_meta = {**dset.metadata, 'split':kind, 'split_opts':split_opts}
        new_ds[kind] = Dataset(dataset_name=dset_name, metadata=dset_meta)
    X_train, X_test, y_train, y_test = train_test_split(dset.data, dset.target, **split_opts)

    new_ds['train'].data = X_train
    new_ds['train'].target = y_train
    logger.info(f"Writing Transformed Dataset: {new_ds['train'].name}")
    new_ds['train'].dump(force=force, dump_path=dump_path, dump_metadata=dump_metadata, create_dirs=create_dirs)

    new_ds['test'].data = X_test
    new_ds['test'].target = y_test
    logger.info(f"Writing Transformed Dataset: {new_ds['test'].name}")
    new_ds['test'].dump(force=force, dump_path=dump_path, dump_metadata=dump_metadata, create_dirs=create_dirs)
    return dset

def pivot(dset, **pivot_opts):
    """Pivot data stored as a Pandas Dataframe

    pivot_opts:
        keyword arguments passed to pandas.Dataframe.pivot_table
    """
    pivoted = dset.data.pivot_table(**pivot_opts)
    ds_pivot = Dataset(dataset_name=f"{dset.name}_pivoted", metadata=dset.metadata, data=pivoted, target=None)
    ds_pivot.metadata['pivot_opts'] = pivot_opts

    return ds_pivot

def index_to_date_time(dset, suffix='dt'):
    """Transformer: Extract a datetime index into Date and Time columns"""
    df = dset.data.copy()
    df['Time']=df.index.time
    df['Date']=df.index.date
    df.reset_index(inplace=True, drop=True)
    new_ds = Dataset(dataset_name=f"{dset.name}_{suffix}", metadata=dset.metadata, data=df)
    return new_ds

def sklearn_transform(dset, transformer_name, transformer_opts=None, subselect_column=None, **opts):
    """
    Wrapper for any 1:1 (data in to data out) sklearn style transformer. Will run the .fit_transform
    method of the transformer on dset.data. If subselect_column is not None, it will treat the data
    like a dataframe and will subselect dset.data[subselect_column] to run the transformer on.

    Parameters
    ----------
    dset:
        Dataset
    transformer_name: string
        sklearn style transformer with a .fit_transform method avaible via sklearn_transformers.
    transformer_opts: dict
        options to pass on to the transformer
    subselect_column: string
        column name for dset.data to run the transformer on
    return_whole: boolean
        return the whole dataframe with a new column named "transformed"
    **opts:
        options to pass on to the fit_transform method

    Returns
    -------
    Dataset whose data is the result of the transformer.fit_transform
    """
    if transformer_name in sklearn_transformers():
        transformer = sklearn_transformers(keys_only=False).get(transformer_name)(**transformer_opts)
    else:
        raise ValueError(f"Invalid transformer name: {transformer_name}. See sklearn_transformers for available names.")
    if subselect_column:
        new_data = transformer.fit_transform(dset.data[subselect_column], **opts)
    else:
        new_data = transformer.fit_transform(dset.data, **opts)

    ds = Dataset(dataset_name=f"{dset.name}_{transformer.__class__.__name__}", metadata=dset.metadata, data=new_data)
    return ds


def add_srm_to_reviews(review_dset, *, srm_dset_name):
    """
    Augments beer reviews with SRM (color assessment) data.

    See notebook 04 for what this does and why.

    Parameters
    ----------
    review_dset:
        beer review dataset as a pandas dataframe
    srm_dset_name: string
        name of corresponding srm Dataset

    Returns
    -------
    style-by-review DataFrame
    """

    reviews = review_dset.data
    srm_ds = Dataset.load(srm_dset_name)
    srm_data = srm_ds.data

    # Groupby to select the fields that we want to use
    beer_style = reviews.groupby('beer_style').agg({
        'beer_name':lambda x: x.mode(),
        'brewery_name':lambda x: x.mode(),
        'beer_abv':'mean',
        'review_aroma':'mean',
        'review_appearance':'mean',
        'review_palate':'mean',
        'review_taste':'mean',
        'review_overall':'mean',
        'review_profilename':len
    }).reset_index()

    beer_style.columns = """beer_style common_beer common_brewer abv
    aroma appearance overall palate taste
    num_reviews""".split()

    # Augment beer style with SRM and RGB data
    beer_style = beer_style.merge(srm_data[['kaggle_review_style','Style Category',
                                            'SRM Mid','srm_rgb']], how='left',
                    left_on='beer_style', right_on='kaggle_review_style')
    beer_style.rename(columns={'SRM Mid':'srm_mid', 'Style Category':'style_category'},
                      inplace=True)

    # merge the metadata
    merged_meta = {'descr': "Beer reviews augmented with SRM (colour) data. "
                   f"See {review_dset.DATASET_NAME} and {srm_ds.DATASET_NAME} "
                   "Datasets for complete details.",
                   'license': f"See license information from {review_dset.DATASET_NAME} and "
                   f"{srm_ds.DATASET_NAME} Datasets."
    }
    ds = Dataset(dataset_name="beer_style", metadata=merged_meta, data=beer_style)
    return ds


def groupby_style_to_reviewers(review_dset):
    """
    Turn our reviews data frame into a frame with one row per beer style instead of one row per review.

    We groupby the column we'd like to embedd and then use agg with a dictionary of column names to
    aggregation functions to tell it how to summarize the many reviews about a single beer into one record.
    (Median and max are great functions for dealing with numeric fields).

    Parameters
    ----------
    review_dset: Dataset
        Dataset containing the beer reviews data

    Returns
    -------
    beer style dataset with a dataframe representing beer style by reviewers
    """
    reviews = review_dset.data
    beer_style = reviews.groupby('beer_style').agg({
        'beer_name':lambda x: x.mode(),
        'brewery_name':lambda x: x.mode(),
        'beer_abv':'mean',
        'review_aroma':'mean',
        'review_appearance':'mean',
        'review_overall':'mean',
        'review_palate':'mean',
        'review_taste':'mean',
        'review_profilename': [lambda x: list(x.unique()), lambda x: len(x.unique())],
        'brewery_id':lambda x: len(x.unique()),
    }).reset_index()

    beer_style.columns = """beer_style beer_name brewery_name beer_abv
    review_aroma review_appearance review_overall review_palate review_taste
    review_profilename_list num_reviewers num_ids""".split()
    beer_style.review_profilename_list = cast_tokens_to_strings(beer_style.review_profilename_list)
    ds = Dataset(dataset_name="beer_style_reviewers", metadata=review_dset.metadata, data=beer_style)
    return ds


def groupby_beer_to_reviewers(review_dset, positive_threshold=None):
    """
    Turn our reviews data frame into a frame with one row per beer instead of one row per review.

    We will also restrict to positive reviews only if a positive threshold value is set.

    Parameters
    ----------
    review_dset: Dataset
        Dataset containing the beer reviews data

    positive_threshold: Default: None
        Number between 0 and 5 representing the threshold for a postive review (aka. a positive
        review is defined as a review with a value greater than positive_threshold).

    Returns
    -------
    beer dataset with a dataframe representing beer by positive reviewers
    """
    reviews = review_dset.data
    if positive_threshold is not None:
        pos_reviews = reviews[reviews.review_overall>=positive_threshold]
    else:
        pos_reviews = reviews

    beer = pos_reviews.groupby('beer_beerid').agg({
        'beer_name':'first',
        'brewery_name':'first',
        'beer_style':'first',
        'beer_abv':'mean',
        'review_aroma':'mean',
        'review_appearance':'mean',
        'review_overall':'mean',
        'review_palate':'mean',
        'review_taste':'mean',
        'review_profilename': [lambda x: list(x.unique()), lambda x: len(x.unique())],
    }).reset_index()

    beer.columns = """beer_beerid beer_name brewery_name beer_style beer_abv
    review_aroma review_appearance review_overall review_palate review_taste
    review_profilename_list review_profilename_len""".split()
    beer.review_profilename_list = cast_tokens_to_strings(beer.review_profilename_list)

    ds = Dataset(dataset_name="beer_reviewers", metadata=review_dset.metadata, data=beer)
    return ds

def groupby_breweries(review_dset):
    """
    Transform to one row per brewery instead of one row per reviews.

    It turns out there are a number of breweries with multiple brewery_ids for the same brewery_name.
    Upon examining thse breweries they are inevitably chains of brew pubs with multiple locations.  We
    feel that they should be treated as the same brewery.  Thus we chose to group by brewery_name
    instead of brewery_id.

    Parameters
    ----------
    review_dset: Dataset
        Dataset containing the beer reviews data

    Returns
    -------
    brewery dataset with a dataframe representing breweries by reviewers
    """
    reviews = review_dset.data
    breweries = reviews.groupby('brewery_name').agg({
        'beer_name':lambda x: x.mode(),
        'beer_style':lambda x: x.mode(),
        'beer_abv':'mean',
        'review_aroma':'mean',
        'review_appearance':'mean',
        'review_overall':'mean',
        'review_palate':'mean',
        'review_taste':'mean',
        'review_profilename': [lambda x: list(x.unique()), lambda x: len(x.unique())],
        'brewery_id':lambda x: len(x.unique()),
    }).reset_index()

    breweries.columns = """brewery_name beer_name beer_style beer_abv
    review_aroma review_appearance review_overall review_palate review_taste
    review_profilename_list num_reviewers num_ids""".split()
    breweries.review_profilename_list = cast_tokens_to_strings(breweries.review_profilename_list)
    ds = Dataset(dataset_name="breweries_reviewers", metadata=review_dset.metadata, data=breweries)
    return ds


def groupby_breweries_by_style(review_dset):
    """
    Transform to one row per brewery instead of one row per reviews.

    It turns out there are a number of breweries with multiple brewery_ids for the same brewery_name.
    Upon examining thse breweries they are inevitably chains of brew pubs with multiple locations.  We
    feel that they should be treated as the same brewery.  Thus we chose to group by brewery_name
    instead of brewery_id.

    We will build a list for each brewery with one instance of the beer style for each review. This will
    allow us differentiate breweries who claim to make every style of beer but who from the perspective
    of most reviewers only make two styles.
    Parameters
    ----------
    review_dset: Dataset
        Dataset containing the beer reviews data

    Returns
    -------
    brewery dataset with a dataframe representing breweries by most common beer style
    """
    reviews = review_dset.data
    breweries = reviews.groupby('brewery_name').agg({
        'beer_name':lambda x: x.mode().iloc[0],
        'beer_style':[lambda x:custom_join(x,","),len, lambda x:x.mode().iloc[0]],
        'beer_abv':'mean',
        'review_aroma':'mean',
        'review_appearance':'mean',
        'review_overall':'mean',
        'review_palate':'mean',
        'review_taste':'mean',
        'review_profilename':len,
        'brewery_id':lambda x: len(x.unique()),
    }).reset_index()

    breweries.columns = """brewery_name beer_name beer_style num_beer_style favorite_style beer_abv
    review_aroma review_appearance review_overall review_palate review_taste
    num_reviewers num_ids""".split()

    ds = Dataset(dataset_name="breweries_by_style", metadata=review_dset.metadata, data=breweries)
    return ds
