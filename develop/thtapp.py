# -*- coding: utf-8 -*-

#####################################
# Python 3.7
# 作成者: 立石卓也
# 作成時所属: 北海道大学 素粒子論研究室
#####################################

#### モジュールのインポート
import sys
import os
# 自作モジュール
sys.path.append(os.getcwd())
from thtmodules import finitegroup as fg
from thtmodules import gui as thtgui


def setup(master_gens,gui=False,maximal=2000,equal_zero=0.000001):
    rulebook = fg.Constructor.setup(master_gens,maximal,equal_zero)
    master = rulebook.master_group
    trivial = rulebook.trivial_group
    cmd = CMD(rulebook)
    #
    print("以下の群を生成しました:")
    print("Name\tOrder")
    print("%s\t%d" % (master.name(),master.order()))
    print("%s\t%d" % (trivial.name(),trivial.order()))
    if not gui:
        return cmd
    else:
        print("\n以降は新しく開いた画面上で操作してください.\n")
        gui = thtgui.GUI(rulebook,cmd)
        cmd.gui = gui
        print("\n解析画面を閉じました.")
        print("再度画面を開きたい場合はコンソール上で cmd.gui() と入力してください.\n")
        return cmd
    #End if
#End def


#### GUI/コンソール からの呼び出し用の機能
class CMD(object):
    def __init__(self,rulebook):
        self._rulebook = rulebook
        self._update()
    #End def
    
    def __call__(self):
        return self._update()
    #End def
    
    # CMD インスタンスに 全ての Group インスタンスに対応する属性を付与する
    # cmd.[group.name()] = group
    def _update(self):
        for group in self._rulebook.group_storage:
            setattr(self,("%s" % group.name()),group)
        #End for
        return True
    #End def
    
    ####
    ####
    ####
    
    def element(self,group):
        text_full = "\n"
        #
        text = ("[%s]の要素:" % group.name())
        print(text)
        text_full = text_full + text + "\n"
        #
        text = str(sorted(list(group.element())))
        print(text)
        text_full = text_full + text + "\n"
        #
        self._update()
        return text_full[:-1]
    #End def
    
    def table(self,group):
        text_full = "\n"
        #
        text = ("[%s]の乗積表:" % group.name())
        print(text)
        text_full = text_full + text + "\n"
        #
        text = str(group.subtable())
        print(text)
        text_full = text_full + text + "\n"
        #
        self._update()
        return text_full[:-1]
    #End def
    
    # conjugacyclass
    def conjugacy_class(self,group):
        text_full = "\n"
        #
        text = ("[%s]の共役類の一覧:" % group.name())
        print(text)
        text_full = text_full + text + "\n"
        #
        text = "位数\t要素数\t共役類"
        print(text)
        text_full = text_full + text + "\n"
        #        
        conjugacy_data = group.conjugacy_data()
        for data in conjugacy_data:
            text = ("%d\t%d\t%s" % (data[0],len(data[1]),
                                    str(sorted(list(data[1])))))
            print(text)
            text_full = text_full + text + "\n"
        #End for
        #
        self._update()
        return text_full[:-1]
    #End def

    # conjugacy_count を表示
    def conjugacy_count(self,group):
        text_full = "\n"
        #
        text = ("[%s]の共役類のカウント:" % group.name())
        print(text)
        text_full = text_full + text + "\n"
        #
        text = str(group.conjugacy_count())
        print(text)
        text_full = text_full + text + "\n"
        #
        self._update()
        return text_full[:-1]
    #End def
        
    # 全ての正規部分群を表示
    def normalsub(self,group):
        text_full = "\n"
        #
        grouplist = group.all_normalsub()
        text = ("[%s]の正規部分群の一覧:" % group.name())
        print(text)
        text_full = text_full + text + "\n"
        #
        text = "Name\tOrder\tIsAbelian\t\tIsomorphic"
        print("Name\tOrder\tIsAbelian\tIsomorphic")
        text_full = text_full + text + "\n"
        #
        for group1 in grouplist:
            if group1.is_abelian(): is_abelian = "Abelian"
            else: is_abelian = "non"
            symbol = fg.Classifier.search_isomorphic(group1)
            if symbol is None: symbol = "?"
            text = ("%s\t%d\t%s\t\t%s"
                    % (group1.name(),group1.order(),is_abelian,symbol))
            print(text)
            text_full = text_full + text + "\n"
        #End for
        #
        self._update()
        return text_full[:-1]
    #End def
    
    # 全ての部分群を表示
    def subgroup(self,group,n_max=200):
        text_full = "\n"
        #
        grouplist = group.all_subgroup(n_max)
        #
        # 部分群の数がn_maxを超えると False が返ってくる
        if grouplist == False:
            text_1 = ("発見した部分群の数が%dを超えたため, 処理を放棄します." % n_max)
            text_2 = "\n-> 提案: 先に直積/半直積への分解を行う"
            return text_1 + text_2
        #End if
        #
        text = ("[%s]の部分群の一覧:" % group.name())
        print(text)
        text_full = text_full + text + "\n"
        text = "Name\tOrder\tIsAbelian\t\tIsomorphic"
        print("Name\tOrder\tIsAbelian\tIsomorphic")
        text_full = text_full + text + "\n"
        #
        for group1 in grouplist:
            if group1.is_abelian(): is_abelian = "Abelian"
            else: is_abelian = "non"
            symbol = fg.Classifier.search_isomorphic(group1)
            if symbol is None: symbol = "?"
            text = ("%s\t%d\t%s\t\t%s" 
                    % (group1.name(),group1.order(),is_abelian,symbol))
            print(text)
            text_full = text_full + text + "\n"
        #End for
        #
        self._update()
        return text_full[:-1]
    #End def
    
    def center(self,group):
        text_full = "\n"
        #
        text = ("[%s]の中心:" % group.name())
        print(text)
        text_full = text_full + text + "\n"
        #
        group1 = group.center()
        text = "Name\tOrder\tIsomorphic"
        print(text)
        text_full = text_full + text + "\n"
        #
        symbol = fg.Classifier.search_isomorphic(group1)
        if symbol is None: symbol = "?"
        text = ("%s\t%d\t%s" % (group1.name(),group1.order(),symbol))
        print(text)
        text_full = text_full + text + "\n"
        #
        self._update()
        return text_full[:-1]
    #End def
    
    def derived_series(self,group):
        text_full = "\n"
        #
        grouplist = group.derived_series()
        text = ("[%s]の導来列:" % group.name())
        print(text)
        text_full = text_full + text + "\n"
        #
        text = ("\tName\tOrder\tIsAbelian\t\tIsomorphic")
        print("\tName\tOrder\tIsAbelian\tIsomorphic")
        text_full = text_full + text + "\n"
        #
        suffix_dict = {1:"st", 2:"nd",3:"rd"}
        n = 0
        for group1 in grouplist:
            n += 1
            if n in [1,2,3]: suffix = suffix_dict[n]
            else: suffix = "th"
            suffix = "%d%s" % (n,suffix)
            if group1.is_abelian(): is_abelian = "Abelian"
            else: is_abelian = "non"
            symbol = fg.Classifier.search_isomorphic(group1)
            if symbol is None: symbol = "?"
            text = ("%s\t%s\t%d\t%s\t\t%s" 
                    % (suffix,group1.name(),group1.order(),is_abelian,symbol))
            print(text)
            text_full = text_full + text + "\n"
        #End for
        #
        self._update()
        return text_full[:-1]
    #End def

    def generator(self,group):
        text_full = "\n"
        #
        text = ("[%s]の生成元:" % group.name())
        print(text)
        text_full = text_full + text + "\n"
        #
        text = str(fg.Exam.generator(group))
        print(text)
        text_full = text_full + text + "\n"
        #
        self._update()
        return text_full[:-1]
    #End def
    
    def mat(self,indexlist):
        text_full = "\n"
        #
        for index in indexlist:
            try:
                mat = self._rulebook.index_to_mat[index]
            except KeyError:
                print("mat[%d]は存在しません." % index)
                continue
            #End try
            text = ("mat[%s]:\n" % index) + str(mat) + "\n"
            print(text)
            text_full = text_full + text + "\n"
        #End for
        text_full = text_full[:-1]
        #
        self._update()
        return text_full[:-1]
    #End def

    def decompose(self,group):
        text_full = "\n"
        #
        if group.is_abelian():
            t_list = ["" for i in range(4)]
            t_list[0] = ("[%s]を直積/半直積に分解" % group.name())
            t_list[1] = ("[%s]は可換群であり, 以下の通りに分解されます:" % group.name())
            t_list[2] = ("(注意: 同型を除いて一意的)")
            t_list[3] = ("(\'x\' means \'times\')")
            text = ""
            for tmp_text in t_list: text = text + tmp_text + "\n"
            text = text[:-1]
            print(text)
            text_full = text_full + text + "\n"
            #
            factor = fg.Exam.dp_abelian(group)
            message1 = "group:\t\t"
            message2 = "isomorphic:\t"
            for group1 in factor:
                message1 = message1 + ("%s x " % group1.name())
                message2 = message2 + ("C(%d) x " % group1.order())
            #End for
            message1 = message1[:-2]
            message2 = message2[:-2]
            text = message1 + "\n" + message2
            print(text)
            text_full = text_full + text + "\n"
            #
            return text_full[:-1]
        #End if
        #
        text = ("[%s]を直積/半直積に分解" % group.name())
        print(text)
        text_full = text_full + text + "\n"
        #
        if group.is_simple():
            text = ("[%s]は単純群です." % group.name())
            print(text)
            text_full = text_full + text + "\n"
            #
            return text_full[:-1]
        #End if
        #
        text = "(注意: 積の右側は同型を除いて一意的)"
        text = text + ("\n分解対象: Name(Order) = %s(%d)" 
                       % (group.name(),group.order()))
        print(text)
        text_full = text_full + text + "\n"
        #
        grouplist = group.all_normalsub()[1:-1]
        omit = []
        text = "\n直積への分解:\n(\'x\' means \'times\')"
        print(text)
        text_full = text_full + text + "\n"
        #
        for normal1 in grouplist:
            if normal1.order() ** 2 < group.order(): break
            for normal2 in grouplist:
                if not group.order() == normal1.order() * normal2.order():
                    continue
                #End if
                result, group1 = normal1.try_cartesian_product(normal2)
                if not group1 == group: continue
                if not result == "times": continue
                omit = omit + [normal1,normal2]
                message1 = ("%s(%d) x %s(%d)" 
                            % (normal1.name(),normal1.order(),
                               normal2.name(),normal2.order()))
                message2 = " <==> "
                for normal3 in [normal1,normal2]:
                    symbol = fg.Classifier.search_isomorphic(normal3)
                    if symbol is None: symbol = "?"
                    message2 = message2 + ("( %s ) x " % symbol)
                #End for
                message2 = message2[:-3]
                text = message1 + message2
                print(text)
                text_full = text_full + text + "\n"
            #End for
        #End for
        #
        text = "\n半直積への分解:\n(\'r\' means \'rtimes\')"
        print(text)
        text_full = text_full + text + "\n"
        #
        for normal in grouplist:
            if normal in omit: continue
            embedding = group.try_quotient_decomposition(normal)
            if embedding is None: continue
            message1 = ("%s(%d) r %s(%d)" 
                        % (normal.name(),normal.order(),
                           embedding.name(),embedding.order()))

            #End if
            message2 = " <==> "
            for group1 in [normal,embedding]:
                symbol = fg.Classifier.search_isomorphic(group1)
                if symbol is None: symbol = "?"
                message2 = message2 + ("( %s ) r " % symbol)
            #End for
            message2 = message2[:-3]
            text = message1 + message2
            print(text)
            text_full = text_full + text + "\n"
        #End for
        #
        self._update()
        return text_full[:-1]
    #End def

    def info(self,group):
        text_full = "\n"
        #
        text = ("[%s]の情報を表示:\n" % group.name())
        print(text)
        text_full = text_full + text + "\n"
        #
        symbol = fg.Classifier.search_isomorphic(group)
        if symbol is None: symbol = "?"
        text = "Name\tOrder\tIsomorphic\n"
        text = text + ("%s\t%d\t%s\n" % (group.name(),group.order(),symbol))
        print(text)
        text_full = text_full + text + "\n"
        #
        t_list = ["" for i in range(4)]
        t_list[0] = ("IsAbelian:\t%s" % str(group.is_abelian()))
        t_list[1] = ("IsPerfect:\t%s" % str(group.is_perfect()))
        t_list[2] = ("IsSolvable:\t%s" % str(group.is_solvable()))
        t_list[3] = ("IsSimple:\t%s" % str(group.is_simple()))
        text = ""
        for tmp_text in t_list: text = text + tmp_text + "\n"
        text = text[:-1]
        print(text)
        text_full = text_full + text + "\n"
        #
        t_list = [self.element(group),
                  self.table(group),
                  self.center(group),
                  self.derived_series(group),
                  self.conjugacy_class(group),
                  self.normalsub(group),
                  self.decompose(group)]
        for tmp_text in t_list: text_full = text_full + tmp_text + "\n\n"
        text_full = text_full[:-1]
        #
        text_full = text_full + "\n以上.\n"
        #
        self._update()
        return text_full[:-1]
    #End def

    def generate_group(self,indexlist):
        text_full = "\n"
        #
        rulebook = self._rulebook
        for index in indexlist:
            if not index in rulebook.master_group.element():
                print("要素[%s]は存在しません." % str(index))
                return False
            #End if
        #End for
        group = rulebook.generate_group(frozenset(indexlist),False)
        text = "指定の生成元から群を生成しました.\n生成元:\n" + str(indexlist)
        print(text)
        text_full = text_full + text + "\n"
        #
        symbol = fg.Classifier.search_isomorphic(group)
        if symbol is None: symbol = "?"
        text = "Name\tOrder\tIsomorphic\n"
        text = text + ("%s\t%d\t%s" % (group.name(),group.order(),symbol))
        print(text)
        text_full = text_full + text + "\n"
        #
        self._update()
        return text_full[:-1]
    #End def
    
    def product(self,indexlist):
        text_full = "\n"
        #
        new = self._rulebook.prod(indexlist)
        text = str(new)
        print(text)
        text_full = text_full + text + "\n"
        #
        self._update()
        return text_full[:-1]
    #End def
    
    def inverse(self,index):
        text_full = ""
        #
        inv = self._rulebook.inverse(index)
        text = str(inv)
        text_full = text_full + text + "\n"
        #
        self._update()
        return text_full[:-1]
    #End def
    
    def who(self,group):
        text_full = "\n"
        #
        symbol = fg.Classifier.search_isomorphic(group)
        if symbol is None: symbol = "?"
        text = "Name\tOrder\tIsomorphic\n"
        text = text + ("%s\t%d\t%s\n" % (group.name(),group.order(),symbol))
        print(text)
        text_full = text_full + text
        #
        text = self.decompose(group)
        print("\n" + text)
        text_full = text_full + text + "\n"
        #
        self._update()
        return text_full[:-1]
    #End def
    
    def quotient(self,group1,group2):
        if not group2.is_normalsub_of(group1): return "正規部分群ではありません."
        #
        text_full = "\n"
        #
        quotient = group1.generate_quotient(group2)
        text = ("剰余群 %s/%s\n" % (group1.name(),group2.name()))
        print(text)
        text_full = text_full + text + "\n"
        #
        text1 = ("位数:\t%d\n\n" % quotient.order)
        text2 = "代表元:\n" + str(quotient.residue) + "\n\n"
#        text3 = "Mod:\n" + str(sorted(list(group2.element()))) + "\n\n"
        text4 = "乗積表:\n" + str(quotient.subtable) 
        text = text1 + text2 + text4
        print(text)
        text_full = text_full + text + "\n"
        #
        self._update()
        return text_full[:-1]
    #End def
#End class


####
def main():
    pass
#End def

## thtmodule のimport確認
def import_print():
    print("[thtapp.py]がインポートされました.")
    return True
#End def

if __name__ == '__main__':
    main()
else:
#    import_print()
    pass
#End if