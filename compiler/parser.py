# parser.py
import ply.yacc as yacc
from .lexer import tokens, lexer
from .errors import SyntaxCompilerError, SemanticCompilerError

# ─── AST simple ────────────────────────────────────────────────────────────────
class Node:
    def __init__(self, tag, children=None, value=None):
        self.tag = tag
        self.children = children or []
        self.value = value
    def __repr__(self):
        return f'{self.tag}({self.value if self.value is not None else ""}, {self.children})'

# ─── Gramática ────────────────────────────────────────────────────────────────
def p_program(p):
    'program : PROGRAM ID BEGIN sentence_list END DOT'
    p[0] = Node('program', [p[4]], p[2])

def p_sentence_list(p):
    '''sentence_list : sentence_list sentence
                     | sentence'''
    p[0] = p[1] + [p[2]] if len(p) == 3 else [p[1]]

def p_sentence(p):
    'sentence : instruction SEMICOLON'
    p[0] = p[1]

def p_instruction_single(p):
    '''instruction : move_instr
                   | draw_instr'''
    p[0] = p[1]

def p_instruction_combo(p):
    'instruction : instruction PLUS instruction'
    p[0] = Node('combo', [p[1], p[3]])

# ─── Movimiento ───────────────────────────────────────────────────────────────
def p_move_instr(p):
    '''move_instr : girar
                  | avanzar_vlts
                  | avanzar_ctms
                  | avanzar_mts
                  | rotar
                  | caminar
                  | moonwalk'''
    p[0] = p[1]

def p_girar(p):
    'girar : GIRAR LPAREN NUMBER RPAREN'
    if p[3] not in (-1, 0, 1):
        _semantic_error('girar(n) solo acepta -1, 0 ó 1.', p)
    p[0] = Node('girar', value=p[3])

def p_avanzar_vlts(p):
    'avanzar_vlts : AVANZAR_VLTS LPAREN NUMBER RPAREN'
    _validate_nonzero(p, 3)
    p[0] = Node('avanzar_vlts', value=p[3])

def p_avanzar_ctms(p):
    'avanzar_ctms : AVANZAR_CTMS LPAREN NUMBER RPAREN'
    _validate_nonzero(p, 3)
    p[0] = Node('avanzar_ctms', value=p[3])

def p_avanzar_mts(p):
    'avanzar_mts : AVANZAR_MTS LPAREN NUMBER RPAREN'
    _validate_nonzero(p, 3)
    p[0] = Node('avanzar_mts', value=p[3])

def p_rotar(p):
    'rotar : ROTAR LPAREN NUMBER RPAREN'
    _validate_nonzero(p, 3)
    p[0] = Node('rotar', value=p[3])

def p_caminar(p):
    'caminar : CAMINAR LPAREN NUMBER RPAREN'
    _validate_nonzero(p, 3)
    p[0] = Node('caminar', value=p[3])

def p_moonwalk(p):
    'moonwalk : MOONWALK LPAREN NUMBER RPAREN'
    _validate_nonzero(p, 3)
    p[0] = Node('moonwalk', value=p[3])

# ─── Dibujo ───────────────────────────────────────────────────────────────────
def p_draw_instr(p):
    '''draw_instr : circulo
                  | cuadrado'''
    p[0] = p[1]

def p_circulo(p):
    'circulo : CIRCULO LPAREN NUMBER RPAREN'
    r = p[3]
    if not (10 <= r <= 200):
        _semantic_error(f'Radio {r} fuera de rango (10–200 cm).', p)
    p[0] = Node('circulo', value=r)

def p_cuadrado(p):
    'cuadrado : CUADRADO LPAREN NUMBER RPAREN'
    l = p[3]
    if not (10 <= l <= 200):
        _semantic_error(f'Lado {l} fuera de rango (10–200 cm).', p)
    p[0] = Node('cuadrado', value=l)

# ─── Manejo de errores ────────────────────────────────────────────────────────
def p_error(p):
    if p:
        raise SyntaxCompilerError(f'Error de sintaxis: símbolo inesperado "{p.value}" '
                                  f'(línea {p.lineno})')
    else:
        raise SyntaxCompilerError('Error de sintaxis: fin de archivo inesperado.')

def _validate_nonzero(p, idx):
    if p[idx] == 0:
        _semantic_error('El parámetro no puede ser 0.', p)

def _semantic_error(msg, p):
    raise SemanticCompilerError(f'Error semántico: {msg} (línea {p.lineno(1)})')

parser = yacc.yacc()
