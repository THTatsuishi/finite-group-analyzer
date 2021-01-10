"""
群を同定するためのモジュール。
"""
from .conjugacy import ConjugacyCount
from .calctools import prime_factorize

class NamedGroup(object):
    def __init__(self, name: str, data):
        self._name = name
        self._conjugacy_count = ConjugacyCount.create_from_data(data)
        order = 0
        for unit in self.conjugacy_count.count:
            order += unit.element_num * unit.degeneracy
        self._order = order
        
    @property
    def name(self):
        return self._name
    
    @property
    def conjugacy_count(self):
        return self._conjugacy_count
    
    @property
    def order(self):
        return self._order
    
    def is_isomorpic_to_group(self, group) -> bool:
        """
        指定の群と同型であるか判定する。
        conjugacy_countが一致すれば同型であると判定する。

        Parameters
        ----------
        group : TYPE
            指定の群・

        Returns
        -------
        bool
            True:
                同型である。
            False:
                同型でない。

        """
        return self.conjugacy_count.equal_to(group.conjugacy_count)

 
####
#### 実装中
####
class GroupIdentifier(object):
    _not_exist_symbol = "?"
    _trivial_symbol = "Id"
    _cyclic_symbol = "Z"
    
    @classmethod
    def find_isomorphic(cls, group) -> str:
        return (cls._find_isomorphic_abelian(group) 
                if group.is_abelian else 
                cls._find_isomorphic_non_abelian(group))
    
    @classmethod
    def _find_isomorphic_abelian(cls, group) -> str:
        """
        可換群のを同定する。
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
            同定結果。

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
        非可換群を同定する。
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
        # 辞書にkeyが含まれていない
        if group.order not in cls._named_group_dict:
            return cls._not_exist_symbol
        # keyが含まれている
        target_list = cls._named_group_dict[group.order]
        for target in target_list:
            if target.is_isomorpic_to_group(group):
                return target.name
        # 該当する群なし
        return cls._not_exist_symbol
    
    # 非可換群の位数ごとの conjugacy_count
    # (確定)ならば, 非可換群ならば必ずいずれかと同型となる
    # (候補)ならば, 他の候補が存在する (分解など)
    _named_group_dict = dict()
    
    #### 6 -> (確定): D3
    D3 = ((1, 1, 1), (2, 3, 1), (3, 2, 1))
    _named_group_dict[6] = (
        NamedGroup("D(3)",D3),
        )
    
    #### 8 -> (確定): Q4, D4
    D4 = ((1, 1, 1), (2, 1, 1), (2, 2, 2), (4, 2, 1))
    Q4 = ((1, 1, 1), (2, 1, 1), (4, 2, 3))
    _named_group_dict[8] = (
        NamedGroup("D(4)",D4),
        NamedGroup("Q(4)",Q4),
        )
    
    #### 10 -> (確定) D5
    D5 = ((1, 1, 1), (2, 5, 1), (5, 2, 2))
    _named_group_dict[10] = (
        NamedGroup("D(5)",D5),
        )
    
    #### 12 -> (確定): D6, Q6, A4
    D6 = ((1, 1, 1), (2, 1, 1), (2, 3, 2), (3, 2, 1), (6, 2, 1))
    Q6 = ((1, 1, 1), (2, 1, 1), (3, 2, 1), (4, 3, 2), (6, 2, 1))
    A4  = ((1, 1, 1), (2, 3, 1), (3, 4, 2))
    _named_group_dict[12] = (
        NamedGroup("D(6)",D6),
        NamedGroup("Q(6)",Q6),
        NamedGroup("A(4)",A4),
        )
    
    #### 14 -> (確定): D7
    D7 = ((1, 1, 1), (2, 7, 1), (7, 2, 3))
    _named_group_dict[14] = (
        NamedGroup("D(7)",D7),
        )
    
    #### 16 -> (候補): D8, Q8, QD16
    D8 = ((1, 1, 1), (2, 1, 1), (2, 4, 2), (4, 2, 1), (8, 2, 2))
    Q8 = ((1, 1, 1), (2, 1, 1), (4, 2, 1), (4, 4, 2), (8, 2, 2))
    QD16 = ((1, 1, 1), (2, 1, 1), (2, 4, 1), (4, 2, 1), (4, 4, 1), (8, 2, 2))
    _named_group_dict[16] = (
        NamedGroup("D(8)",D8),
        NamedGroup("Q(8)",Q8),
        NamedGroup("QD(16)",QD16),
        )
    
    #### 18 -> (候補): D9, Sigma18
    D9 = ((1, 1, 1), (2, 9, 1), (3, 2, 1), (9, 2, 3))
    Sigma18 = ((1, 1, 1), (2, 3, 1), (3, 1, 2), (3, 2, 3), (6, 3, 2))
    _named_group_dict[18] = (
        NamedGroup("D(9)",D9),
        NamedGroup("Sigma(18)",Sigma18),
        )
    
    #### 20 -> (候補): D10, Q10
    D10 = ((1, 1, 1), (2, 1, 1), (2, 5, 2), (5, 2, 2), (10, 2, 2))
    Q10 = ((1, 1, 1), (2, 1, 1), (4, 5, 2), (5, 2, 2), (10, 2, 2))
    _named_group_dict[20] = (
        NamedGroup("D(10)",D10),
        NamedGroup("Q(10)",Q10),
        )
    
    #### 21 -> (候補): T7
    T7 = ((1, 1, 1), (3, 7, 2), (7, 3, 2))
    _named_group_dict[21] = (
        NamedGroup("T(7)",T7),
        )
    
    #### 22 -> (確定): D11
    D11 = ((1, 1, 1), (2, 11, 1), (11, 2, 5))
    _named_group_dict[22] = (
        NamedGroup("D(11)",D11),
        )
    
    #### 24 -> (候補): D12, Q12, S4, Tprime, Sigma24
    D12 = ((1, 1, 1), (2, 1, 1), (2, 6, 2), (3, 2, 1), (4, 2, 1), 
           (6, 2, 1), (12, 2, 2))
    Q12 = ((1, 1, 1), (2, 1, 1), (3, 2, 1), (4, 2, 1), (4, 6, 2), 
           (6, 2, 1), (12, 2, 2))
    S4 = ((1, 1, 1), (2, 3, 1), (2, 6, 1), (3, 8, 1), (4, 6, 1))
    Tprime = ((1, 1, 1), (2, 1, 1), (3, 4, 2), (4, 6, 1), (6, 4, 2))
    Sigma24 = ((1, 1, 1), (2, 1, 1), (2, 3, 2), (3, 4, 2), (6, 4, 2))
    _named_group_dict[24] = (
        NamedGroup("D(12)",D12),
        NamedGroup("Q(12)",Q12),
        NamedGroup("S(4)",S4),
        NamedGroup("Tprime",Tprime),
        NamedGroup("Sigma(24)",Sigma24),
        )
    
    #### 26 -> (確定): D13
    D13 = ((1, 1, 1), (2, 13, 1), (13, 2, 6))
    _named_group_dict[26] = (
        NamedGroup("D(13)",D13),
        )
    
    #### 27 -> (候補): Delta27
    Delta27 = ((1, 1, 1), (3, 1, 2), (3, 3, 8))
    _named_group_dict[27] = (
        NamedGroup("Delta(27)",Delta27),
        )

    #### 28 -> (確定): D14, Q14
    D14 = ((1, 1, 1), (2, 1, 1), (2, 7, 2), (7, 2, 3), (14, 2, 3))
    Q14 = ((1, 1, 1), (2, 1, 1), (4, 7, 2), (7, 2, 3), (14, 2, 3))
    _named_group_dict[28] = (
        NamedGroup("D(14)",D14),
        NamedGroup("Q(14)",Q14),
        )
    
    #### 30 -> (確定): D15
    D15 = ((1, 1, 1), (2, 15, 1), (3, 2, 1), (5, 2, 2), (15, 2, 4))
    _named_group_dict[30] = (
        NamedGroup("D(15)",D15),
        )
    
    ##### 32 -> (候補): D16, Q16, QD32, Sigma(32)
    D16 = ((1, 1, 1), (2, 1, 1), (2, 8, 2), (4, 2, 1), (8, 2, 2), (16, 2, 4))
    Q16 = ((1, 1, 1), (2, 1, 1), (4, 2, 1), (4, 8, 2), (8, 2, 2), (16, 2, 4))
    QD32 = ((1, 1, 1), (2, 1, 1), (2, 8, 1), (4, 2, 1), (4, 8, 1), 
            (8, 2, 2), (16, 2, 4))
    Sigma32 = ((1, 1, 1), (2, 1, 1), (2, 2, 1), (2, 4, 1), (4, 1, 2), 
               (4, 2, 5), (4, 4, 1), (8, 4, 2))
    _named_group_dict[32] = (
        NamedGroup("D(16)",D16),
        NamedGroup("Q(16)",Q16),
        NamedGroup("QD(32)",QD32),
        NamedGroup("Sigma(32)",Sigma32),
        )
    
    ##### 34 -> (確定): D17
    D17 = ((1, 1, 1), (2, 17, 1), (17, 2, 8))
    _named_group_dict[34] = (
        NamedGroup("D(17)",D17),
        )
    
    ##### 36 -> (候補): D18, Q18
    D18 = ((1, 1, 1), (2, 1, 1), (2, 9, 2), (3, 2, 1), (6, 2, 1), 
           (9, 2, 3), (18, 2, 3))
    Q18 = ((1, 1, 1), (2, 1, 1), (3, 2, 1), (4, 9, 2), (6, 2, 1), 
           (9, 2, 3), (18, 2, 3))
    _named_group_dict[36] = (
        NamedGroup("D(18)",D18),
        NamedGroup("Q(18)",Q18),
        )

    ##### 38 -> (確定): D19
    D19 = ((1, 1, 1), (2, 19, 1), (19, 2, 9))
    _named_group_dict[38] = (
        NamedGroup("D(19)",D19),
        )
    
    #### 39 -> (候補): T13
    T13 = ((1, 1, 1), (3, 13, 2), (13, 3, 4))
    _named_group_dict[39] = (
        NamedGroup("T(13)",T13),
        )    
    
    ##### 40 -> (候補) D20, Q20
    D20 = ((1, 1, 1), (2, 1, 1), (2, 10, 2), (4, 2, 1), (5, 2, 2), 
           (10, 2, 2), (20, 2, 4))
    Q20 = ((1, 1, 1), (2, 1, 1), (4, 2, 1), (4, 10, 2), (5, 2, 2), 
           (10, 2, 2), (20, 2, 4))
    _named_group_dict[40] = (
        NamedGroup("D(20)",D20),
        NamedGroup("Q(20)",Q20),
        )
    
    #### 42 -> (候補)D21
    D21 = ((1, 1, 1), (2, 21, 1), (3, 2, 1), (7, 2, 3), (21, 2, 6))
    _named_group_dict[42] = (
        NamedGroup("D(21)",D21),
        )
    
    #### 44 -> (候補) D22, Q22
    D22 = ((1, 1, 1), (2, 1, 1), (2, 11, 2), (11, 2, 5), (22, 2, 5))
    Q22 = ((1, 1, 1), (2, 1, 1), (4, 11, 2), (11, 2, 5), (22, 2, 5))
    _named_group_dict[44] = (
        NamedGroup("D(22)",D22),
        NamedGroup("Q(22)",Q22),
        )
    
    #### 46 -> (確定): D23
    D23 = ((1, 1, 1), (2, 23, 1), (23, 2, 11))
    _named_group_dict[46] = (
        NamedGroup("D(23)",D23),
        )
    
    #### 48 -> (候補): D24, Q24, Delta48
    D24 = ((1, 1, 1), (2, 1, 1), (2, 12, 2), (3, 2, 1), (4, 2, 1), 
           (6, 2, 1), (8, 2, 2), (12, 2, 2), (24, 2, 4))
    Q24 = ((1, 1, 1), (2, 1, 1), (3, 2, 1), (4, 2, 1), (4, 12, 2), 
           (6, 2, 1), (8, 2, 2), (12, 2, 2), (24, 2, 4))
    Delta48 = ((1, 1, 1), (2, 3, 1), (3, 16, 2), (4, 3, 4))
    _named_group_dict[48] = (
        NamedGroup("D(24)",D24),
        NamedGroup("Q(24)",Q24),
        NamedGroup("Delta(48)",Delta48),
        )
    
    #### 50 -> (候補): Sigma50
    Sigma50 = ((1, 1, 1), (2, 5, 1), (5, 1, 4), (5, 2, 10), (10, 5, 4))
    _named_group_dict[50] = (
        NamedGroup("Sigma(50)",Sigma50),
        )
    
    #### 54 -> (候補): Delta54
    Delta54 = ((1, 1, 1), (2, 9, 1), (3, 1, 2), (3, 6, 4), (6, 9, 2))
    _named_group_dict[54] = (
        NamedGroup("Delta(54)",Delta54),
        )
    
    #### 57 -> (候補): T19
    T19 = ((1, 1, 1), (3, 19, 2), (19, 3, 6))
    _named_group_dict[57] = (
        NamedGroup("T(19)",T19),
        )    
    
    #### 60 -> (候補): A5
    A5 = ((1, 1, 1), (2, 15, 1), (3, 20, 1), (5, 12, 2))
    _named_group_dict[60] = (
        NamedGroup("A(5)",A5),
        )
    
    #### 64 -> (候補): QD64
    QD64 = ((1, 1, 1), (2, 1, 1), (2, 16, 1), (4, 2, 1), (4, 16, 1), 
            (8, 2, 2), (16, 2, 4), (32, 2, 8))
    _named_group_dict[64] = (
        NamedGroup("QD(64)",QD64),
        )
    
    #### 72 -> (候補): Sigma72
    Sigma72 = ((1, 1, 1), (2, 1, 1), (2, 2, 1), (2, 6, 1), (3, 1, 2), 
               (3, 2, 3), (4, 6, 1), (6, 1, 2), (6, 2, 11), (6, 6, 2), 
               (12, 6, 2))
    _named_group_dict[72] = (
        NamedGroup("Sigma(72)",Sigma72),
        )

    #### 75 -> (候補): Delta75
    Delta75 = ((1, 1, 1), (3, 25, 2), (5, 3, 8))
    _named_group_dict[75] = (
        NamedGroup("Delta(75)",Delta75),
        )
    
    #### 81 -> (候補): Sigma81
    Sigma81 = ((1, 1, 1), (3, 1, 2), (3, 3, 8), (3, 9, 2), (9, 9, 4))
    _named_group_dict[81] = (
        NamedGroup("Sigma(81)",Sigma81),
        )
    
    #### 96 -> (候補): Delta96
    Delta96 = ((1, 1, 1), (2, 3, 1), (2, 12, 1), (3, 32, 1), (4, 3, 2), 
               (4, 6, 1), (4, 12, 1), (8, 12, 2))
    _named_group_dict[96] = (
        NamedGroup("Delta(96)",Delta96),
        )
    
    #### 98 -> (候補): Sigma98
    Sigma98 = ((1, 1, 1), (2, 7, 1), (7, 1, 6), (7, 2, 21), (14, 7, 6))
    _named_group_dict[98] = (
        NamedGroup("Sigma(98)",Sigma98),
        )
    
    #### 108 -> (候補): Delta108
    Delta108 = ((1, 1, 1), (2, 3, 1), (3, 1, 2), (3, 3, 2), (3, 12, 6), 
               (6, 3, 8))
    _named_group_dict[108] = (
        NamedGroup("Delta(108)",Delta108),
        )
    
    #### 120 -> (候補): S5
    S5 = ((1, 1, 1), (2, 10, 1), (2, 15, 1), (3, 20, 1), 
          (4, 30, 1), (5, 24, 1), (6, 20, 1))
    _named_group_dict[120] = (
        NamedGroup("S(5)",S5),
        )
    
    #### 128 -> (候補): QD128, Sigma128
    QD128 = ((1, 1, 1), (2, 1, 1), (2, 32, 1), (4, 2, 1), (4, 32, 1), 
             (8, 2, 2), (16, 2, 4), (32, 2, 8), (64, 2, 16))
    Sigma128 = ((1, 1, 1), (2, 1, 1), (2, 2, 1), (2, 8, 1), (4, 1, 2), 
                (4, 2, 5), (4, 8, 1), (8, 1, 4), (8, 2, 22), (8, 8, 2), 
                (16, 8, 4))
    _named_group_dict[128] = (
        NamedGroup("QD(128)",QD128),
        NamedGroup("Sigma(128)",Sigma128),
        )
        
    #### 147 -> (候補): Delta147
    Delta147 = ((1, 1, 1), (3, 49, 2), (7, 3, 16))
    _named_group_dict[147] = (
        NamedGroup("Delta(147)",Delta147),
        )
    
    #### 150 -> (候補): Delta150
    Delta150 = ((1, 1, 1), (2, 15, 1), (3, 50, 1), (5, 3, 4), 
                (5, 6, 2), (10, 15, 4))
    _named_group_dict[150] = (
        NamedGroup("Delta(150)",Delta150),
        )
    
    #### 162 -> (候補): Sigma162
    Sigma162 = ((1, 1, 1), (2, 9, 1), (3, 1, 2), (3, 2, 3), (6, 9, 2), 
                (9, 1, 6), (9, 2, 33), (18, 9, 6))
    _named_group_dict[162] = (
        NamedGroup("Sigma(162)",Sigma162),
        )

    #### 192 -> (候補): Delta192, Sigma192
    Delta192 = ((1, 1, 1), (2, 3, 1), (3, 64, 2), (4, 3, 4), (8, 3, 16))
    Sigma192 =((1, 1, 1), (2, 1, 1), (2, 3, 2), (3, 16, 2), (4, 1, 2), 
               (4, 3, 18), (6, 16, 2), (12, 16, 4))
    _named_group_dict[192] = (
        NamedGroup("Delta(192)",Delta192),
        NamedGroup("Sigma(192)",Sigma192),
        )
    
    #### 200 -> (候補): Sigma200
    Sigma200 = ((1, 1, 1), (2, 1, 1), (2, 2, 1), (2, 10, 1), (4, 10, 1), 
                (5, 1, 4), (5, 2, 10), (10, 1, 4), (10, 2, 34), 
                (10, 10, 4), (20, 10, 4))
    _named_group_dict[200] = (
        NamedGroup("Sigma(200)",Sigma200),
        )
    
    ### 216 -> (候補): Delta216
    Delta216 = ((1, 1, 1), (2, 3, 1), (2, 18, 1), (3, 1, 2), (3, 6, 1), 
                (3, 24, 3), (4, 18, 1), (6, 3, 2), (6, 6, 3), (6, 18, 2), 
                (12, 18, 2))
    _named_group_dict[216] = (
        NamedGroup("Delta(216)",Delta216),
        )
    
    #### 256 -> (候補): QD256
    QD256 = ((1, 1, 1), (2, 1, 1), (2, 64, 1), (4, 2, 1), (4, 64, 1), 
             (8, 2, 2), (16, 2, 4), (32, 2, 8), (64, 2, 16), (128, 2, 32))
    _named_group_dict[256] = (
        NamedGroup("QD(256)",QD256),
        )
    
    #### 360 -> (候補): A6
    A6 = ((1, 1, 1), (2, 45, 1), (3, 40, 2), (4, 90, 1), (5, 72, 2))
    _named_group_dict[360] = (
        NamedGroup("A(6)",A6),
        )

    #### 720 -> (候補): S6
    S6 = ((1, 1, 1), (2, 15, 2), (2, 45, 1), (3, 40, 2), 
          (4, 90, 2), (5, 144, 1), (6, 120, 2))
    _named_group_dict[720] = (
        NamedGroup("S(6)",S6),
        )
