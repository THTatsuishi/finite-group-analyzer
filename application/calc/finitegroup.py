# -*- coding: utf-8 -*-

#####################################
# Python 3.7
# 作成者: 立石卓也
# 作成時所属: 北海道大学 素粒子論研究室
#####################################

import numpy
import collections

#### 解析準備を行うためのクラス
class Constructor(object):
    call_flag = True
    @classmethod
    def setup(cls,master_gens,maximal,equal_zero):
        # setup は一度しか実行できない
        if cls.call_flag:
            cls.call_flag = False
        else:
            raise Exception("[Constructor] "\
                            "Constructor.setup() は一度しか呼び出せません.")
        #End if
        # 引数を確認
        ExprCheck.check(master_gens,"matlist")
        if not maximal > 0:
            raise Exception["[Constructor] maximalには非負整数を指定してください."]
        if not equal_zero < 0.001:
            text = "[Constructor] equal_zeroが大きすぎます."
            raise Exception[text]
        #End if
        #
        # 行列計算用クラス MatCal に equal_zero を適用
        MatCal.equal_zero = equal_zero
        #
        # 生成元から群要素（行列）を取得
        # この計算では 引数チェックによる計算コストは無視できるため 念のためチェックしておく
        all_mat = MatCal.generate_group(master_gens,maximal,exprcheck=True)
        # all_mat の乗積表を取得, 念のため引数チェックもしておく
        table = MatCal.get_cayleytable(all_mat,exprcheck=True)       
        # これ以降では基本的に行列計算は不要
        #
        # 生成された群の位数
        max_order = len(all_mat)
        ExprCheck.maximal_index = max_order - 1
        # 群の要素や部分群の性質をまとめたクラス RuleBook のインスタンスを生成する
        RuleBook.locked = False
        rulebook = RuleBook(all_mat,table)
        RuleBook.locked = True
        # 逆元への対応辞書を付与
        cls.__append_inverse_dict(rulebook)
        # 共役変換表を付与
        cls.__append_conjugate_table(rulebook)
        # 約数リストを付与
        rulebook.divisor_dict = cls.get_divisor_dict(max_order)
        # 最大の群を生成して rulebook に記載
        g = rulebook.packing(frozenset([i for i in range(max_order)]),False)
        rulebook.master_group = g
        # 自明群を生成して rulebook に記載
        t = rulebook.packing(frozenset([0]),False)
        rulebook.trivial_group = t
        #
        return rulebook
    #End def
    
    ####
    #### setup() 内でのみ用いる機能
    ####
    
    # 逆元の対応辞書を作成して rulebook に付与する
    @classmethod
    def __append_inverse_dict(cls,rulebook):
        inverse_dict = dict()
        order = rulebook.max_order
        for index1 in range(order):
            for index2 in range(order):
                if rulebook.prod([index1,index2],False) == 0:
                    inverse_dict[index1] = index2
                    break
                #end if
            #End for
        #End for
        rulebook.inverse_dict = inverse_dict
    #End def

    # 共役変換表を作成して rulebook に付与する
    # [index1,index2] <==> index1 の index2 による共役
    @classmethod
    def __append_conjugate_table(cls,rulebook):
        order = rulebook.max_order
        conjugate_table = [[0 for i1 in range(order)] \
                           for i2 in range(order)]
        for index1 in range(order):
            for index2 in range(order):
                conjugate_table[index1][index2] = rulebook.prod([index2,
                          index1,rulebook.inverse_dict[index2]],False)
            #End for
        #End for
        rulebook.conjugate_table = conjugate_table
    #End def
    
    # 群の解析で便利なので, 約数リストを作成しておく
    # 約数を求める, 自明なものも含む
    @classmethod
    def get_divisor(cls,integer,exprcheck=True):
        if exprcheck: ExprCheck.check(integer,"int")
        div_max = numpy.sqrt(integer)
        div_set = set()
        div = 1
        while div <= div_max:
           quot,mod = divmod(integer,div)
           if mod == 0:
               div_set = div_set | {div,quot}
           div += 1
        #End while
        return div_set
    #End def
    # [integer] の約数を key として, 約数の tuple を値にもつ辞書を返す
    # 約数と言っているが 1 も含む (便利なので)
    # 例: 12 の約数は 12, 8, 6, 4, 3, 2, 1
    # -> { 12:(12,6,4,3,2,1), 8:(8,4,2,1), 4:(4,2,1), 3:(3,1), 2:(2,1), 1:(1) }
    @classmethod
    def get_divisor_dict(cls,integer,exprcheck=True):
        if exprcheck: ExprCheck.check(integer,"int")
        divisor_list = cls.get_divisor(integer,False)
        divisor_dict = dict()
        for integer1 in divisor_list:
            tmp_set = cls.get_divisor(integer1,False)
            divisor_dict[integer1] = tuple(sorted(list(tmp_set),reverse=True))
        #End for
        return divisor_dict
    #End def   
#End def

#### 解析結果などの画面出力制御用クラス
class Output(object):
    @classmethod
    def log(cls,text):
        print(text,end="")
    #End def
#End class

#### 引数チェック用クラス
class ExprCheck(object):
    my_int = [int,numpy.int_]
    my_num = [int,float,complex,numpy.int_,numpy.float_,numpy.complex_]
    my_mat = [numpy.ndarray]
    my_matlist = [list]  
    my_index = [int,numpy.int_]
    my_indexset = [frozenset] # 群の要素のindexの集合
    my_text = [str]
    my_group = []
    my_types = {"int":my_int,"num":my_num,"mat":my_mat,"matlist":my_matlist,
                "index":my_index,"indexset":my_indexset,"text":my_text,
                "group":my_group}
    maximal_index = None

    @classmethod
    def check(cls,expr,expected_type:str):
        if not expected_type in cls.my_types:
            text = "invalid \'expected_type\'."
            raise cls.exception(text)
        #End if
        #
        # my_groupは自分で作成したclassなので別の処理が必要       
        if expected_type == "group":
            if isinstance(expr,Group):
                return True
            else:
                text = "type(expr) must be \'%s\' but %s."\
                            % (expected_type,type(expr))
        #End if
        #
        if not type(expr) in cls.my_types[expected_type]:
            text = "type(expr) must be \'%s\' but %s."\
                        % (expected_type,type(expr))
            raise cls.exception(text)
        #End if
        if expected_type in ["int","num","text"]: return True
        if expected_type == "mat": return cls.check_mat(expr)
        if expected_type == "matlist":
            for mat in expr: cls.check_mat(mat)
            return True
        #End if
        if expected_type == "index": return cls.check_index(expr)
        #End if
        if expected_type == "indexset":
            for index in expr: cls.check_index(index)
            return True
        #End if
        #
        return True
    #End def   
    
    @classmethod
    def check_mat(cls,expr):
        if expr.ndim != 2:
            text = "invalid dimension of matrix."
            raise cls.exception(text)
        #End if
        if expr.shape[0] != expr.shape[1]:
            text = "invalid shape of matrix."
            raise cls.exception(text)
        #End if
        if not expr.dtype in cls.my_num:
            text = "invalid type of matrix element."
            raise cls.exception(text)
        #End if
        return True
    #End def
    
    @classmethod
    def check_index(cls,expr):
        if cls.maximal_index is None:
            text = "maximal_index has not been defined."
            raise cls.exception(text)
        #End if
        if not type(expr) in cls.my_index:
            text = "invalid type of index."\
            " -> type(%s) = %s" % (expr,type(expr))
            raise cls.exception(text)
        #End if
        if not (0 <= expr <= cls.maximal_index):
            text = "invalid number of index."
            raise cls.exception(text)
        #End if
        return True
    #End def
    
    @staticmethod
    def exception(text):
        return Exception("[ExprCheck] " + text)
    #End def
#End class



