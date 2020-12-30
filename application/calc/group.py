"""
群の計算を行うためのモジュール。
"""
import itertools
import numpy
from .mastergroup import MasterGroup

class Group(object):
    def __init__(self, master: 'MasterGroup', closure: 'set[int]'):
        self._master = master
        self._elements = frozenset(closure)
        self._order =  len(self._elements)
        self._name = "nameless"
        # 以降は初期状態ではNone
        # 初回の呼び出し時にのみ計算される
        self._cayley_table = None
    
    @property
    def name(self) -> str:
        """

        Returns
        -------
        str
            この群の名前。
            任意の文字列が設定されたものであり、数学的な意味はもたない。

        """
        return self._name
    
    @name.setter
    def name(self, name: str):
        """
        この群の呼び名を設定する。
        任意の文字列を設定するものであり、数学的な意味は持たない。

        Parameters
        ----------
        name : str
            設定する名前。

        Returns
        -------
        None.

        """
        self._name = name
    
    @property
    def elements(self) -> 'frozenset[int]':
        """

        Returns
        -------
        'frozenset[int]'
            この群の元のインデックスの一覧。

        """
        return self._elements
    
    @property
    def order(self) -> int:
        """

        Returns
        -------
        int
            この群の位数。

        """
        return self._order
    
    @property
    def cayley_table(self) -> numpy.ndarray:
        """

        Returns
        -------
        numpy.ndarray
            この群の乗積表。
            元のインデックスの昇順に並ぶ。

        """
        if self._cayley_table is None:
            self._cayley_table = self._calc_cayley_table()
        return self._cayley_table  
    
    def _calc_cayley_table(self) -> numpy.ndarray:
        """
        この群の乗積表を計算する。
        元のインデックスが昇順に並ぶ。

        Returns
        -------
        numpy.ndarray
            乗積表。

        """
        mastertable = self._master.cayley_table
        table = numpy.identity(self.order,int)
        indexlist = sorted(self.elements)
        row = 0
        for i1 in indexlist:
            column= 0
            for i2 in indexlist:
                table[row][column] = mastertable[i1][i2]
                column += 1
            row += 1
        return table
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
        