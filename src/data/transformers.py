import sys
import pathlib
import os
from sklearn.model_selection import train_test_split
from .datasets import Dataset
from ..logging import logger

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
    ============                ====================================

    Parameters
    ----------
    keys_only: boolean
        If True, return only keys. Otherwise, return a dictionary mapping keys to algorithms
    """
    _TRANSFORMERS = {
        "add_srm_to_reviews": add_srm_to_reviews,
        "index_to_date_time": index_to_date_time,
        "pivot": pivot,
        "train_test_split": split_dataset_test_train,
    }

    if keys_only:
        return list(_TRANSFORMERS.keys())
    return _TRANSFORMERS

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
    ds_pivot = Dataset(name=f"{dset.name}_pivoted", metadata=dset.metadata, data=pivoted, target=None)
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

    # subselect the columns we want to work with
    numeric_columns = 'aroma appearance palate taste'.split()
    style_by_reviews = beer_style[numeric_columns]
    merged_meta = {'descr': "Beer reviews augmented with SRM (colour) data. "
                   f"See {review_dset.DATASET_NAME} and {srm_ds.DATASET_NAME} "
                   "Datasets for complete details.",
                   'license': f"See license information from {review_dset.DATASET_NAME} and "
                   f"{srm_ds.DATASET_NAME} Datasets."
    }
    ds = Dataset(dataset_name="beer_style_by_reviews", metadata=merged_meta, data=style_by_reviews)
    return ds