# 行列計算を必要とする機能をまとめたクラス
class MatCal(object):
    # this value is defined automatically by construction()
    equal_zero = None
    
    #### [num] == 0 を判定
    @classmethod
    def is_zero_num(cls,num,exprcheck=True) -> bool:
        if exprcheck: ExprCheck.check(num,"num")
        n_zero = cls.equal_zero
        if (abs(num.real) > n_zero or abs(num.imag) > n_zero):
            return False
        else:
            return True
        #End if
    #End def
    
    #### [mat] == 0 (零行列) を判定
    @classmethod
    def is_zero_mat(cls,mat,exprcheck=True) -> bool:
        if exprcheck: ExprCheck.check(mat,"mat")
        dim_mat = mat.shape
        for i1 in range(dim_mat[0]):
            for i2 in range(dim_mat[1]):
                if not cls.is_zero_num(mat[i1,i2],False):
                    return False
                #End if
            #End for
        return True
    #End def
    
    @classmethod
    #### 複数の行列の積を計算
    def mat_multi_prod(cls,matlist,exprcheck=True):
        if exprcheck: ExprCheck.check(matlist,"matlist")
        if len(matlist)==0:
            raise Exception("[mat_prod] ERROR: invalid list.")
        #End if
        mat_prod = numpy.identity(matlist[0].shape[0])
        for mat in matlist:
            mat_prod = numpy.dot(mat_prod,mat)
        #End for
        return mat_prod
    #End def
    
    @classmethod
    #### [mat] が [matlist] に含まれているか判別
    def is_mat_in_matlist(cls,mat,matlist,exprcheck=True):
        if exprcheck: ExprCheck.check(mat,"mat")
        if exprcheck: ExprCheck.check(matlist,"matlist")
        for mat1 in matlist:
            if cls.is_zero_mat(mat-mat1,False):
                return True
            #End if
        #End for
        return False
    #End def
 
    @classmethod
    #### [matlist] を生成系として群を作成
    # 要素数が基準を超える場合には例外発生
    def generate_group(cls,generators,maximal,exprcheck=True):
        if exprcheck: ExprCheck.check(generators,"matlist")
        if exprcheck: ExprCheck.check(maximal,"int")
        n_gen = len(generators)
        Output.log("%d個の生成元から群を生成\n" % n_gen)
        identity = numpy.identity(generators[0].shape[0])
        # 行列式が 0 の行列が含まれる場合はエラー
        # 生成元に単位元が入っている場合には単位元を除外
        gen_list = []
        for gen in generators:
            det = numpy.linalg.det(gen)
            if cls.is_zero_num(det,False): 
                raise Exception("行列式が 0 の行列が含まれています.")
            if cls.is_zero_mat(identity-gen,False): continue
            gen_list.append(gen)
        #End for
        if len(gen_list) == 0: raise Exception("自明群です.")
        # 単位元は必ず先頭に入れる
        element_all = [identity] + gen_list
        element_prev = gen_list[:]
        element_new = []
        n_all = len(element_all)
        n_prev = len(element_prev)
        loop = 0
        while n_prev != 0:
            if n_all > maximal:
                text = ("要素数が設定値（%d)を超えても群が閉じません." 
                       % maximal)
                raise Exception("[generate_group]"+text)
            #End if
            loop += 1
            Output.log("\r-- loop(%d): 要素数(%d)" % (loop,n_all))
            for mat in element_prev:
                for gen in gen_list:
                    new_mat = numpy.dot(mat,gen)
                    if cls.is_mat_in_matlist(new_mat,element_all,False): 
                        continue
                    #End if
                    element_new.append(new_mat)
                    element_all.append(new_mat)
                #End for
            #End for
            n_new = len(element_new)
            n_all += n_new
            element_prev = element_new[:]
            n_prev = n_new
            element_new = []
        #End while
        Output.log("　-> 完了\n")
        return element_all
    #End def
    
    #### [matlist] の乗積表を作成
    # 群が閉じていない場合は例外発生
    @classmethod
    def get_cayleytable(cls,matlist,exprcheck=True):
        if exprcheck: ExprCheck.check(matlist,"matlist")
        Output.log("乗積表を作成\n")
        n = len(matlist)
        table = numpy.zeros((n,n),dtype=numpy.int)
        check_list_column = [[False for i1 in range(n)] for i2 in range(n)]
        for i1 in range(n):
            check_list_row = [False for i2 in range(n)]
            for i2 in range(n):
                mat = numpy.dot(matlist[i1],matlist[i2])
                flag = False
                for i3 in range(n):
                    if check_list_row[i3]: continue
                    if check_list_column[i2][i3]: continue
                    if cls.is_zero_mat(mat-matlist[i3],False):
                        flag = True
                        table[i1,i2] = i3
                        check_list_row[i3] = True
                        check_list_column[i2][i3] = True
                        break
                    #End if
                #End for
                if not flag:
                    print("")
                    print(mat)
                    text = "群が閉じていないため, 乗積表を作れません."
                    raise Exception("[cayleytable]"+text)
                #End if
            #End for
            Output.log("\r-- 進捗: %d/%d" % (i1+1,n))
        #End for
        Output.log(" -> 完了\n")
        return table
    #End def
#End class

# 群の要素や部分群などの情報をまとめたクラス
# 全ての要素や最大の群に関する性質のみを記述する
# このクラスのインスタンスは Constructor.setup() によって一度だけ生成される
class RuleBook(object):
    locked = True
    def __init__(self,all_mat,table):
        if RuleBook.locked:
            raise Exception("[RuleBook] インスタンスが不正に生成されました.")
        #End if
        self.max_order = len(all_mat)
        # index と mat の対応表を作成
        index_to_mat = dict()
        for i in range(self.max_order): index_to_mat[i] = all_mat[i]
        self.index_to_mat = index_to_mat
        self.table = table
        self.group_storage = []
        self.name_to_group = dict()
        #
        # 以降の属性は Constructor.setup() 内で順次定義される
        self.inverse_dict = None
        self.conjugate_table = None
        self.divisor_dict = None
        self.master_group = None
        self.trivial_group = None
        #
    #End def
    
    #
    #### なるべく基本的な機能のみを持たせる
    #
     
    def __prod_single(self,index1,index2):
        return self.table[index1,index2]
    #End def

    def prod(self,index_list,exprcheck=True):
        if exprcheck:
            if not type(index_list) in [list,tuple]:
                raise Exception("[multi_prod] expr must be list or tuple.")
            #End if
            if len(index_list) == 0:
                raise Exception("[multi_prod] invalid expr.")
            #End if
            for index in index_list: ExprCheck.check(index,"index")
        #End if
        index_new = 0
        for index in index_list:
            index_new = self.__prod_single(index_new,index)
        #End for
        return index_new
    #End def

    def inverse(self,index,exprcheck=True):
        if exprcheck: ExprCheck.check(index,"index")
        return self.inverse_dict[index]
    #End def
    
    def conjugate(self,index1,index2,exprcheck=True):
        if exprcheck: ExprCheck.check(index1,"index")
        if exprcheck: ExprCheck.check(index2,"index")
        return self.conjugate_table[index1][index2]
    #End def
    
    def commutator(self,index1,index2,exprcheck=True):
        if exprcheck: ExprCheck.check(index1,"index")
        if exprcheck: ExprCheck.check(index2,"index")
        i1 = self.inverse(index1)
        i2 = self.inverse(index2)
        return self.prod([index1,index2,i1,i2])
    #End def
    
    #
    # 群を生成するために必要な機能
    #

    # [indexset] を生成元として新しい indexset を生成 -> "indexset"
    def get_closure(self,indexset,exprcheck=True):
        if exprcheck: ExprCheck.check(indexset,"indexset")
        if len(indexset) == 0: return frozenset()
        # 部分群の位数は元の群の位数の約数である
        nontrivial_div = self.divisor_dict[self.max_order]
        n_max = nontrivial_div[0]
        #
        generated = set(indexset)
        element_prev = list(indexset)
        element_new = []
        n_prev = len(element_prev)
        n_all = n_prev
        while n_prev != 0:
            for index1 in element_prev:
                for index2 in indexset:
                    index3 = self.prod([index1,index2],False)
                    if not index3 in generated:
                        element_new.append(index3)
                        generated.add(index3)
                    #End if
                #End for
            #End for
            element_prev = element_new[:]
            n_prev = len(element_prev)
            n_all += n_prev
            if n_all > n_max: return self.master_group.element
            element_new = []
        #End while
        return frozenset(generated)
    #End def

    # [indexset] が閉じているか判別 -> bool
    def is_closed(self,indexset,exprcheck=True) -> bool:
        if exprcheck: ExprCheck.check(indexset,"indexset")
        closure = self.get_closure(indexset,False)
        return (True if (len(closure) == len(indexset)) else False)
    #End def  

    # [indexset] が閉じている場合に "group" を構成 -> "group"
    # 閉じていないと エラー: 原理的に閉じているべき計算でエラーが出るとバグに気付ける
    # Group() インスタンスの生成は本質的にこの関数のみ
    def packing(self,indexset,exprcheck=True):
        if exprcheck:
            ExprCheck.check(indexset,"indexset")
            if not self.is_closed(indexset,False):
                raise Exception("[indexset]は閉じていません.")
            #End if
        #End if
        # 同一の群は一度しか生成させない
        for group in self.group_storage:
            if indexset == group._element:
                return group
            #End if
        #End for
        # 群を生成して group_storage に追加する
        Group.locked = False
        group = Group(self,indexset)
        Group.locked = True
        # group_id がずれている場合, プログラムのどこかで不正に "group" が作成されている
        if ((group.group_id + 1) != len(self.group_storage)):
            raise Exception("[RuleBook] Group のインスタンスが"\
                            "予期しない方法で生成されています.")
        #
        return group
    #End def

    # [indexset] を生成元として群を生成し "group" を構成 -> "group"
    def generate_group(self,indexset,exprcheck=True):
        if exprcheck: ExprCheck.check(indexset,"indexset")
        closure = self.get_closure(indexset,False)
        return self.packing(closure,False)
    #End def

    #
    # 生成された群の検索に関する機能
    #

    # [name] を .name に持つ group を返す
    # 存在しない場合には None
    def search_name(self,name,exprcheck=True):
        if exprcheck: ExprCheck.check(name,"text")
        for group in self.group_storage:
            if group._name == name: return group
        #End for
        return None
    #End def
    
    # grouplist を位数の昇順/降順にソート -> tuple(group1,group2,...)
    def sort_grouplist(self,grouplist,ordering="descend"):
        n = len(grouplist)
        tmp_dict = dict()
        for i in range(n): tmp_dict[i] = grouplist[i]
        tmp_list = [[grouplist[i].order(),i] for i in range(n)]
        reverse_flag = (True if ordering == "descend" else False)
        tmp_list.sort(reverse=reverse_flag)
        return tuple(tmp_dict[tmp_list[i][1]] for i in range(n))
    #End def
    
