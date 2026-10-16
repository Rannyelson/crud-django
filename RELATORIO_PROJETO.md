# Relatório — Sistema CRUD de Produtos com Django

## 1. Visão geral

Este projeto é uma aplicação web para cadastro e gerenciamento de produtos. Ele foi desenvolvido com Python e o framework Django e demonstra as quatro operações fundamentais de persistência de dados, conhecidas pela sigla CRUD:

- **Create (Criar):** cadastrar um produto;
- **Read (Ler):** listar os produtos cadastrados;
- **Update (Atualizar):** alterar os dados de um produto;
- **Delete (Excluir):** remover um produto.

Cada produto possui nome, preço, descrição e imagem. A interface usa Bootstrap 5 para oferecer uma apresentação responsiva e componentes prontos, como cartões, barra de navegação e janelas modais.

## 2. Objetivo acadêmico

O objetivo do sistema é demonstrar como uma aplicação web organiza a comunicação entre interface, regras de aplicação e banco de dados. O projeto também exemplifica o padrão arquitetural MTV utilizado pelo Django:

- **Model:** representa e manipula os dados;
- **Template:** apresenta as páginas HTML ao usuário;
- **View:** recebe as requisições, executa a lógica e devolve uma resposta.

O MTV é semelhante ao MVC. No Django, a View exerce boa parte do papel de controlador, enquanto o Template representa a camada visual.

## 3. Tecnologias utilizadas

| Tecnologia | Função no projeto |
|---|---|
| Python 3.12 | Linguagem de programação |
| Django 5.0.6 | Framework web e ORM |
| SQLite | Banco de dados local padrão |
| PostgreSQL | Banco opcional para produção por meio de `DATABASE_URL` |
| HTML e Bootstrap 5 | Estrutura e aparência das páginas |
| Django Crispy Forms | Renderização do formulário com Bootstrap |
| Pillow | Validação e processamento de imagens |
| WhiteNoise | Entrega de arquivos estáticos em produção |
| Gunicorn | Servidor WSGI para implantação em Linux |

## 4. Organização do projeto

```text
crud-django/
├── crud_app/                  # Aplicação de produtos
│   ├── migrations/            # Histórico da estrutura do banco
│   ├── admin.py               # Registro no painel administrativo
│   ├── forms.py               # Formulário baseado no modelo
│   ├── models.py              # Modelo Product
│   ├── tests.py               # Testes automatizados do CRUD
│   ├── urls.py                # Rotas da aplicação
│   └── views.py               # Lógica das operações CRUD
├── crud_project/              # Configuração geral do Django
│   ├── settings.py            # Banco, idioma, apps e arquivos estáticos
│   └── urls.py                # Roteamento principal
├── templates/                 # Páginas HTML
├── staticfiles/               # Arquivos estáticos coletados
├── db.sqlite3                 # Banco de dados local
├── manage.py                  # Utilitário de administração do Django
└── requirements.txt           # Dependências Python
```

## 5. Modelo de dados

A entidade principal é `Product`, definida em `crud_app/models.py`.

| Campo | Tipo | Finalidade |
|---|---|---|
| `id` | BigAutoField | Identificador gerado automaticamente |
| `name` | CharField | Nome do produto, com até 100 caracteres |
| `price` | IntegerField | Preço armazenado como número inteiro |
| `description` | TextField | Descrição livre do produto |
| `image` | ImageField | Caminho da imagem salva em `media/products/` |

O ORM do Django converte operações Python, como `Product.objects.all()` e `form.save()`, em comandos SQL. Assim, a aplicação não precisa montar SQL manualmente.

## 6. Fluxo das funcionalidades

### Listagem

A rota `/` executa a função `index`. Ela consulta todos os produtos e envia a coleção ao template `index.html`, que monta um cartão Bootstrap para cada item.

### Cadastro

A rota `/create` exibe um `ModelForm`. Em uma requisição POST, o Django valida texto, número e imagem. Se os dados forem válidos, `form.save()` grava o produto e o usuário volta à página inicial.

### Atualização

A rota `/update` lista os produtos. Cada cartão abre uma janela modal preenchida com os dados atuais. Ao confirmar, a View localiza o registro pela chave primária, atualiza os campos e salva as mudanças.

### Exclusão

A rota `/delete` lista os produtos e abre uma confirmação em modal. O formulário envia o identificador por POST e a View exclui o registro correspondente. O token CSRF protege a requisição contra envios originados de sites maliciosos.

