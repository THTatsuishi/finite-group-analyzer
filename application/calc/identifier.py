"""
群を同定するためのモジュール。
"""
from .calctools import prime_factorize
from ..namedgroup.gdata import NamedGroupData

class GroupIdentifier(object):
    _not_exist_symbol = "?"
    _trivial_symbol = "Id"
    _cyclic_symbol = "Z"
    
    @classmethod
    def find_isomorphic(cls, group) -> str:
        """
        指定の群の同定を行う。

        Parameters
        ----------
        cls : TYPE
            DESCRIPTION.
        group : TYPE
            指定の群。

        Returns
        -------
        str
            群の同型の表示。

        """
        return (cls._find_isomorphic_abelian(group) 
                if group.is_abelian else 
                cls._find_isomorphic_non_abelian(group))
    
    @classmethod
    def _find_isomorphic_abelian(cls, group) -> str:
        """
        可換群の同定を行う。
        アーベルの基本定理:
            有限可換群は 「素数の自然数冪の位数の巡回群」の直積と同型である
        分解は要素としては一意的でないが、群同型の意味では一意的である。
        ここでは、最も細かい直積分解の一つの方法を与える。

        Parameters
        ----------
        cls : TYPE
            DESCRIPTION.
        group : TYPE
            可換群。

        Returns
        -------
        str
            群の同型の表示。

        """
        # アルゴリズム上、自明群は省いておく必要がある
        # 可換群は正規部分群の探索に時間がかかるので, 単純群であるかの判定はしない
        if group.is_trivial: return cls._trivial_symbol       
        # 一般の場合の処理
        master = group.master
        # STEP 1. 可換群を巡回群の積に分解する
        # 「要素の位数の最大値」より大きな位数の巡回群は存在しない
        # よって、要素の位数の最大値 max_order で分解できる
        # 例： G(8) は (Z2 × Z2 × Z2) or (Z2 × Z4) or Z8 
        # 例： G(12) は (Z2 × Z6) or Z12
        remaining = (group,)
        decomposed_step1 = []
        while len(remaining) != 0:
            next_list = []
            for group1 in remaining:
                max_order = group1.max_element_order
                # max_order == 群の位数 ならば処理終了
                if max_order == group1.order:
                    decomposed_step1.append(group1)
                    continue
                # max_orderを持つ要素を任意に一つ選ぶ
                index = group1.elements_of_order(max_order)[0]
                # G2(max_order) times G3(残り) とできるような　G2,G3 が存在する
                group2 = master.generate_group({index,})
                group3 = cls._decompose_abelian(group1,group2)
                decomposed_step1.append(group2)
                next_list.append(group3)
            remaining = tuple(next_list)
        # STEP 2. 巡回群を「位数が単一素数冪の巡回群」の積に分解する
        # この時点では、 群の位数 = 要素の位数の最大値 となっている
        # 群の位数を素因数分解して、 N = p^n * q^m * ... のとき、
        # Z(N) = Z(p^n) times Z(q^n) times ...　とできる
        # 例： Z6 は (Z2 × Z3)
        # 例: Z12 は (Z3 × Z4) 
        remaining = tuple(decomposed_step1)
        decomposed_step2 = []
        while len(remaining) != 0:
            next_list = []
            for group1 in remaining:
                # 位数を素因数分解
                prime_dict = prime_factorize(group1.order)
                # 単一素数の冪ならば処理終了
                if len(prime_dict) == 1:
                    decomposed_step2.append(group1)
                    continue
                # 分解
                prime = prime_dict.keys()[0]
                power = prime_dict[prime]
                target_order = prime ** power
                index = group1.elements_of_order(target_order)[0]
                group2 = master.generate_group({index,})
                group3 = cls._decompose_abelian(group1,group2)
                decomposed_step2.append(group2)
                next_list.append(group3)
            remaining = tuple(next_list)
        # 分解終了
        # Symbolを決定
        sorted_list = sorted(decomposed_step2)
        total_symbol = ""
        for group1 in sorted_list:
            symbol = f'{cls._cyclic_symbol}({group1.order})'
            total_symbol += symbol + " × "
        return total_symbol[:-3]
    
    @classmethod
    def _decompose_abelian(cls, group1, group2):
        """
        [group1] を [group2] times [group] とするような [group] を見つける。
        

        Parameters
        ----------
        cls : TYPE
            DESCRIPTION.
        group1 : TYPE
            可換群。
        group2 : TYPE
            group1の部分群である可換群。

        Returns
        -------
        group : TYPE
            可換群。

        """
        candidate = set(group1.elements - group2.elements)
        gens = []
        group3 = None
        while len(candidate) != 0:           
            copy_candidate = list(candidate)
            closure = None
            for index in copy_candidate:
                gens_tmp = list(gens)
                gens_tmp.append(index)
                closure = group1.master.calc_closure(gens_tmp)
                if len(group2.elements & closure) != 1:
                    candidate.discard(index)
                else:
                    break
            gens = list(gens_tmp)
            candidate = candidate - closure
            if group1.order == group2.order * len(closure):
                group3 = group1.master.create_group(closure)
                break
        return group3
      
    @classmethod
    def _find_isomorphic_non_abelian(cls, group) -> str:
        """
        非可換群の同定を行う。
        あらかじめ登録されている名付けられた群の一覧の中から、同型なものを探す。

        Parameters
        ----------
        cls : TYPE
            DESCRIPTION.
        group : TYPE
            非可換群。

        Returns
        -------
        str
            同型な群の名前。

        """
        for target in NamedGroupData.groups(group.order):
            if target.is_isomorpic_to_group(group):
                return target.name
        # 該当する群なし
        return cls._not_exist_symbol