#End class

# このクラスのインスタンスは RuleBook.packing() によってのみ生成される
# 群の重複判定は RuleBook.packing() が行う
class Group(object):
    locked = True
    group_count = 0
    def __init__(self,rulebook,indexset):
        if Group.locked:
            raise Exception("[Group] インスタンスの不正な生成が行われました.")
        #End if
        #
        self.rulebook = rulebook
        self.group_id = Group.group_count
        self._name = ("g%d" % self.group_id)
        self.rulebook.group_storage.append(self)
        self.rulebook.name_to_group[self._name] = self
        Group.group_count += 1
        #
        self._element = indexset
        self._order = len(self._element)
        #
        # 以降は群の性質が判明したら追加される
        #
        self._subtable = None
        self._conjugacy_data = None
        self._conjugacy_count = None
        self._center = None
        self._centrizer = None
        self._normalizer = None
        self._derived = None
        self._derived_series = None
        self._is_abelian = None
        self._is_perfect = None
        self._is_solvable = None
        self._all_normalsub = None
        self._is_simple = None
        self._all_subgroup = None
        self._symbol = None
        #
        #
        if self._order == 1: self.__for_trivial()
        #
    #End def

    # インスタンスが呼び出されたら group._element を print する
    # この機能は 変更/削除 しても よい
    def __call__(self):
        print(sorted(list(self.element())))
    #End def

    # インスタンスが print() で呼び出されたら str(group.name) を返す
    # この機能は 変更/削除 しても よい
    def __str__(self):
        return self.name()
    #End def

    #
    # 念のため
    #
    
    # 単位元の index
    def identity_index(self):
        return 0
    #End def

    # 自明群の性質で 最初から追加しておくもの
    def __for_trivial(self):
        self._symbol = "Z(1)"
    #End def



    #
    # rulebook に機能を委譲
    #
    # index の演算
    def prod(self,index_list,exprcheck=True):
        return self.rulebook.prod(index_list,exprcheck)
    def conjugate(self,index1,index2,exprcheck=True):
        return self.rulebook.conjugate(index1,index2,exprcheck)
    def commutator(self,index1,index2,exprcheck=True):
        return self.rulebook.commutator(index1,index2,exprcheck)
    # 群の取得
    def master(self):
        return self.rulebook.master_group
    def trivial(self):
        return self.rulebook.trivial_group
    #
    def my_divisor(self):
        return self.rulebook.divisor_dict[self.order()]
    #
    def get_closure(self,indexset,exprcheck=True):
        return self.rulebook.get_closure(indexset,exprcheck)
    def packing(self,indexset,exprcheck=True):
        return self.rulebook.packing(indexset,exprcheck)
    def generate_group(self,indexset,exprcheck=True):
        return self.rulebook.generate_group(indexset,exprcheck)
    def sort_grouplist(self,grouplist,ordering="descend"):
        return self.rulebook.sort_grouplist(grouplist,ordering)

    #
    # クラスの内外問わず, インスタンス変数にアクセスする場合には必ず以下の関数を介すること
    # 直接インスタンス変数にアクセスできるのは, 最も基本的な関数一つのみ
    #

    ####
    #### 自身のみで完結する機能
    ####

    #### ._name にアクセス
    def name(self):
        return self._name
    #End def
        
    #### ._name にアクセス
    # ._name を [newname] に変更する -> bool
    # [newname] が既に使われている場合には 変更しない
    # ルール: 先頭は 英字, それ以外は 英数字とアンダースコアのみ可能
    # 先頭の禁止文字を設定
    def rename(self,newname,exprcheck=True):
        if exprcheck: ExprCheck.check(newname,"text")
        #
        # 先頭の禁止文字
        list1 = list("ABCDEFGHIJKLMNOPQRSTUVWXYZg")
        #
        if self.rulebook.search_name(newname,False) is not None:
            result = ("変更失敗: [%s]は既に使用されています.\n" % newname)
            Output.log(result)
            return False
        #End if
        #
        # ルールを適用
        available = True
        if newname[0] in list1: available = False
        if not newname[0].isalpha(): available = False
        str_list = newname.split("_")
        for i in str_list:
            if not i.isalnum(): available = False
        #End for
        if not available:
            result = ("変更失敗: 名前は 先頭文字は(gを除く英小文字,日本語),"\
                      " その他は(英数字,日本語,アンダースコア) としてください.\n")
            Output.log(result)
            return False
        #End if
        #
        result = ("部分群の名前を変更: [%s] -> [%s]\n" % (self._name,newname))
        del self.rulebook.name_to_group[self._name]
        self._name = newname
        self.rulebook.name_to_group[newname] = self
        Output.log(result)
        return True
    #End def
    
    #### ._order にアクセス
    def order(self):
        return self._order
    #End def
    
    #### ._element にアクセス
    def element(self):
        return self._element
    #End def

    #### ._subtable にアクセス
    # 全体の乗積表から 部分群の乗積表を抽出 -> np.ndarray
    def subtable(self):
        if self._subtable is not None: return self._subtable
        #
        table = self.rulebook.table
        translator = sorted(list(self.element()))
        subtable = numpy.zeros((self.order(),self.order()),dtype=numpy.int)
        for subindex1 in range(self.order()):
            index1 = translator[subindex1]
            for subindex2 in range(self.order()):
                index2 = translator[subindex2]
                new = table[index1,index2]
                subtable[subindex1,subindex2] = new
            #End for
        #End for
        #
        self._subtable = subtable
        return self._subtable
    #end def
    
    #### ._conjugacy_data にアクセス
    # 共役類を取得し, 共役類と位数をまとめたデータセットを返す
    # -> tuple( (位数1,共役類1),(位数2,共役類2),... )
    # 位数の昇順 -> 要素数の昇順 にソートされている
    def conjugacy_data(self):
        if self._conjugacy_data is not None: return self._conjugacy_data
        #
        # 共役類の作成
        conjugacyclass = []
        remaining = set(self.element())
        while len(remaining) != 0:
            conjugacy = set()
            index = list(remaining)[0]
            # 共役類を決定
            for index1 in self.element():
                conjugacy.add(self.conjugate(index,index1,False))
            #End for
            conjugacy = frozenset(conjugacy)
            conjugacyclass.append(conjugacy)
            remaining = remaining - conjugacy
        #End while
        conjugacyclass = tuple(conjugacyclass)
        #
        # データセットの作成
        conjugacy_data = []
        for conjugacy in conjugacyclass:
            index = list(conjugacy)[0]
            order = 1
            tmp_index = index
            while tmp_index != 0:
                order+= 1
                tmp_index = self.prod([tmp_index,index],False)
            #End while
            conjugacy_data.append((order,conjugacy))
        #End for
        tmp_data = conjugacy_data[:]
        divisor_list = sorted(list(self.my_divisor()))
        conjugacy_data = []
        # ソート
        for integer1 in divisor_list:
            for integer2 in divisor_list:
                for i in range(len(tmp_data)):
                    if integer1 == tmp_data[i][0]:
                        if integer2 == len(tmp_data[i][1]):
                            conjugacy_data.append(tmp_data[i])
                        #End if
                    #End if
                #End for
            #End for
        #End for
        #
        self._conjugacy_data = tuple(conjugacy_data)
        return self._conjugacy_data
    #End def

    #### ._conjugacy_count にアクセス
    # 共役類の (位数,要素数,重複) の組を取得
    # 位数 > 要素数 の優先順で昇順にソートされている
    def conjugacy_count(self):
        if self._conjugacy_count is not None: return self._conjugacy_count
        #
        conjugacy_label = []
        for data in self.conjugacy_data():
            conjugacy_label.append((data[0],len(data[1])))
        #End for
        conjugacy_count = []
        while len(conjugacy_label) !=0:
            next_list = []
            count = 0
            label = conjugacy_label[0]
            for i in range(len(conjugacy_label)):
                if conjugacy_label[i] != label:
                    next_list.append(conjugacy_label[i])
                else:
                    count += 1
                #End if
            #End for
            conjugacy_count.append((label[0],label[1],count))
            conjugacy_label = next_list[:]
        #End while
        # ソート
        divisor_list = sorted(list(self.my_divisor()))
        sorted_list = []
        for i1 in divisor_list:
            for i2 in divisor_list:
                for count in conjugacy_count:
                    if (count[0] == i1 and count[1] == i2):
                        sorted_list.append(count)
                    #End if
                #End for
            #End for
        #End for
        conjugacy_count = tuple(sorted_list)
        #
        self._conjugacy_count = conjugacy_count
        return self._conjugacy_count
    #End for

    #### ._center にアクセス
    # 中心を返す
    def center(self):
        if self._center is not None: return self._center
        #
        center = set()
        for index1 in self.element():
            commutable = True
            for index2 in self.element():
                commutator = self.commutator(index1,index2,False)
                if commutator != 0:
                    commutable = False
                    continue
                #End if
            #End for
            if commutable: center.add(index1)
        #End for
        self._center = self.packing(center,False)
        return self._center
    #End def

    #### ._centrizer にアクセス
    # 中心化群を返す
    def centrizer(self):
        if self._centrizer is not None: return self._centrizer
        #
        index_list = []
        for index1 in self.master().element():
            flag = True
            for index2 in self.element():
                commutator = self.commutator(index1,index2,False)
                if not commutator == self.identity_index():
                    flag = False
                    break
                #End if
            #End for
            if flag: index_list.append(index1)
        #End for
        centrizer = self.packing(frozenset(index_list),False)
        #
        self._centrizer = centrizer
        return self._centrizer
    #End def
    
    #### ._normalizer にアクセス
    # 正規化群を返す
    def normalizer(self):
        if self._normalizer is not None: return self._normalizer
        #
        index_list = []
        for index1 in self.master().element():
            flag = True
            for index2 in self.element():
                conjugated = self.conjugate(index2,index1,False)
                if not conjugated in self.element():
                    flag = False
                    break
                #End if
            #End for
            if flag: index_list.append(index1)
        #End for
        normalizer = self.packing(frozenset(index_list),False)
        #
        self._normalizer = normalizer
        return self._normalizer
    #End def
    
    #### ._derived にアクセス
    # 導来部分群を返す
    def derived(self):
        if self._derived is not None: return self._derived
        #
        index_set = set()
        for index1 in self.element():
            for index2 in self.element():
                index_set.add(self.commutator(index1,index2,False))
            #End for
        #End for
        derived = self.packing(frozenset(index_set),False) 
        #
        self._derived = derived
        return self._derived
    #End def
    
    #### ._derived_series にアクセス
    # 導来列を返す -> (一次導来群, 二次導来群, ...)
    def derived_series(self):
        if self._derived_series is not None: return self._derived_series
        #
        derived_series = []
        group = self
        while True:
            derived = group.derived()
            derived_series.append(derived)
            if derived in [group,group.trivial()]: break
            group = derived
        #End while
        derived_series = tuple(derived_series)
        #
        self._derived_series = derived_series
        return self._derived_series
    #End def

    #### .is_abelian(self) にアクセス
    # 可換群であるか判定 -> bool
    def is_abelian(self):
        if self._is_abelian is not None: return self._is_abelian
        #
        # 導来群が自明群 <==> 可換群
        is_abelian = (True if self.derived() == self.trivial() else False)
        #
        self._is_abelian = is_abelian
        return self._is_abelian
    #End def

    #### ._is_perfect にアクセス
    # 完全群であるか判定 -> bool
    def is_perfect(self):
        if self._is_perfect is not None: return self._is_perfect
        #
        # 導来群が自分自身 <==> 完全群
        is_perfect = (True if self.derived() == self else False)
        #
        self._is_perfect = is_perfect
        return self._is_perfect
    #End def
    
    #### ._is_solvable にアクセス
    # 可解群であるか判定 -> bool
    def is_solvable(self):
        if self._is_solvable is not None: return self._is_solvable
        #
        # 導来群が自明群で終わる <==> 可解群
        if self.derived_series()[-1] == self.trivial(): is_solvable = True
        else: is_solvable = False
        #
        self._is_solvable = is_solvable
        return self._is_solvable
    #End def
    
    #### ._all_normalsub にアクセス
    # 全ての正規部分群を生成 -> tuple(group,group2,...)
    # 自明な正規部分群も含み, 位数の大きい順にソートされている
    def all_normalsub(self):
        if self._all_normalsub is not None: return self._all_normalsub
        #
        # 自明な正規部分群
        t_groupset = set([self.trivial(),self])
        # 非自明な約数の最大値
        # 位数が 1,素数 のとき maximal = 1
        maximal = sorted(list(self.my_divisor()))[-1]
        #
        # 位数が 1,素数 の群は自明な正規部分群のみを持つ
        if maximal == 1:
            all_normalsub = self.__sort_grouplist(tuple(t_groupset),"descend")
            #
            self._all_normalsub = all_normalsub
            return self._all_normalsub
        #End if
        #
        conjugacyclass = []
        for data in self.conjugacy_data(): conjugacyclass.append(data[1])
        normalsub_set = set([self.trivial().element(),self.element()])
        # 非自明な部分群の生成系（群）を取得
        seed = set()
        for conjugacy in conjugacyclass:
            # 共役類の要素数が maximal なら closure は元の群全体
            if len(conjugacy) == maximal: continue
            closure = self.get_closure(conjugacy,False)
            normalsub_set.add(closure)
            # closure が自明な部分群, または　その位数が maximal のとき,
            # closure は非自明な部分群の生成系にはならない
            if (1 < len(closure) < maximal): seed.add(closure)
        #End for
        # closureの和集合を生成系として正規部分群を生成
        # generate_group と同じ手法で全ての正規部分群を生成する
        seed = list(seed)
        normalsub_all = normalsub_set        
        normalsub_prev = seed[:]
        normalsub_new = []
        n_prev = normalsub_prev
        loop = 0
        while n_prev != 0:
            loop += 1
            for normalsub1 in normalsub_prev:
                for normalsub2 in seed:
                    if normalsub1 <= normalsub2: continue
                    if normalsub1 >= normalsub2: continue
                    closure = self.get_closure(normalsub1 | normalsub2,False)
                    if len(closure) == self.order(): continue
                    if closure in normalsub_all: continue
                    normalsub_new.append(closure)
                    normalsub_all.add(closure)
                #End for
            #End for
            n_new = len(normalsub_new)
            normalsub_prev = normalsub_new[:]
            n_prev = n_new
            normalsub_new = []
        #End while
        # 正規部分群の生成完了
        groupset = set()
        for indexset in normalsub_all:
            groupset.add(self.packing(indexset,False))
        #End for
        all_normalsub = self.sort_grouplist(tuple(groupset),"descend")
        #
        self._all_normalsub = all_normalsub
        return self._all_normalsub
    #End def
    
    #### ._is_simple にアクセス
    # 単純群であるか判定 -> bool
    def is_simple(self):
        if self._is_simple is not None: return self._is_simple
        #
        # 可換群は正規部分群が多いため, 全ての正規部分群の生成には時間がかかる
        # 可換群は位数が素数なら単純群, 素数でなければ単純群でない
        if self.is_abelian():
            is_simple = (True if len(self.my_divisor()) in [1,2] else False)
            #
            self._is_simple = is_simple
            return self._is_simple
        #End if
        #
        # 非可換群は全ての正規部分群を生成する
        all_normalsub = self.all_normalsub()
        is_simple = (True if len(all_normalsub) in [0,1] else False)
        #
        self._is_simple = is_simple
        return self._is_simple
    #def
    
    #### ._all_subgroup にアクセス
    # 全ての部分集合を生成する -> tuple("group")
    # 位数の大きい順にソートされている
    # 生成した部分群の数が [n_max] に達したら強制中断
    def all_subgroup(self,n_max=200):
        if self._all_subgroup is not None: return self._all_subgroup
        #
        Output.log("%sの全ての部分群を生成します.\n" % self.name())
        # 自明な部分群
        trivial_indexset = set([frozenset([0]),self.element()])
        trivial_groupset = set([self.trivial(),self])
        # 群の位数が素数なら, 非自明な部分群を持たない
        divisor = self.my_divisor()
        if len(divisor) in [1,2]:
            Output.log("生成完了しました.\n\n")
            all_subgroup = self.__sort_grouplist(tuple(trivial_groupset))
            #
            self._all_subgroup = all_subgroup
            return self._all_subgroup
        #End if
        # maximal = 非自明な約数の最大値
        maximal = sorted(divisor)[-2]
        subgroup_set = set() | trivial_indexset
        seed = set()
        for index in self.element():
            closure = self.get_closure(frozenset([index]),False)
            subgroup_set.add(closure)
            if not (1< len(closure) < maximal): continue
            seed.add(closure)
        #End for
        # closureの和集合を生成系として部分群を生成
        # generate_group と同じ手法で全ての部分群を生成する
        seed = list(seed)
        subgroup_all = subgroup_set        
        subgroup_prev = seed[:]
        subgroup_new = []
        n_prev = subgroup_prev
        loop = 0
        n_all = len(subgroup_all)
        while n_prev != 0:
            if n_all > n_max:
                Output.log("\n発見数が%dを超えたため, 処理を放棄します\n" % n_max)
                Output.log("-- 提案: 先に直積への分解を行う\n")
                Output.log("-- 提案: 引数(n_max)を変更する\n\n")
                return False
            #End if
            loop += 1
            for sub1 in subgroup_prev:
                for sub2 in seed:
                    if sub1 <= sub2: continue
                    if sub1 >= sub2: continue
                    closure = self.get_closure(sub1 | sub2,False)
                    if len(closure) == self.order(): continue
                    if closure in subgroup_all: continue
                    subgroup_new.append(closure)
                    subgroup_all.add(closure)
                #End for
            #End for
            n_new = len(subgroup_new)
            n_all += n_new
            Output.log("\r-- 発見数:%d" % n_all)
            subgroup_prev = subgroup_new[:]
            n_prev = n_new
            subgroup_new = []
        #End while
        Output.log(" -> 完了\n")
        # 生成完了
        grouplist = []
        count = 0
        for indexset in subgroup_all:
            count += 1
            grouplist.append(self.packing(indexset,False))
            Output.log("\r-- 群として構成中: %d/%d" % (count,n_all))
        #End for
        Output.log(" -> 完了\n")
        Output.log("全ての部分群を生成しました.\n\n")
        #
        all_subgroup = self.sort_grouplist(grouplist)
        #
        self._all_subgroup = all_subgroup
        return self._all_subgroup
    #End def
 
    #### ._symbol にアクセス
    def symbol(self):
        return self._symbol
    #End def
    def set_symbol(self,symbol,exprcheck=True):
        if exprcheck: ExprCheck.check(symbol,"text")
        self._symbol = symbol
        return True
    #End def
       
    ####
    #### 引数に group をとる機能
    ####

    # [group] の部分群であるか判定 -> bool
    def is_subgroup_of(self,group,exprcheck=True):
        if exprcheck: ExprCheck.check(group,"group")
        return self.element().issubset(group.element())
    #End def 
    
    # [group] の正規部分群であるか判定 -> bool
    # 自明な場合も True
    # 共役変換で閉じるかを確認している (all_normalsub を経由しない)
    def is_normalsub_of(self,group,exprcheck=True):
        if exprcheck: ExprCheck.check(group,"group")
        if not self.is_subgroup_of(group,False): return False
        diff = group.element() - self.element()
        for index1 in self.element():
            for index2 in diff:
                if not self.conjugate(index1,index2) in self.element():
                    return False
                #End if
            #End for
        #End for
        return True
    #End def

    # [group] とのデカルト積が群をなすか,
    # なす場合には 直積, 右半直積, 左半直積のいずれであるか を判定
    def try_cartesian_product(self,group,exprcheck=True):
        if exprcheck: ExprCheck.check(group,"group")
        # 位数の積がmaster群の位数の約数であるか
        order_list = self.master().my_divisor()
        if not (self.order() * group.order()) in order_list:
            return "False",None
        #End if
        # 共通部分が自明であるか
        if not len(self.element() & group.element()) == 1:
            return "False",None
        #End if
        # デカルト積を取得
        product = set()
        for index1 in self.element():
            for index2 in group.element():
                product.add(self.prod([index1,index2],False))
            #End for
        #End for
        # デカルト積が群をなすか
        generated = self.generate_group(frozenset(product),False)
        if not product == generated.element():
            return "False",None
        #End if
        # ここまでを満たすと直積/半直積である
        kind = {(True,True):"times",(True,False):"Rtimes",
                (False,True):"Ltimes",(False,False):"False"}
        right = self.is_normalsub_of(generated,False)
        left = group.is_normalsub_of(generated,False)
        # 積の種類を generated に保存
        return  kind[(right,left)],generated
    #End def
    
    # [group] と剰余群 [self]/[group] の半直積として分解できるか調べる
    # ただし, 直積分解可能な場合でも, 直積を優先することはない
    # -> 剰余群
    # 分解不可能な場合は -> None, 自明な場合も None
    # 半直積の分解は一意的でないため, 一つの方法のみを返す (群同型の意味では一意的)
    # index の番号の小さい要素を優先的に選択する
    def try_quotient_decomposition(self,group):
        # 単純群は分解不可能
        if self.is_simple(): return None
        # 正規部分群でなければ分解不可能, 自明な場合は除外する
        if not group in self.all_normalsub()[1:-1]: return None
        #
        candidate = set(self.element() - group.element())
        selected = set()
        while len(candidate) != 0:
            generated = set()
            index = sorted(list(candidate))[0]
            candidate.discard(index)
            selected_dummy = frozenset(selected | set([index]))
            closure = self.get_closure(selected_dummy,False)
            if len(closure.intersection(group.element())) != 1: continue
            for index1 in closure:
                for index2 in group.element():
                    new = self.prod([index1,index2],False)
                    generated.add(new)
                #End for
            #End for
            candidate = candidate - generated
            selected.add(index)
        #End while
        closure = self.get_closure(frozenset(selected),False)
        if len(closure)*group.order() != self.order(): return None
        return self.packing(closure,False)
    #End def

    # self における [group] を法とした 左/右 ([side]) 剰余類を返す
    # -> (side,法,代表元のリスト)
    # self > [group] でなければエラー (自明な部分群は可能)
    # 代表元は index の数字が小さい順に選択
    def coset(self,group,side="left",exprcheck=True):
        if exprcheck: ExprCheck.check(group,"group")
        if not group.is_subgroup_of(self,False):
            raise Exception("[Group.coset] ERROR: 部分群が正しく指定されていません.")
        #End if
        #
        residue_class = []
        remaining = set(self.element())
        while len(remaining) != 0:
            same_class = set()
            index1 = list(remaining)[0]
            for index2 in group.element():
                if side == "right": new = self.prod([index2,index1],False)
                else: new = self.prod([index1,index2],False)
                same_class.add(new)
            #End for
            remaining = remaining - same_class
            residue_class.append(sorted(list(same_class))[0])
        #End while
        #
        return (side,group,sorted(residue_class))
    #End def
    
    # 剰余群を生成
    def generate_quotient(self,group,exprcheck=True):
        if exprcheck: ExprCheck.check(group,"group")
        if not group.is_normalsub_of(self,False):
            message = "[Group.generate_quotient] ERROR: "\
            +"正規部分群が正しく指定されていません."
            raise Exception(message)
        #End if
        residue_class = self.coset(group,"left",False)[2]
        return Quotient(self,group,residue_class)
    #End def
