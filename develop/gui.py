# -*- coding: utf-8 -*-

#####################################
# Python 3.7
# 作成者: 立石卓也
# 作成時所属: 北海道大学 素粒子論研究室
#####################################

import tkinter
import tkinter.scrolledtext
import tkinter.ttk
#

#### GUIを作成
class GUI(object):
    def __init__(self,rulebook,cmd):
        self.rulebook = rulebook
        self.cmd = cmd
        self.interpreter = Interpreter(rulebook,cmd)
        #
        self.thtapp()
    #End def
    
    def __call__(self):
        self.thtapp()
    #End def
    
    def thtapp(self):
        main_width = 60
        main_height = 30
        
        root = tkinter.Tk()
        root.title("有限群解析プログラム")
        root.minsize(250,250)
        root.columnconfigure(0, weight=1)
        root.rowconfigure(1, weight=1)

        n_row = -1

        n_row += 1
        cmd_window = tkinter.Entry(root,width=main_width)
        cmd_window.insert('0',"コマンドを入力してEnterで実行")
        cmd_window.grid(column=0, row=n_row, 
                        sticky=tkinter.EW, padx=20, pady=20)
        self.cmd_window = cmd_window
        
        n_row += 1
        master = self.rulebook.master_group
        text_ini = ("位数 %d の群[%s]が生成されました." % (master.order(),master.name()))
        result_window = tkinter.scrolledtext.ScrolledText(
                root,height=main_height,width=main_width)
        result_window.insert('1.0',text_ini)
        result_window.configure(state='disable')
        result_window.grid(column=0, row=n_row, 
                           sticky=tkinter.NSEW, padx=20, pady=0)
        self.result_window = result_window
        
        n_row += 1
        sizegrip = tkinter.ttk.Sizegrip(root)
        sizegrip.grid(column=0, row=n_row,
                      sticky=tkinter.NSEW, padx=0, pady=0)
        
        root.bind('<Return>', self.jikkou)
        root.mainloop()
    #End def

    # enter を押してコマンド実行
    cmd_count = 0
    def jikkou(self,event):
        self.cmd_count += 1
        #
        cmd_text = self.cmd_window.get()
        if cmd_text == "":
            self.cmd_count -= 1
            return True
        #End if        
        self.print_command(cmd_text)
        
        result = self.interpreter(cmd_text)
        self.print_result(result)
        
    #End def  
        
    def print_command(self,cmd_text):
        text1 = ("\n\nIn [%d]:" % self.cmd_count)
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
    #End def

    def print_result(self,result):
        self.cmd_window.delete(0,tkinter.END)
        self.result_window.configure(state='normal')
        self.result_window.insert('end',result)
        self.result_window.configure(state='disable')
        self.result_window.see('end')
    #End def
#end def

