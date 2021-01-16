"""
プログラム全体の処理を担う。
"""
from application.controller import ConsoleController
from application.calc import matcal
from application.calc.group import MasterGroup
from application.view import AppWindow

class AppServise(object):
    _errmsg_format = "書式が不適切です。"
    _errmsg_cmd = "コマンド名が不適切です。"
    _errmsg_expr = "引数が不適切です。"
    _errmsg_exec = "コマンド実行エラー。"
    
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
        
    def _create_cmd_func_dict(self):
        return {
            "?": self._cmd_overview_of,
            }
     
    def _exec_cmd(self, cmd_text):
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
        except Exception:
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
        text = ("作成された群の一覧：\nName\tOrder")
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
        return f'order:\t{group.order}'

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