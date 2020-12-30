"""
数値計算に使用する関数。
"""
import numpy

def calc_divisor(a: int, include_one: bool) -> 'tuple[int]':
    """
    指定の値の約数を求める。
    自明な約数も含む。
    厳密な意味での約数とは異なるが、include_one=Trueの場合には1を含める。

    Parameters
    ----------
    a : int
        正の整数。
    should_include_one : bool
        約数の一覧に1を含めるかどうか。
        True:
            1を含める。
        False:
            1を含めない。

    Returns
    -------
    'tuple[int]'
        約数の一覧。
        降順に並ぶ。

    """
    div_set = set()
    div = 1 if include_one else 2
    div_max = numpy.sqrt(a)
    while div <= div_max:
       quot,mod = divmod(a,div)
       if mod == 0:
           div_set = div_set | {div,quot}
       div += 1
    return tuple(sorted(list(div_set),reverse=True))