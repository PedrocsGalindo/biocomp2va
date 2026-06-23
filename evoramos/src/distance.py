"""Funções básicas para calcular distâncias entre sequências de DNA."""

from typing import Any


def hamming_distance(seq1: str, seq2: str) -> int:
    """Retorna o número de posições diferentes entre duas sequências.

    As sequências precisam possuir o mesmo tamanho.
    """
    if len(seq1) != len(seq2):
        raise ValueError("As sequências devem ter o mesmo tamanho.")

    return sum(base1 != base2 for base1, base2 in zip(seq1, seq2))


def build_distance_matrix(sequences: list[dict[str, Any]]) -> list[list[int]]:
    """Constrói uma matriz simétrica de distâncias de Hamming.

    Cada item da lista deve ser um organismo com uma chave ``sequence``.
    """
    return [
        [
            hamming_distance(organism_a["sequence"], organism_b["sequence"])
            for organism_b in sequences
        ]
        for organism_a in sequences
    ]
