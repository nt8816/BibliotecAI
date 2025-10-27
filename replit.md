# BibliotecAI - Sistema de Gestão de Biblioteca

## Visão Geral
BibliotecAI é um sistema de gestão de biblioteca desenvolvido em HTML, CSS e JavaScript puro. O sistema permite gerenciar livros, usuários (alunos e professores) e gerar relatórios em PDF.

## Estrutura do Projeto
```
.
├── dashboard.html      # Painel principal com resumo de estatísticas
├── livros.html         # Gestão de livros (CRUD)
├── usuarios.html       # Gestão de usuários (CRUD)
├── relatorios.html     # Relatórios e geração de PDF
├── script.js           # Lógica para gestão de livros
├── usuarios.js         # Lógica para gestão de usuários
├── relatorios.js       # Lógica para relatórios e PDF
├── style.css           # Estilos customizados
└── server.py           # Servidor HTTP Python para desenvolvimento
```

## Tecnologias Utilizadas
- **Frontend**: HTML5, CSS3, JavaScript (ES6+)
- **Frameworks CSS**: TailwindCSS (via CDN)
- **Ícones**: Font Awesome 6.4.0
- **Fontes**: Google Fonts (Nunito)
- **Bibliotecas JS**:
  - html2canvas (para captura de tela)
  - jsPDF (para geração de PDF)
- **Armazenamento**: LocalStorage do navegador
- **Servidor**: Python HTTP Server (desenvolvimento)

## Funcionalidades

### Dashboard
- Resumo visual de:
  - Total de livros
  - Total de usuários
  - Leituras ativas
  - Alertas
- Feed de atividades recentes

### Gestão de Livros
- Adicionar novos livros com campos:
  - Área do conhecimento
  - Tombo, ID
  - Autor, Título
  - Volume, Edição
  - Local, Editora, Ano
- Editar livros existentes
- Deletar livros
- Busca de livros

### Gestão de Usuários
- Adicionar usuários (Aluno/Professor/Outro)
- Campos dinâmicos baseados no tipo:
  - **Aluno**: Matrícula, Turma, Telefone
  - **Professor**: CPF, Telefone
- Editar e deletar usuários
- Persistência em LocalStorage

### Relatórios
- Visualização de estatísticas gerais:
  - Total de livros
  - Total de usuários
  - Alunos e professores
  - Pendências
- Tabela de usuários com pendências
- Geração de relatórios em PDF

## Como Executar

O servidor HTTP Python está configurado para rodar automaticamente na porta 5000.

### Manualmente
```bash
python server.py
```

Acesse: http://localhost:5000/dashboard.html

## Persistência de Dados
- Os dados são armazenados no **LocalStorage** do navegador
- Dados persistem entre sessões
- Nenhum banco de dados backend é necessário

## Arquitetura
Este é um aplicativo **frontend-only** que roda completamente no navegador:
- Sem backend ou API
- Sem banco de dados externo
- Toda lógica de negócio em JavaScript client-side
- Armazenamento local no navegador

## Navegação
O sistema possui uma sidebar fixa com navegação entre:
1. Dashboard (dashboard.html)
2. Livros (livros.html)
3. Usuários (usuarios.html)
4. Relatórios (relatorios.html)

## Estado Atual
- ✅ Frontend completo e funcional
- ✅ Sistema de CRUD para livros
- ✅ Sistema de CRUD para usuários
- ✅ Geração de relatórios em PDF
- ✅ Interface responsiva
- ✅ Persistência em LocalStorage

## Próximos Passos Potenciais
- Implementar busca funcional
- Adicionar sistema de empréstimos/devoluções
- Implementar autenticação de usuários
- Migrar para backend com banco de dados real
- Adicionar validações mais robustas

## Data de Importação
27 de outubro de 2025
