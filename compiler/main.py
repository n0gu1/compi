# main.py
from lexer import lexer
from parser import parser
from errors import CompilerError

def compile_text(src: str):
    try:
        ast = parser.parse(src, lexer=lexer)
        print('✓ Análisis completado sin errores.')
        print('AST →', ast)
    except CompilerError as e:
        print('\n⚠️  ', e)

if __name__ == '__main__':
    with open('samples/demo.umgpp', encoding='utf-8') as f:
        source = f.read()
    compile_text(source)
