import lexer
from parser import Parser

def main():
    src_code = """
    while true do 
        a = 3+3*5^3
        a.print(2, 3)
        break
    end
    """
    # test_lua = r'/Users/qinggang/PersonalData/open-src/xmake/xmake/core/main.lua'
    # with open(test_lua, 'r') as f:
    #     src_code = f.read()
    lex = lexer.Lexer(src_code, 'main.lua')
    # token = lex.next_token()
    # while token.kind != lexer.TokenKind.EOF:
    #     print(token)
    #     token = lex.next_token()
    parser = Parser(lex)
    ast = parser.parse()
    ast.print()
    #with open('test/factorial.lua') as f:
    #    src_code = f.read()
    #for token in lua_lexer.lexer(src_code):
    #    print(token)
    #tree = lua_parser.parse(lua_lexer.get_lexer(src_code))
    #tree.display(0)

if __name__ == '__main__':
    main()