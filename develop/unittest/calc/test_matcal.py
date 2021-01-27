import sys
import numpy
sys.path.append('../../')
from application.calc import matcal
import unittest

class TestMatcal(unittest.TestCase):
    def test_are_equal_True(self):
        test_case = [
            (0, 0, 0.001),
            (0, 0.001, 0.001),
            (0, 0.0001, 0.001),
            (0, -0.0001, 0.001)
            ]
        for (a, b, zero_base) in test_case:
            with self.subTest(a=a, b=b, zero_base=zero_base):
                actual = matcal.are_equal(a, b, zero_base)
                self.assertTrue(actual)
 
    def test_are_equal_False(self):
        test_case = [
            (0, 0, -0.001),
            (0, 0.01, 0.001),
            (0, 0.0001, 0.00001),
            (0, -0.0001, 0.00001)
            ]
        for (a, b, zero_base) in test_case:
            with self.subTest(a=a, b=b, zero_base=zero_base):
                actual = matcal.are_equal(a, b, zero_base)
                self.assertFalse(actual)
                
    def test_has_unit_determinant_True(self):
        matlist = [numpy.array([[1,0,0],
                                [0,1,0],
                                [0,0,1]]),
                   numpy.array([[1,0,0],
                                [0,1,0],
                                [0,0,1j]]),
                   numpy.array([[0,1,0],
                                [1,0,0],
                                [0,0,1]]),
                   numpy.array([[0,-1,0],
                                [1,0,0],
                                [0,0,1]]) ,
                   numpy.array([[1,0,0],
                                [0,0,1],
                                [0,1,0]]) 
                   ]
        csmatlist = [matcal.ComplexSquareMatrix(i) for i in matlist]
        for csmat in csmatlist:
            with self.subTest(csmat=csmat):
                self.assertTrue(csmat.has_unit_determinant(0.001))
        
    def test_has_unit_determinant_False(self):
        matlist = [numpy.array([[1,0,0],
                                [0,1,0],
                                [0,0,2]]),
                   numpy.array([[1+1j,0,0],
                                [0,1,0],
                                [0,0,1j]])
                   ]
        csmatlist = [matcal.ComplexSquareMatrix(i) for i in matlist]
        for csmat in csmatlist:
            with self.subTest(csmat=csmat):
                self.assertFalse(csmat.has_unit_determinant(0.001))       
        
if __name__ == "__main__":
    unittest.main()