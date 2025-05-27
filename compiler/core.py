# core.py
from __future__ import annotations

from .lexer   import lexer
from .parser  import parser, Node
from .errors  import CompilerError


def compile_text(src: str) -> str:
    """
    Analiza «src» y devuelve:
      • "OK" .......................... si todo pasó sin errores
      • "<mensaje de error>" .......... si se lanzó Lexical/Syntax/Semantic error
    """
    lexer.lineno = 1          # ← reinicia el contador de líneas de PLY
    try:
        parser.parse(src, lexer=lexer)
        return "OK"
    except CompilerError as e:
        return str(e)


def compile_to_ast(src: str) -> Node | None:
    """
    Devuelve el AST (objeto Node) o None si hubo fallo.
    """
    lexer.lineno = 1          # ← también reinicia aquí
    try:
        return parser.parse(src, lexer=lexer)
    except CompilerError:
        return None
