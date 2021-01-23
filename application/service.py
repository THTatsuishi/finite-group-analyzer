"""
プログラム全体の処理を担う。
"""
import traceback;
from application.controller import ConsoleController
from application.calc import matcal
from application.calc.group import MasterGroup
from application.view import AppWindow

class AppServise(object):
    def _create_cmd_func_dict(self):
        """
        解析画面で使用するコマンド名と処理メソッドの対応辞書を作成する。
        """
        return {
            # 概要
            "?": self._cmd_overview_of,
            # 要素の一覧
            "Elements": self._cmd_elements,
            # 乗積表
            "Table": self._cmd_cayley_table,
            # 共役類の一覧
            "ConjClass": self._cmd_conj_class,
            # 共役類のカウント
            "ConjCount": self._cmd_conj_count,
            # 群同型
            "Isomorphic": self._cmd_isomorphic,
            # 可換群であるか
            "IsAbelian": self._cmd_is_abelian,
            # 完全群であるか
            "IsPerfect": self._cmd_is_perfect,
            # 可解群であるか
            "IsSolvable": self._cmd_is_solvable,
            # 単純群であるか
            "IsSimple": self._cmd_is_simple,
            # 中心
            "Center": self._cmd_center,
            # 中心化群
            "Centrizer": self._cmd_centrizer,
            # 導来部分群
            "Derived": self._cmd_derived,
            # 導来列
            "DerivedSeries": self._cmd_derived_series,
            # 正規部分群の一覧
            "Normal": self._cmd_normal,
            # 直積分解
            "DirectDecompose": self._cmd_direct_decompose,
            # 直積分解
            "SemidirectDecompose": self._cmd_semidirect_decompose,
            # 直積/半直積分解
            "Decompose": self._cmd_decompose,
            }
        
    _errmsg_format = "書式が不適切です。"
    _errmsg_cmd = "コマンド名が不適切です。"
    _errmsg_expr = "引数が不適切です。"
    _errmsg_exec = "プログラムエラー：実行時エラー"
    _errmsg_not_implemented = "プログラムエラー：未完成"
    
    def __init__(self, generators, zero_base, maximal):
        self._cmd_func_dict = self._create_cmd_func_dict()
        self._console_ctrl = ConsoleController()
        self._master = self._generate_master(generators, zero_base, maximal)
        maximal = self._master.maximal_group
        self._console_ctrl.message(
            "\n以下の群を生成しました:\n"+
            "Name\tOrder\n"+
            f'{maximal.name}\t{maximal.order}'
            )
        self._app_window = AppWindow(self._exec_cmd)
    
    def __call__(self):
        self._console_ctrl.message(
            "\n解析画面を開きました。\n"+
            "以降は解析画面上で操作してください。"
            )
        self._app_window.text_ini = self._create_text_ini()
        self._app_window()
        self._console_ctrl.message(
            "\n解析画面を閉じました。\n"+
            "再び解析画面を開くには、コンソールに app() と入力して実行してください。"
            )
        
    def _exec_cmd(self, cmd_text):
        """
        解析画面上に入力されたコマンドを実行する。
        """
        # コマンドと引数に分離
        divide_result = self._divide_command_expr(cmd_text)
        if not divide_result.has_value:
            return self._errmsg_format
        # コマンド関数を取得
        cmd_func = self._cmd_to_func(divide_result.cmd)
        if cmd_func is None:
            return self._errmsg_cmd
        # 引数の群を取得
        group = self._name_to_group(divide_result.expr)
        if group is None:
            return self._errmsg_expr
        # コマンド関数実行
        try:
            return cmd_func(group)
        except NotImplementedError:
            print(traceback.format_exc())
            return self._errmsg_not_implemented
        except Exception:
            print(traceback.format_exc())
            return self._errmsg_exec
    
    def _generate_master(self, generators, zero_base, maximal):
        """
        行列表示の生成元を与えて群を生成する。
        """
        ctrl = self._console_ctrl
        # TODO:引数チェックを追加する
        result = matcal.generate_group(generators, zero_base, maximal,ctrl)
        if not result.has_value:
            raise Exception("閉じた群の生成に失敗しました。")
        result = matcal.calc_cayleytable(result.value, zero_base, ctrl)
        if not result.has_value:
            raise Exception("乗積表の作成に失敗しました。")
        master = MasterGroup(result.value)
        master.group_initial  = "g"
        return master
    
    def _create_text_ini(self) -> str:
        """
        作成された群の一覧を表す文字列を作成する。
        """
        text = "作成された群の一覧：\nName\tOrder"
        for group in self._master.all_groups:
            text += f'\n{group.name}\t{group.order}'
        return text
    
    def _divide_command_expr(self, cmd_text):
        """
        コマンドと引数に分離する。
        """
        ini = cmd_text.find("[")
        fin = cmd_text.rfind("]")
        if not 0 <= ini < fin == (len(cmd_text)-1): 
            return CmdExprPair.CreateFailed()
        cmd = cmd_text[0:ini]
        expr = cmd_text[ini+1:fin]
        return CmdExprPair.CreateSucceeded(cmd,expr)
            
    def _cmd_to_func(self, cmd: str):
        if not cmd in self._cmd_func_dict:
            return None
        return self._cmd_func_dict[cmd]
    
    def _name_to_group(self, name: str):
        return self._master.name_to_group(name)
    
    def _cmd_overview_of(self, group):
        text = (
            f'{group.name} の概要：\n'+
            "Name\tOrder\tIsomorphic\n"+
            f'{group.name}\t{group.order}\t{group.isomorphic}'
            )
        text += "\n"
        text += f'\nIsAbelian\t\t{group.is_abelian}'
        text += f'\nIsPerfect\t\t{group.is_perfect}'
        text += f'\nIsSimple\t\t{group.is_simple}'
        text += f'\nIsSolvable\t\t{group.is_solvable}'
        text += "\n\n分解パターン"
        text += "\n\n" + self._cmd_direct_decompose(group)
        text += "\n\n" + self._cmd_semidirect_decompose(group)
        return text

    def _cmd_elements(self, group):
        elements = sorted(list(group.elements))
        text = (
            f'{group.name} の要素：\n'+
            f'{elements}'
            )
        return text
    
    def _cmd_cayley_table(self, group):
        table = group.cayley_table
        text = (
            f'{group.name} の乗積表：\n'+
            f'{table}'
            )
        return text
    
    def _cmd_conj_class(self, group):
        conj_classes = group.conjugacy_classes
        text = (
            f'{group.name} の共役類の一覧：\n'+
            "位数\t要素数\t共役類"
            )
        for c in conj_classes:
            elements = sorted(list(c.elements))
            text += f'\n{c.order}\t{c.element_num}\t{elements}'
        return text
    
    def _cmd_conj_count(self, group):
        conj_count = group.conjugacy_count
        text = (
            f'{group.name} の共役類のカウント：\n'+
            "(位数, 要素数, 重複度)の一覧\n"+
            f'{conj_count}'
            )
        return text
    
    def _cmd_isomorphic(self, group):
        text = (f'{group.name} の群同型： {group.isomorphic}\n')
        return text

    def _cmd_is_abelian(self, group):
        result = "可換群" if group.is_abelian else "非可換群"
        text = (f'{group.name} は {result} である。\n')
        return text
    
    def _cmd_is_perfect(self, group):
        result = "完全群" if group.is_perfect else "不完全群"
        text = (f'{group.name} は {result} である。\n')
        return text
    
    def _cmd_is_solvable(self, group):
        result = "可解群" if group.is_solvable else "非可解群"
        text = (f'{group.name} は {result} である。\n')
        return text

    def _cmd_is_simple(self, group):
        result = "ある" if group.is_solvable else "ない"
        text = (f'{group.name} は 単純群で{result}。\n')
        return text

    def _cmd_center(self, group):
        center = group.center
        text = (
            f'{group.name} の中心：\n'+
            "Name\tOrder\tIsomorphic\n"+
            f'{center.name}\t{center.order}\t{center.isomorphic}'
            )
        return text
    
    def _cmd_centrizer(self, group):
        centrizer = group.centrizer
        text = (
            f'{group.name} の中心化群：\n'+
            "Name\tOrder\tIsomorphic\n"+
            f'{centrizer.name}\t{centrizer.order}\t{centrizer.isomorphic}'
            )
        return text
    
    def _cmd_derived(self, group):
        derived = group.derived
        text = (
            f'{group.name} の導来部分群：\n'+
            "Name\tOrder\tIsomorphic\n"+
            f'{derived.name}\t{derived.order}\t{derived.isomorphic}'
            )
        return text
    
    def _cmd_derived_series(self, group):
        series = group.derived_series
        text = (
            f'{group.name} の導来列の一覧：\n'+
            "Name\tOrder\tIsomorphic"
            )
        for g in series:
            text += f'\n{g.name}\t{g.order}\t{g.isomorphic}'
        return text

    def _cmd_normal(self, group):
        normals = group.all_normalsub
        text = (
            f'{group.name} の正規部分群の一覧：\n'+
            "Name\tOrder\tIsAbelian\t\tIsomorphic"
            )
        for g in normals:
            is_abelian = 'Abelian'if g.is_abelian else 'non'
            text += f'\n{g.name}\t{g.order}\t{is_abelian}\t\t{g.isomorphic}'
        return text
    
    def _cmd_direct_decompose(self, group):
        direct_list = group.direct_product
        text = (
            f'{group.name} の直積への分解：\n'+
            "(\'x\' means \'\\times\')\n"+
            "Name(Order)"
            )
        if not direct_list:
            return text + "\n分解なし"
        for data in direct_list:
            left = data.left
            right = data.right
            text += (
                f'\n{left.name}({left.order}) x {right.name}({right.order})'+
                f'\t<==> ( {left.isomorphic} ) x ( {right.isomorphic} )'
                )
        return text
    
    def _cmd_semidirect_decompose(self, group):
        semi_list = group.semidirect_product
        text = (
            f'{group.name} の半直積への分解：\n'+
            "(\'r\' means \'\\rtimes\')\n"+
            "Name(Order)"
            )
        if not semi_list:
            return text + "\n分解なし"
        for data in semi_list:
            left = data.left
            right = data.right
            text += (
                f'\n{left.name}({left.order}) r {right.name}({right.order})'+
                f'\t<==> ( {left.isomorphic} ) r ( {right.isomorphic} )')
        return text

    def _cmd_decompose(self, group):
        text = f'{group.name} の分解：\n'
        text += self._cmd_direct_decompose(group)
        text += "\n\n"
        text += self._cmd_semidirect_decompose(group)   
        return text
    
class CmdExprPair(object):
    def __init__(self, has_value: bool, cmd: str, expr: str):
        self._has_value = has_value
        self._cmd = cmd
        self._expr = expr
        
    @property
    def has_value(self):
        return self._has_value
    
    @property
    def cmd(self):
        return self._cmd
    
    @property
    def expr(self):
        return self._expr
    
    @staticmethod
    def CreateSucceeded(cmd: str, expr: str):
        return CmdExprPair(True,cmd,expr)
    
    @staticmethod
    def CreateFailed():
        return CmdExprPair(False,None,None)

class CmdResult(object):
    def __init(self, has_value: bool, text: str):
        self._has_value = has_value
        self._text = text
        
    @property
    def has_value(self):
        return self._has_value
    
    @property
    def text(self):
        return self._text
    
    @staticmethod
    def CreateSucceeded(text: str):
        return CmdResult(True,text)
    
    @staticmethod
    def CreateFailed():
        return CmdResult(False,None)