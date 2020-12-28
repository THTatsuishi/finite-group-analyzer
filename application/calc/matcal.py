"""
行列計算用のモジュール。
"""
import itertools
import numpy
import sys
sys.path.append('../')
from application.controller import Controller, NullController

def are_equal(a:complex, b:complex, zero_base:float) -> bool:
    """
    許容誤差の範囲で二つの複素数が一致しているとみなせるか判定する。

    Parameters
    ----------
    a : complex
        一つ目の複素数。
    b : complex
        二つ目の複素数。
    zero_base : float
        許容誤差。

    Returns
    -------
    bool
        True:
            (a-b)の実部の絶対値と虚部の絶対値がともにzero_base以下である。 
        False:
            (a-b)の実部の絶対値がzero_baseより大きい。
            (a-b)の虚部の絶対値がzero_baseより大きい。
            許容誤差が負である。         

    """
    delta = a - b
    return abs(delta.real) <= zero_base and abs(delta.imag) <= zero_base

def generate_group(
        matlist: 'list[ComplexSquareMatrix]', zero_base: float, maximal: int,
        controller: 'Controller' = None
        ) -> 'GenerateGroupResult':
    """
    指定の生成元のリストから群を生成する。
    以下のいずれかの場合は生成に失敗する。
    許容誤差が負である。
    生成元の個数が0である。
    生成元の次元が合っていない。
    生成元に行列式の絶対値が1でないものが含まれている。
    要素数が最大値を超えても群が閉じない。

    Parameters
    ----------
    matlist : 'list[ComplexSquareMatrix]'
        生成元のリスト。
    zero_base : float
        許容誤差。
    maximal : int
        群の要素の最大値。
        生成された群の要素数がこの値を超えた場合、有限では閉じないものと判定する。
    controller : 'Controller'
        コントローラー。The default is None.

    Returns
    -------
    GenerateGroupResult
        生成結果を表すクラス。

    """
    cntl = (controller if controller is not None
            else NullController())
    n_mat = len(matlist)
    cntl.calc_progress("%d個の生成元から群の生成を開始" % n_mat)
    # 許容誤差が負ならば失敗
    # 一致判定で常に不一致とされて、無限に生成されるため
    if zero_base < 0:
        cntl.calc_progress("失敗：許容誤差が負の値である")
        return GenerateGroupResult()   
    # 生成元が0個ならば失敗
    if n_mat == 0:
        cntl.calc_progress("失敗：生成元の個数が0である")
        return GenerateGroupResult()
    order = matlist[0].order
    # 生成元の次元が合っていなければ失敗
    if any(i.order != order for i in matlist):
        cntl.calc_progress("失敗：生成元の次元が合っていない")
        return GenerateGroupResult()
    # 生成元に行列式の絶対値が1でないものが含まれていたら失敗
    # 有限で閉じないため
    if any(not i.has_unit_determinant(zero_base) for i in matlist):
        cntl.calc_progress(
            "失敗：生成元に行列式の絶対値が1でないものが含まれている")
        return GenerateGroupResult()
    # 生成元の整理：単位元の除外、重複削除
    gen_list = []
    identity = ComplexSquareMatrix.identity(order)
    for i in matlist:
        if i.equal_to(identity,zero_base):
            continue
        if i.is_included(gen_list,zero_base):
            continue
        gen_list.append(i)
    # 元の生成
    element_all = [identity] + gen_list
    element_prev = gen_list[:]
    element_new = []
    n_all = len(element_all)
    n_loop= 0
    while len(element_prev) != 0:
        if n_all > maximal:
            cntl.calc_progress(
                "失敗：要素数が最大値(%d)を超えても群が閉じない" % maximal)
            return GenerateGroupResult()
        n_loop += 1
        cntl.calc_progress("-- loop(%d): 要素数(%d)" % (n_loop,n_all))
        # 新しい行列を生成
        new_list = [mat1.dot(mat2) for (mat1, mat2) 
                    in itertools.product(element_prev,gen_list)]
        # 生成されたものが既存の行列と被っていなければリストに追加
        for i in new_list:
            if not i.is_included(element_all,zero_base):
                element_new.append(i)
                element_all.append(i)
        # 情報を更新
        n_all += len(element_new)
        element_prev = element_new[:]
        element_new = []
    cntl.calc_progress("生成完了：位数(%d)" % n_all)
    return GenerateGroupResult(element_all)

