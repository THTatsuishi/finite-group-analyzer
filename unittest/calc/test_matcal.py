import sys
import numpy
sys.path.append('../../')
from application.calc import matcal
import unittest

class TestMatcal(unittest.TestCase):
    def test_are_equal(self):
        zero_base = 0.001
        value1 = 0
        value2 = 0.0001
        actual = matcal.are_equal(value1, value2,zero_base)
        self.assertTrue(actual)

        
        
if __name__ == "__main__":
    unittest.main()