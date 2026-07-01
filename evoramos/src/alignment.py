"""Alinhamento global de sequências usado pelo EvoRamos.

Este módulo reaproveita a ideia central do notebook da disciplina: o algoritmo
Needleman-Wunsch. A versão aqui foi isolada para ficar reutilizável pelo app e
não carregar a lógica de impressão/visualização do notebook para dentro do
projeto web.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class AlignmentResult:
    """Resultado de um alinhamento par a par."""

    aligned_a: str
    aligned_b: str
    score: int


def needleman_wunsch(
    seq_a: str,
    seq_b: str,
    match: int = 1,
    mismatch: int = -1,
    gap: int = -2,
) -> AlignmentResult:
    """Alinha duas sequências pelo algoritmo de Needleman-Wunsch.

    Needleman-Wunsch é um algoritmo clássico de programação dinâmica para
    alinhamento global. Ele compara duas sequências inteiras, permitindo a
    inserção de gaps ("-") quando isso melhora o alinhamento. No EvoRamos isso
    é importante porque usuários podem importar sequências fictícias com
    tamanhos diferentes.

    O score é útil para encontrar um bom alinhamento, mas ele não é usado
    diretamente pelo UPGMA. Para a árvore, convertemos o alinhamento em uma
    distância didática: número de mismatches e gaps.
    """

    seq_a = seq_a.upper()
    seq_b = seq_b.upper()
    rows = len(seq_a) + 1
    cols = len(seq_b) + 1
    matrix = [[0 for _ in range(cols)] for _ in range(rows)]

    for row in range(rows):
        matrix[row][0] = gap * row
    for col in range(cols):
        matrix[0][col] = gap * col

    for row in range(1, rows):
        for col in range(1, cols):
            diagonal_score = match if seq_a[row - 1] == seq_b[col - 1] else mismatch
            diagonal = matrix[row - 1][col - 1] + diagonal_score
            up = matrix[row - 1][col] + gap
            left = matrix[row][col - 1] + gap
            matrix[row][col] = max(diagonal, up, left)

    aligned_a: list[str] = []
    aligned_b: list[str] = []
    row = len(seq_a)
    col = len(seq_b)

    while row > 0 and col > 0:
        diagonal_score = match if seq_a[row - 1] == seq_b[col - 1] else mismatch
        if matrix[row][col] == matrix[row - 1][col - 1] + diagonal_score:
            aligned_a.append(seq_a[row - 1])
            aligned_b.append(seq_b[col - 1])
            row -= 1
            col -= 1
        elif matrix[row][col] == matrix[row - 1][col] + gap:
            aligned_a.append(seq_a[row - 1])
            aligned_b.append("-")
            row -= 1
        else:
            aligned_a.append("-")
            aligned_b.append(seq_b[col - 1])
            col -= 1

    while row > 0:
        aligned_a.append(seq_a[row - 1])
        aligned_b.append("-")
        row -= 1

    while col > 0:
        aligned_a.append("-")
        aligned_b.append(seq_b[col - 1])
        col -= 1

    return AlignmentResult(
        aligned_a="".join(reversed(aligned_a)),
        aligned_b="".join(reversed(aligned_b)),
        score=matrix[-1][-1],
    )


def alignment_difference_count(aligned_a: str, aligned_b: str) -> int:
    """Conta diferenças em duas sequências já alinhadas.

    A distância didática usada no projeto é simples: cada coluna diferente conta
    1, seja uma substituição de base ou a presença de gap. Colunas iguais contam
    0. Essa contagem não tenta modelar taxas evolutivas reais; ela só fornece uma
    medida intuitiva para o jogo.
    """

    if len(aligned_a) != len(aligned_b):
        raise ValueError("As sequências alinhadas devem ter o mesmo tamanho.")
    return sum(base_a != base_b for base_a, base_b in zip(aligned_a, aligned_b))
