"""
数値計算に使用する関数。
"""
import numpy
from enum import Enum, auto

def calc_divisor(a: int, include_one: bool) -> 'tuple[int]':
    """
    指定の値の約数を求める。
    自明な約数も含む。
    厳密な意味での約数とは異なるが、include_one=Trueの場合には1を含める。

    Parameters
    ----------
    a : int
        正の整数。
    should_include_one : bool
        約数の一覧に1を含めるかどうか。
        True:
            1を含める。
        False:
            1を含めない。

    Returns
    -------
    'tuple[int]'
        約数の一覧。
        降順に並ぶ。

    """
    div_set = set()
    div = 1 if include_one else 2
    div_max = numpy.sqrt(a)
    while div <= div_max:
       quot,mod = divmod(a,div)
       if mod == 0:
           div_set = div_set | {div,quot}
       div += 1
    return tuple(sorted(list(div_set),reverse=True))

class CartesianProduct(object):
    def __init_(self, product_type, group):
        self._product_type = product_type
        self._group = group
        
    @property
    def product_type(self):
        return self._product_type
    
    @property
    def group(self):
        return self._group
    
    @staticmethod
    def create_direct(group):
        return CartesianProduct(ProductType.DIRECT, group)
    
    @staticmethod
    def create_left(group):
        return CartesianProduct(ProductType.LEFT, group)

    @staticmethod
    def create_right(group):
        return CartesianProduct(ProductType.RIGHT, group)

    @staticmethod
    def create_invalid():
        return CartesianProduct(ProductType.INVALID, None)

class ProductType(Enum):
    DIRECT = auto()
    LEFT = auto()
    RIGHT = auto()
    INVALID = auto()
       
    def is_direct_product(self) -> bool:
        return self is ProductType.DIRECT
    
    def is_semidirect_product(self) -> bool:
        return self in {ProductType.LEFT, ProductType.RIGHT}
    
    def is_left_semidirect_product(self) -> bool:
        return self is ProductType.LEFT
    
    def is_right_semidirect_product(self) -> bool:
        return self is ProductType.RIGHT
    
    def is_valid(self) -> bool:
        return self is not ProductType.INVALID
    
    def is_INVALID(self) -> bool:
        return self is ProductType.INVALID
    
class QuotientDecomposition(object):
    def __init__(self, is_valid, quotient):
        self._is_valid = is_valid
        self._quotient = quotient
    
    @property
    def is_valid(self):
        return self._is_valid
    
    @property
    def quotient(self):
        return self._quotient
    
    @staticmethod
    def create_valid(quotient):
        return QuotientDecomposition(True,quotient)

    @staticmethod
    def create_invalid():
        return QuotientDecomposition(False,None)