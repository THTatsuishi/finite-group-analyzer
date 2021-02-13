"""
有限群解析プログラムの起点ファイル。
"""
import sys
import numpy
sys.path.append('../')
from application.service import AppServise

############
############ 以降を編集する
############ ↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓

####
#### STEP1 生成元を定義する
####
# 生成元は numpy.array() で定義すること
# 複素数も使用可能
# 正方行列の次数は変更可能

gen1 = numpy.array([[0,1,0],
                    [1,0,0],
                    [0,0,1j]])

gen2 = numpy.array([[1,0,0],
                    [0,0,1],
                    [0,1,0]])

####
#### STEP2 定義した生成元を全て [generators] に追加する
####
# 例えば, 生成元が 3個 ならば
# generators = [gen1,gen2,gen3]

generators = [gen1,gen2]

####
#### STEP3 群の位数の最大値[maximal]を決定する
####
# 当プログラムでは 有限群 のみを扱う
# 生成された要素数が [maximal] を超えたときに "群が有限で閉じない" と判断する
# 大きな群を扱う際には, 適宜 [maximal] の値を変更すること

maximal = 2000

############ ↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑
############ 編集はここまで

# 浮動小数点の許容誤差
# 基本的に編集不要(0.0001)
zero_base = 0.0001

# 群の生成を実行
app = AppServise(generators, zero_base, maximal)
# 生成成功なら解析画面を開く
if app.is_succeeded:
    app()