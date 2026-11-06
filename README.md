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

## Como executar

### 1. Pré-requisitos
- **Python 3.9 ou superior:** https://www.python.org/downloads/
  Durante a instalação, **marque a caixa "Add python.exe to PATH"** antes de clicar em Install Now.
- **Git** (opcional): https://git-scm.com/download/win
  Sem o Git, clique em **Code → Download ZIP** neste repositório e extraia o arquivo.

### 2. Baixar o projeto
```bash
git clone https://github.com/MatheusRxzs/Projeto-Final-Engenharia-de-Software.git
```

### 3. Abrir o terminal dentro da pasta do projeto (Windows)
Abra a pasta do projeto (a que contém o arquivo `app.py`), clique na barra de
endereço do Explorador de Arquivos, apague o texto, digite `cmd` e aperte Enter.

### 4. Instalar e executar
```bash
cd Projeto-Final-Engenharia-de-Software
pip install -r requirements.txt
python app.py
```
Se aparecer "Acesso negado" na instalação, use: `python -m pip install --user -r requirements.txt`

### 5. Abrir o sistema
Acesse http://localhost:5000 no navegador e **mantenha o terminal aberto**.
O banco de dados é criado automaticamente na primeira execução.

### Executar os testes
```bash
python tests/test_api.py
```
## Capturas de tela

*Imagens do Projeto referenciadas no Relatorio Final*

## Gerenciamento do projeto

Quadro Trello: https://trello.com/b/Hubx4SVi/achados-e-perdidos-unima-projeto-final

## Documentação

Requisitos, diagramas UML, protótipos e casos de teste: [`docs/DOCUMENTACAO.md`](docs/DOCUMENTACAO.md)
