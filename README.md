# 📌 SolidariHub – Sistema de Doações Comunitárias

O **SolidariHub** é uma plataforma web que conecta **ONGs** e **doadores** de forma simples, segura e transparente.  
Nosso objetivo é **organizar e facilitar o processo de doação**, garantindo mais confiança e clareza tanto para quem doa quanto para quem recebe.

---

## 🚀 Funcionalidades principais

- **Cadastro de Usuários**  
  ONGs e Doadores podem se registrar e acessar o sistema com segurança.  

- **Gerenciamento de Listas de Necessidades**  
  ONGs criam listas de itens organizados por categoria, subcategoria e quantidade necessária.  

- **Intenções de Doação**  
  Doadores demonstram interesse em doar itens de uma lista específica.  

- **Aprovação pela ONG**  
  A ONG pode aprovar, reprovar ou reverter intenções de doação, adicionando observações.  

- **Pedidos de Doação**  
  Quando a intenção é aprovada e confirmada pelo doador, o sistema gera automaticamente um pedido formal.  

- **Histórico e Acompanhamento**  
  Doadores e ONGs acompanham o status de intenções e pedidos em tempo real.  

- **Perfis de ONGs**  
  Doadores podem visualizar o perfil completo de uma ONG (informações, campanhas ativas, avaliações e feedbacks).  

- **Feedbacks**  
  Doadores podem avaliar pedidos concluídos e listas, ajudando a construir reputação e transparência.  

- **Notificações no Menu**  
  Doadores visualizam rapidamente quantas intenções e pedidos estão pendentes, aprovados ou em andamento.  

---

## 🗂️ Entidades principais

- **ONG** → dados cadastrais, status de verificação, descrição, campanhas criadas e avaliações recebidas.  
- **Doador** → informações básicas para login, contato e histórico de doações.  
- **Item** → categorias e subcategorias de produtos que podem ser doados.  
- **Lista** → criada pela ONG, agrupa os itens necessários em uma campanha de arrecadação.  
- **Intenção de Doação** → registro do interesse do doador em atender uma lista, com status:  
  - `0` → Pendente  
  - `1` → Aprovado  
  - `2` → Reprovado  
  - `3` → Finalizado  
- **Pedido** → confirmação formal da doação, gerado a partir de uma intenção aprovada e confirmada.  
- **Feedback** → avaliações e comentários feitos pelos doadores sobre pedidos e listas.  

---

## 🛠️ Tecnologias utilizadas

- **Linguagem**: Python (Flask)  
- **Banco de Dados**: PostgreSQL (RDS AWS)  
- **Bibliotecas**: psycopg2, bcrypt  
- **Frontend**: HTML5, CSS3, JavaScript  
- **Integrações**: busca de CEP, sistema de e-mails para recuperação de senha  