## 7. Rotas

| Método | URL | View | Resultado |
|---|---|---|---|
| GET | `/` | `index` | Lista produtos |
| GET/POST | `/create` | `create` | Exibe o formulário ou cria um produto |
| GET/POST | `/update` | `update` | Lista ou atualiza um produto |
| GET/POST | `/delete` | `delete` | Lista ou exclui um produto |
| GET | `/admin/` | Django Admin | Painel administrativo |

## 8. Segurança e configurações

O código recebido continha uma chave secreta e credenciais de PostgreSQL diretamente em `settings.py`. A configuração local foi corrigida para usar SQLite por padrão e variáveis de ambiente em produção:

- `DJANGO_SECRET_KEY`: chave secreta da aplicação;
- `DJANGO_DEBUG`: ativa ou desativa o modo de depuração;
- `DJANGO_ALLOWED_HOSTS`: hosts permitidos, separados por vírgula;
- `DATABASE_URL`: conexão opcional com PostgreSQL.

As credenciais que já apareceram no histórico Git devem ser revogadas e substituídas no provedor do banco. Apagar apenas o texto do arquivo atual não remove o segredo dos commits anteriores.

O Django também fornece proteção CSRF, escape automático de HTML, validação de formulários, sistema de autenticação e ORM, recursos que reduzem riscos comuns quando usados corretamente.

## 9. Instalação e execução no Windows

Na pasta do projeto, execute:

```powershell
.\.venv\Scripts\Activate.ps1
python manage.py migrate
python manage.py runserver
```

Depois, abra `http://127.0.0.1:8000/` no navegador. Para encerrar o servidor, pressione `Ctrl+C`.

Para carregar ou atualizar os seis produtos fictícios da demonstração:

```powershell
python manage.py seed_products
```

O comando é idempotente: pode ser executado novamente sem duplicar os produtos. Para apagar os produtos atuais e restaurar somente os dados de demonstração, use `python manage.py seed_products --reset`.

Se for necessário recriar o ambiente:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

## 10. Testes e validação

A suíte em `crud_app/tests.py` verifica listagem, cadastro, atualização e exclusão. Ela usa um banco temporário, separado do banco local.

```powershell
python manage.py check
python manage.py test
```

Também foi executado `collectstatic`, que prepara os arquivos usados pelo painel administrativo e pelo WhiteNoise.

## 11. Pontos positivos e melhorias futuras

### Pontos positivos

- separação clara entre Model, Template e View;
- uso do ORM e de `ModelForm`;
- suporte a upload de imagens;
- interface responsiva com Bootstrap;
- painel administrativo nativo do Django;
- configuração para SQLite local e PostgreSQL em produção.

### Melhorias recomendadas

- usar `DecimalField` em vez de `IntegerField` para preços com centavos;
- adicionar autenticação e autorização para impedir alterações anônimas;
- usar formulários Django também na atualização;
- tratar registros inexistentes com `get_object_or_404`;
- excluir o arquivo de imagem quando um produto for removido;
- adicionar paginação, pesquisa e ordenação;
- melhorar acessibilidade e traduzir todos os textos da interface;
- definir limites de tamanho e tipos permitidos no upload;
- ampliar os testes para validações e casos de erro.

## 12. Roteiro curto para apresentação

1. **Problema:** apresentar a necessidade de cadastrar e administrar produtos.
2. **Conceito central:** explicar que CRUD significa criar, ler, atualizar e excluir.
3. **Arquitetura:** mostrar Model, View e Template e como eles se comunicam.
4. **Banco:** apresentar a tabela de produtos e explicar o ORM.
5. **Demonstração:** cadastrar, listar, editar e excluir um produto.
6. **Segurança:** destacar POST, token CSRF e variáveis de ambiente.
7. **Qualidade:** executar ou mencionar os quatro testes automatizados.
8. **Conclusão:** comentar as melhorias futuras, especialmente autenticação e preço decimal.

## 13. Conclusão

O projeto cumpre o propósito de demonstrar um CRUD completo com Django. Apesar de simples, ele percorre o fluxo essencial de uma aplicação web: o navegador envia uma requisição, uma View executa a regra, o ORM acessa o banco e um Template devolve HTML. Com as configurações locais e os testes adicionados, o sistema pode ser executado e apresentado de forma reproduzível.
