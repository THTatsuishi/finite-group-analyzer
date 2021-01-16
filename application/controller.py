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
    def message(self, text: str):
        """
        メッセージを表示。

        Parameters
        ----------
        text : str
            DESCRIPTION.

        Returns
        -------
        None.

        """
        pass
    
    @abstractmethod
    def calc_start(self, text: str):
        """
        計算の開始を把握するためのメソッド。

        Parameters
        ----------
        text : str
            計算開始を表す文章。

        Returns
        -------
        None.

        """
        pass
    
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
    
    @abstractmethod
    def calc_end(self, text: str):
        """
        計算の終了を把握するためのメソッド。

        Parameters
        ----------
        text : str
            計算終了を表す文章。

        Returns
        -------
        None.

        """
        pass

class NullController(Controller):
    """
    コントローラーを指定しない場合に用いるダミーのコントローラー。
    何の機能も持たない。
    
    """
    def calc_start(self, text: str):
        pass
    def calc_progress(self, text: str):
        pass
    def calc_end(self, text: str):
        pass

class ConsoleController(Controller):
    """
    コンソール出力のみを扱うコントローラー。
    
    """
    def message(self, text: str):
        print(text)
    def calc_start(self, text: str):
        print(text)
    def calc_progress(self, text: str):
        print("\r"+text,end ="")
    def calc_end(self, text: str):
        print("\n"+text)

class APPController(Controller):
    """
    アプリケーションを制御するためのコントローラー。
    
    """
    def calc_progress(self, text: str):
        print(text)
        
    


