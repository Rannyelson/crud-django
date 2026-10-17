# CRUD de Produtos com Django

Aplicação web acadêmica para gerenciamento de produtos, desenvolvida com Python e Django. O sistema demonstra as quatro operações fundamentais de persistência de dados:

- cadastro de produtos;
- listagem dos registros;
- atualização de informações;
- exclusão com confirmação.

Cada produto possui nome, preço, descrição, imagem e categoria. As categorias são cadastradas em um modelo próprio e relacionadas aos produtos por meio de uma chave estrangeira (ForeignKey). A interface utiliza Bootstrap 5, Django Crispy Forms e cards responsivos, com mensagens de feedback após cada operação.

## Tecnologias

- Python 3.12;
- Django 5.0.6;
- SQLite para desenvolvimento local;
- PostgreSQL opcional por meio de `DATABASE_URL`;
- Bootstrap 5 e Crispy Forms;
- Pillow para imagens;
- WhiteNoise e Gunicorn para implantação.

## Instalação no Windows

```powershell
git clone https://github.com/Rannyelson/crud-django.git
cd crud-django
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python manage.py migrate
python manage.py seed_products
python manage.py runserver
```

Acesse `http://127.0.0.1:8000/`.

Se a ativação do ambiente virtual for bloqueada, os comandos podem ser executados diretamente:

```powershell
.\.venv\Scripts\python.exe manage.py migrate
.\.venv\Scripts\python.exe manage.py seed_products
.\.venv\Scripts\python.exe manage.py runserver
```

## Produtos de demonstração

O projeto inclui seis produtos fictícios em três categorias (Eletrônicos, Acessórios e Casa). As imagens de demonstração são geradas automaticamente com Pillow. Para inserir ou atualizar os dados:

```powershell
python manage.py seed_products
```

O comando é idempotente e não cria duplicatas. Para substituir os produtos atuais pelos dados de demonstração:

```powershell
python manage.py seed_products --reset
```

## Testes

```powershell
python manage.py check
python manage.py test
```

A suíte automatizada cobre listagem, cadastro, atualização, exclusão e idempotência dos seeds.

## Relatório acadêmico

O arquivo [`RELATORIO_PROJETO.md`](RELATORIO_PROJETO.md) contém a explicação completa da arquitetura MTV, modelo de dados, rotas, segurança, instalação, melhorias futuras e um roteiro curto para apresentação.

## Configuração de produção

Informações sensíveis não ficam no código. Em produção, configure as variáveis:

- `DJANGO_SECRET_KEY`;
- `DJANGO_DEBUG=False`;
- `DJANGO_ALLOWED_HOSTS`;
- `DATABASE_URL`.

## Licença

Distribuído sob a licença MIT presente no arquivo `LICENSE`.
