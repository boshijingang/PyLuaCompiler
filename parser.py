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
        exp_list.append(self.parse_exp())
        while self.lex.look_ahead().kind == lexer.TokenKind.SEP_COMMA:
            exp_list.append(self.parse_exp())
        return exp_list

    # exp ::= (simpleexp | unop exp) {binop exp}
    # simpleexp ::= nil | false | true | Numeral | LiteralString | ‘...’ | functiondef | prefixexp | tableconstructor
    def parse_exp(self):
        pass

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
