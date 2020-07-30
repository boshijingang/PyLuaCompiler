class AstNode:
    def __init__(self, name):
        self.name = name

    def __str__(self):
        return '<%s>'%(self.name)
    
    def print(self, pre_num=0):
        pre = "  " * pre_num
        print(pre+str(self))

class Block(AstNode):
    def __init__(self, stats=[], name = 'block'):
        super().__init__(name)
        self.stats = stats
    
    def print(self, pre_num=0):
        pre = "  " * pre_num
        print("%s"%(pre)+str(self))
        print("%s{" % (pre))
        for it in self.stats:
            it.print(pre_num+1)
        print("%s}" % (pre))

    def append_stat(self, stat):
        self.stats.append(stat)

class EmptyStat(AstNode):
    def __init__(self, name = "empty_stat"):
        super().__init__(name)

class BreakStat(AstNode):
    def __init__(self, name = 'break_stat'):
        super().__init__(name)

class LabelStat(AstNode):
    def __init__(self, label, name = 'label_stat'):
        super().__init__(name)
        self.label = label

class GotoStat(AstNode):
    def __init__(self, label, name = 'goto_stat'):
        super().__init__(name)
        self.label = label

class DoStat(AstNode):
    def __init__(self, block, name = 'do_stat'):
        super().__init__(name)
        self.block = block

class WhileStat(AstNode):
    def __init__(self, exp, block, name = 'while_stat'):
        super().__init__(name)
        self.exp = exp
        self.block = block
    
    def print(self, pre_num=0):
        pre = "  " * pre_num
        print("%s"%(pre)+str(self))
        self.exp.print(pre_num+1)
        self.block.print(pre_num+1)

class RepeatStat(AstNode):
    def __init__(self, exp, block, name = 'repeat_stat'):
        super().__init__(name)
        self.exp = exp
        self.block = block

class IfStat(AstNode):
    def __init__(self, exp_list, block_list, name = 'if_stat'):
        super().__init__(name)
        self.exp_list = exp_list
        self.block_list = block_list

class AssignStat(AstNode):
    def __init__(self, var_list, exp_list, name = 'assign_stat'):
        super().__init__(name)
        self.var_list = var_list
        self.exp_list = exp_list

class RetStat(AstNode):
    def __init__(self, exp_list, name = 'ret_stat'):
        super().__init__(name)
        self.exp_list = exp_list
        
class StringExp(AstNode):
    def __init__(self, string, name = 'string_exp'):
        super().__init__(name)
        self.string = string

class BinopExp(AstNode):
    def __init__(self, op_left, op_right, binop, name = 'binop_exp'):
        super().__init__(name)
        self.op_left = op_left
        self.op_right = op_right
        self.binop = binop

class UnopExp(AstNode):
    def __init__(self, op_num, unop, name = 'unop_exp'):
        super().__init__(name)
        self.op_num = op_num
        self.unop = unop

class NilExp(AstNode):
    def __init__(self, name = 'nil_exp'):
        super().__init__(name)

class BoolConstExp(AstNode):
    def __init__(self, bool_val, name = 'bool_constant_exp'):
        super().__init__(name)
        self.bool_val = bool_val

class VarargExp(AstNode):
    def __init__(self, name = 'vararg_exp'):
        super().__init__(name)

class NameExp(AstNode):
    def __init__(self, id_name, name = 'name_exp'):
        super().__init__(name)
        self.name = id_name

class TableAccessExp(AstNode):
    def __init__(self, exp, idx_exp, name = 'table_access_exp'):
        super().__init__(name)
        self.exp = exp
        self.idx_exp = idx_exp

class FunctionCallExp(AstNode):
    def __init__(self, prefix_exp, func_name_exp, args_exp, name = 'function_call_exp'):
        super().__init__(name)
        self.prefix_exp = prefix_exp
        self.func_name_exp = func_name_exp
        self.args_exp = args_exp