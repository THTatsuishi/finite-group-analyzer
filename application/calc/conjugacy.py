"""
共役類を扱うためのクラス。
"""
class ConjugacyClass(object):
    """
    共役類を表す。

    Parameters
    ----------
    indexset : 'set[int]'
        共役類の要素。
        備考：共役類の要素数は、その群の位数の約数である。
    order : int
        共役類の位数。
        共役類の要素の位数乗が単位元となる。

    """
    def __init__(self, indexset: 'set[int]', order: int):
        self._elements = frozenset(indexset)
        self._element_num = len(self._elements)
        self._order = order
    
    def __lt__(self, other) -> bool:
        """
        位数 > 要素数 の優先順で大小比較する。

        Parameters
        ----------
        other : TYPE
            DESCRIPTION.

        Returns
        -------
        bool
            DESCRIPTION.

        """
        if self.order == other.order:
            return self.element_num < other.element_num
        return self.order < other.order
    
    def __str__(self):
        return f'({self.order}, {self.element_num}): {set(self.elements)}'
    
    @property
    def elements(self) -> 'frozenset[int]':
        """

        Returns
        -------
        'frozenset[int]'
            この共役類の要素のインデックスの一覧。

        """
        return self._elements
    
    @property
    def element_num(self) -> int:
        """

        Returns
        -------
        int
            この共役類の要素の数。
            備考：共役類の要素数は、その群の位数の約数である。

        """
        return self._element_num
    
    @property
    def order(self) -> int:
        """

        Returns
        -------
        int
            この共役類の位数。
            共役類の要素の位数乗が単位元となる。

        """
        return self._order

class ConjugacyCountUnit(object):
    """
    共役類の特性の単位を表す。

    Parameters
    ----------
    order : int
        共役類の位数。
        共役類の要素の位数乗が単位元となる。
    element_num : int
        共役類の要素数。
        備考：共役類の要素数は、その群の位数の約数である。
    degeneracy : int
        共役類の重複度。
        同じ（位数、要素数）の共役類の数を表す。

    """
    def __init__(self, order: int, element_num: int, degeneracy: int):
        self._order = order
        self._element_num = element_num
        self._degeneracy = degeneracy
        
    def __lt__(self, other) -> bool:
        """
        位数 > 要素数 の優先順で大小比較する。

        Parameters
        ----------
        other : TYPE
            DESCRIPTION.

        Returns
        -------
        bool
            DESCRIPTION.

        """
        if self.order == other.order:
            return self.element_num < other.element_num
        return self.order < other.order
    
    def __str__(self):
        return f'({self.order}, {self.element_num}, {self.degeneracy})'
    
    @property
    def order(self) -> int:
        """

        Returns
        -------
        int
            共役類の位数。
            共役類の要素の位数乗が単位元となる。

        """
        return self._order
    
    @property
    def element_num(self) -> int:
        """

        Returns
        -------
        int
            共役類の要素数。
            備考：共役類の要素数は、その群の位数の約数である。

        """
        return self._element_num
    
    @property
    def degeneracy(self) -> int:
        """

        Returns
        -------
        int
            共役類の重複度。
            同じ（位数、要素数）の共役類の数を表す。

        """
        return self._degeneracy
    
    @staticmethod
    def create_from_data(data: 'list[int]') -> 'ConjugacyCountUnit':
        if(len(data) != 3):
            raise ValueError("[ConjugacyCountUnit] リストの要素数が3でない。")
        return ConjugacyCountUnit(data[0],data[1],data[2])
    
    def equal_to(self, other: 'ConjugacyCount') -> bool:
        """
        共役類の特性が等しいか判定する。

        Parameters
        ----------
        other : 'ConjugacyCount'
            比較対象。

        Returns
        -------
        bool
            True:
                （位数、要素数、重複度）の全ての値がそれぞれ一致する。
            False:
                （位数、要素数、重複度）のいずれか一つ以上の値が異なる。

        """
        return (self.order == other.order 
                and self.element_num == other.element_num 
                and self.degeneracy == other.degeneracy)
        
class ConjugacyCount(object):
    """
    共役類の特性を表す。
    共役類の（位数、要素数、重複度）の一覧として表現する。

    Parameters
    ----------
    conjugacy_count_units : 'list[ConjugacyCountUnit]'
        共役類の特性の単位の一覧。

    """
    def __init__(self, conjugacy_count_units: 'list[ConjugacyCountUnit]'):
        self._conjugacy_count = tuple(sorted(conjugacy_count_units))
        
    def __str__(self):
        result = "("
        num = len(self.conjugacy_count)
        for i in range(num):
            if i == 0:
                result += f'{self.conjugacy_count[i]}'
            else:
                result += f', {self.conjugacy_count[i]}'
        result += ")"
        return result
        
    @property
    def conjugacy_count(self) -> 'tuple[ConjugacyCountUnit]':
        """

        Returns
        -------
        'tuple[ConjugacyCountUnit]'
            共役類の特性。
            位数 > 要素数 の優先順位で昇順にソートされている。

        """
        return self._conjugacy_count             
    
    @staticmethod
    def create_from_conjugacy_classes(
            conjugacy_classes: 'list[ConjugacyClass]'
                                      ) -> 'ConjugacyCount':
        """
        共役類の一覧から共役類の特性を作成する。

        Parameters
        ----------
        conjugacy_classes : 'list[ConjugacyClass]'
            共役類の一覧。

        Returns
        -------
        ConjugacyCout
            共役類の特性。

        """
        c_classes = sorted(conjugacy_classes)
        unitlist = []
        prev_order = 0
        prev_num = 0
        degeneracy = 1
        for c_class in c_classes:
            order = c_class.order
            num = c_class.element_num
            if order == prev_order and num == prev_num:
                degeneracy += 1
                continue
            unitlist.append(ConjugacyCountUnit(prev_order,prev_num,degeneracy))
            prev_order = order
            prev_num = num
            degeneracy = 1
        unitlist.append(ConjugacyCountUnit(prev_order,prev_num,degeneracy))
        del unitlist[0]
        return ConjugacyCount(unitlist)
    
    @staticmethod
    def create_from_data(data: 'list[list[int]]') -> 'ConjugacyCount':
        unit_data_list = [ConjugacyCountUnit.create_from_data(unit_data) 
                          for unit_data in data]
        return ConjugacyCount(unit_data_list)
    
    def is_equivalent_to(self, other: 'ConjugacyCount') -> bool:
        """
        共役類の特性が等しいか判定する。

        Parameters
        ----------
        other : 'ConjugacyCount'
            比較対象。

        Returns
        -------
        bool
            True:
                全ての共役類の(位数、要素数、重複度)が等しい。
            False:
                それ以外。

        """
        if self.conjugacy_count != len(other.conjugacy_count): return False
        return all(a.equal_to(b) for (a,b) 
                   in zip(self.conjugacy_count, other.conjugacy_count))
    