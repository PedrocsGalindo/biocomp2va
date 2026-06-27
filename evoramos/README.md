# EvoRamos

EvoRamos é um MVP de jogo educativo individual sobre árvores filogenéticas.
O jogador observará árvores construídas a partir de sequências fictícias de DNA
e deverá reconhecer eventos evolutivos, como especiação, hibridização e
transferência horizontal de genes.

O MVP oferece conceitos introdutórios, cinco exercícios guiados, comparação de
sequências e árvores didáticas interativas. Os exemplos destacam especiação,
hibridização e transferência horizontal de genes.

## Stack

- Python
- Dash
- Dash Cytoscape
- NetworkX
- SciPy
- pandas
- Biopython

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

## Estrutura

```text
evoramos/
├── app.py
├── requirements.txt
├── README.md
├── .gitignore
├── data/
│   ├── sequences.json
│   └── examples.json
├── src/
│   ├── __init__.py
│   ├── distance.py
│   ├── example_loader.py
│   ├── tree_builder.py
│   ├── game_rules.py
│   └── cytoscape_elements.py
├── assets/
│   └── style.css
└── docs/
    └── project_notes.md
```

## Próximos passos

1. Substituir o agrupamento didático por uma implementação completa de UPGMA.
2. Permitir que o jogador selecione eventos diretamente no grafo.
3. Adicionar validação das respostas, pontuação e feedback.
4. Explorar alinhamento de sequências com Biopython.
5. Criar testes automatizados para os módulos e callbacks.

## Exercícios disponíveis

- Sequências muito parecidas
- Exemplo de especiação
- Exemplo de hibridização
- Exemplo de transferência horizontal
- Desafio misto

As árvores atuais usam distância de Hamming e agrupamento didático. Elas foram
projetadas para aprendizagem e não representam reconstruções filogenéticas
científicas completas.
