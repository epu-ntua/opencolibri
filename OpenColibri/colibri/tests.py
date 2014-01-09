from django.utils import unittest
from library import *
from organizations.models import *


class TestLibrary(unittest.TestCase):
    def test_array_unique_do_not_contain_duplicates(self):
        self.assertEquals([1, 2, 3, 4], array_unique([1, 2, 3, 1, 2, 3, 4, 1, 2, 3]))

    def test_array_diff_return_diff_of_lists(self):
        self.assertEquals([1, 2, 3], array_diff([1, 2, 3], []))
        self.assertEquals([1, 3], array_diff([1, 2, 3], [2]))
        self.assertEquals([1], array_diff([1], [2, 3]))

    def test_array_explode_return_list_defined_by_separator(self):
        self.assertEquals(['1'], array_explode('-', '1'))
        self.assertEquals(['1', ''], array_explode('-', '1-'))
        self.assertEquals(['1', '2', '3', '4'], array_explode('-', '1-2-3-4'))

    def test_get_slug(self):
        self.assertEquals('john-econ', get_slug('John Econ'))


if __name__ == '__main__':
    unittest.main()