#End class

# 剰余群
class Quotient(object):
    def __init__(self,group1,group2,indexlist):
        rulebook = group1.rulebook
        self.origin = group1
        self.modulo = group2
        self.residue = tuple(indexlist)
        self.order = len(self.residue)
        index_to_residue = dict()
        for index1 in indexlist:
            for index2 in group2.element():
                new = rulebook.prod([index1,index2])
                index_to_residue[new] = index1
            #End for
        #End for
        self.index_to_residue = index_to_residue
        subtable = numpy.zeros((self.order,self.order),dtype=numpy.int)
        for i1 in range(self.order):
            index1 = self.residue[i1]
            for i2 in range(self.order):
                index2 = self.residue[i2]
                new = rulebook.prod([index1,index2])
                residue = self.index_to_residue[new]
                subtable[i1][i2] = residue
            #End for
        #End for
        self.subtable = subtable
    #End def
#End class




# 数学的には一意的でない結果を与える機能
class Exam(object):
    
    ####
    #### 群の生成元を与える
    ####
    
    @classmethod
    def generator(cls,group):
        rulebook = group.rulebook
        gens = []
        candidate = sorted(list(group.element() - set([0])))
        while len(candidate)!=0:
            index = candidate.pop(0)
            gens.append(index)
            generated = rulebook.generate_group(frozenset(gens),False)
            if generated == group: break
        #End while
        # 生成元の冗長性を排除
        gens_dummy = gens[:]
        flag = True
        while flag:
            for i in range(len(gens)):
                flag = False
                gens_dummy = gens[:]
                gens_dummy.pop(i)
                generated = rulebook.generate_group(frozenset(gens_dummy),
                                                    False)
                if generated == group:
                    flag = True
                    gens = gens_dummy[:]
                    break
                #End if
            #End for
        #End while
        #
        return gens
    #End def
    
    
    ####
    #### 可換群を完全に分解
    ####

    # 素因数分解
    @classmethod
    def prime_factorize(cls,n):
        prime_list = []
        while (n % 2 == 0):
            prime_list.append(2)
            n //= 2
        #End while
        f = 3
        while (f * f <= n):
            if (n % f == 0):
                prime_list.append(f)
                n //= f
            else:
                f += 2
        #End if
        if n != 1: prime_list.append(n)
        return collections.Counter(prime_list)
    #End def
    
    #### ._symbol にアクセス
    # 可換群の直積分解
    # アーベルの基本定理 -> 有限可換群は 素数の自然数冪の位数の巡回群の直積と同型である
    # 分解は要素としては一意的でないが, 群同型の意味では一意的である
    # ここでは, 最も細かい直積分解の一つの方法を与える
    # -> tuple(group1,group2,...) 位数の大きい順にソート
    # 分解不可能な場合には -> tuple(self)
    @classmethod
    def dp_abelian(cls,group):
        rulebook = group.rulebook
        if not group.is_abelian():
            raise Exception("不正な操作: 可換群ではありません")
        #End if
        # アルゴリズム上, 自明群は省いておく必要がある
        # 可換群は正規部分群の探索に時間がかかるので, 単純群であるかの判定はしない
        if group == group.trivial(): return (group,)
        #
        remaining = [group]
        #
        # 要素の order の最大値より大きな位数の巡回群は出ない
        # -> orderの最大値 max_order で分解できる
        flag = True
        while flag:
            flag = False
            new_remaining = []
            for group1 in remaining:
                max_order = group1.conjugacy_data()[-1][0]
                # max_order == 位数　なら何もしない
                if max_order == group1.order():
                    new_remaining.append(group1)
                    continue
                #End if
                # max_order を持つ要素を任意に一つ選び,
                # G1(max_order) times (残り) とできるような　G1 が存在する
                conjugacy_data = group1.conjugacy_data()
                highest_conjugacy = conjugacy_data[-1][1]
                index = list(highest_conjugacy)[0]
                group2 = rulebook.generate_group(frozenset([index]),False)
                group3 = cls.__for_abelian_decompose(group1,group2)
                new_remaining = new_remaining + [group2,group3]
                flag = True
            #End for
            remaining = new_remaining[:]
        #End while
        #
        # この段階では, 位数 = max_order
        # 位数を素因数分解して, N = p^n * q^m * ...
        # G(n) = G1(p^n) times G2(q^n) times ...　とできる
        flag = True
        while flag:
            flag = False
            new_remaining = []
            for group1 in remaining:
                factor_dict = cls.prime_factorize(group1.order())
                prime_list = list(factor_dict.keys())
                # 念のため, エラーチェック
                if len(prime_list) == 0: raise Exception("[Classifier] ERROR:")
                # 単一の素数冪なら何もしない
                if len(prime_list) == 1:
                    new_remaining.append(group1)
                    continue
                #End if
                prime = prime_list[0]
                max_power = factor_dict[prime]
                power = max_power
                conjugacy_data = group1.conjugacy_data()
                flag = False
                while power != 0:
                    n_order = prime ** power
                    for data in conjugacy_data:
                        if data[0] == n_order:
                            index = list(data[1])[0]
                            flag = True
                            break
                        #End if
                    #End for
                    if flag: break
                    else: power -= 1
                #End while
                if not flag: raise Exception("[Classifier] ERROR:")
                group2 = rulebook.generate_group(frozenset([index]),False)
                group3 = cls.__for_abelian_decompose(group1,group2)
                new_remaining = new_remaining + [group2,group3]
                flag = False
            #End for
            remaining = new_remaining[:]
        #End while
        factor = tuple(remaining)
        # 分解完了
        factor = rulebook.sort_grouplist(factor,"descend")
        # ._symbol を付与
        tot_symbol = ""
        for group1 in factor:
            group1.set_symbol("Z(%d)" % group1.order())
            tot_symbol = tot_symbol + group1._symbol + " x "
        #End for
        tot_symbol = tot_symbol[:-3]
        group.set_symbol(tot_symbol)
        #
        return tuple(factor)
    #End def
    # 可換群限定, [group1] を [group2] times group とするような group を見つける
    @classmethod
    def __for_abelian_decompose(cls,group1,group2):
        rulebook = group1.rulebook
        candidate = set(group1.element()) - set(group2.element())
        gens = []
        group3 = None
        while len(candidate) != 0:           
            copy_candidate = list(candidate)
            for index in copy_candidate:
                gens_tmp = gens[:]
                gens_tmp.append(index)
                generated = rulebook.generate_group(frozenset(gens_tmp),
                                                        False)
                if len(group2.element() & generated.element()) != 1:
                    candidate.discard(index)
                else:
                    break
                #End if
            #End for
            gens = gens_tmp[:]
            candidate = candidate - generated.element()
            
            if group1.order() == group2.order() * generated.order():
                group3 = generated
                break
            #End if
        #End while
        if group3 is None:
            raise Exception("[Classifier] ERROR __for_abelian_decompose()")
        #End if
        return group3
    #End def    
