import lexer
import ast


class Parser:
    block_end_tokens = [lexer.TokenKind.KW_RETURN, lexer.TokenKind.EOF,
                        lexer.TokenKind.KW_END, lexer.TokenKind.KW_ELSE,
                        lexer.TokenKind.KW_ELSEIF, lexer.TokenKind.KW_UNTIL]
    priority_table = {
        lexer.TokenKind.OP_ADD: {left: 10, right: 10},  # +
        lexer.TokenKind.OP_SUB: {left: 10, right: 10},  # -
        lexer.TokenKind.OP_MUL: {left: 11, right: 11},  # *
        lexer.TokenKind.OP_MOD: {left: 11, right: 11},  # %
        lexer.TokenKind.OP_DIV: {left: 11, right: 11},  # /
        lexer.TokenKind.OP_IDIV: {left: 11, right: 11},  # //
        lexer.TokenKind.OP_POW: {left: 14, right: 13},  # ^
        lexer.TokenKind.OP_BAND: {left: 6, right: 6},  # &
        lexer.TokenKind.OP_BOR: {left: 4, right: 4},  # |
        lexer.TokenKind.OP_BNOT: {left: 5, right: 5},  # ~
        lexer.TokenKind.OP_SHL: {left: 7, right: 7},  # <<
        lexer.TokenKind.OP_SHR: {left: 7, right: 7},  # >>
        lexer.TokenKind.OP_CONCAT: {left: 9, right: 8},  # ..
        lexer.TokenKind.OP_EQ: {left: 3, right: 3},  # ==
        lexer.TokenKind.OP_LE: {left: 3, right: 3},  # <=
        lexer.TokenKind.OP_LT: {left: 3, right: 3},  # <
        lexer.TokenKind.OP_NE: {left: 3, right: 3},  # ~=
        lexer.TokenKind.OP_GT: {left: 3, right: 3},  # >
        lexer.TokenKind.OP_GE: {left: 3, right: 3},  # >=
        lexer.TokenKind.OP_AND: {left: 2, right: 2},  # and
        lexer.TokenKind.OP_OR: {left: 1, right: 1},  # or
    }

    unops = [
        lexer.TokenKind.OP_SUB, lexer.TokenKind.OP_NOT,
        lexer.TokenKind.OP_LEN, lexer.TokenKind.OP_BNOT
    ]

    binops = [
        lexer.TokenKind.OP_ADD, lexer.TokenKind.OP_SUB,
        lexer.TokenKind.OP_MUL, lexer.TokenKind.OP_MOD,
        lexer.TokenKind.OP_POW, lexer.TokenKind.OP_DIV,
        lexer.TokenKind.OP_IDIV, lexer.TokenKind.OP_BAND,
        lexer.TokenKind.OP_BOR, lexer.TokenKind.OP_BXOR,
        lexer.TokenKind.OP_SHL, lexer.TokenKind.OP_SHR,
        lexer.TokenKind.OP_CONCAT, lexer.TokenKind.OP_NE,
        lexer.TokenKind.OP_EQ, lexer.TokenKind.OP_LT,
        lexer.TokenKind.OP_LE, lexer.TokenKind.OP_GT,
        lexer.TokenKind.OP_GE, lexer.TokenKind.OP_AND,
        lexer.TokenKind.OP_OR
    ]

    unary_priority = 12

    def __init__(self, lex):
        self.lex = lex

    def parse(self):
        block = self.parse_block()
        self.lex.next_token_of_kind(lexer.TokenKind.EOF)
        return block

    # explist ::= exp {‘,’ exp}
    def parse_exp_list(self):
        exp_list = []
        exp_list.append(self.parse_exp(0)[1])
        while self.lex.look_ahead().kind == lexer.TokenKind.SEP_COMMA:
            exp_list.append(self.parse_exp(0)[1])
        return exp_list

    # exp ::= (simpleexp | unop exp) {binop exp}
    def parse_exp(self, prev_priority):
        token = self.lex.look_ahead()
        if token.kind in self.unops:
            self.lex.next_token()
            op_left = ast.UnopExp(self.parse_exp(self.unary_priority)[1], token.kind)
        else:
            op_left = self.parse_simple_exp()
        bin_op = self.lex.look_ahead().kind
        while bin_op in self.binops and self.priority_table[bin_op].left > prev_priority:
            bin_op, op_left = self.parse_binop_exp(op_left, self.priority_table[bin_op].right)
        return bin_op, op_left

    # simpleexp ::= nil | false | true | Numeral | LiteralString | ‘...’ | 
    #                           functiondef | prefixexp | tableconstructor
    def parse_simple_exp(self):
        look_token = self.lex.look_ahead()
        if look_token.kind == lexer.TokenKind.KW_NIL:
            self.lex.next_token()
            return ast.NilExp()
        elif look_token.kind == lexer.TokenKind.KW_FALSE:
            self.lex.next_token()
            return ast.BoolConstExp(False)
        elif look_token.kind == lexer.TokenKind.KW_TRUE:
            self.lex.next_token()
            return ast.BoolConstExp(True)
        elif look_token.kind == lexer.TokenKind.NUMBER:
            self.lex.next_token()
            return self.parse_number_exp()
        elif look_token.kind == lexer.TokenKind.STRING:
            self.lex.next_token()
            return ast.StringExp(look_token.data)
        elif look_token.kind == lexer.TokenKind.VARARG:
            self.lex.next_token()
            return ast.VarargExp()
        elif look_token.kind == lexer.TokenKind.KW_FUNCTION:
            return self.parse_func_def_exp()
        elif look_token.kind == lexer.TokenKind.KW_SEP_LCURLY:
            return self.parse_table_constructor_exp()
        else:
            return self.parse_prefix_exp()

    # binop exp
    def parse_binop_exp(self, op_left, prev_priority):
        token = self.lex.next_token()
        if token.kind not in self.binops:
           raise Exception("syntax error near '%s'" % token)
        bin_op, op_right = self.parse_exp(prev_priority)
        return bin_op, ast.BinopExp(op_left, op_right, token.kind)

    # retstat ::= return [explist] [‘;’]
    def parse_retstat(self):
        self.lex.next_token_of_kind(lexer.TokenKind.KW_RETURN)
        exp_list = []
        token = self.lex.look_ahead()
        if not self.is_block_end(token.kind) and token.kind != lexer.TokenKind.SEP_SEMI:
            exp_list = self.parse_exp_list()
        return ast.RetStat(exp_list)

    # block ::= {stat} [retstat]
    def parse_block(self):
        block = ast.Block()
        stats = self.parse_stats()
        block.append_stat(stats)
        if self.lex.look_ahead().kind == lexer.TokenKind.KW_RETURN:
            retstat = self.parse_retstat()
            block.append_stat(retstat)
        return block

    def parse_goto_stat(self):
        self.lex.next_token_of_kind(lexer.TokenKind.KW_GOTO)
        label = self.lex.next_token_of_kind(lexer.TokenKind.IDENTIFIER)
        return ast.GotoStat(label)

    def parse_do_stat(self):
        self.lex.next_token_of_kind(lexer.TokenKind.KW_DO)
        block = self.parse_block()
        self.lex.next_token_of_kind(lexer.TokenKind.KW_END)
        return ast.DoStat(block)

    def parse_exp(self):
        pass

    def parse_while_stat(self):
        self.lex.next_token_of_kind(lexer.TokenKind.KW_WHILE)
        exp = self.parse_exp()
        self.lex.next_token_of_kind(lexer.TokenKind.KW_DO)
        block = self.parse_block()
        self.lex.next_token_of_kind(lexer.TokenKind.KW_END)
        return ast.WhileStat(exp, block)

    def parse_repeat_stat(self):
        self.lex.next_token_of_kind(lexer.TokenKind.KW_REPEAT)
        block = self.parse_block()
        self.lex.next_token_of_kind(lexer.TokenKind.KW_UNTIL)
        exp = self.parse_exp()
        return ast.RepeatStat(exp, block)

    def parse_if_stat(self):
        exp_list = []
        block_list = []
        self.lex.next_token_of_kind(lexer.TokenKind.KW_IF)
        exp = self.parse_exp()
        exp_list.append(exp)
        self.lex.next_token_of_kind(lexer.TokenKind.KW_THEN)
        block = self.parse_block()
        block_list.append(block)
        while self.lex.look_ahead().kind == lexer.TokenKind.KW_ELSEIF:
            self.lex.next_token_of_kind(lexer.TokenKind.KW_ELSEIF)
            exp_list.append(self.parse_exp())
            self.lex.next_token_of_kind(lexer.TokenKind.KW_THEN)
            block_list.append(self.parse_block())
        if self.lex.look_ahead().kind == lexer.TokenKind.KW_ELSE:
            self.lex.next_token_of_kind(lexer.TokenKind.KW_ELSE)
            exp_list.append(ast.TrueExp)
            block_list.append(self.parse_block())
        self.lex.next_token_of_kind(lexer.TokenKind.KW_END)
        return ast.IfStat(exp_list, block_list)

    def parse_for_stat(self):
        self.lex.next_token_of_kind(lexer.TokenKind.KW_FOR)
        name = self.lex.next_token_of_kind(lexer.TokenKind.IDENTIFIER)
        if self.lex.look_ahead().kind == lexer.TokenKind.OP_ASSIGN:
            return self.finish_for_num_stat(name)
        else:
            return self.finish_for_in_stat(name)

    def parse_func_def_stat(self):
        self.lex.next_token_of_kind(lexer.TokenKind.KW_FUNCTION)
        func_name_exp = self.parse_func_name_exp()
        func_body_exp = self.parse_func_body_exp()
        return ast.AssignStat([func_name_exp], [func_body_exp])

    def parse_local_def_stat(self):
        self.lex.next_token_of_kind(lexer.TokenKind.KW_LOCAL)
        if self.lex.look_ahead().kind == lexer.TokenKind.KW_FUNCTION:
            return self.parse_local_func_def_stat()
        else:
            return self.parse_local_var_decl_stat()

    def parse_assign_or_func_call_stat(self):
        exp = parse_prefixexp()
        if isinstance(exp, ast.FunctionCallExp):
            return exp
        else:
            return finsh_assign_stat(exp)

    """
    stat ::=  ‘;’ |
        break |
        ::Name:: |
        goto Name |
        do block end |
        while exp do block end |
        repeat block until exp |
        if exp then block {elseif exp then block} [else block] end |
        for Name ‘=’ exp ‘,’ exp [‘,’ exp] do block end |
        for namelist in explist do block end |
        function funcname funcbody |
        local function Name funcbody |
        local namelist [‘=’ explist]
        varlist ‘=’ explist |
        functioncall 
    """

    def parse_stat(self):
        token = self.lex.look_ahead()
        if token.kind == lexer.TokenKind.SEP_SEMI:
            return self.parse_empty_stat()
        elif token.kind == lexer.TokenKind.KW_BREAK:
            return self.parse_break_stat()
        elif token.kind == lexer.TokenKind.SEP_LABEL:
            return self.parse_label_stat()
        elif token.kind == lexer.TokenKind.KW_GOTO:
            return self.parse_goto_stat()
        elif token.kind == lexer.TokenKind.KW_DO:
            return self.parse_do_stat()
        elif token.kind == lexer.TokenKind.KW_WHILE:
            return self.parse_while_stat()
        elif token.kind == lexer.TokenKind.KW_REPEAT:
            return self.parse_repeat_stat()
        elif token.kind == lexer.TokenKind.KW_IF:
            return self.parse_if_stat()
        elif token.kind == lexer.TokenKind.KW_FOR:
            return self.parse_for_stat()
        elif token.kind == lexer.TokenKind.KW_FUNCTION:
            return self.parse_func_def_stat()
        elif token.kind == lexer.TokenKind.KW_LOCAL:
            return self.parse_local_def_stat()
        else:
            return self.parse_assign_or_func_call_stat()

    def parse_empty_stat(self):
        self.lex.next_token_of_kind(lexer.TokenKind.SEP_SEMI)
        return ast.EmptyStat

    def parse_break_stat(self):
        self.lex.next_token_of_kind(lexer.TokenKind.KW_BREAK)
        return ast.BreakStat

    def parse_label_stat(self):
        self.lex.next_token_of_kind(lexer.TokenKind.SEP_LABEL)
        label = self.lex.next_token_of_kind(lexer.TokenKind.IDENTIFIER)
        self.lex.next_token_of_kind(lexer.TokenKind.SEP_LABEL)
        return ast.LabelStat(label)

    def parse_stats(self):
        stats = []
        while not self.is_block_end(self.lex.look_ahead().kind):
            stat = self.parse_stat()
            stats.append(stat)
        return stats

    def is_block_end(self, kind):
        if kind in self.block_end_tokens:
            return True
        return False