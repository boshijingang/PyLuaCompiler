class AstNode:
    def __init__(self, name):
        self.name = name

    def __str__(self):
        return '{%s}'%(self.name)

class Block:
    def __init__(self, stats=[]):
        self.stats = stats

    def __str__(self):
        ret =  '{block}'
        for it in self.stats:
            ret = ret + '\n' + str(it)
        return ret

    def append_stat(self, stat):
        self.stats.extend(stat)

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
    def __init__(self, bool_val, name = 'bool__constant_exp'):
        super().__init__(name)
        self.bool_val = bool_val

class VarargExp(AstNode):
    def __init__(self, name = 'vararg_exp'):
        super().__init__(name)