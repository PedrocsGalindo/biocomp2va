# Anotações iniciais do EvoRamos

## Conceitos biológicos

- **Sequência de DNA:** representação simplificada do material genético de cada
  organismo fictício.
- **Distância genética:** medida das diferenças entre duas sequências. O MVP
  começa com a distância de Hamming, adequada para sequências de mesmo tamanho.
- **Árvore filogenética:** representação das relações evolutivas entre
  organismos, baseada em características herdadas e diferenças genéticas.
- **Ancestral comum:** organismo ou população ancestral compartilhada por duas
  ou mais linhagens.

As sequências e os organismos do jogo são fictícios e têm finalidade didática.

## Eventos evolutivos a identificar

- **Especiação:** separação de uma linhagem em linhagens evolutivas distintas.
- **Hibridização:** combinação de material genético de linhagens diferentes.
- **Transferência horizontal de genes:** passagem de genes entre organismos sem
  uma relação direta de ancestralidade e descendência.

## Decisões técnicas do MVP

- Dash será usado para a interface web em Python.
- Dash Cytoscape exibirá e permitirá futuras interações com os grafos.
- NetworkX representará a árvore e outros relacionamentos evolutivos.
- Os dados iniciais ficarão em JSON para facilitar leitura e edição.
- O cálculo inicial usará distância de Hamming; SciPy e Biopython ficam
  disponíveis para algoritmos mais completos nas próximas etapas.
- O primeiro grafo é deliberadamente simples e não deve ser interpretado como
  uma reconstrução filogenética científica.
- A lógica de interface, cálculo, regras e visualização permanecerá separada em
  módulos para facilitar testes e evolução incremental.
