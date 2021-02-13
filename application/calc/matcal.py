"""
行列計算を行うためのモジュール。
"""
import itertools
import numpy
from ..controller import Controller, NullController

def is_zero_num(num: complex, zero_base: float) -> bool:
    """
    指定の複素数が許容誤差の範囲で0であるか判定する。

    Parameters
    ----------
    num : complex
        複素数。
    zero_base : float
        許容誤差。

    Returns
    -------
    bool
        True:
            numの実部の絶対値と虚部の絶対値がともにzero_base以下である。 
        False:
            numの実部の絶対値がzero_baseより大きい。
            numの虚部の絶対値がzero_baseより大きい。
            許容誤差が負である。         

    """
    return abs(num.real) <= zero_base and abs(num.imag) <= zero_base

def is_zero_mat(
        mat: numpy.ndarray, zero_base: float
        ) -> bool:
    """
    指定の行列が許容誤差の範囲でゼロ行列に一致するか判定する。

    Parameters
    ----------
    mat : numpy.ndarray
        複素正方行列。
    zero_base : float
        許容誤差。

    Returns
    -------
    bool
        True:
            全ての要素が許容誤差の範囲で一致する。
        False:
            許容誤差の範囲で0でない要素が存在する。
            許容誤差が負である。

    """
    # この関数は何度も呼び出されるため、速度が重要である
    for row in mat:
        for num in row:
            if not is_zero_num(num,zero_base): return False
    return True

def is_mat_in_list(
        mat: numpy.ndarray, matlist: 'list[numpy.ndarray]', zero_base: float
        ) -> bool:
    """
    指定の行列が指定のリストの中に含まれているか判定する。
    許容誤差の範囲で一致する行列が含まれているか判定する。

    Parameters
    ----------
    mat : numpy.ndarray
        複素行列。
    matlist : 'list[numpy.ndarray]'
        複素行列のリスト。
    zero_base : float
        許容誤差。

    Returns
    -------
    bool
        True:
            含まれている。
        False:
            含まれていない。
            許容誤差が負である。

    """
    return any(is_zero_mat(mat-i,zero_base) for i in matlist)
   
def has_unit_determinant(mat: numpy.ndarray, zero_base: float) -> bool:
    """
    指定の行列の行列式の絶対値が、許容誤算範囲で1であるか判定する。

    Parameters
    ----------
    mat : numpy.ndarray
        複素正方行列。
    zero_base : float
        許容誤差。

    Returns
    -------
    bool
        True:
            （行列式の絶対値）-1の絶対値がzero_base以下である。
        False:
            （行列式の絶対値）-1の絶対値がzero_baseより大きい。
            許容誤差が負である。

    """
    return is_zero_num(abs(numpy.linalg.det(mat))-1,zero_base)

def generate_group(
        matlist: 'list[numpy.ndarray]', zero_base: float, maximal: int,
        controller: 'Controller' = None
        ) -> 'GenerateGroupResult':
    """
    指定の生成元のリストから群を生成する。
    以下のいずれかの場合は生成に失敗する。
    許容誤差が負である。
    生成元の個数が0である。
    生成元が正方行列でない。
    生成元の次数が合っていない。
    生成元に行列式の絶対値が1でないものが含まれている。
    要素数が最大値を超えても群が閉じない。

    Parameters
    ----------
    matlist : 'list[numpy.ndarray]'
        生成元のリスト。
    zero_base : float
        許容誤差。
    maximal : int
        群の要素の最大値。
        生成された群の要素数がこの値を超えた場合、有限では閉じないものと判定する。
    controller : 'Controller', optional
        コントローラー。
        The default is None.

    Returns
    -------
    GenerateGroupResult
        生成結果を表すクラス。

    """
    ctrl = (controller if controller is not None else NullController())
    n_mat = len(matlist)
    ctrl.calc_start("%d個の生成元から群の生成を開始" % n_mat)
    # 許容誤差が負ならば失敗
    # 一致判定で常に不一致とされて、無限に生成されるため
    if zero_base < 0:
        ctrl.calc_end("失敗：許容誤差が負である")
        return GenerateGroupResult()   
    # 生成元が0個ならば失敗
    if n_mat == 0:
        ctrl.calc_end("失敗：生成元の個数が0である")
        return GenerateGroupResult()
    # 生成元が正方行列でなければ失敗。
    if any(i.ndim != 2 for i in matlist):
        ctrl.calc_end("失敗：生成元が正方行列でない")
        return GenerateGroupResult()        
    order = matlist[0].shape[0]
    correct_shape = (order, order)
    # 生成元の次数が合っていなければ失敗
    if any(i.shape != correct_shape for i in matlist):
        ctrl.calc_end("失敗：生成元の次数が合っていない")
        return GenerateGroupResult()
    # 生成元に行列式の絶対値が1でないものが含まれていたら失敗
    # 有限で閉じないため
    if any(not has_unit_determinant(i,zero_base) for i in matlist):
        ctrl.calc_end("失敗：生成元に行列式の絶対値が1でないものが含まれている")
        return GenerateGroupResult()
    # 生成元の整理：単位元の除外、重複削除
    gen_list = []
    identity = numpy.identity(order)
    for i in matlist:
        if is_zero_mat(i-identity,zero_base): continue
        if is_mat_in_list(i,gen_list,zero_base): continue
        gen_list.append(i)
    # 元の生成
    element_all = [identity] + gen_list
    element_prev = tuple(gen_list)
    element_new = []
    n_all = len(element_all)
    n_loop= 0
    while element_prev:
        if n_all > maximal:
            ctrl.calc_end(
                "失敗：要素数が最大値(%d)を超えても群が閉じない" % maximal)
            return GenerateGroupResult()
        n_loop += 1
        ctrl.calc_progress("-- loop(%d): 要素数(%d)" % (n_loop,n_all))
        # 新しい行列を生成
        new_list = [numpy.dot(mat1,mat2) for (mat1, mat2) 
                    in itertools.product(element_prev,gen_list)]
        # 生成されたものが既存の行列と被っていなければリストに追加
        for i in new_list:
            if is_mat_in_list(i,element_all,zero_base): continue
            element_new.append(i)
            element_all.append(i)
        # 情報を更新
        n_all += len(element_new)
        element_prev = tuple(element_new)
        element_new = []
    ctrl.calc_end("生成完了：位数(%d)" % n_all)
    return GenerateGroupResult(element_all)

