import lexer
from parser import Parser
from code import CodeGenerator

def main():
    src_code = """
    local function b(ad, bd, cd)
        print("local_function")
    end
    local a, b, c = 2+3, 3*4, 5^4
    function b.a.c.d(bd, dc, ...)
        do
            print("do_stat")
        end
        if bd > 2 then
            print(2222)
        elseif dc<=6 then
            print(33333)
        else
            print(3333)
        end
        for a=2^4, i do
            print("for_stat")
        end
        for a,b in 2+3, 35 do
            print("for_in")
        end
    end

    while -3^6 do 
        a = (3.3+3)*5^3;
        b = '53535'..'34234'..'re64646'
        c[54] = '34535'
        b.print(2, 3)
        d.c:print(2, 3)
        break
    end
    repeat print.print(3445) until a[323]
    return 2+3, 3, 5
    """
    test_lua = r'/Users/qinggang/PersonalData/open-src/xmake/xmake/core/base/option.lua' #r'/Users/qinggang/PersonalData/open-src/xmake/xmake/core/main.lua'
    with open(test_lua, 'r') as f:
        src_code = f.read()
    lex = lexer.Lexer(src_code, 'main.lua')
    # token = lex.next_token()
    # while token.kind != lexer.TokenKind.EOF:
    #     print(token)
    #     token = lex.next_token()
    parser = Parser(lex)
    ast = parser.parse()
    # ast.print()
    code_gen = CodeGenerator()
    main_proto = code_gen.gen_entry_proto(ast)
    #with open('test/factorial.lua') as f:
    #    src_code = f.read()
    #for token in lua_lexer.lexer(src_code):
    #    print(token)
    #tree = lua_parser.parse(lua_lexer.get_lexer(src_code))
    #tree.display(0)

if __name__ == '__main__':
    main()