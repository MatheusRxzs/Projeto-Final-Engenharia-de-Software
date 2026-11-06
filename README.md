# Achados e Perdidos UNIMA

Sistema web para registrar e buscar objetos perdidos e achados no campus do Centro Universitário de Maceió (UNIMA).

## Problema que resolve

Hoje, objetos perdidos no campus dependem de avisos em grupos de mensagens e do "boca a boca". O sistema centraliza os registros em um só lugar, com busca e contato direto entre quem perdeu e quem achou.

## Integrantes da equipe

* *Matheus Embs Carvalho Embs*
* Mateus Souza da Silva Barboza
* Kalle Anthony dos Santos
* Carlos Eduardo Lessa Tenório

## Tecnologias

* **Back end:** Python 3 + Flask (API REST)
* **Banco de dados:** SQLite (arquivo `achados.db`, criado automaticamente)
* **Front end:** HTML, CSS e JavaScript puros (pasta `static/`)
* **Testes:** `unittest`

## Principais funcionalidades

* Criar conta e entrar (senha armazenada com hash)
* Registrar item perdido ou achado, com contato por e-mail, telefone/WhatsApp ou ambos
* Listar, buscar por texto e filtrar por tipo, categoria e situação
* Marcar item como devolvido
* Editar e excluir os próprios registros
* Contato de quem registrou visível apenas para usuários logados

## Como executar

Requer Python 3.9+.

```bash
git clone <URL-DO-REPOSITORIO>
cd achados-perdidos-unima
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\\\\\\\\Scripts\\\\\\\\activate
pip install -r requirements.txt
python app.py
```

Abra http://localhost:5000. O banco é criado na primeira execução.

Para rodar os testes: `python tests/test\\\\\\\_api.py`

## Capturas de tela

*Adicionar em `docs/img/` e referenciar aqui (tela inicial, cadastro de item, lista filtrada).*

## Gerenciamento do projeto

Quadro Trello: https://trello.com/b/Hubx4SVi/achados-e-perdidos-unima-projeto-final

## Documentação

Requisitos, diagramas UML, protótipos e casos de teste: [`docs/DOCUMENTACAO.md`](docs/DOCUMENTACAO.md)
