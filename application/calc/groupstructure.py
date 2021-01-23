"""
群の構造を表現するためのモジュール。
"""
from enum import Enum, auto

class CartesianProduct(object):
    def __init__(self, product_type, group):
        self._product_type = product_type
        self._group = group
        
    @property
    def product_type(self):
        return self._product_type
    
    @property
    def group(self):
        return self._group
       
    @property
    def is_direct_product(self) -> bool:
        return self._product_type is ProductType.DIRECT
    
    @property
    def is_semidirect_product(self) -> bool:
        return self._product_type in {ProductType.LEFT, ProductType.RIGHT}
    
    @property
    def is_left_semidirect_product(self) -> bool:
        return self._product_type is ProductType.LEFT
    
    @property
    def is_right_semidirect_product(self) -> bool:
        return self._product_type is ProductType.RIGHT
    
    @property
    def is_valid(self) -> bool:
        return self._product_type is not ProductType.INVALID
    
    @property
    def is_invalid(self) -> bool:
        return self._product_type is ProductType.INVALID
    
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

class DirectProduct(object):
    """
    二つの群の直積であることを表す。
    位数の大きな方の群を left、小さな方を right として、
    (left) \times (right) であることを表す。
    
    """
    def __init__(self, group1, group2):
        groups = sorted([group1,group2])
        self._left = groups[1]
        self._right = groups[0]
        
    def __lt__(self, other):
        return self.left.order < other.left.order
        
    @property
    def left(self):
        return self._left
    
    @property
    def right(self):
        return self._right
    
class SemidirectProduct(object):
    """
    二つの群の右半直積であることを表す。
    (left) \rtimes (right) であることを表す。
    
    """
    def __init__(self, left, right):
        self._left = left
        self._right = right

    def __lt__(self, other):
        return self.left.order < other.left.order

    @property
    def left(self):
        return self._left
    
    @property
    def right(self):
        return self._right