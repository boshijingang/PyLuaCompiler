from enum import Enum
import re

class TokenKind(Enum):
    EOF = 0            # end-of-file
    VARARG = 2         # ...
    SEP_SEMI = 3       # ;
    SEP_COMMA = 4      # ,
    SEP_DOT = 5        # .
    SEP_COLON = 6      # :
    SEP_LABEL = 7      # ::
    SEP_LPAREN = 8     # (
    SEP_RPAREN = 9     # )
    SEP_LBRACK = 10    # [
    SEP_RBRACK = 11    # ]
    SEP_LCURLY = 12    # {
    SEP_RCURLY = 13    # }
    OP_ASSIGN = 14     # =
    OP_MINUS = 15      # - (sub or unm)
    OP_WAVE = 16       # ~ (bnot or bxor)
    OP_ADD = 17        # +
    OP_MUL = 18        # *
    OP_DIV = 19        # /
    OP_IDIV = 20       # //
    OP_POW = 21        # ^
    OP_MOD = 22        # %
    OP_BAND = 23       # &
    OP_BOR = 24        # |
    OP_SHR = 25        # >>
    OP_SHL = 26        # <<
    OP_CONCAT = 27     # ..
    OP_LT = 28         # <
    OP_LE = 29         # <=
    OP_GT = 30         # >
    OP_GE = 31         # >=
    OP_EQ = 32         # ==
    OP_NE = 33         # ~=
    OP_LEN = 34        # #
    OP_AND = 35        # and
    OP_OR = 36         # or
    OP_NOT = 37        # not
    KW_BREAK = 38      # break
    KW_DO = 39         # do
    KW_ELSE = 40       # else
    KW_ELSEIF = 41     # elseif
    KW_END = 42        # end
    KW_FALSE = 43      # false
    KW_FOR = 44        # for
    KW_FUNCTION = 45   # function
    KW_GOTO = 46       # goto
    KW_IF = 47         # if
    KW_IN = 48         # in
    KW_LOCAL = 49      # local
    KW_NIL = 50        # nil
    KW_REPEAT = 51     # repeat
    KW_RETURN = 52     # ret rn
    KW_THEN = 53       # then
    KW_TRUE = 54       # true
    KW_UNTIL = 55      # until
    KW_WHILE = 56      # while
    IDENTIFIER = 57    # identifier
    NUMBER = 58        # number literal
    STRING = 59        # string literal
    OP_UNM = OP_MINUS  # unary minus
    OP_SUB = OP_MINUS
    OP_BNOT = OP_WAVE
    OP_BXOR = OP_WAVE

class Token:
    def __init__(self, kind, line, data):
        self.kind = kind
        self.line = line
        self.data = data

    def __str__(self):
        return "{kind:'%s', line:'%d', data:'%s'}" % (self.kind.name, self.line, self.data)