#End class

class Classifier(object):    
    
    @classmethod
    def search_isomorphic(cls,group,exprcheck=True):
        if exprcheck: ExprCheck.check(group,"group")
        if group.symbol() is not None: return group.symbol()
        if group.is_abelian():
            Exam.dp_abelian(group)
            return group.symbol()
        else:
            flag = cls.identify_non_abelian(group)
            if flag: return group.symbol()
            else: return None
        #End if
    #End def
    
    # 非可換群の位数ごとの conjugacy_count
    # (確定)ならば, 非可換群ならば必ずいずれかと同型となる
    # (候補)ならば, 他の候補が存在する (分解など)
    conj_dict = dict()
    
    #### 6 -> (確定): D3
    D3 = ((1, 1, 1), (2, 3, 1), (3, 2, 1))
    conj_dict[6] = (
            [D3,"D(3)"],)
    
    #### 8 -> (確定): Q4, D4
    D4 = ((1, 1, 1), (2, 1, 1), (2, 2, 2), (4, 2, 1))
    Q4 = ((1, 1, 1), (2, 1, 1), (4, 2, 3))
    conj_dict[8] = (
            [D4,"D(4)"],
            [Q4,"Q(4)"])
    
    #### 10 -> (確定) D5
    D5 = ((1, 1, 1), (2, 5, 1), (5, 2, 2))
    conj_dict[10] = (
            [D5,"D(5)"],)
    
    #### 12 -> (確定): D6, Q6, A4
    D6 = ((1, 1, 1), (2, 1, 1), (2, 3, 2), (3, 2, 1), (6, 2, 1))
    Q6 = ((1, 1, 1), (2, 1, 1), (3, 2, 1), (4, 3, 2), (6, 2, 1))
    A4  = ((1, 1, 1), (2, 3, 1), (3, 4, 2))
    conj_dict[12] = (
            [D6,"D(6)"],
            [Q6,"Q(6)"],
            [A4,"A(4)"])
    
    #### 14 -> (確定): D7
    D7 = ((1, 1, 1), (2, 7, 1), (7, 2, 3))
    conj_dict[14] = (
            [D7,"D(7)"],)
    
    #### 16 -> (候補): D8, Q8, 分解
    D8 = ((1, 1, 1), (2, 1, 1), (2, 4, 2), (4, 2, 1), (8, 2, 2))
    Q8 = ((1, 1, 1), (2, 1, 1), (4, 2, 1), (4, 4, 2), (8, 2, 2))
    QD16 = ((1, 1, 1), (2, 1, 1), (2, 4, 1), (4, 2, 1), (4, 4, 1), (8, 2, 2))
    conj_dict[16] = (
            [D8,"D(8)"],
            [Q8,"Q(8)"],
            [QD16,"QD(16)"])
    
    #### 18 -> (候補): D9, Sigma18
    D9 = ((1, 1, 1), (2, 9, 1), (3, 2, 1), (9, 2, 3))
    Sigma18 = ((1, 1, 1), (2, 3, 1), (3, 1, 2), (3, 2, 3), (6, 3, 2))
    conj_dict[18] = (
            [D9,"D(9)"],
            [Sigma18,"Sigma(18)"])
    
    #### 20 -> (候補): D10, Q10, 分解
    D10 = ((1, 1, 1), (2, 1, 1), (2, 5, 2), (5, 2, 2), (10, 2, 2))
    Q10 = ((1, 1, 1), (2, 1, 1), (4, 5, 2), (5, 2, 2), (10, 2, 2))
    conj_dict[20] = (
            [D10,"D(10)"],
            [Q10,"Q(10)"])
    
    #### 21 -> (候補): T7
    T7 = ((1, 1, 1), (3, 7, 2), (7, 3, 2))
    conj_dict[21] = (
            [T7,"T(7)"],)
    
    #### 22 -> (確定): D11
    D11 = ((1, 1, 1), (2, 11, 1), (11, 2, 5))
    conj_dict[22] = (
            [D11,"D(11)"],)
    
    #### 24 -> (候補): D12, Q12, S4, Tprime, Sigma24
    D12 = ((1, 1, 1), (2, 1, 1), (2, 6, 2), (3, 2, 1), (4, 2, 1), 
           (6, 2, 1), (12, 2, 2))
    Q12 = ((1, 1, 1), (2, 1, 1), (3, 2, 1), (4, 2, 1), (4, 6, 2), 
           (6, 2, 1), (12, 2, 2))
    S4 = ((1, 1, 1), (2, 3, 1), (2, 6, 1), (3, 8, 1), (4, 6, 1))
    Tprime = ((1, 1, 1), (2, 1, 1), (3, 4, 2), (4, 6, 1), (6, 4, 2))
    Sigma24 = ((1, 1, 1), (2, 1, 1), (2, 3, 2), (3, 4, 2), (6, 4, 2))
    conj_dict[24] = (
            [D12,"D(12)"],
            [Q12,"Q(12)"],
            [S4,"S(4)"],
            [Tprime,"Tprime"],
            [Sigma24,"Sigma(24)"])
    
    #### 26 -> (確定): D13
    D13 = ((1, 1, 1), (2, 13, 1), (13, 2, 6))
    conj_dict[26] = (
            [D13,"D(13)"],)
    
    #### 27 -> (候補): Delta27
    Delta27 = ((1, 1, 1), (3, 1, 2), (3, 3, 8))
    conj_dict[27] = (
            [Delta27,"Delta(27)"],)

    #### 28 -> (確定): D14, Q14
    D14 = ((1, 1, 1), (2, 1, 1), (2, 7, 2), (7, 2, 3), (14, 2, 3))
    Q14 = ((1, 1, 1), (2, 1, 1), (4, 7, 2), (7, 2, 3), (14, 2, 3))
    conj_dict[28] = (
            [D14,"D(14)"],
            [Q14,"Q(14)"])
    
    #### 30 -> (確定): D15
    D15 = ((1, 1, 1), (2, 15, 1), (3, 2, 1), (5, 2, 2), (15, 2, 4))
    conj_dict[30] = (
            [D15,"D(15)"],)
    
    ##### 32 -> (候補): D16, Q16, QD32, Sigma(32)
    D16 = ((1, 1, 1), (2, 1, 1), (2, 8, 2), (4, 2, 1), (8, 2, 2), (16, 2, 4))
    Q16 = ((1, 1, 1), (2, 1, 1), (4, 2, 1), (4, 8, 2), (8, 2, 2), (16, 2, 4))
    QD32 = ((1, 1, 1), (2, 1, 1), (2, 8, 1), (4, 2, 1), (4, 8, 1), 
            (8, 2, 2), (16, 2, 4))
    Sigma32 = ((1, 1, 1), (2, 1, 1), (2, 2, 1), (2, 4, 1), (4, 1, 2), 
               (4, 2, 5), (4, 4, 1), (8, 4, 2))
    conj_dict[32] = (
            [D16,"D(16)"],
            [Q16,"Q(16)"],
            [QD32,"QD(32)"],
            [Sigma32,"Sigma(32)"])
    
    ##### 34 -> (確定): D17
    D17 = ((1, 1, 1), (2, 17, 1), (17, 2, 8))
    conj_dict[34] = (
            [D17,"D(17)"],)
    
    ##### 36 -> (候補): D18, Q18
    D18 = ((1, 1, 1), (2, 1, 1), (2, 9, 2), (3, 2, 1), (6, 2, 1), 
           (9, 2, 3), (18, 2, 3))
    Q18 = ((1, 1, 1), (2, 1, 1), (3, 2, 1), (4, 9, 2), (6, 2, 1), 
           (9, 2, 3), (18, 2, 3))
    conj_dict[36] = (
            [D18,"D(18)"],
            [Q18,"Q(18)"])

    ##### 38 -> (確定): D19
    D19 = ((1, 1, 1), (2, 19, 1), (19, 2, 9))
    conj_dict[38] = (
            [D19,"D(19)"],)
    
    #### 39 -> (候補): T13
    T13 = ((1, 1, 1), (3, 13, 2), (13, 3, 4))
    conj_dict[39] = (
            [T13,"T(13)"],)    
    
    ##### 40 -> (候補) D20, Q20
    D20 = ((1, 1, 1), (2, 1, 1), (2, 10, 2), (4, 2, 1), (5, 2, 2), 
           (10, 2, 2), (20, 2, 4))
    Q20 = ((1, 1, 1), (2, 1, 1), (4, 2, 1), (4, 10, 2), (5, 2, 2), 
           (10, 2, 2), (20, 2, 4))
    conj_dict[40] = (
            [D20,"D(20)"],
            [Q20,"Q(20)"])
    
    #### 42 -> (候補)D21
    D21 = ((1, 1, 1), (2, 21, 1), (3, 2, 1), (7, 2, 3), (21, 2, 6))
    conj_dict[42] = (
            [D21,"D(21)"],)
    
    #### 44 -> (候補) D22, Q22
    D22 = ((1, 1, 1), (2, 1, 1), (2, 11, 2), (11, 2, 5), (22, 2, 5))
    Q22 = ((1, 1, 1), (2, 1, 1), (4, 11, 2), (11, 2, 5), (22, 2, 5))
    conj_dict[44] = (
            [D22,"D(22)"],
            [Q22,"Q(22)"])
    
    #### 46 -> (確定): D23
    D23 = ((1, 1, 1), (2, 23, 1), (23, 2, 11))
    conj_dict[46] = (
            [D23,"D(23)"],)
    
    #### 48 -> (候補): D24, Q24, Delta48
    D24 = ((1, 1, 1), (2, 1, 1), (2, 12, 2), (3, 2, 1), (4, 2, 1), 
           (6, 2, 1), (8, 2, 2), (12, 2, 2), (24, 2, 4))
    Q24 = ((1, 1, 1), (2, 1, 1), (3, 2, 1), (4, 2, 1), (4, 12, 2), 
           (6, 2, 1), (8, 2, 2), (12, 2, 2), (24, 2, 4))
    Delta48 = ((1, 1, 1), (2, 3, 1), (3, 16, 2), (4, 3, 4))
    conj_dict[48] = (
            [D24,"D(24)"],
            [Q24,"Q(24)"],
            [Delta48,"Delta(48)"])
    
    #### 50 -> (候補): Sigma50
    Sigma50 = ((1, 1, 1), (2, 5, 1), (5, 1, 4), (5, 2, 10), (10, 5, 4))
    conj_dict[50] = (
            [Sigma50,"Sigma(50)"],)
    
    #### 54 -> (候補): Delta54
    Delta54 = ((1, 1, 1), (2, 9, 1), (3, 1, 2), (3, 6, 4), (6, 9, 2))
    conj_dict[54] = (
            [Delta54,"Delta(54)"],)
    
    #### 57 -> (候補): T19
    T19 = ((1, 1, 1), (3, 19, 2), (19, 3, 6))
    conj_dict[57] = (
            [T19,"T(19)"],)    
    
    #### 60 -> (候補): A5
    A5 = ((1, 1, 1), (2, 15, 1), (3, 20, 1), (5, 12, 2))
    conj_dict[60] = (
            [A5,"A(5)"],)
    
    #### 64 -> (候補): QD64
    QD64 = ((1, 1, 1), (2, 1, 1), (2, 16, 1), (4, 2, 1), (4, 16, 1), 
            (8, 2, 2), (16, 2, 4), (32, 2, 8))
    conj_dict[64] = (
            [QD64,"QD(64)"],)
    
    #### 72 -> (候補): Sigma72
    Sigma72 = ((1, 1, 1), (2, 1, 1), (2, 2, 1), (2, 6, 1), (3, 1, 2), 
               (3, 2, 3), (4, 6, 1), (6, 1, 2), (6, 2, 11), (6, 6, 2), 
               (12, 6, 2))
    conj_dict[72] = (
            [Sigma72,"Sigma(72)"],)

    #### 75 -> (候補): Delta75
    Delta75 = ((1, 1, 1), (3, 25, 2), (5, 3, 8))
    conj_dict[75] = (
            [Delta75,"Delta(75)"],)
    
    #### 81 -> (候補): Sigma81
    Sigma81 = ((1, 1, 1), (3, 1, 2), (3, 3, 8), (3, 9, 2), (9, 9, 4))
    conj_dict[81] = (
            [Sigma81,"Sigma(81)"],)
    
    #### 96 -> (候補): Delta96
    Delta96 = ((1, 1, 1), (2, 3, 1), (2, 12, 1), (3, 32, 1), (4, 3, 2), 
               (4, 6, 1), (4, 12, 1), (8, 12, 2))
    conj_dict[96] = (
            [Delta96,"Delta(96)"],)
    
    #### 98 -> (候補): Sigma98
    Sigma98 = ((1, 1, 1), (2, 7, 1), (7, 1, 6), (7, 2, 21), (14, 7, 6))
    conj_dict[98] = (
            [Sigma98,"Sigma(98)"],)
    
    #### 108 -> (候補): Delta108
    Delta108 = ((1, 1, 1), (2, 3, 1), (3, 1, 2), (3, 3, 2), (3, 12, 6), 
               (6, 3, 8))
    conj_dict[108] = (
            [Delta108,"Delta(108)"],)
    
    #### 120 -> (候補): S5
    S5 = ((1, 1, 1), (2, 10, 1), (2, 15, 1), (3, 20, 1), 
          (4, 30, 1), (5, 24, 1), (6, 20, 1))
    conj_dict[120] = (
            [S5,"S(5)"],)
    
    #### 128 -> (候補): QD128, Sigma128
    QD128 = ((1, 1, 1), (2, 1, 1), (2, 32, 1), (4, 2, 1), (4, 32, 1), 
             (8, 2, 2), (16, 2, 4), (32, 2, 8), (64, 2, 16))
    Sigma128 = ((1, 1, 1), (2, 1, 1), (2, 2, 1), (2, 8, 1), (4, 1, 2), 
                (4, 2, 5), (4, 8, 1), (8, 1, 4), (8, 2, 22), (8, 8, 2), 
                (16, 8, 4))
    conj_dict[128] = (
            [QD128,"QD(128)"],
            [Sigma128,"Sigma(128)"])
        
    #### 147 -> (候補): Delta147
    Delta147 = ((1, 1, 1), (3, 49, 2), (7, 3, 16))
    conj_dict[147] = (
            [Delta147,"Delta(147)"],)
    
    #### 150 -> (候補): Delta150
    Delta150 = ((1, 1, 1), (2, 15, 1), (3, 50, 1), (5, 3, 4), 
                (5, 6, 2), (10, 15, 4))
    conj_dict[150] = (
            [Delta150,"Delta(150)"],)
    
    #### 162 -> (候補): Sigma162
    Sigma162 = ((1, 1, 1), (2, 9, 1), (3, 1, 2), (3, 2, 3), (6, 9, 2), 
                (9, 1, 6), (9, 2, 33), (18, 9, 6))
    conj_dict[162] = (
            [Sigma162,"Sigma(162)"],)

    #### 192 -> (候補): Delta192, Sigma192
    Delta192 = ((1, 1, 1), (2, 3, 1), (3, 64, 2), (4, 3, 4), (8, 3, 16))
    Sigma192 =((1, 1, 1), (2, 1, 1), (2, 3, 2), (3, 16, 2), (4, 1, 2), 
               (4, 3, 18), (6, 16, 2), (12, 16, 4))
    conj_dict[192] = (
            [Delta192,"Delta(192)"],
            [Sigma192,"Sigma(192)"])
    
    #### 200 -> (候補): Sigma200
    Sigma200 = ((1, 1, 1), (2, 1, 1), (2, 2, 1), (2, 10, 1), (4, 10, 1), 
                (5, 1, 4), (5, 2, 10), (10, 1, 4), (10, 2, 34), 
                (10, 10, 4), (20, 10, 4))
    conj_dict[200] = (
            [Sigma200,"Sigma(200)"],)
    
    ### 216 -> (候補): Delta216
    Delta216 = ((1, 1, 1), (2, 3, 1), (2, 18, 1), (3, 1, 2), (3, 6, 1), 
                (3, 24, 3), (4, 18, 1), (6, 3, 2), (6, 6, 3), (6, 18, 2), 
                (12, 18, 2))
    conj_dict[216] = (
            [Delta216,"Delta(216)"],)
    
    #### 256 -> (候補): QD256
    QD256 = ((1, 1, 1), (2, 1, 1), (2, 64, 1), (4, 2, 1), (4, 64, 1), 
             (8, 2, 2), (16, 2, 4), (32, 2, 8), (64, 2, 16), (128, 2, 32))
    conj_dict[256] = (
            [QD256,"QD(256)"],)
    
    #### 360 -> (候補): A6
    A6 = ((1, 1, 1), (2, 45, 1), (3, 40, 2), (4, 90, 1), (5, 72, 2))
    conj_dict[360] = (
            [A6,"A(6)"],)

    #### 720 -> (候補): S6
    S6 = ((1, 1, 1), (2, 15, 2), (2, 45, 1), (3, 40, 2), 
          (4, 90, 2), (5, 144, 1), (6, 120, 2))
    conj_dict[720] = (
            [S6,"S(6)"],)

    # 非可換群の場合には共役類を用いる
    @classmethod
    def identify_non_abelian(cls,group):
        n = group.order()
        try:
            target_list = cls.conj_dict[n]
        except KeyError:
            return False
        #End try
        c_count = group.conjugacy_count()
        for target in target_list:
            target_c_count = target[0]
            if set(c_count) == set(target_c_count):
                group.set_symbol(target[1])
                return True
            #End if
        #End for
        return False
    #End def