def calc_cayleytable(matlist: 'list[numpy.ndarray]', zero_base: float,
                     controller: 'Controller' = None
                     ) -> 'CalcCayleyTableResult':
    """
    指定の群の乗積表を作成する。
    generate_group()で作成された行列のリストを指定する。
    以下のいずれかの場合には作成に失敗する。
    許容誤差が負である。
    位数が0である。
    群が閉じていない。   

    Parameters
    ----------
    matlist : 'list[numpy.ndarray]'
        群の要素のリスト。
        generate_group()で作成された行列のリストを指定する。
    zero_base : float
        許容誤差。
    controller : 'Controller', optional
        コントローラー。
        The default is None.

    Returns
    -------
    CalcCayleyTableResult
        作成結果を表すクラス。

    """
    ctrl = controller if controller is not None else NullController()
    n = len(matlist)
    ctrl.calc_start("位数(%d)の群の乗積表の作成を開始" % n)
    # 許容誤差が負ならば失敗
    # 一致判定で常に不一致と判定されるため
    if zero_base < 0:
        ctrl.calc_end("失敗：許容誤差が負である")
        return CalcCayleyTableResult()
    # 位数が0ならば失敗
    if n == 0:
        ctrl.calc_end("失敗：位数が0である")
        return CalcCayleyTableResult()   
    # 乗積表を表す行列を作成
    table = numpy.zeros((n,n),dtype=numpy.int)
    # 行列の一致判定にコストがかかるため、なるべく回避する   
    check_list_column = [[False for i1 in range(n)] for i2 in range(n)]
    for i1 in range(n):
        check_list_row = [False for i2 in range(n)]
        for i2 in range(n):
            mat = numpy.dot( matlist[i1],matlist[i2])
            flag = False
            for i3 in range(n):
                if check_list_row[i3]: continue
                if check_list_column[i2][i3]: continue
                if is_zero_mat(mat-matlist[i3],zero_base):
                    flag = True
                    table[i1,i2] = i3
                    check_list_row[i3] = True
                    check_list_column[i2][i3] = True
                    break
            # 見つからなかった場合は失敗
            # 群が閉じていないため
            if not flag:
                ctrl.calc_end("失敗：群が閉じていない")
                return CalcCayleyTableResult()
        ctrl.calc_progress("-- 進捗: %d/%d" % (i1+1,n))
    ctrl.calc_end("作成完了")
    cayley_table = CayleyTable(matlist, table)
    return CalcCayleyTableResult(cayley_table)     

class GenerateGroupResult(object):
    """
    群の生成結果を表す。

    Attributes
    ----------
    has_value : bool
        生成に成功したかどうか。
        
        True:
            生成に成功した。
        
        False:
            生成に失敗した。
    
    value : 'tuple[numpy.ndarray]'
        生成された行列のタプル。
        生成に失敗した場合はNone。

    Parameters
    ----------
    matlist : 'list[numpy.ndarray]', optional
        生成された行列のリスト。
        リストがNoneでなければ生成成功の結果を作成する。
        リストがNoneならば生成失敗の結果を作成する。
        The default is None.

    """
    def __init__(self, matlist: 'list[numpy.ndarray]' = None):
        self.has_value = True if matlist is not None else False
        self.value = tuple(matlist) if matlist is not None else None
        
class CalcCayleyTableResult(object):
    """
    乗積表の作成結果を表す。
    
    Attributes
    ----------
    has_value : bool
        作成に成功したかどうか。
        
        True:
            作成に成功した。
        
        False:
            作成に失敗した。
    
    value : numpy.ndarray
        作成された乗積表。
        作成に失敗した場合はNone。
    
    Parameters
    ----------
    table : 'CaylayTable', optional
        生成された乗積表。
        値がNoneでなければ作成成功の結果を作成する。
        値がNoneならば作成失敗の結果を作成する。
        The default is None.  
        
    """
    def __init__(self, table: 'CayleyTable'= None):
        self.has_value = True if table is not None else False
        self.value = table
        
class CayleyTable(object):
    """
    乗積表を表す。
    
    Attributes
    ----------
    matlist : 'tuple[numpy.ndarray]'
        要素のタプル。
    
    table: numpy.ndarray
        乗積表。
    
    Parameters
    ----------
    matlist : 'list[numpy.ndarray]'
        要素のリスト。
        この順番で採番する。
    table : numpy.ndarray
        乗積表。

    """
    def __init__(self, matlist: 'list[numpy.ndarray]', table: numpy.ndarray):
        self.matlist = tuple(matlist)
        self.table = table.copy()