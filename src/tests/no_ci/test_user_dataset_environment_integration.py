## Test dataset information
import unittest

from src.data import Dataset


class TestDatasets(unittest.TestCase):
    """
    Basic smoke tests to ensure that all of the available datasets
    load and have some expected property.
    """
    def test_wine_reviews_130k(self):
        ds = Dataset.load('wine_reviews_130k')
        assert ds.data.shape == (129971, 13)

    def test_wine_reviews_150k(self):
        ds = Dataset.load('wine_reviews_150k')
        assert ds.data.shape == (150930, 10)

    def test_wine_reviews_130k_varietals_75(self):
        ds = Dataset.load('wine_reviews_130k_varietals_75')
        assert ds.data.shape == (123495, 13)
