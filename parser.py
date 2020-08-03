import lexer
import ast


class Parser:
    block_end_tokens = [lexer.TokenKind.KW_RETURN, lexer.TokenKind.EOF,
                        lexer.TokenKind.KW_END, lexer.TokenKind.KW_ELSE,
                        lexer.TokenKind.KW_ELSEIF, lexer.TokenKind.KW_UNTIL]
    priority_table = {
        lexer.TokenKind.OP_ADD: {'left': 10, 'right': 10},  # +
        lexer.TokenKind.OP_SUB: {'left': 10, 'right': 10},  # -
        lexer.TokenKind.OP_MUL: {'left': 11, 'right': 11},  # *
        lexer.TokenKind.OP_MOD: {'left': 11, 'right': 11},  # %
        lexer.TokenKind.OP_DIV: {'left': 11, 'right': 11},  # /
        lexer.TokenKind.OP_IDIV: {'left': 11, 'right': 11},  # //
        lexer.TokenKind.OP_POW: {'left': 14, 'right': 13},  # ^
        lexer.TokenKind.OP_BAND: {'left': 6, 'right': 6},  # &
        lexer.TokenKind.OP_BOR: {'left': 4, 'right': 4},  # |
        lexer.TokenKind.OP_BNOT: {'left': 5, 'right': 5},  # ~
        lexer.TokenKind.OP_SHL: {'left': 7, 'right': 7},  # <<
        lexer.TokenKind.OP_SHR: {'left': 7, 'right': 7},  # >>
        lexer.TokenKind.OP_CONCAT: {'left': 9, 'right': 8},  # ..
        lexer.TokenKind.OP_EQ: {'left': 3, 'right': 3},  # ==
        lexer.TokenKind.OP_LE: {'left': 3, 'right': 3},  # <=
        lexer.TokenKind.OP_LT: {'left': 3, 'right': 3},  # <
        lexer.TokenKind.OP_NE: {'left': 3, 'right': 3},  # ~=
        lexer.TokenKind.OP_GT: {'left': 3, 'right': 3},  # >
        lexer.TokenKind.OP_GE: {'left': 3, 'right': 3},  # >=
        lexer.TokenKind.OP_AND: {'left': 2, 'right': 2},  # and
        lexer.TokenKind.OP_OR: {'left': 1, 'right': 1},  # or
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
            self.lex.next_token()
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
        while bin_op in self.binops and self.priority_table[bin_op]['left'] > prev_priority:
            bin_op, op_left = self.parse_binop_exp(op_left, self.priority_table[bin_op]['right'])
        return bin_op, op_left
    
    # args ::=  ‘(’ [explist] ‘)’ | tableconstructor | LiteralString 
    # tableconstructor ::= ‘{’ [fieldlist] ‘}’
    def parse_func_args(self):
        look_token = self.lex.look_ahead()
        exp_list = []
        if look_token.kind == lexer.TokenKind.SEP_LPAREN:
            self.lex.next_token()
            if self.lex.look_ahead().kind != lexer.TokenKind.SEP_RPAREN:
                exp_list = self.parse_exp_list()
            self.lex.next_token_of_kind(lexer.TokenKind.SEP_RPAREN)
        elif look_token.kind == lexer.TokenKind.SEP_LCURLY:
            exp_list = [self.parse_table_constructor_exp()]
        else:
            exp_list = [ast.String(self.lex.next_token_of_kind(lexer.TokenKind.STRING)).data]
        return exp_list

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
            return self.parse_number_exp()
        elif look_token.kind == lexer.TokenKind.STRING:
            self.lex.next_token()
            return ast.StringExp(look_token.data)
        elif look_token.kind == lexer.TokenKind.VARARG:
            self.lex.next_token()
            return ast.VarargExp()
        elif look_token.kind == lexer.TokenKind.KW_FUNCTION:
            return self.parse_func_def_exp()
        elif look_token.kind == lexer.TokenKind.SEP_LCURLY:
            return self.parse_table_constructor_exp()
        else:
            return self.parse_prefix_exp()

    def parse_func_def_exp(self):
        self.lex.next_token_of_kind(lexer.TokenKind.KW_FUNCTION)
        func_body_exp = self.parse_func_body_exp(False)
        return func_body_exp

    # tableconstructor ::= ‘{’ [fieldlist] ‘}’
    def parse_table_constructor_exp(self):
        self.lex.next_token_of_kind(lexer.TokenKind.SEP_LCURLY)
        if self.lex.look_ahead().kind != lexer.TokenKind.SEP_RCURLY:
            key_list, val_list = self.parse_field_list()
        else:
            key_list = []
            val_list = []
        self.lex.next_token_of_kind(lexer.TokenKind.SEP_RCURLY)
        return ast.TableConstructorExp(key_list, val_list)

    # fieldlist ::= field {fieldsep field} [fieldsep]
	# fieldsep ::= ‘,’ | ‘;’
    def parse_field_list(self):
        key, val = self.parse_field()
        key_list = [key]
        val_list = [val]
        while self.lex.look_ahead().kind in [lexer.TokenKind.SEP_COMMA, lexer.TokenKind.SEP_SEMI]:
            self.lex.next_token()
            if self.lex.look_ahead().kind == lexer.TokenKind.SEP_RCURLY:
                break
            else:
                key, val = self.parse_field()
                key_list.append(key)
                val_list.append(val)
        return key_list, val_list

    # field ::= ‘[’ exp ‘]’ ‘=’ exp | Name ‘=’ exp | exp
    def parse_field(self):
        if self.lex.look_ahead().kind == lexer.TokenKind.SEP_LBRACK:
            self.lex.next_token()
            key_exp = self.parse_exp(0)[1]
            self.lex.next_token_of_kind(lexer.TokenKind.SEP_RBRACK)
            self.lex.next_token_of_kind(lexer.TokenKind.OP_ASSIGN)
            val_exp = self.parse_exp(0)[1]
            return key_exp, val_exp
        exp = self.parse_exp(0)[1]
        if self.lex.look_ahead().kind == lexer.TokenKind.OP_ASSIGN:
            if not isinstance(exp, ast.NameExp):
                raise Exception("syntax error near '%s'" % token)
            self.lex.next_token()
            key_exp = ast.StringExp(exp.id_name)
            val_exp = self.parse_exp(0)[1]
            return key_exp, val_exp
        return ast.NilExp(), exp

    # binop exp
    def parse_binop_exp(self, op_left, prev_priority):
        token = self.lex.next_token()
        if token.kind not in self.binops:
           raise Exception("syntax error near '%s'" % token)
        bin_op, op_right = self.parse_exp(prev_priority)
        return bin_op, ast.BinopExp(op_left, op_right, token.kind)

    def parse_number_exp(self):
        token = self.lex.next_token_of_kind(lexer.TokenKind.NUMBER)
        val = eval(token.data)
        if isinstance(val, int):
            return ast.IntegerExp(val)
        else:
            return ast.FloatExp(val)

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
        stats = self.parse_stats()
        block = ast.Block(stats)
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

    def parse_while_stat(self):
        self.lex.next_token_of_kind(lexer.TokenKind.KW_WHILE)
        exp = self.parse_exp(0)[1]
        self.lex.next_token_of_kind(lexer.TokenKind.KW_DO)
        block = self.parse_block()
        self.lex.next_token_of_kind(lexer.TokenKind.KW_END)
        return ast.WhileStat(exp, block)

    def parse_repeat_stat(self):
        self.lex.next_token_of_kind(lexer.TokenKind.KW_REPEAT)
        block = self.parse_block()
        self.lex.next_token_of_kind(lexer.TokenKind.KW_UNTIL)
        exp = self.parse_exp(0)[1]
        return ast.RepeatStat(exp, block)

    def parse_if_stat(self):
        exp_list = []
        block_list = []
        self.lex.next_token_of_kind(lexer.TokenKind.KW_IF)
        exp = self.parse_exp(0)[1]
        exp_list.append(exp)
        self.lex.next_token_of_kind(lexer.TokenKind.KW_THEN)
        block = self.parse_block()
        block_list.append(block)
        while self.lex.look_ahead().kind == lexer.TokenKind.KW_ELSEIF:
            self.lex.next_token_of_kind(lexer.TokenKind.KW_ELSEIF)
            exp_list.append(self.parse_exp(0)[1])
            self.lex.next_token_of_kind(lexer.TokenKind.KW_THEN)
            block_list.append(self.parse_block())
        if self.lex.look_ahead().kind == lexer.TokenKind.KW_ELSE:
            self.lex.next_token_of_kind(lexer.TokenKind.KW_ELSE)
            exp_list.append(ast.BoolConstExp(True))
            block_list.append(self.parse_block())
        self.lex.next_token_of_kind(lexer.TokenKind.KW_END)
        return ast.IfStat(exp_list, block_list)

    def parse_for_stat(self):
        self.lex.next_token_of_kind(lexer.TokenKind.KW_FOR)
        name = ast.NameExp(self.lex.next_token_of_kind(lexer.TokenKind.IDENTIFIER).data)
        if self.lex.look_ahead().kind == lexer.TokenKind.OP_ASSIGN:
            return self.finish_for_num_stat(name)
        else:
            return self.finish_for_in_stat(name)

    def finish_for_num_stat(self, var):
        self.lex.next_token_of_kind(lexer.TokenKind.OP_ASSIGN)
        init_exp = self.parse_exp(0)[1]
        self.lex.next_token_of_kind(lexer.TokenKind.SEP_COMMA)
        limit_exp = self.parse_exp(0)[1]
        step_exp = None
        if self.lex.look_ahead().kind == lexer.TokenKind.SEP_COMMA:
            self.lex.next_token()
            step_exp = self.parse_exp(0)[1]
        self.lex.next_token_of_kind(lexer.TokenKind.KW_DO)
        block = self.parse_block()
        self.lex.next_token_of_kind(lexer.TokenKind.KW_END)
        return ast.ForNumStat(var, init_exp, limit_exp, step_exp, block)

    def finish_for_in_stat(self, name):
        var_list = self.parse_name_list(name)
        self.lex.next_token_of_kind(lexer.TokenKind.KW_IN)
        exp_list = self.parse_exp_list()
        self.lex.next_token_of_kind(lexer.TokenKind.KW_DO)
        block = self.parse_block()
        self.lex.next_token_of_kind(lexer.TokenKind.KW_END)
        return ast.ForInStat(var_list, exp_list, block)

    def parse_func_def_stat(self):
        self.lex.next_token_of_kind(lexer.TokenKind.KW_FUNCTION)
        func_name_exp, has_colon = self.parse_func_name_exp()
        func_body_exp = self.parse_func_body_exp(has_colon)
        return ast.AssignStat([func_name_exp], [func_body_exp])

    # parlist ::= namelist [‘,’ ‘...’] | ‘...’
    # namelist ::= Name {‘,’ Name}
    def parse_parlist(self):
        parlist = []
        is_var_arg = False
        if self.lex.look_ahead().kind == lexer.TokenKind.SEP_RPAREN:
            return parlist, is_var_arg
        if self.lex.look_ahead().kind == lexer.TokenKind.VARARG:
            is_var_arg = True
            self.lex.next_token()
            return parlist, is_var_arg
        parlist.append(ast.StringExp(self.lex.next_token_of_kind(lexer.TokenKind.IDENTIFIER).data))
        while self.lex.look_ahead().kind == lexer.TokenKind.SEP_COMMA:
            self.lex.next_token()
            if self.lex.look_ahead().kind == lexer.TokenKind.IDENTIFIER:
                parlist.append(ast.StringExp(self.lex.next_token_of_kind(lexer.TokenKind.IDENTIFIER).data))
            else:
                self.lex.next_token_of_kind(lexer.TokenKind.VARARG)
                is_var_arg = True
                break
        return parlist, is_var_arg

    # funcbody ::= ‘(’ [parlist] ‘)’ block end
    def parse_func_body_exp(self, has_colon):
        self.lex.next_token_of_kind(lexer.TokenKind.SEP_LPAREN)
        parlist, is_var_arg = self.parse_parlist()
        self.lex.next_token_of_kind(lexer.TokenKind.SEP_RPAREN)
        if has_colon:
            parlist.insert(0, ast.StringExp('self'))
        body = self.parse_block()
        self.lex.next_token_of_kind(lexer.TokenKind.KW_END)
        return ast.FunctionDefExp(parlist, is_var_arg, body)

    # funcname ::= Name {‘.’ Name} [‘:’ Name]
    def parse_func_name_exp(self):
        has_colon = False
        name_exp = ast.NameExp(self.lex.next_token_of_kind(lexer.TokenKind.IDENTIFIER).data)
        while self.lex.look_ahead().kind == lexer.TokenKind.SEP_DOT:
            self.lex.next_token()
            name_exp = ast.TableAccessExp(name_exp, ast.StringExp(self.lex.next_token_of_kind(lexer.TokenKind.IDENTIFIER).data))
        if self.lex.look_ahead().kind == lexer.TokenKind.SEP_COLON:
            self.lex.next_token()
            name_exp = ast.TableAccessExp(name_exp, ast.StringExp(self.lex.next_token_of_kind(lexer.TokenKind.IDENTIFIER).data))
            has_colon = True
        return name_exp, has_colon

    def parse_local_def_stat(self):
        self.lex.next_token_of_kind(lexer.TokenKind.KW_LOCAL)
        if self.lex.look_ahead().kind == lexer.TokenKind.KW_FUNCTION:
            return self.parse_local_func_def_stat()
        else:
            return self.parse_local_var_decl_stat()
    
    # namelist ::= Name {‘,’ Name}
    def parse_name_list(self, name=None):
        if name:
            var_list = [name]
        else:
            var_list = [ast.StringExp(self.lex.next_token_of_kind(lexer.TokenKind.IDENTIFIER).data)]
        while self.lex.look_ahead().kind == lexer.TokenKind.SEP_COMMA:
            self.lex.next_token()
            var_list.append(ast.StringExp(self.lex.next_token_of_kind(lexer.TokenKind.IDENTIFIER).data))
        return var_list

    # local function Name funcbody
    def parse_local_func_def_stat(self):
        self.lex.next_token_of_kind(lexer.TokenKind.KW_FUNCTION)
        var_list = [ast.StringExp(self.lex.next_token_of_kind(lexer.TokenKind.IDENTIFIER).data)]
        exp_list = [self.parse_func_body_exp(False)]
        return ast.LocalDeclStat(var_list, exp_list)

    # local namelist [‘=’ explist] 
    def parse_local_var_decl_stat(self):
        var_list = self.parse_name_list()
        exp_list = []
        if self.lex.look_ahead().kind == lexer.TokenKind.OP_ASSIGN:
            self.lex.next_token_of_kind(lexer.TokenKind.OP_ASSIGN)
            exp_list = self.parse_exp_list()
        return ast.LocalDeclStat(var_list, exp_list)

    # var ::=  Name | prefixexp ‘[’ exp ‘]’ | prefixexp ‘.’ Name
    # functioncall ::=  prefixexp args | prefixexp ‘:’ Name args 
    # prefixexp ::= var | functioncall | ‘(’ exp ‘)’
    # prefixexp ::=    prefixexp args 
    #                         | prefixexp ‘:’ Name args  
    #                         | prefixexp ‘[’ exp ‘]’
    #                         | prefixexp ‘.’ Name
    #                         | ‘(’ exp ‘)’ 
    #                         | Name  
    # args ::=  ‘(’ [explist] ‘)’ | tableconstructor | LiteralString 
    # tableconstructor ::= ‘{’ [fieldlist] ‘}’
    def parse_prefix_exp(self):
        look_token = self.lex.look_ahead()
        if look_token.kind == lexer.TokenKind.SEP_LPAREN:
            self.lex.next_token()
            exp = self.parse_exp(0)[1]
            self.lex.next_token_of_kind(lexer.TokenKind.SEP_RPAREN)
        else:
            name = self.lex.next_token_of_kind(lexer.TokenKind.IDENTIFIER)
            exp = ast.NameExp(name.data)
        while True:
            look_token = self.lex.look_ahead()
            if look_token.kind == lexer.TokenKind.SEP_DOT:
                self.lex.next_token()
                idx_exp = ast.StringExp(self.lex.next_token_of_kind(lexer.TokenKind.IDENTIFIER).data)
                exp = ast.TableAccessExp(exp, idx_exp)
            elif look_token.kind ==  lexer.TokenKind.SEP_COLON:
                self.lex.next_token()
                args_exp = [exp]
                idx_exp = ast.StringExp(self.lex.next_token_of_kind(lexer.TokenKind.IDENTIFIER).data)
                exp = ast.TableAccessExp(exp, idx_exp)
                args_exp.extend(self.parse_func_args())
                exp = ast.FunctionCallExp(exp, args_exp)
            elif look_token.kind in [lexer.TokenKind.SEP_LPAREN, lexer.TokenKind.SEP_LCURLY, lexer.TokenKind.STRING]:
                args_exp = self.parse_func_args()
                exp = ast.FunctionCallExp(exp, args_exp)
            elif look_token.kind == lexer.TokenKind.SEP_LBRACK:
                self.lex.next_token()
                idx_exp = self.parse_exp(0)[1]
                exp = ast.TableAccessExp(exp, idx_exp)
                self.lex.next_token_of_kind(lexer.TokenKind.SEP_RBRACK)
            else:
                break
        return exp

    # varlist ‘=’ explist
    # functioncall
    def parse_assign_or_func_call_stat(self):
        exp = self.parse_prefix_exp()
        look_token = self.lex.look_ahead()
        if look_token.kind in [lexer.TokenKind.OP_ASSIGN, lexer.TokenKind.SEP_COMMA]:
            return self.finsh_assign_stat(exp)
        elif isinstance(exp, ast.FunctionCallExp):
            return exp
        else:
            raise Exception("syntax error near '%s'" % look_token)

    def check_var(self, exp):
        if isinstance(exp, ast.TableAccessExp) or isinstance(exp, ast.NameExp):
            return exp
        raise Exception("syntax error near '%s'" % token)

    # varlist ‘=’ explist
    # varlist ::= var {‘,’ var}
    # var ::=  Name | prefixexp ‘[’ exp ‘]’ | prefixexp ‘.’ Name
    def finsh_assign_stat(self, first_var):
        var_list = [first_var]
        while self.lex.look_ahead().kind == lexer.TokenKind.SEP_COMMA:
            self.lex.next_token()
            var_list.append(self.check_var(self.parse_prefix_exp()))
        self.lex.next_token_of_kind(lexer.TokenKind.OP_ASSIGN)
        exp_list = self.parse_exp_list()
        return ast.AssignStat(var_list, exp_list)

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

    def parse_break_stat(self):
        self.lex.next_token_of_kind(lexer.TokenKind.KW_BREAK)
        return ast.BreakStat()

    def parse_label_stat(self):
        self.lex.next_token_of_kind(lexer.TokenKind.SEP_LABEL)
        label = self.lex.next_token_of_kind(lexer.TokenKind.IDENTIFIER)
        self.lex.next_token_of_kind(lexer.TokenKind.SEP_LABEL)
        return ast.LabelStat(label)

    def parse_stats(self):
        stats = []
        while not self.is_block_end(self.lex.look_ahead().kind):
            stat = self.parse_stat()
            if stat:
                stats.append(stat)
        return stats

    def is_block_end(self, kind):
        if kind in self.block_end_tokens:
            return True
        return False