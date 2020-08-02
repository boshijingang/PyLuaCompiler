import lexer
from parser import Parser

def main():
    src_code = """
    function b.a.c.d(bd, dc, ...)
        print(2222)
    end

    while -3^6 do 
        a = (3.3+3)*5^3;
        b = '53535'..'34234'..'re64646'
        c[54] = '34535'
        b.print(2, 3)
        d.c:print(2, 3)
        break
    end
    return 2+3, 3, 5
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