#End class


##### [位数:2n] D(n) の生成元      
#n = 24
#p = numpy.cos(2*numpy.pi/float(n))
#q = numpy.sin(2*numpy.pi/float(n))
#gen1 = numpy.array([[p,-q],
#                    [q,p]])
#gen2 = numpy.array([[1,0],
#                    [0,-1]])
#generators = [gen1,gen2]

##### [位数:2n] Q(n) の生成元
#n = 24
#p = numpy.exp(2*numpy.pi*1j / float(n))
#q = numpy.exp(-2*numpy.pi*1j / float(n))
#gen1 = numpy.array([[p,0],
#                    [0,q]])
#gen2 = numpy.array([[0,1j],
#                    [1j,0]])
#generators = [gen1,gen2]

#### [位数:n!] S(n) の生成元
#n = 6
#generators = []
#for i1 in range(n-1):
#    gen = numpy.zeros((n,n),dtype=numpy.int)
#    for i2 in range(n):
#        if i2 == i1:
#            gen[i2,i2+1] = 1
#        elif i2 == i1 + 1:
#            gen[i2,i2-1] = 1
#        else:
#            gen[i2,i2] = 1
#        #End if
#    #End for
#    generators.append(gen)
##End for
    
##### [位数:2n] QD(2n) の生成元
## n = 2^k, k = 1,2,...
#n = 128
#p = numpy.exp(2*numpy.pi*1j / float(n))
#q = numpy.exp(-2*numpy.pi*1j / float(n)) * (-1)
#gen1 = numpy.array([[p,0],
#                    [0,q]])
#gen2 = numpy.array([[0,1],
#                    [1,0]])
#generators = [gen1,gen2]

