"""
アプリ画面。
"""
import tkinter
import tkinter.scrolledtext
import tkinter.ttk

class AppWindow(object):
    def __init__(self, exec_cmd):
        self._exec_cmd = exec_cmd
        self._text_ini = "デフォルトメッセージ"
        self._cmd_count = 0
    
    def __call__(self):
        self._app_window()
    
    @property
    def text_ini(self):
        return self._text_ini
    
    @text_ini.setter
    def text_ini(self, value):
        if value is None: return
        self._text_ini = value
    
    def _app_window(self):
        main_width = 60
        main_height = 30
        #
        root = tkinter.Tk()
        root.title("有限群解析プログラム")
        root.minsize(250,250)
        root.columnconfigure(0, weight=1)
        root.rowconfigure(1, weight=1)
        #
        n_row = 0
        cmd_window = tkinter.Entry(root,width=main_width)
        cmd_window.insert('0',"コマンドを入力してEnterで実行")
        cmd_window.grid(column=0, row=n_row, 
                        sticky=tkinter.EW, padx=20, pady=20)
        self.cmd_window = cmd_window
        #
        n_row += 1
        result_window = tkinter.scrolledtext.ScrolledText(
                root,height=main_height,width=main_width)
        result_window.insert('1.0',self._text_ini)
        result_window.configure(state='disable')
        result_window.grid(column=0, row=n_row, 
                           sticky=tkinter.NSEW, padx=20, pady=0)
        self.result_window = result_window
        #
        n_row += 1
        sizegrip = tkinter.ttk.Sizegrip(root)
        sizegrip.grid(column=0, row=n_row,
                      sticky=tkinter.NSEW, padx=0, pady=0)
        #
        root.bind('<Return>', self._pressed_entere)
        root.mainloop()

    def _pressed_entere(self,event):
        """
        Enterキー押下時の処理。
        ただし、コマンドが空文字ならば何もしない。
        """
        # コマンド入力欄からコマンド文字列を取得
        cmd_text = self.cmd_window.get()
        # コマンド文字列が空文字なら処理終了
        if cmd_text == "": return
        # コマンド実行回数    
        self._cmd_count += 1
        # 実行内容を出力
        self._print_command(cmd_text)
        # 実行結果を取得
        result = self._exec_cmd(cmd_text)
        # 実行結果を出力
        self._print_result(result)
        
    def _print_command(self, cmd_text: str):
        """
        コマンド画面に記入された文字列をメイン画面に出力する。
        """
        text1 = ("\n\nIn [%d]:" % self._cmd_count)
        text2 = (" %s\n-> " % cmd_text)
        self.cmd_window.delete(0,tkinter.END)
        self.result_window.configure(state='normal')
        #
        self.result_window.insert('end',text1)
        self.result_window.tag_configure('Blue', background="#00ffff")
        self.result_window.tag_add('Blue',"insert linestart","insert lineend")
        self.result_window.insert('end',text2)
        #
        self.result_window.configure(state='disable')
        self.result_window.see('end')

    def _print_result(self, result: str):
        """
        コマンド実行結果の文字列をメイン画面に出力する。
        """
        self.cmd_window.delete(0,tkinter.END)
        self.result_window.configure(state='normal')
        self.result_window.insert('end',result)
        self.result_window.configure(state='disable')
        self.result_window.see('end')

if __name__ == '__main__':
    AppWindow(None)()