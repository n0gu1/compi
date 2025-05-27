# utils.py
from compiler.parser import Node

def flatten_ast(root) -> list[list]:
    """
    Recorre recursivamente el AST (que puede venir como Node o list[Node])
    y devuelve una lista de pasos en formato [comando, parámetro].
    """
    pasos: list[list] = []

    def walk(n):
        # Si es una lista, recorrer cada elemento
        if isinstance(n, list):
            for item in n:
                walk(item)
            return

        # Asegurarse de que sea un Node
        if not isinstance(n, Node):
            return

        # Instrucciones simples
        if n.tag in {
            "avanzar_mts", "avanzar_ctms", "avanzar_vlts",
            "girar", "rotar", "caminar", "moonwalk",
            "circulo", "cuadrado"
        }:
            pasos.append([n.tag, n.value])

        # Recorrer hijos
        for h in n.children:
            walk(h)

    walk(root)
    return pasos
