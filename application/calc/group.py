"""
群の計算を行うためのモジュール。
"""
import itertools
import numpy
from . import calctools
from .matcal import CayleyTable
from .conjugacy import ConjugacyClass, ConjugacyCount

class MasterGroup(object):
    """
    解析対象となる最大の群を表す。
 
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
        # 交換子対応表
        self._commutator_data = self._calc_commutator_data()
        # 元の位数の対応表
        self._index_order_data = self._calc_index_order_data()
        # 約数リスト
        self._divisor_dict = self._calc_divisor_dict()
        # 部分群の採番
        self._group_count = 0
        # 部分群の名前の接頭辞
        self._group_initial = "group"
        # 生成された部分群の一覧
        self._group_storage = set()
        # 最大の群
        self._maximal_group = None
        # 自明群
        self._trivial_group = None
    
    @property
    def group_initial(self) -> str:
        return self._group_initial    
    
    @group_initial.setter
    def group_initial(self, initial: str):
        self._group_initial = initial   
   
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
    
    @property
    def maximal_group(self) -> 'Group':
        """

        Returns
        -------
        'Group'
            MasterGroupの最大の部分群。
            MasterGroupに対応する群オブジェクト。

        """
        if self._maximal_group is None:
            self._maximal_group = self.create_group(self.all_elements)
        return self._maximal_group
    
    @property
    def trivial_group(self) -> 'Group':
        """

        Returns
        -------
        'Group'
            自明群。単位元のみからなる群。

        """
        if self._trivial_group is None:
            self._trivial_group = self.create_group({self._identity_index})
        return self._trivial_group
    
    def naming_group(self, group: 'Group'):
        name = f'{self.group_initial}{self._group_count}'
        group.name = name
    
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
    
    def index_commutator(self, index1: int, index2: int) -> int:
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
        return self._commutator_data[index1][index2]
   
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
    
    def indices_are_commutable(self, index1: int, index2: int) -> bool:
        """
        指定の二つの元が可換であるか判定する。

        Parameters
        ----------
        index1 : int
            一つ目の元のインデックス。
        index2 : int
            二つ目の元のインデックス。

        Returns
        -------
        bool
            True:
                可換である。
            False:
                可換でない。

        """
        return self.index_commutator(index1,index2) == self._identity_index
    
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
         
    def create_group(self, closure: 'set[int]') ->'Group':
        """
        閉じた集合を指定して群オブジェクトを作成する。
        ただし、完全に同じ要素を持つ群が存在している場合には、その群オブジェクトを返す。
        
        注意:
            集合が閉じていない場合には、不適切な群オブジェクトが作成される。

        Parameters
        ----------
        closure : 'set[int]'
            閉じた元の集合。

        Returns
        -------
        'Group'
            作成された群オブジェクト。

        """
        group = Group(self, closure)
        for i in self._group_storage:
            if group.equal_to(i): return i
        self._group_storage.add(group)
        self.naming_group(group)
        self._group_count += 1
        return group
    
    def generate_group(self, indexset: 'set[int]') -> 'Group':
        """
        指定の集合から閉じた集合を生成し、群オブジェクトを作成する。
    
        Parameters
        ----------
        indexset : 'set[int]'
            元の集合。

        Returns
        -------
        'Group'
            生成された群オブジェクト。

        """
        closure = self.calc_closure(indexset)
        return self.create_group(closure)
    
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
    
    def _calc_commutator_data(self) -> numpy.ndarray:
        """
        元の交換子を計算する。
        gとhの交換子： [g,h] = g * h * g^(-1) * h^(-1)

        Returns
        -------
        numpy.ndarray
            交換子表。

        """
        commutator_table = numpy.identity(self.order,dtype=int)
        for (g, h) in itertools.product(self.all_elements,self.all_elements):
            g_inv = self.index_inverse(g)
            h_inv = self.index_inverse(h)
            result = self.index_prod(g,h)
            result = self.index_prod(result,g_inv)
            result = self.index_prod(result,h_inv)
            commutator_table[g][h] = result
        return commutator_table 
    
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

class Group(object):
    """
    MasterGroupの部分群を表す。

    Parameters
    ----------
    master : 'MasterGroup'
        親となる群。
    closure : 'set[int]'
        閉じた集合。
        
    """
    def __init__(self, master: 'MasterGroup', closure: 'set[int]'):
        self._master = master
        self._elements = frozenset(closure)
        self._order =  len(self._elements)
        self._name = "nameless"
        # 以降は初期状態ではNone
        # 初回の呼び出し時にのみ計算される
        self._cayley_table = None
        self._conjugacy_classes = None
        self._conjugacy_count = None
        self._center = None
        self._centrizer = None
        self._derived = None
        self._derived_series = None
        self._is_abelian = None
        self._is_perfect = None
        self._is_solvable = None
    
    def __str__(self):
        return f'{self.name}: {tuple(sorted(list(self.elements)))}'
    
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
    
    @property
    def conjugacy_classes(self) -> 'tuple[ConjugacyClass]':
        """

        Returns
        -------
        'tuple[ConjugacyClass]'
            共役類の一覧。
            位数 > 要素数 の優先度で昇順にソートされている。

        """
        if self._conjugacy_classes is None:
            self._conjugacy_classes = self._calc_conjugacy_classes()
        return self._conjugacy_classes
    
    @property
    def conjugacy_count(self) -> 'ConjugacyCount':
        """

        Returns
        -------
        'ConjugacyCount'
            共役類の特性。

        """
        if self._conjugacy_count is None:
            self._conjugacy_count = ConjugacyCount \
                .create_from_conjugacy_classes(self.conjugacy_classes)
        return self._conjugacy_count
    
    @property
    def center(self) -> 'Group':
        """

        Returns
        -------
        'Group'
            この群の中心。
            
            備考:
            この群の元のうち、この群の全ての元と可換な元の集合を指す。
            この集合は群をなす。

        """
        if self._center is None:
            self._center = self._calc_center()
        return self._center   

    @property
    def centrizer(self) -> 'Group':
        """

        Returns
        -------
        'Group'
            MasterGroupに対するこの群の中心化群。
            
            備考:
            MasterGroupの元のうち、この群の全ての元と可換な元の集合を指す。
            この集合は群をなす。

        """
        if self._centrizer is None:
            self._centrizer = self._calc_centrizer()
        return self._centrizer 
    
    @property
    def derived(self) -> 'Group':
        """

        Returns
        -------
        'Group'
            この群の導来部分群。
            
            備考:
                交換子部分群とも呼ばれる。
                この群の全ての元の交換子の集合であり、この集合は群をなす。
            
        """
        if self._derived is None:
            self._derived = self._calc_derived()
        return self._derived
    
    @property
    def derived_series(self) -> 'tuple[Group]':
        """

        Returns
        -------
        tuple[Group]
            この群の導来列。
            (一次導来群, 二次同来群,...)と並ぶ。
            
            備考:
                この群の導来部分群を第一次導来群とよび、
                n次導来群の導来部分群をn+1次導来群と呼ぶ。
                有限群の導来列は完全群で終わる。
            
            備考:
                完全群とは、導来部分群が自分自身となる群を指す。

        """
        if self._derived_series is None:
            self._derived_series = self._calc_derived_series()
        return self._derived_series   
    
    @property
    def is_abelian(self) -> bool:
        """

        Returns
        -------
        bool
            この群が可換群と非可換群のどちらであるか。
            True:
                可換群である。
            False:
                非可換群である。
                
            備考:
                可換群とは、導来部分群が自明群となる群を指す。

        """
        if self._is_abelian is None:
            # 導来部分群が自明群と一致するかどうかで判定する
            derived = self.derived
            trivial = self._master.trivial_group
            self._is_abelian = derived.equal_to(trivial)
        return self._is_abelian    

    @property
    def is_perfect(self) -> bool:
        """

        Returns
        -------
        bool
            この群が完全群であるか。
            True:
                完全群である。
            False:
                完全群でない。
                
            備考:
                完全群とは、導来部分群が自分自身となる群を指す。

        """
        if self._is_perfect is None:
            # 導来部分群が自分自身と一致するかで判定する
            derived = self.derived
            self._is_perfect = derived.equal_to(self)
        return self._is_perfect    

    @property
    def is_solvable(self) -> bool:
        """

        Returns
        -------
        bool
            この群が可解群であるか。
            True:
                可解群である。
            False:
                可解群でない。
                
            備考:
                可解群とは、導来列が自明群で終わる群を指す。

        """
        if self._is_solvable is None:
            # 導来列の最後が自明群であるかでどうかで判定する
            group = self.derived_series[-1]
            trivial = self._master.trivial_group
            self._is_solvable = group.equal_to(trivial)
        return self._is_solvable 

    def equal_to(self, other: 'Group') -> bool:
        """
        この群と指定の群の要素が完全に一致するか判定する。

        Parameters
        ----------
        other : 'Group'
            指定の群。

        Returns
        -------
        bool
            True:
                同一オブジェクトである。
                要素が完全に一致する。
            False:
                それ以外。

        """
        return (self is other) or (self.elements == other.elements)
    
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
    
    def _calc_conjugacy_classes(self) -> 'tuple[ConjugacyClass]':
        """
        この群の共役類の一覧を計算する。

        Returns
        -------
        'tuple[ConjugacyClass]'
            共役類の一覧。
            位数 > 要素数 の優先度で昇順にソートされている。

        """
        c_classes = []
        remaining = set(self.elements)
        while len(remaining) != 0:
            # 任意の要素を一つ取得
            g = list(remaining)[0]
            # 群の各元で共役変換
            conjugacy = {self._master.index_conjugate(g,h) for h 
                         in self.elements}
            # 共役類の位数
            order = self._master.index_order(g)
            c_classes.append(ConjugacyClass(conjugacy, order))
            remaining = remaining.difference(conjugacy)
        return tuple(sorted(c_classes))
    
    def _calc_center(self) -> 'Group':
        """
        この群の中心を計算する。

        Returns
        -------
        'Group'
            この群の中心。

        """
        closure = {g for g in self.elements
                   if all(self._master.indices_are_commutable(g, h)
                          for h in self.elements)}
        return self._master.create_group(closure)
    
    def _calc_centrizer(self) -> 'Group':
        """
        MasterGroupに対するこの群の中心化群を計算する。

        Returns
        -------
        'Group'
            MasterGroupに対するこの群の中心化群。

        """
        closure = {g for g in self._master.all_elements
                   if all(self._master.indices_are_commutable(g, h)
                          for h in self.elements)}
        return self._master.create_group(closure)
    
    def _calc_derived(self) -> 'Group':
        """
        この群の導来群を計算する。

        Returns
        -------
        'Group'
            この群の導来群。

        """
        closure = {self._master.index_commutator(g, h) for (g,h) 
                   in itertools.product(self.elements, self.elements)}
        return self._master.create_group(closure)
    
    def _calc_derived_series(self) -> 'tuple[Group]':
        """
        この群の導来列を計算する。

        Returns
        -------
        'tuple[Group]'
            この群の導来列。

        """
        series = []
        current = self
        while True:
            derived = current.derived
            if current.equal_to(derived): break
            series.append(derived)
            current = derived
        return tuple(series)
            
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
        