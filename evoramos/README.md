# EvoRamos

EvoRamos é um MVP de jogo educativo individual sobre árvores filogenéticas.
O jogador observará árvores construídas a partir de sequências fictícias de DNA
e deverá reconhecer eventos evolutivos, como especiação, hibridização e
transferência horizontal de genes.

Neste estágio, o projeto oferece somente uma base funcional: dados fictícios,
uma tabela de organismos e um grafo demonstrativo.

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
│   └── sequences.json
├── src/
│   ├── __init__.py
│   ├── distance.py
│   ├── tree_builder.py
│   ├── game_rules.py
│   └── cytoscape_elements.py
├── assets/
│   └── style.css
└── docs/
    └── project_notes.md
```

## Próximos passos

1. Implementar um algoritmo filogenético adequado.
2. Criar fases e desafios com dificuldade progressiva.
3. Permitir que o jogador selecione eventos no grafo.
4. Adicionar validação das respostas, pontuação e feedback educativo.
5. Incluir exemplos de hibridização e transferência horizontal de genes.
6. Criar testes automatizados para os módulos da aplicação.
