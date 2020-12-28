"""
アプリ制御用のモジュール。
"""  
from abc import ABCMeta
from abc import abstractmethod

class Controller(metaclass = ABCMeta):
    """
    コントローラー。
    画面部分や計算部分をつなぐための抽象クラス。
    
    """
    @abstractmethod
    def calc_progress(self, text: str):
        """
        主に時間のかかる計算の進捗を把握するためのメソッド。

        Parameters
        ----------
        text : str
            計算の進捗を表す文章。

        Returns
        -------
        None.

        """
        pass

class NullController(Controller):
    """
    コントローラーを指定しない場合に用いるダミーのコントローラー。
    何の機能も持たない。
    Singletonパターン。
    
    """
    _instance = None
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

class ConsoleController(Controller):
    """
    コンソール出力のみを扱うコントローラー。
    
    """
    def calc_progress(self, text: str):
        print(text)


class APPController(Controller):
    """
    アプリケーションを制御するためのコントローラー。
    
    """
    def calc_progress(self, text: str):
        print(text)
        
    


