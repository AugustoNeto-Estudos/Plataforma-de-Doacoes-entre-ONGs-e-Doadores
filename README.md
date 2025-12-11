# SolidariHub – Plataforma de Doações entre ONGs e Doadores

**SolidariHub** é uma plataforma web desenvolvida para conectar ONGs e doadores de forma simples, segura e transparente. O objetivo é facilitar o processo de doação, tornando-o mais organizado e confiável para ambas as partes.

## Funcionalidades Principais

- **Cadastro de Usuários**: ONGs e doadores podem se registrar e acessar o sistema.
- **Gerenciamento de Listas(Campanhas)**: ONGs criam listas(campanhas) de itens necessários, organizadas por categoria e quantidade.
- **Intenção de Doação**: Doadores demonstram interesse em doar para listas específicas.
- **Pedidos de Doação**: Após confirmação mútua, o sistema gera um pedido formal.
- **Histórico e Acompanhamento**: Acompanhamento de status de listas, intenções e pedidos.

## Entidades do Sistema

- **ONG**: Dados cadastrais, status de verificação e descrição.
- **Doador**: Informações básicas para login e contato.
- **Item**: Categorias e subcategorias de itens.
- **Lista**: Criada pela ONG, agrupa os itens necessários.
- **Intenção de Doação**: Registro do interesse do doador.
- **Pedido**: Confirmação da doação após aceite da ONG e doador.

## Tecnologias Utilizadas

- **Linguagem**: Python com Flask(Microframework)
- **Banco de Dados**: PostgreSQL (Hospedado no RDS AWS)
- **Server**: Em nosso projeto optamos e recomendamos utilização de computação em nuvem para maior escalabilidade, Utilizamos em nosso caso hospedagem http em um EC2, configurando o systemd para que o sistema rode em background junto a instancia, liberando a porta 5000 para conexão de usuarios comuns ao website
- **Bibliotecas**: psycopg2, psycopg2-binary, Flask, Flask-Mail, geopy, bcrypt, requests, reportlab, python-dotenv



## Objetivo do Projeto

Promover a solidariedade e fortalecer a relação entre ONGs e doadores, oferecendo uma solução tecnológica que garanta transparência, organização e eficiência em todo o processo de doação.

---

> ⚠️ Este repositório contém o código-fonte do projeto, com exceção das variáveis de ambiente e credenciais sensíveis.
