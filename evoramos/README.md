# EvoRamos

EvoRamos é um MVP de jogo educativo sobre árvores filogenéticas.
O jogador observa organismos fictícios com sequências de DNA, uma árvore gerada
automaticamente e precisa reconhecer eventos evolutivos como especiação,
hibridização e transferência horizontal de genes.

A construção da árvore usa uma implementação didática inspirada no UPGMA. A
solução é adequada para o MVP educacional, mas não deve ser apresentada como uma
ferramenta científica completa de reconstrução filogenética.

## Stack

- Python
- Dash
- Dash Cytoscape
- NetworkX
- SciPy
- pandas
- Biopython

## Lógica da árvore

A árvore é gerada em `src/tree_builder.py`, com apoio de `src/alignment.py` e
`src/distance.py`.

Fluxo usado:

1. Cada organismo começa como um cluster separado.
2. Cada par de sequências é alinhado com Needleman-Wunsch.
3. O alinhamento é convertido em distância contando mismatches e gaps.
4. A matriz de distâncias é construída.
5. O UPGMA agrupa sempre os dois clusters de menor distância.
6. A distância do novo cluster para os demais é recalculada por média ponderada:

```text
d((A,B), C) = (|A| * d(A,C) + |B| * d(B,C)) / (|A| + |B|)
```

7. A altura do novo cluster é calculada como metade da distância agrupada. O
   comprimento de ramo é registrado nas arestas como `branch_length`, mesmo que a
   visualização atual não use esse valor diretamente.

Importante: o UPGMA não escolhe o maior score de alinhamento. O score do
Needleman-Wunsch serve para produzir o alinhamento; o agrupamento da árvore usa a
menor distância entre clusters.

## Instalação

Entre na pasta do projeto, crie um ambiente virtual e instale as dependências:

```bash
cd evoramos
python -m venv .venv
```

No Windows:

```powershell
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

No Linux ou macOS:

```bash
source .venv/bin/activate
pip install -r requirements.txt
```

## Execução

```bash
python app.py
```

Depois, abra no navegador o endereço exibido no terminal, normalmente
`http://127.0.0.1:8050`.

## Verificação do UPGMA

Para testar apenas a lógica da árvore, sem abrir o Dash:

```bash
python -m scripts.verify_upgma
```

Esse script imprime:

- entrada com sequências fictícias;
- matriz de distâncias;
- agrupamentos feitos em ordem;
- arestas da árvore final com comprimentos de ramo.

## Importação de sequências

O modo livre aceita arquivo TXT com uma sequência por linha. Formatos aceitos:

```text
ATGCTACGTTAG
Musgo-serrano:ATGCTACGTCAG
Ramo curto:AGCT
```

Também é possível usar FASTA:

```text
>Musgo-claro
ATGCTACGTTAG
>Ramo curto
AGCT
```

As sequências podem ter tamanhos diferentes porque agora são alinhadas antes do
cálculo de distância.

## Estrutura

```text
evoramos/
├── app.py
├── requirements.txt
├── README.md
├── data/
│   ├── sequences.json
│   └── examples.json
├── src/
│   ├── alignment.py
│   ├── distance.py
│   ├── example_loader.py
│   ├── tree_builder.py
│   ├── game_rules.py
│   └── cytoscape_elements.py
├── frontend/
├── scripts/
│   └── verify_upgma.py
├── assets/
└── docs/
    └── project_notes.md
```

## Exercícios disponíveis

- Sequências muito parecidas
- Exemplo de especiação
- Exemplo de hibridização
- Exemplo de transferência horizontal
- Desafio misto

## Limitações

- A distância é didática: mismatches e gaps têm peso simples.
- Não há modelo evolutivo, correção por múltiplas substituições ou avaliação de
  incerteza.
- UPGMA assume uma ideia de relógio molecular/ultrametricidade, que não é
  verificada no MVP.
- Hibridização e transferência horizontal continuam como relações manuais do
  jogo, não como inferência automática.
