"""
有限群解析プログラムの起点ファイル
"""
import sys
import numpy
sys.path.append('../')
from application.calc import matcal, mastergroup, group
from application.controller import ConsoleController
############
############ 以降を編集する
############ ↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓

####
#### STEP1 生成元を定義する
####
# 生成元は numpy.array() で定義すること
# 複素数も使用可能

# gen1 = numpy.array([[0,-1,0],
#                     [1,0,0],
#                     [0,0,1]])

# gen2 = numpy.array([[1,0,0],
#                     [0,0,1],
#                     [0,1,0]])


###### [位数:6n^2] Delta(6n^2) の生成元
n = 4
p = numpy.exp(2*numpy.pi*1j / float(n))
q = numpy.exp(-2*numpy.pi*1j / float(n))
gen1 = numpy.array([[0,1,0],
                    [0,0,1],
                    [1,0,0]])
gen2 = numpy.array([[0,0,1],
                    [0,1,0],
                    [1,0,0]])
gen3 = numpy.array([[p,0,0],
                    [0,q,0],
                    [0,0,1]])
gen4 = numpy.array([[1,0,0],
                    [0,p,0],
                    [0,0,q]])
generators = [gen1,gen2,gen3,gen4]


####
#### STEP2 定義した生成元を全て [generators] に追加する
####
# 例えば, 生成元が 3個 ならば
# generators = [gen1,gen2,gen3]

#generators = [gen1,gen2]

####
#### STEP3 群の位数の最大値[maximal]を決定する
####
# 当プログラムでは 有限群 のみを扱う
# 生成された要素数が [maximal] を超えたときに "群が有限で閉じない" と判断する
# 大きな群を扱う際には, 適宜 [maximal] の値を変更すること

maximal = 2000

############ ↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑
############ 編集はここまで
############
zero_base = 0.0001

ctrl = ConsoleController()
matlist = matcal.generate_group(generators, zero_base, maximal, ctrl).value
result = matcal.calc_cayleytable(matlist, zero_base, ctrl)
master = mastergroup.MasterGroup(result.value)
g0 = group.Group(master,master.all_elements)
g1 = group.Group(master,master.calc_closure({1,}))
print(g0.conjugacy_count)

