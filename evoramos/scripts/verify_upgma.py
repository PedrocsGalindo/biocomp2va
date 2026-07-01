"""Verificação simples da construção UPGMA didática.

Execute na raiz do projeto:

    python -m scripts.verify_upgma

O script imprime a matriz de distâncias, a ordem de agrupamentos e as arestas da
árvore final. Ele não depende do Dash e serve como teste rápido da lógica pura.
"""

from __future__ import annotations

from src.tree_builder import build_upgma_tree


EXAMPLE_ORGANISMS = [
    {
        "id": "a",
        "name": "Ramo-alfa",
        "sequence": "ATGCT",
        "description": "Sequência fictícia curta.",
    },
    {
        "id": "b",
        "name": "Ramo-beta",
        "sequence": "ATGTT",
        "description": "Difere de Ramo-alfa em uma posição.",
    },
    {
        "id": "c",
        "name": "Ramo-gama",
        "sequence": "AGCT",
        "description": "Tem tamanho menor, exigindo alinhamento com gap.",
    },
    {
        "id": "d",
        "name": "Ramo-delta",
        "sequence": "CGGTA",
        "description": "Sequência mais distante.",
    },
]


def main() -> None:
    result = build_upgma_tree(EXAMPLE_ORGANISMS)

    print("Matriz de distâncias por Needleman-Wunsch + mismatches/gaps")
    print("".ljust(16), end="")
    for label in result.labels:
        print(label[:14].rjust(16), end="")
    print()

    for label, row in zip(result.labels, result.distance_matrix):
        print(label[:14].ljust(16), end="")
        for value in row:
            print(str(value).rjust(16), end="")
        print()

    print("\nAgrupamentos UPGMA")
    for step in result.merge_steps:
        print(
            f"{step.step}. {step.left_id} + {step.right_id} -> {step.new_cluster_id} | "
            f"distância={step.distance:.3f} | altura={step.new_height:.3f} | "
            f"membros={', '.join(step.new_members)}"
        )

    print("\nArestas da árvore final")
    for source, target, data in result.graph.edges(data=True):
        print(
            f"{source} -> {target} | branch_length={data.get('branch_length')} | "
            f"merge_distance={data.get('merge_distance')}"
        )

    root_candidates = [node for node in result.graph.nodes if result.graph.in_degree(node) == 0]
    print(f"\nRaiz: {root_candidates[0] if root_candidates else 'não encontrada'}")


if __name__ == "__main__":
    main()
