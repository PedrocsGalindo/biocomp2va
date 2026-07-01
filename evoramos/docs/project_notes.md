# Anotações do EvoRamos

## Conceitos biológicos

- **Sequência de DNA:** representação simplificada do material genético de cada
  organismo fictício.
- **Alinhamento de sequências:** comparação entre sequências que podem ter
  tamanhos diferentes. O projeto usa Needleman-Wunsch para inserir gaps quando
  necessário.
- **Distância genética didática:** medida das diferenças entre duas sequências
  após alinhamento. No MVP, cada mismatch ou gap conta como 1 diferença.
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

- Dash é usado para a interface web em Python.
- Dash Cytoscape exibe e permite interações com os grafos.
- NetworkX representa a árvore e os relacionamentos evolutivos.
- Os dados iniciais ficam em JSON para facilitar leitura e edição.
- A construção da árvore usa uma implementação didática inspirada no UPGMA:
  1. alinhamento global par a par com Needleman-Wunsch;
  2. conversão do alinhamento em distância por contagem de mismatches e gaps;
  3. matriz de distâncias;
  4. agrupamento pelo par de menor distância;
  5. atualização de distância por média ponderada pelo tamanho dos clusters.
- O UPGMA não escolhe o maior score de alinhamento diretamente. O score é usado
  apenas para obter o alinhamento; a árvore é construída por menor distância.
- Hibridização e transferência horizontal são relações especiais manuais e
  didáticas. O MVP não tenta inferir esses eventos automaticamente.
- A árvore não deve ser interpretada como reconstrução filogenética científica
  completa. Ela é uma simplificação honesta para fins educacionais.
