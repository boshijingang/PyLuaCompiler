import ast
from enum import Enum

class OpCode(Enum):
    OP_MOVE = 0
    OP_LOADK = 1
    OP_LOADKX = 2
    OP_LOADBOOL = 3
    OP_LOADNIL = 4
    OP_GETUPVAL = 5
    OP_GETTABUP = 6
    OP_GETTABLE = 7
    OP_SETTABUP = 8
    OP_SETUPVAL = 9
    OP_SETTABLE = 10
    OP_NEWTABLE = 11
    OP_SELF = 12
    OP_ADD = 13
    OP_SUB = 14
    OP_MUL = 15
    OP_MOD = 16
    OP_POW = 17
    OP_DIV = 18
    OP_IDIV = 19
    OP_BAND = 20
    OP_BOR = 21
    OP_BXOR = 22
    OP_SHL = 23
    OP_SHR = 24
    OP_UNM = 25
    OP_BNOT = 26
    OP_NOT = 27
    OP_LEN = 28
    OP_CONCAT = 29
    OP_JMP = 30
    OP_EQ = 31
    OP_LT = 32
    OP_LE = 33
    OP_TEST = 34
    OP_TESTSET = 35
    OP_CALL = 36
    OP_TAILCALL = 37
    OP_RETURN = 38
    OP_FORLOOP = 39
    OP_FORPREP = 40
    OP_TFORCALL = 41
    OP_TFORLOOP = 42
    OP_SETLIST = 43
    OP_CLOSURE = 44
    OP_VARARG = 45
    OP_EXTRAARG = 46

class LocalVarInfo:
    def __init__(self, name, prev, scope_level, slot):
        self.name = name
        self.prev = prev
        self.scope_level = scope_level
        self.slot = slot

class FunctionInfo:
    def __init__(self, parent, func_def_exp):
        self.parent = parent
        self.sub_func_list = []
        self.local_var_list = []
        self.local_var_table = {}
        self.constants_table = {}
        self.unvalue_table = {}
        self.break_list = []
        self.inst_list = []
        self.scope_level = 0
        self.used_reg = 0
        self.max_reg = 0
        self.param_num = len(func_def_exp.parlist)
        self.is_var_arg = func_def_exp.is_var_arg

    def add_local_vars(self, names):
        for name in names:
            self.add_local_var(name)

    def add_local_var(self, name):
        local_var = LocalVarInfo(name, self.local_var_table.get(name), self.scope_level, self.alloc_reg())
        self.local_var_list.append(local_var)
        self.local_var_table[name] = local_var
        return local_var.slot
    
    def exit_scope(self):
        pass

    def alloc_reg(self):
        self.used_reg = self.used_reg + 1
        if self.used_reg >= 255:
            raise Exception("function or expression needs too many registers")
        if self.used_reg > self.max_reg:
            self.max_reg = self.used_reg
        return self.used_reg - 1

    def free_reg(self):
        if self.used_reg <= 0:
            raise Exception("used_reg <= 0")
        self.used_reg = self.used_reg - 1

    def emit_ABC(self, op, a, b, c):
        pass

    def emit_return(self, first_slot, num):
        self.emit_ABC(OpCode.OP_RETURN, first_slot, num+1, 0)

class CodeGenerator:
    def __init__(self):
        super().__init__()

    def gen_entry_proto(self, main_block):
        entry_fd = ast.FunctionDefExp([], True, None)
        entry_fi = FunctionInfo(None, entry_fd)
        entry_fi.add_local_var('_ENV')
        main_fd = ast.FunctionDefExp([], True, main_block)
        self.gen_func_def_exp(entry_fi, main_fd)

    def gen_func_def_exp(self, fi, fd):
        sub_fi = FunctionInfo(fi, fd)
        sub_fi.add_local_vars(fd.parlist)
        self.gen_block(sub_fi, fd.body)
        sub_fi.exit_scope()
        sub_fi.emit_return(0, 0)

    def gen_block(self, fi, block):
        pass
