# lexer.py
import re
import ply.lex as lex
from .errors import LexicalError

# ─── Tokens ────────────────────────────────────────────────────────────────────
reserved = {
    'PROGRAM':      'PROGRAM',
    'BEGIN':        'BEGIN',
    'END':          'END',
    'girar':        'GIRAR',
    'avanzar_vlts': 'AVANZAR_VLTS',
    'avanzar_ctms': 'AVANZAR_CTMS',
    'avanzar_mts':  'AVANZAR_MTS',
    'circulo':      'CIRCULO',
    'cuadrado':     'CUADRADO',
    'rotar':        'ROTAR',
    'caminar':      'CAMINAR',
    'moonwalk':     'MOONWALK',
}

tokens = [
    'ID', 'NUMBER',
    'PLUS', 'LPAREN', 'RPAREN',
    'SEMICOLON', 'DOT',
] + list(reserved.values())

# ─── Expresiones regulares sencillas ───────────────────────────────────────────
t_PLUS       = r'\+'
t_LPAREN     = r'\('
t_RPAREN     = r'\)'
t_SEMICOLON  = r';'
t_DOT        = r'\.'
t_ignore     = ' \t'

def t_NEWLINE(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

def t_COMMENT(t):
    r'//.*'
    pass

def t_NUMBER(t):
    r'-?\d+'
    t.value = int(t.value)
    return t

def t_ID(t):
    r'[A-Za-z_][A-Za-z0-9_]*'
    t.type = reserved.get(t.value, 'ID')
    return t

def t_error(t):
    col = _find_column(t)
    raise LexicalError(f'Error léxico: carácter inesperado "{t.value[0]}" '
                       f'(línea {t.lineno}, columna {col})')

def _find_column(token):
    last_cr = token.lexer.lexdata.rfind('\n', 0, token.lexpos)
    return (token.lexpos - last_cr)

lexer = lex.lex()