##### [位数:] Sigma(2n^2) の生成元
#n = 10
#p = numpy.exp(2*numpy.pi*1j / float(n))
#gen1 = numpy.array([[1,0],
#                    [0,p]])
#gen2 = numpy.array([[p,0],
#                    [0,1]])
#gen3 = numpy.array([[0,1],
#                    [1,0]])
#generators = [gen1,gen2,gen3]

##### [位数:3n^2] Delta(3n^2) の生成元
#n = 8
#p = numpy.exp(2*numpy.pi*1j / float(n))
#q = numpy.exp(-2*numpy.pi*1j / float(n))
#gen1 = numpy.array([[0,1,0],
#                    [0,0,1],
#                    [1,0,0]])
#gen2 = numpy.array([[p,0,0],
#                    [0,1,0],
#                    [0,0,q]])
#gen3 = numpy.array([[q,0,0],
#                    [0,p,0],
#                    [0,0,1]]) 
#generators = [gen1,gen2,gen3]

##### [位数:3n] T(n) の生成元
## n = 7,13,19,31,43,49,...
## gen2 を手動で変更する必要有り
#n = 19
#p = numpy.exp(2*numpy.pi*1j / float(n))
#gen1 = numpy.array([[0,1,0],
#                    [0,0,1],
#                    [1,0,0]])
#gen2 = numpy.array([[p,0,0],
#                    [0,p**7,0],
#                    [0,0,p**11]])
#generators = [gen1,gen2]

