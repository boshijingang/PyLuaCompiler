class AstNode:
    tree_tag = '+--- '

    def __init__(self, name):
        self.name = name

    def __str__(self):
        return '<%s>' % (self.name)

    def get_prefix(self, pre_num):
        tag_len = len(self.tree_tag)
        pre = " " * tag_len * pre_num
        count = pre_num
        pre_list = list(pre)
        while count > 0:
            pre_list[(count-1)*tag_len] = '|'
            count = count - 1
        pre = ''.join(pre_list)
        return pre+self.tree_tag

    def print(self, pre_num=0):
        print(self.get_prefix(pre_num)+str(self))


class Block(AstNode):
    def __init__(self, stats=[], name='block'):
        super().__init__(name)
        self.stats = stats

    def print(self, pre_num=0):
        super().print(pre_num)
        for it in self.stats:
            it.print(pre_num+1)

    def append_stat(self, stat):
        self.stats.append(stat)


class EmptyStat(AstNode):
    def __init__(self, name="empty_stat"):
        super().__init__(name)


class BreakStat(AstNode):
    def __init__(self, name='break_stat'):
        super().__init__(name)


class LabelStat(AstNode):
    def __init__(self, label, name='label_stat'):
        super().__init__(name)
        self.label = label


class GotoStat(AstNode):
    def __init__(self, label, name='goto_stat'):
        super().__init__(name)
        self.label = label


class DoStat(AstNode):
    def __init__(self, block, name='do_stat'):
        super().__init__(name)
        self.block = block


class WhileStat(AstNode):
    def __init__(self, exp, block, name='while_stat'):
        super().__init__(name)
        self.exp = exp
        self.block = block

    def print(self, pre_num=0):
        super().print(pre_num)
        self.exp.print(pre_num+1)
        self.block.print(pre_num+1)


class RepeatStat(AstNode):
    def __init__(self, exp, block, name='repeat_stat'):
        super().__init__(name)
        self.exp = exp
        self.block = block


class IfStat(AstNode):
    def __init__(self, exp_list, block_list, name='if_stat'):
        super().__init__(name)
        self.exp_list = exp_list
        self.block_list = block_list


class AssignStat(AstNode):
    def __init__(self, var_list, exp_list, name='assign_stat'):
        super().__init__(name)
        self.var_list = var_list
        self.exp_list = exp_list

    def print(self, pre_num=0):
        super().print(pre_num)
        for it in self.var_list:
            it.print(pre_num+1)
        for it in self.exp_list:
            it.print(pre_num+1)


class RetStat(AstNode):
    def __init__(self, exp_list, name='ret_stat'):
        super().__init__(name)
        self.exp_list = exp_list
    
    def print(self, pre_num=0):
        super().print(pre_num)
        for it in self.exp_list:
            it.print(pre_num+1)

class StringExp(AstNode):
    def __init__(self, string, name='string_exp'):
        super().__init__(name)
        self.string = string

    def __str__(self):
        return '<%s "%s">'%(self.name, self. string)


class BinopExp(AstNode):
    def __init__(self, op_left, op_right, binop, name='binop_exp'):
        super().__init__(name)
        self.op_left = op_left
        self.op_right = op_right
        self.binop = binop

    def __str__(self):
        return '<%s %s>'%(self.name, str(self.binop))

    def print(self, pre_num=0):
        super().print(pre_num)
        self.op_left.print(pre_num+1)
        self.op_right.print(pre_num+1)


class UnopExp(AstNode):
    def __init__(self, op_num, unop, name='unop_exp'):
        super().__init__(name)
        self.op_num = op_num
        self.unop = unop

    def __str__(self):
        return '<%s %s>'%(self.name, str(self.unop))

    def print(self, pre_num=0):
        super().print(pre_num)
        self.op_num.print(pre_num+1)


class NilExp(AstNode):
    def __init__(self, name='nil_exp'):
        super().__init__(name)


class BoolConstExp(AstNode):
    def __init__(self, bool_val, name='bool_constant_exp'):
        super().__init__(name)
        self.bool_val = bool_val

    def __str__(self):
        return '<%s %d>'%(self.name, self. bool_val)


class VarargExp(AstNode):
    def __init__(self, name='vararg_exp'):
        super().__init__(name)


class NameExp(AstNode):
    def __init__(self, id_name, name='name_exp'):
        super().__init__(name)
        self.id_name = id_name
    
    def __str__(self):
        return '<%s %s>'%(self.name, self. id_name)

class TableAccessExp(AstNode):
    def __init__(self, exp, idx_exp, name='table_access_exp'):
        super().__init__(name)
        self.exp = exp
        self.idx_exp = idx_exp

    def print(self, pre_num=0):
        super().print(pre_num)
        self.exp.print(pre_num+1)
        self.idx_exp.print(pre_num+1)


class FunctionCallExp(AstNode):
    def __init__(self, prefix_exp, args_exp, name='function_call_exp'):
        super().__init__(name)
        self.prefix_exp = prefix_exp
        self.args_exp = args_exp

    def print(self, pre_num=0):
        super().print(pre_num)
        self.prefix_exp.print(pre_num+1)
        for it in self.args_exp:
            it.print(pre_num+1)

class FunctionDefExp(AstNode):
    def __init__(self, parlist, is_var_arg, body, name = 'function_def_exp'):
        super().__init__(name)
        self.parlist = parlist
        self.is_var_arg = is_var_arg
        self.body = body
    
    def print(self, pre_num=0):
        super().print(pre_num)
        for it in self.parlist:
            it.print(pre_num+1)
        self.body.print(pre_num+1)

class IntegerExp(AstNode):
    def __init__(self, int_val, name = 'integer_exp'):
        super().__init__(name)
        self.int_val = int_val

    def __str__(self):
        return '<%s %d>'%(self.name, self. int_val)

class FloatExp(AstNode):
    def __init__(self, float_val, name = 'float_exp'):
        super().__init__(name)
        self.float_val = float_val

    def __str__(self):
        return '<%s %f>'%(self.name, self. float_val)