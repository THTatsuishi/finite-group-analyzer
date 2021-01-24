"""
数値計算に使用する関数など。
"""
import numpy
import collections

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

def prime_factorize(n: int):
    """
    正の整数を素因数分解する。

    Parameters
    ----------
    n : int
        正の整数。

    Returns
    -------
    TYPE
        DESCRIPTION.

    """
    prime_list = []
    while (n % 2 == 0):
        prime_list.append(2)
        n //= 2
    f = 3
    while (f * f <= n):
        if (n % f == 0):
            prime_list.append(f)
            n //= f
        else:
            f += 2
    if n != 1: prime_list.append(n)
    return collections.Counter(prime_list)