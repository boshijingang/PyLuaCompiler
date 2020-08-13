import ast
from enum import Enum

SIZE_C = 9
SIZE_B = 9
SIZE_Bx = (SIZE_C + SIZE_B)
SIZE_A = 8
SIZE_Ax = (SIZE_C + SIZE_B + SIZE_A)
SIZE_OP = 6
POS_OP = 0
POS_A = (POS_OP + SIZE_OP)
POS_C = (POS_A + SIZE_A)
POS_B = (POS_C + SIZE_C)
POS_Bx = POS_C
POS_Ax = POS_A
INS_MASK = 0xffffffff
MAXARG_Bx = (1 << 18) - 1
MAXARG_sBx = MAXARG_Bx >> 1
MAXARG_A = ((1 << SIZE_A)-1)
MAXARG_B = ((1 << SIZE_B)-1)
MAXARG_C = ((1 << SIZE_C)-1)


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


class Prototype:
    def __init__(self, parent):
        # 固定参数的数目
        self.num_params = 0
        # 是否可变参数函数
        self.is_vararg = False
        # 函数用到最大的寄存器数目
        self.max_stack_size = 0
        # 常量列表
        self.k_list = []
        # 局部变量列表
        self.local_val_list = []
        # upvalue列表
        self.upvalue_list = []
        # 指令列表
        self.inst_list = []
        # 内部定义函数列表
        self.sub_proto_list = []
        self.parent = parent

    def dump(self):
        self.print_header()
        self.print_code()
        self.print_detail()
        for p in self.sub_proto_list:
            p.dump()

    def print_header(self):
        func_type = 'function' if self.parent != None else 'main'
        print('%s (%d instructions)' % (func_type, len(self.inst_list)))
        var_arg_flag = '+' if self.is_vararg == True else ''
        print('%d%s params, %d slots, %d upvalues, %d locals, %d constants, %d functions'
              % (self.num_params, var_arg_flag, self.max_stack_size, len(self.upvalue_list), len(self.local_val_list), len(self.k_list), len(self.sub_proto_list)))

    def print_code(self):
        for idx, item in enumerate(self.inst_list):
            inst = Instruction(item)
            print('\t%d\t[]\t%s' % (idx+1, str(inst)))

    def print_detail(self):
        if len(self.k_list) <= 0:
            return
        print('constants (%d):' % (len(self.k_list)))
        for idx, item in enumerate(self.k_list):
            print('\t%d\t%s' % (idx+1, item))


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

    def add_sub_func(self, fi):
        self.sub_func_list.append(fi)

    def add_local_vars(self, names):
        for name in names:
            self.add_local_var(name)

    def add_local_var(self, name):
        local_var = LocalVarInfo(name, self.local_var_table.get(
            name), self.scope_level, self.alloc_reg())
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
        if a > MAXARG_A or b > MAXARG_B or c > MAXARG_C:
            raise Exception("emit_ABC arg is to big")
        inst = (c << POS_C | b << POS_B | a << POS_A | op << POS_OP) & INS_MASK
        self.inst_list.append(inst)

    def emit_ABx(self, op, a, bx):
        if a > MAXARG_A or bx > MAXARG_Bx:
            raise Exception("emit_ABx arg is to big")
        inst = (bx << POS_Bx | a << POS_A | op << POS_OP) & INS_MASK
        self.inst_list.append(inst)

    def emit_AsBx(self, op, a, sbx):
        if a > MAXARG_A or sbx > MAXARG_sBx or sbx < -MAXARG_sBx:
            raise Exception("emit_AsBx arg is to big")
        inst = ((sbx+MAXARG_sBx) << POS_Bx | a << POS_A) & INS_MASK
        self.inst_list.append(inst)

    # OP_RETURN,/*	A B	return R(A), ... ,R(A+B-2)	(see note)	*/
    def emit_return(self, first_slot, num):
        self.emit_ABC(OpCode.OP_RETURN.value, first_slot, num+1, 0)

    # OP_CLOSURE,/*	A Bx	R(A) := closure(KPROTO[Bx])			*/
    def emit_closure(self, des_reg, idx):
        self.emit_ABx(OpCode.OP_CLOSURE.value, des_reg, idx)

    def to_proto(self, parent):
        curr = Prototype(parent)
        curr.is_vararg = self.is_var_arg
        curr.max_stack_size = self.max_reg
        curr.num_params = self.param_num
        curr.inst_list = self.inst_list
        curr.upvalue_list = self.get_upvalues()
        curr.k_list = self.get_constants()
        curr.local_val_list = self.local_var_list
        for fi in self.sub_func_list:
            curr.sub_proto_list.append(fi.to_proto(curr))
        return curr


class CodeGenerator:
    def __init__(self):
        super().__init__()

    def gen_main_proto(self, main_block):
        entry_fd = ast.FunctionDefExp([], True, None)
        entry_fi = FunctionInfo(None, entry_fd)
        entry_fi.add_local_var('_ENV')
        main_fd = ast.FunctionDefExp([], True, main_block)
        self.gen_func_def_exp(entry_fi, main_fd, 0)
        return entry_fi.sub_func_list[0].to_proto(None)

    def gen_func_def_exp(self, fi, fd, alloc_reg):
        sub_fi = FunctionInfo(fi, fd)
        fi.add_sub_func(sub_fi)
        sub_fi.add_local_vars(fd.parlist)
        self.gen_block(sub_fi, fd.body)
        sub_fi.exit_scope()
        sub_fi.emit_return(0, 0)
        fi.emit_closure(alloc_reg, len(fi.sub_func_list)-1)

    def gen_block(self, fi, block):
        pass
