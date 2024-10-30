# PySite - Aplicação Flask

**PySite** é uma aplicação web desenvolvida com Flask que oferece uma variedade de funcionalidades práticas e interativas. Com um design amigável e uma experiência do usuário intuitiva, o PySite é projetado para facilitar o acesso a diversas ferramentas úteis.

## Funcionalidades

- **Autenticação de Usuário**: Registro e login seguros, incluindo logout e proteção de rotas para usuários autenticados.
- **Calculadora**: Uma calculadora simples para realizar operações matemáticas básicas, como adição, subtração, multiplicação e divisão.
- **Valores de Moedas**: Exibe os valores atualizados do Dólar, Euro e Bitcoin em tempo real.
- **Praias Limpas do Brasil**: Uma lista de algumas das praias mais limpas do Brasil, promovendo turismo responsável.
- **Bloco de Notas**: Permite aos usuários criar e salvar notas pessoais para facilitar a organização.
- **Gestão Financeira**: Ferramenta para registrar despesas e calcular o total gasto, com a opção de baixar as despesas em formato CSV e excluir entradas.
- **Blog**: Seção dedicada a postagens de blog, permitindo a leitura de artigos sobre diversos temas.
- **Notícias**: Tela para exibição de notícias atualizadas, mantendo os usuários informados sobre eventos recentes.
- **Projetos e Sobre**: Informações sobre projetos e trabalhos realizados, destacando as experiências e conquistas da equipe.

## Instalação

Siga as etapas abaixo para configurar a aplicação localmente:

1. **Clone o repositório**:

   ```bash
   git clone https://github.com/seu-usuario/py-site.git
   cd py-site

2. **Crie e ative um ambiente virtual:**:

   ```bash
   python3 -m venv venv
   source venv/bin/activate  # Para Windows, use `venv\Scripts\activate`
   
3. **Instale as dependências:**:

   ```bash
   pip install -r requirements.txt
   
   
4. **Configure o banco de dados:**:

   ```bash
   flask init-db
   

5. **Execute a aplicação:**:

   ```bash
      flask run


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
│   │   ├── blog.html
│   │   ├── noticias.html
│   │   ├── projetos.html
│   │   ├── sobre.html
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

## Contribuição

Contribuições são bem-vindas! Para contribuir:

1. Fork o repositório.
2. Crie sua branch de feature: `git checkout -b feature/MinhaFeature`.
3. Commit suas mudanças: `git commit -am 'Adicionar minha feature'`.
4. Push para a branch: `git push origin feature/MinhaFeature`.
5. Abra um Pull Request.

## Licença

Este projeto está licenciado sob a MIT License - veja o arquivo LICENSE para mais detalhes.
