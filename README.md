### README.md

# PySite - Aplicação Flask

PySite é uma aplicação web construída usando Flask, oferecendo várias funcionalidades como um sistema de autenticação, uma calculadora, exibição de valores de moedas, lista de praias limpas no Brasil, um bloco de notas e uma ferramenta de gestão financeira.

## Funcionalidades

1. **Autenticação de Usuário**:
   - Registro e login de usuários.
   - Logout e proteção de rotas para usuários autenticados.

2. **Calculadora**:
   - Calculadora simples para operações matemáticas básicas (adição, subtração, multiplicação e divisão).

3. **Valores de Moedas**:
   - Exibe os valores do dia para Dólar, Euro e Bitcoin.

4. **Praias Limpas do Brasil**:
   - Lista de algumas das praias mais limpas do Brasil.

5. **Bloco de Notas**:
   - Ferramenta para os usuários salvarem notas pessoais.

6. **Gestão Financeira**:
   - Registro de despesas e cálculo do total gasto.

## Instalação

1. Clone o repositório:
   ```bash
   git clone https://github.com/seu-usuario/py-site.git
   cd py-site
   ```

2. Crie e ative um ambiente virtual:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # No Windows use `venv\Scripts\activate`
   ```

3. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```

4. Configure o banco de dados:
   ```bash
   flask init-db
   ```

5. Execute a aplicação:
   ```bash
   flask run
   ```

## Uso

### Autenticação de Usuário

1. **Registro**:
   - Acesse `/auth/register` para criar uma nova conta de usuário.
   
2. **Login**:
   - Acesse `/auth/login` para fazer login.

### Calculadora

- Acesse `/calculadora` para utilizar a calculadora.

### Valores de Moedas

- Acesse `/moedas` para ver os valores atualizados de Dólar, Euro e Bitcoin.

### Praias Limpas do Brasil

- Acesse `/praias` para visualizar uma lista de praias limpas no Brasil.

### Bloco de Notas

- Acesse `/bloco-de-notas` para criar e salvar suas notas pessoais.

### Gestão Financeira

- Acesse `/gestao-financeira` para registrar suas despesas e visualizar o total gasto.

## Estrutura do Projeto

```plaintext
py-site/
│
├── app/
│   ├── __init__.py
│   ├── auth.py
│   ├── db.py
│   ├── views.py
│   ├── templates/
│   │   ├── base.html
│   │   ├── auth/
│   │   │   ├── login.html
│   │   │   ├── register.html
│   │   ├── calculadora.html
│   │   ├── moedas.html
│   │   ├── praias.html
│   │   ├── bloco_de_notas.html
│   │   ├── gestao_financeira.html
│   ├── static/
│   │   ├── css/
│   │   ├── js/
│
├── venv/
├── .gitignore
├── requirements.txt
├── config.py
├── run.py
└── README.md
```

## Dependências

- Flask
- Werkzeug
- requests

## Contribuição

1. Fork o repositório.
2. Crie sua feature branch (`git checkout -b feature/MinhaFeature`).
3. Commit suas mudanças (`git commit -am 'Adicionar minha feature'`).
4. Push para a branch (`git push origin feature/MinhaFeature`).
5. Abra um Pull Request.

## Licença

Este projeto está licenciado sob a MIT License - veja o arquivo [LICENSE](LICENSE) para mais detalhes.
