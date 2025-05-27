# errors.py
class CompilerError(Exception):
    """Base para cualquier fallo en el compilador."""

class LexicalError(CompilerError):
    pass

class SyntaxCompilerError(CompilerError):
    pass

class SemanticCompilerError(CompilerError):
    pass