class ComplexSquareMatrix(object):
    """
    複素正方行列を表す。
    
    """
    def __init__(self, matrix: numpy.ndarray):
        """
        複素正方行列を作成する。

        Parameters
        ----------
        matrix : numpy.ndarray
            複素正方行列。
            要素が複素数である。
            次元数が2である。
            行数と列数が一致する。

        Returns
        -------
        None.

        """
        self.matrix = matrix
        self.order = matrix.shape[0]
    
    @classmethod
    def identity(cls, order: int) -> 'ComplexSquareMatrix':
        """
        指定の次数の単位行列を作成する。

        Parameters
        ----------
        cls : 'ComplexSquareMatrix'
            'ComplexSquareMatrix'
        order : int
            次数。正の整数。

        Returns
        -------
        ComplexSquareMatrix
            単位行列。

        """
        return ComplexSquareMatrix(numpy.identity(order))
    
    def dot(self, csmatrix: 'ComplexSquareMatrix') -> 'ComplexSquareMatrix':
        """
        この行列に指定の行列を右から掛ける。

        Parameters
        ----------
        csmatrix : 'ComplexSquareMatrix'
            右から掛ける複素正方行列。
            この行列と同じ次数でなければならない。

        Returns
        -------
        ComplexSquareMatrix
            演算結果の複素正方行列。

        """
        return ComplexSquareMatrix(numpy.dot(self.matrix,csmatrix.matrix))
         
    def equal_to(
            self, csmatrix: 'ComplexSquareMatrix', zero_base: float
            ) -> bool:
        """
        許容誤差の範囲でこの行列と指定の行列が一致するか判定する。

        Parameters
        ----------
        csmatrix : ComplexSquareMatrix
            比較対象の複素正方行列。
        zero_base : float
            許容誤差。

        Returns
        -------
        bool
            True:
                全ての要素が許容誤差の範囲で一致する。
            False:
                次数が一致しない。
                許容誤差の範囲で一致しない要素が存在する。
                許容誤差が負である。

        """
        if self.order!=csmatrix.order:
            return False
        mat = self.matrix - csmatrix.matrix
        return all(are_equal(i,0,zero_base) for i in numpy.ravel(mat))
    
    def has_unit_determinant(self, zero_base: float) -> bool:
        """
        許容誤差の範囲で行列式の絶対値が1であるか判定する。

        Parameters
        ----------
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
        return are_equal(abs(numpy.linalg.det(self.matrix)),1,zero_base)

    def is_included(
            self, matlist: 'list[ComplexSquareMatrix]', zero_base: float
            ) -> bool:
        """
        指定のリストの中に、許容誤差の範囲でこの行列に一致する行列が含まれているか判定する。
        ----------
        matlist : list[ComplexSquareMatrix]
            複素正方行列のリスト。
        zero_base : float
            許容誤差。
    
        Returns
        -------
        bool
            True:
                一致する行列が含まれている。
            False:
                一致する行列が含まれていない。
                許容誤差が負である。
    
        """
        return any(self.equal_to(i,zero_base) for i in matlist)

class GenerateGroupResult(object):
    """
    群の生成結果を表す。
    生成に成功した場合:
        has_value = True,
        value = (生成された行列のリスト)
    生成に失敗した場合:
        has_value = False,
        value = None

    """
    def __init__(self, csmatlist: 'list[ComplexSquareMatrix]' = None):
        """
        群の生成結果を作成する。

        Parameters
        ----------
        csmatlist : 'list[ComplexSquareMatrix]', optional
            生成された行列のリスト。
            リストがNoneでなければ生成成功の結果を作成する。
            リストがNoneならば生成失敗の結果を作成する。
            The default is None.

        Returns
        -------
        None.

        """
        self.has_value = True if csmatlist is not None else False
        self.value = csmatlist