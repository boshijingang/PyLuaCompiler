import lexer

src_code = """
; . .  ... |
<<
>>
"""
"""
print('"你是谁！"')
3   345   0xff   0xBEBADA 3.0     3.1416     314.16e-2     0.31416E1     34e1
0x0.1E 
"""
lex = lexer.Lexer(src_code, '11')
token = lex.next_token()
while token.kind != lexer.TokenKind.EOF:
    print(token)
    token = lex.next_token()
#with open('test/factorial.lua') as f:
#    src_code = f.read()
#for token in lua_lexer.lexer(src_code):
#    print(token)
#tree = lua_parser.parse(lua_lexer.get_lexer(src_code))
#tree.display(0)