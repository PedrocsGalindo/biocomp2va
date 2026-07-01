"""Distâncias didáticas entre sequências de DNA."""

from __future__ import annotations

from typing import Any

from src.alignment import alignment_difference_count, needleman_wunsch


def aligned_sequence_distance(seq1: str, seq2: str) -> int:
    """Calcula distância entre duas sequências após Needleman-Wunsch.

    Diferente da distância de Hamming, esta função aceita sequências de tamanhos
    diferentes. Primeiro ela faz alinhamento global e depois conta mismatches e
    gaps no alinhamento gerado.
    """

    alignment = needleman_wunsch(seq1, seq2)
    return alignment_difference_count(alignment.aligned_a, alignment.aligned_b)


def hamming_distance(seq1: str, seq2: str) -> int:
    """Retorna o número de posições diferentes entre sequências de mesmo tamanho.

    Mantida por compatibilidade, mas a construção da árvore agora usa
    ``aligned_sequence_distance`` para suportar sequências com tamanhos
    diferentes.
    """

    if len(seq1) != len(seq2):
        raise ValueError("As sequências devem ter o mesmo tamanho.")
    return sum(base1 != base2 for base1, base2 in zip(seq1, seq2))


def build_distance_matrix(sequences: list[dict[str, Any]]) -> list[list[int]]:
    """Constrói uma matriz simétrica de distâncias por alinhamento.

    Cada item da lista deve ser um organismo com uma chave ``sequence``. A matriz
    resultante é a base da etapa UPGMA: o agrupamento escolhe a menor distância,
    não o maior score de alinhamento.
    """

    return [
        [
            aligned_sequence_distance(organism_a["sequence"], organism_b["sequence"])
            for organism_b in sequences
        ]
        for organism_a in sequences
    ]