# コマンド解釈用のクラス
class Interpreter(object):
    def __init__(self,rulebook,cmd):
        self.rulebook = rulebook
        self.cmd = cmd
    #End def
    
    error_massage1 = "コマンドを解釈できませんでした"
    error_message2 = "引数が不適切です"
    def __call__(self,cmd_text):
        # command[expr] -> command, expr
        command, expr = self.command_expr(cmd_text)
        if command == "False": return self.error_massage1
        # command の種別を特定
        commandtype = self.search_command(command)
        if commandtype == None: return self.error_massage1
        # 引数を分割
        expr_list = self.split_expr(expr)
        if expr_list == "False": return self.error_message2
        # 引数の種別を特定
        expr_type, expr_list = self.search_expr(expr_list)
        if expr_type == "False": return self.error_message2
        #
        result = self.exec_command(commandtype,command,expr_type,expr_list)   
        if result == "False": return self.error_message2
        return result
    #End def
    
    # command と expr に分離
    def command_expr(self,cmd_text):
        ini = cmd_text.find("[")
        fin = cmd_text.rfind("]")
        if not ( 0 <= ini < fin == (len(cmd_text)-1) ): return "False", "False"
        cmd_name = cmd_text[0:ini]
        expr = cmd_text[ini+1:fin]
        return cmd_name, expr
    #End def
    
    #
    cmd_list_none = []
    cmd_list_index = ["Mat","GenerateGroup","Product","Inverse"]
    cmd_list_group = ["Element","Table","ConjugacyClass","ConjugacyCount",
                      "NormalSub","SubGroup","Center","DerivedSeries",
                      "Generator","Decompose","Info","?","Quotient"]
    cmd_list_composite = []
    cmd_list_other = []
    
    cmd_all = [cmd_list_none,
               cmd_list_index,
               cmd_list_group,
               cmd_list_composite,
               cmd_list_other]
    cmd_type_name = ["none","index","group","composite","other"]
    
    # [command] の種別を特定
    def search_command(self,command):
        for i in range(len(self.cmd_all)):
            if command in self.cmd_all[i]: return self.cmd_type_name[i]
        #End for
        return None
    #End def
    
    # [expr] をカンマで分割 -> [expr1,expr2,...]
    def split_expr(self,expr):
        if expr == "": return []
        expr = expr.replace(' ','')
        expr_list = expr.split(",")
        if "" in expr_list: return "False"
        return expr_list
    #End def
    
    # 引数の種別を特定
    # none, index, group, composite
    def search_expr(self,expr_list):
        if len(expr_list) == 0: return "none", []
        new_list = []
        type_set = set()
        for expr in expr_list:
            index_ = self.is_index(expr)
            if index_ != "False":
                new_list.append(("index",index_))
                type_set.add("index")
                continue
            #End if
            group_ = self.search_group(expr)
            if group_ != None:
                new_list.append(("group",group_))
                type_set.add("group")
                continue
            #End if
            return "False", "False"
        #End for
        if len(type_set) > 1: return "composite", new_list
        return new_list[0][0], new_list
    #End
    
    # [expr] -> index or "False"
    def is_index(self,expr):
        try:
            integer = int(expr)
        except ValueError:
            return "False"
        #End try
        if (0 <= integer < (self.rulebook.max_order-1)): return integer
        else: return "False"
    #End def
    
    # [expr] -> group or None
    def search_group(self,expr):
        return self.rulebook.search_name(expr)
    #End def
    
    ####
    ####
    ####
    
    def exec_command(self,commandtype,command,expr_type,expr_list):
        if commandtype in ["none","index","group","composite"]:
            if commandtype != expr_type: return "False"
        #End if
        if commandtype == "none":
            result = self.exec_cmd_none(command)
        elif commandtype == "index":
            result = self.exec_cmd_index(command,expr_list)
        elif commandtype == "group":
            result = self.exec_cmd_group(command,expr_list)
        elif commandtype == "composite":
            result = self.exec_cmd_composite(command,expr_list)
        else:
            result = self.exec_cmd_other(command,expr_list)
        #End if
        return result
    #End def
    
    def exec_cmd_none(self,command):
        return "未実装"
    #End def
    def exec_cmd_index(self,command,expr_list):
        indexlist = []
        for expr in expr_list: indexlist.append(expr[1])
        if command == "Mat":
            result = self.cmd.mat(indexlist)
            return result
        elif command == "GenerateGroup":
            result = self.cmd.generate_group(indexlist)
            return result
        #End if
        elif command == "Product":
            result = self.cmd.product(indexlist)
            return result
        #End if
        elif command == "Inverse":
            result = ""
            for index in indexlist:
                result = result + self.cmd.inverse(index) + ", "
            #End for
            return result[:-2]

        return "未実装"
    #End def
    def exec_cmd_group(self,command,expr_list):
        if command == "Element":
            result = ""
            for dummy, group in expr_list:
                result = result + self.cmd.element(group) + "\n"
            #End for
            return result[:-1]
        elif command == "Table":
            result = ""
            for dummy, group in expr_list:
                result = result + self.cmd.table(group) + "\n"
            #End for
            return result[:-1]
        #End if
        elif command == "ConjugacyClass":
            result = ""
            for dummy, group in expr_list:
                result = result + self.cmd.conjugacy_class(group) + "\n"
            #End for
            return result[:-1]
        elif command == "ConjugacyCount":
            result = ""
            for dummy, group in expr_list:
                result = result + self.cmd.conjugacy_count(group) + "\n"
            #End for
            return result[:-1]
        elif command == "NormalSub":
            result = ""
            for dummy, group in expr_list:
                result = result + self.cmd.normalsub(group) + "\n"
            #End for
            return result[:-1]
        elif command == "SubGroup":
            result = ""
            for dummy, group in expr_list:
                result = result + self.cmd.subgroup(group) + "\n"
            #End for
            return result[:-1]
        elif command == "Center":
            result = ""
            for dummy, group in expr_list:
                result = result + self.cmd.center(group) + "\n"
            #End for
            return result[:-1]
        elif command == "DerivedSeries":
            result = ""
            for dummy, group in expr_list:
                result = result + self.cmd.derived_series(group) + "\n"
            #End for
            return result[:-1]
        elif command == "Generator":
            result = ""
            for dummy, group in expr_list:
                result = result + self.cmd.generator(group) + "\n"
            #End for
            return result[:-1]
        elif command == "Decompose":
            result = ""
            for dummy, group in expr_list:
                result = result + self.cmd.decompose(group) + "\n"
            #End for
            return result[:-1]
        elif command == "Info":
            result = ""
            for dummy, group in expr_list:
                result = result + self.cmd.info(group) + "\n"
            #End for
            return result[:-1]
        elif command == "?":
            result = ""
            for dummy, group in expr_list:
                result = result + self.cmd.who(group) + "\n"
            #End for
            return result[:-1]
        elif command == "Quotient":
            if len(expr_list) != 2: return "引数が不適切です."
            
            return self.cmd.quotient(expr_list[0][1],expr_list[1][1])
        
        #End if
        return "未実装"
    #End def
    def exec_cmd_composite(self,command,expr_list):
        return "未実装"
    #End def
    def exec_cmd_other(self,command,expr_list):
        return "未実装"
    #End def
#End class

    
####
def main():
    pass
#End def
#
##  のimport確認
def import_print():
    print("[gui.py]がインポートされました.")
    return True
#End def
#
if __name__ == '__main__':
    main()
else:
#    import_print()
    pass
#End if