class Lexer:
    re_Identifier = re.compile(r'[_A-Za-z][_A-Za-z0-9]*')
    re_number = re.compile(r"0[xX][0-9a-fA-F]*(\.[0-9a-fA-F]*)?([pP][+\-]?[0-9]+)?|"
                           r"[0-9]*(\.[0-9]*)?([eE][+\-]?[0-9]+)?")
    re_opening_long_bracket = re.compile(r'\[=*\[')
    re_short_string = re.compile(r"(?s)('(\\\\|\\'|\\\n|\\z\s*|[^'\n])*')|(\"(\\\\|\\\"|\\\n|\\z\s*|[^\"\n])*\")")

    keywords_tokens = {
        "and":      TokenKind.OP_AND,
        "break":    TokenKind.KW_BREAK,
        "do":       TokenKind.KW_DO,
        "else":     TokenKind.KW_ELSE,
        "elseif":   TokenKind.KW_ELSEIF,
        "end":      TokenKind.KW_END,
        "false":    TokenKind.KW_FALSE,
        "for":      TokenKind.KW_FOR,
        "function": TokenKind.KW_FUNCTION,
        "goto":     TokenKind.KW_GOTO,
        "if":       TokenKind.KW_IF,
        "in":       TokenKind.KW_IN,
        "local":    TokenKind.KW_LOCAL,
        "nil":      TokenKind.KW_NIL,
        "not":      TokenKind.OP_NOT,
        "or":       TokenKind.OP_OR,
        "repeat":   TokenKind.KW_REPEAT,
        "return":   TokenKind.KW_RETURN,
        "then":     TokenKind.KW_THEN,
        "true":     TokenKind.KW_TRUE,
        "until":    TokenKind.KW_UNTIL,
        "while":    TokenKind.KW_WHILE
    }

    single_symbol_tokens = {
        ';':        TokenKind.SEP_SEMI,
        ',':        TokenKind.SEP_COMMA,
        '(':        TokenKind.SEP_LPAREN,
        ')':        TokenKind.SEP_RPAREN,
        ']':        TokenKind.SEP_RBRACK,
        '{':        TokenKind.SEP_LCURLY,
        '}':        TokenKind.SEP_RCURLY,
        '+':        TokenKind.OP_ADD,
        '-':        TokenKind.OP_MINUS,
        '*':        TokenKind.OP_MUL,
        '^':        TokenKind.OP_POW,
        '%':        TokenKind.OP_MOD,
        '&':        TokenKind.OP_BAND,
        '|':        TokenKind.OP_BOR,
        '#':        TokenKind.OP_LEN,
    }

    special_symbols = {
        'new_line': ['\r', '\n'],
        'white_space': ['\t', '\n', '\v', '\f', '\r', ' ']
    }

    def __init__(self, chunk, file_name):
        self.chunk = chunk
        self.file_name = file_name
        self.cur_line = 1
        self.cur_pos = 0
        self.cached_token = None

    def look_ahead(self):
        if self.cached_token:
            return self.cached_token
        self.cached_token = self.next_token()
        return self.cached_token
    
    def next_token_of_kind(self, kind):
        token = self.next_token()
        if token.kind != kind:
            raise Exception("syntax error near '%s'" % token)
        return token
    
    def next_token(self):
        if self.cached_token:
            token = self.cached_token
            self.cached_token = None
            return token
        self.skip_white_spaces()
        if self.cur_pos >= len(self.chunk):
            return Token(TokenKind.EOF, self.cur_line, None)
        c = self.chunk[self.cur_pos]
        if c in self.single_symbol_tokens:
            self.move_point(1)
            return Token(self.single_symbol_tokens[c], self.cur_line, c)
        elif c == ':':
            if self.is_start_with('::'):
                self.move_point(2)
                return Token(TokenKind.SEP_LABEL, self.cur_line, '::')
            self.move_point(1)
            return Token(TokenKind.SEP_COLON, self.cur_line, ':')
        elif c == '~':
            if self.is_start_with('~='):
                self.move_point(2)
                return Token(TokenKind.OP_NE, self.cur_line, '~=')
            self.move_point(1)
            return Token(TokenKind.OP_WAVE, self.cur_line, '~')
        elif c == '<':
            if self.is_start_with('<<'):
                self.move_point(2)
                return Token(TokenKind.OP_SHL, self.cur_line, '<<')
            elif self.is_start_with('<='):
                self.move_point(2)
                return Token(TokenKind.OP_LE, self.cur_line, '<=')
            self.move_point(1)
            return Token(TokenKind.OP_LT, self.cur_line, '<')
        elif c == '>':
            if self.is_start_with('>>'):
                self.move_point(2)
                return Token(TokenKind.OP_SHR, self.cur_line, '>>')
            elif self.is_start_with('>='):
                self.move_point(2)
                return Token(TokenKind.OP_GE, self.cur_line, '>=')
            self.move_point(1)
            return Token(TokenKind.OP_GT, self.cur_line, '>')
        elif c == '/':
            if self.is_start_with('//'):
                self.move_point(2)
                return Token(TokenKind.OP_IDIV, self.cur_line, '//')
            self.move_point(1)
            return Token(TokenKind.OP_DIV, self.cur_line, '/')
        elif c == '=':
            if self.is_start_with('=='):
                self.move_point(2)
                return Token(TokenKind.OP_EQ, self.cur_line, '==')
            self.move_point(1)
            return Token(TokenKind.OP_ASSIGN, self.cur_line, '=')
        elif c == '.':
            if self.is_start_with('...'):
                self.move_point(3)
                return Token(TokenKind.VARARG, self.cur_line, '...')
            elif self.is_start_with('..'):
                self.move_point(2)
                return Token(TokenKind.OP_CONCAT, self.cur_line, '..')
            elif self.isdigit(self.chunk[self.cur_pos+1]):
                return self.scan_number()
            self.move_point(1)
            return Token(TokenKind.SEP_DOT, self.cur_line, '.')
        elif c == '[':
            if self.is_start_with('[[') or self.is_start_with('[='):
                return self.scan_long_string()
            self.move_point(1)
            return Token(TokenKind.SEP_LBRACK, self.cur_line, '[')
        elif c == "'" or c == '"':
            return self.scan_short_string()
        elif self.isdigit(c):
            return self.scan_number()
        elif c == '_' or c.isalpha():
            token = self.scan_identifier()
            if token.data in self.keywords_tokens:
                return Token(self.keywords_tokens[token.data], self.cur_line, token.data)
            return token
        else:
            raise Exception("unexpected symbol near %s" % c)

    def skip_white_spaces(self):
        while not self.is_chunk_end():
            if self.is_start_with('--'):
                self.move_point(2)
                self.skip_comment()
            elif self.is_start_with('\r\n') or self.is_start_with('\n\r'):
                self.move_point(2)
                self.cur_line = self.cur_line + 1
            elif self.chunk[self.cur_pos] in self.special_symbols['new_line']:
                self.move_point(1)
                self.cur_line = self.cur_line + 1
            elif self.chunk[self.cur_pos] in self.special_symbols['white_space']:
                self.move_point(1)
            else:
                break

    def skip_comment(self):
        if self.chunk[self.cur_pos] == '[':
            token = self.scan_long_string()
        else:
            while not self.is_chunk_end():
                if self.chunk[self.cur_pos] in '\n\r':
                    self.cur_line = self.cur_line + 1
                    self.move_point(1)
                    break
                else:
                    self.move_point(1)

    def is_chunk_end(self):
        return self.cur_pos >= len(self.chunk)

    def is_start_with(self, prefix):
        return self.chunk.startswith(prefix, self.cur_pos)
    
    def scan_number(self):
        token = self.re_match(self.re_number)
        self.move_point(len(token))
        print("get number: ")
        print(eval(token))
        return Token(TokenKind.NUMBER, self.cur_line, token)
    
    def re_match(self, pattern):
        m = pattern.match(self.chunk, self.cur_pos)
        if m:
            token = m.group()
            return token
        raise Exception('unreachable')

    def scan_identifier(self):
        token = self.re_match(self.re_Identifier)
        self.move_point(len(token))
        return Token(TokenKind.IDENTIFIER, self.cur_line, token)

    def skip_sep(self, sep):
        count = 0
        while self.chunk[self.cur_pos] == sep:
            self.move_point(1)
            count = count + 1
        return count

    # [=*[]=*]
    def scan_long_string(self):
        self.move_point(1)
        sep_num = self.skip_sep('=')
        if self.chunk[self.cur_pos] != '[':
            raise Exception("invalid long string delimiter near '%s'"%('['+'='*sep_num))
        self.move_point(1)
        token = ''
        is_finish = False
        while not self.is_chunk_end():
            if self.chunk[self.cur_pos] == ']':
                self.move_point(1)
                close_sep_num = self.skip_sep('=')
                if close_sep_num == sep_num and self.chunk[self.cur_pos] == ']':
                    self.move_point(1)
                    is_finish = True
                    break
                token = token + ']'+'='*close_sep_num
            elif self.chunk[self.cur_pos] in '\n\r':
                self.cur_line = self.cur_line + 1
                token = token + '\n'
                self.move_point(1)
            else:
                token = token + self.chunk[self.cur_pos]
                self.move_point(1)
        if not is_finish:
            raise Exception('unfinished long string (starting at line %d) near <eof>'%(self.cur_line))
        return Token(TokenKind.STRING, self.cur_line, token)


    def scan_long_string_re(self):
        opening_bracket = self.re_match(self.re_opening_long_bracket)
        start_pos = self.chunk.find(opening_bracket, self.cur_pos)
        if start_pos == -1:
            raise Exception('unreachable')
        closing_bracket = opening_bracket.replace('[', ']')
        end_pos = self.chunk.find(closing_bracket, self.cur_pos)
        if end_pos == -1:
            raise Exception('unreachable')
        self.move_point(end_pos-start_pos+len(closing_bracket))
        start_pos = start_pos + len(opening_bracket)
        return Token(TokenKind.STRING, self.cur_line,  self.chunk[start_pos:end_pos])

    def scan_short_string(self):
        begin_c = self.chunk[self.cur_pos]
        self.move_point(1)
        is_finish = False
        token = ''
        esc_table = {'a': '\a', 'b': '\b', 'f': '\f', 'n': '\n', 'r': '\r', 't': '\t', 'v': '\v', '\\': '\\', '"': '"', "'": "'"}
        while not self.is_chunk_end():
            if self.chunk[self.cur_pos] == begin_c:
                is_finish = True
                self.move_point(1)
                break
            elif self.chunk[self.cur_pos] in '\r\n':
                raise Exception("unfinished string near '%s'"%(token))
            elif self.chunk[self.cur_pos] == '\\':
                self.move_point(1)
                if self.chunk[self.cur_pos] in esc_table:
                    token = token + esc_table[self.chunk[self.cur_pos]]
                    self.move_point(1)
                elif self.chunk[self.cur_pos] == 'x':
                    pass
                elif self.chunk[self.cur_pos] == 'u':
                    pass
                elif self.chunk[self.cur_pos] in '\n\r':
                    self.cur_line = self.cur_line + 1
                    token = token + '\n'
                else:
                    raise Exception('invalid escape sequence')
            else:
                token = token + self.chunk[self.cur_pos]
                self.move_point(1)
        if not is_finish:
                raise Exception('unfinished long string (starting at line %d) near <eof>'%(self.cur_line))
        return Token(TokenKind.STRING, self.cur_line, token)

    def scan_short_string_re(self):
        short_string = self.re_match(self.re_short_string)
        self.move_point(len(short_string))
        short_string = short_string[1:-1]
        return Token(TokenKind.STRING, self.cur_line, short_string)

    def move_point(self, step=1):
        self.cur_pos = self.cur_pos + step

    def isdigit(self, num_str, base=10):
        num_str = num_str.lower()
        if base<=10:
            return num_str>='0' and num_str<=str(base-1)
        if base==16:
            return (num_str>='0' and num_str<='9') or (num_str>='a' and num_str<='f')
        return False