###### [位数:3n^3] Sigma(3n^3) の生成元
#n = 3
#p = numpy.exp(2*numpy.pi*1j / float(n))
#gen1 = numpy.array([[0,1,0],
#                    [0,0,1],
#                    [1,0,0]])
#gen2 = numpy.array([[1,0,0],
#                    [0,1,0],
#                    [0,0,p]])
#gen3 = numpy.array([[1,0,0],
#                    [0,p,0],
#                    [0,0,1]])
#gen4 = numpy.array([[p,0,0],
#                    [0,1,0],
#                    [0,0,1]])
#generators = [gen1,gen2,gen3,gen4]

###### [位数:6n^2] Delta(6n^2) の生成元
#n = 6
#p = numpy.exp(2*numpy.pi*1j / float(n))
#q = numpy.exp(-2*numpy.pi*1j / float(n))
#gen1 = numpy.array([[0,1,0],
#                    [0,0,1],
#                    [1,0,0]])
#gen2 = numpy.array([[0,0,1],
#                    [0,1,0],
#                    [1,0,0]])
#gen3 = numpy.array([[p,0,0],
#                    [0,q,0],
#                    [0,0,1]])
#gen4 = numpy.array([[1,0,0],
#                    [0,p,0],
#                    [0,0,q]])
#generators = [gen1,gen2,gen3,gen4]


def main():
    pass
#End def

## thtmodule のimport確認
def import_print():
    print("[finitegroup.py]がインポートされました.")
    return True
#End def

if __name__ == '__main__':
    main()
else:
#    import_print()
    pass
#End if