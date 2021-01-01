"""
解析対象となる最大の群を扱うためのモジュール。
"""
import itertools
import numpy
from . import calctools
from .matcal import CayleyTable

class MasterGroup(object):
    """
    解析対象となる最大の群を表す。
    
    Attributes
    ----------    

    Parameters
    ----------
    cayley_table : 'CayleyTable'
        群の乗積表。
   
    """
    def __init__(self, cayley_table: 'CayleyTable'):
        # 全ての要素の行列表現のリスト。並び順の通りに採番する
        self._matrix_rep_of_elements = cayley_table.matlist
        # 乗積表
        self._cayley_table = cayley_table.table
        # 群の位数
        self._order = len(self._matrix_rep_of_elements)
        # 位数が1なら例外
        if self._order == 1:
            raise Exception("自明群です。")
        # 全ての要素
        self._all_elements = frozenset(range(self.order))
        # 単位元のインデックス
        self._identity_index = self._find_identity_index()
        # 逆元の対応表
        self._inverse_data = self._calc_inverse_data()
        # 共役変換表
        self._conjugate_data = self._calc_conjugate_data()
        # 元の位数の対応表
        self._index_order_data = self._calc_index_order_data()
        # 約数リスト
        self._divisor_dict = self._calc_divisor_dict()
    
    @property
    def order(self) -> int:
        """

        Returns
        -------
        int
            群の位数。

        """
        return self._order

    @property
    def all_elements(self) -> 'frozenset[int]':
        """

        Returns
        -------
        'frozenset[int]'
            全ての元のインデックスの一覧。

        """
        return self._all_elements
    
    @property
    def cayley_table(self) -> numpy.ndarray:
        """

        Returns
        -------
        numpy.ndarray
            群の乗積表。

        """
        return self._cayley_table
    
    @property
    def matrix_rep_of_elements(self) -> 'tuple[numpy.ndarray]':
        """

        Returns
        -------
        'tuple[numpy.ndarray]'
            全ての元の行列表現の一覧。

        """
        return self._matrix_rep_of_elements
    
    def index_prod(self, index1: int, index2: int) -> int:
        """
        二つの元の積を返す。
        一つ目の元に右から二つ目の元を掛ける。
        この群の元のインデックスを指定する。

        Parameters
        ----------
        index1 : int
            一つ目の元のインデックス。
        index2 : int
            二つ目の元のインデックス。

        Returns
        -------
        int
            演算結果の元のインデックス。

        """
        return self._cayley_table[index1][index2]
    
    def index_inverse(self, index: int) -> int:
        """
        元の逆元を返す。
        この群の元のインデックスを指定する。

        Parameters
        ----------
        index : int
            元のインデックス。

        Returns
        -------
        int
            逆元のインデックス。

        """
        return self._inverse_data[index]
    
    def index_conjugate(self, index1: int, index2: int) -> int:
        """
        一つ目の元を、二つ目の元で共役変換する。
        gをhで共役変換: h * g * h^(-1)
        この群の元のインデックスを指定する。

        Parameters
        ----------
        index1 : int
            一つ目の元のインデックス。
            gに対応する。
        index2 : int
            二つ目の元のインデックス。
            hに対応する。

        Returns
        -------
        int
            演算結果の元のインデックス。

        """
        return self._conjugate_data[index1][index2]
    
    def index_comutator(self, index1: int, index2: int) -> int:
        """
        二つの元の交換子を返す。
        gとhの交換子： [g,h] = g * h * g^(-1) * h^(-1)

        Parameters
        ----------
        index1 : int
            一つ目の元のインデックス。
            gに対応する。
        index2 : int
            二つ目の元のインデックス。
            hに対応する。

        Returns
        -------
        int
            演算結果の元のインデックス。

        """
        return self._comutator_data[index1][index2]
   
    def index_order(self, index: int) -> int:
        """
        指定の元の位数を返す。
        元を位数乗すると単位元となる。

        Parameters
        ----------
        index : int
            指定の元のインデックス。

        Returns
        -------
        int
            元の位数。

        """
        return self._index_order_data[index]
    
    def divisor_of(self, a: int) -> 'tuple[int]':
        """
        指定の値の約数の一覧を降順で返す。
        自明な役宇数（指定の値）と1を含む。
        1を含むという点で厳密な約数とは異なることに注意せよ。
        指定の値は、この群の位数の約数と1に限られる。
        
        例：位数が12の場合は (12, 8, 6, 4, 3, 2, 1) のいずれかを指定できる。
        
        例：指定の値が8の場合は (8, 6, 4, 3, 2, 1) を返す。
        
        Parameters
        ----------
        a : int
            指定の値。
            この群の位数の約数または1。

        Returns
        -------
        'tuple[int]'
            約数の一覧。
            指定の値と1を含む。

        """
        return self._divisor_dict[a]  

    def divisor_of_order(self) -> 'tuple[int]':
        """
        この群の位数の約数の一覧を降順で返す。
        自明な約数（位数の値）と1を含む。
        1を含むという点で厳密な約数とは異なることに注意せよ。
        
        例：位数が12の場合は (12, 8, 6, 4, 3, 2, 1) を返す。

        Returns
        -------
        'tuple[int]'
            約数の一覧。
            位数の値と1を含む。

        """
        return self._divisor_dict[self.order]
    
    def calc_closure(self, indexset: 'set[int]') -> 'frozenset[int]':
        """
        指定の元を生成元として、閉じた集合を生成する。

        Parameters
        ----------
        indexset : 'set[int]'
            生成元とする元のインデックスの集合。

        Returns
        -------
        'frozenset[int]'
            生成された集合のインデックスの一覧。

        """
        # 部分群の位数は元の群の位数の約数である
        divisor = self.divisor_of_order()
        n_max = divisor[1]
        element_all = set(indexset)
        element_prev = set(indexset)
        n_all = len(element_all)
        while len(element_prev) != 0:
        # 新しいインデックスを生成
            generated = set(self.index_prod(index1,index2) for (index1,index2) 
                      in itertools.product(element_prev,indexset))
            element_new = generated.difference(element_all)
            element_all = element_all.union(element_new)
            n_all += len(element_new)
            element_prev = set(element_new)
            if n_all > n_max: return self.all_elements         
        return frozenset(element_all)
    
    def is_closure(self, indexset: 'set[int]') -> bool:
        """
        元の集合が閉じているかを判定する。

        Parameters
        ----------
        indexset : 'set[int]'
            元のインデックスの集合。

        Returns
        -------
        bool
            True:
                閉じている。
            False:
                閉じていない。

        """
        return len(indexset) == len(self.calc_closure(indexset))
       
    def _find_identity_index(self) -> int:
        """
        単位元のインデックスを特定する。

        Returns
        -------
        int
            単位元のインデックス。

        """
        for i in range(self.order):
            if self._cayley_table[i][i] == i: return i
    
    def _calc_inverse_data(self) -> 'tuple[int]':
        """
        逆元との対応表を作成する。

        Returns
        -------
        'tuple[int]'
            逆元との対応表。

        """
        inverse_list = [None for i in range(self.order)]
        for index1 in range(self.order):
            for index2 in range(self.order):
                if self.index_prod(index1,index2) == self._identity_index:
                    inverse_list[index1] = index2
                    continue
        return tuple(inverse_list)
    
    def _calc_conjugate_data(self) -> 'tuple[tuple[int]]':
        """
        共役変換表を作成する。
        gのhによる共役変換は、 h * g * h^(-1) とする。

        Returns
        -------
        'tuple[tuple[int]]'
            共役変換表。

        """
        conjugate_table = numpy.identity(self.order,dtype=int)
        for (g, h) in itertools.product(self.all_elements,self.all_elements):
            h_inv = self.index_inverse(h)
            result = self.index_prod(h,g)
            result = self.index_prod(result,h_inv)
            conjugate_table[g][h] = result
        return conjugate_table        
    
    def _calc_comutator_data(self) -> numpy.ndarray:
        """
        元の交換子を計算する。
        gとhの交換子： [g,h] = g * h * g^(-1) * h^(-1)

        Returns
        -------
        numpy.ndarray
            交換子表。

        """
        comutator_table = numpy.identity(self.order,dtype=int)
        for (g, h) in itertools(self.all_elements,self.all_elements):
            g_inv = self.index_inverse(g)
            h_inv = self.index_inverse(h)
            result = self.index_prod(g,h)
            result = self.index_prod(result,g_inv)
            result = self.index_prod(result,h_inv)
            comutator_table[g][h] = result
        return comutator_table 
    
    def _calc_index_order(self, index) -> int:
        """
        指定の元の位数を計算する。
        元を位数乗すると単位元となる。

        Parameters
        ----------
        index : TYPE
            指定の元のインデックス。

        Returns
        -------
        int
            元の位数。

        """
        current_index = index
        current_order = 1
        while current_index != self._identity_index:
            current_index = self.index_prod(current_index,index)
            current_order +=1
        return current_order
    
    def _calc_index_order_data(self) -> 'tuple[int]':
        """
        全ての元の位数を計算する。

        Returns
        -------
        TYPE
            元の位数の一覧。

        """
        return tuple(self._calc_index_order(i) for i in self.all_elements)
        
    def _calc_divisor_dict(self):
        """
        約数の辞書を作成する。
        約数と表現しているが、1を含んでいる。
        位数の約数をkeyとして、keyの約数の一覧を降順に並べたタプルをvalueとする。
        
        例：位数が12の場合
        { 12:(12,6,4,3,2,1), 8:(8,4,2,1), 4:(4,2,1), 3:(3,1), 2:(2,1), 1:(1) }
        
        Returns
        -------
        dict
            約数の辞書。

        """
        # 位数の約数。1も含む
        div_tuple = calctools.calc_divisor(self._order, True)        
        return {i: calctools.calc_divisor(i,True) for i in div_tuple}