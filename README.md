# 📘 Flow2Doc - Gerador de Documentação Automática (v2.0)

> **Automatize a criação de manuais, tutoriais e wikis enquanto navega.**

O **Flow2Doc** é uma ferramenta desenvolvida em Python + Playwright que "assiste" a sua navegação e gera automaticamente documentação passo a passo em Markdown. Ele captura telas, destaca cliques, registra preenchimentos de formulários e organiza tudo em uma estrutura pronta para publicação.

---

## 🚀 Novidades da Versão 2.0

Esta versão traz uma reescrita completa da arquitetura do sistema para garantir precisão absoluta nas capturas.

| Recurso | Descrição da Melhoria |
| :--- | :--- |
| **Trava de Navegação** | O sistema intercepta o clique, **pausa o navegador**, tira o print e só então libera a ação. Isso elimina prints tirados "no meio" do carregamento de página. |
| **Smart Debounce** | Evita prints duplicados em formulários. O sistema aguarda você terminar de digitar ou clicar em "Entrar" antes de registrar a ação. |
| **Crash Safe** | Se o navegador for fechado acidentalmente ou travar, o sistema salva automaticamente todo o progresso feito até aquele momento. |
| **Limpeza Real** | O botão "Desfazer" agora remove o passo do log e **deleta o arquivo de imagem** do disco, mantendo a pasta limpa. |
| **Arquitetura Modular** | Código separado em `Core`, `Utils` e `UI`, facilitando a manutenção e expansão. |

---

## 🛠️ Funcionalidades

* **Painel de Controle Injetado:** Interface flutuante dentro do próprio navegador.
* **Captura Inteligente:**
    * 🟡 **Cliques:** Gera destaque visual amarelo e congela a ação para o print.
    * 🟢 **Inputs:** Detecta campos de texto, destaca em verde e oculta senhas (`******`).
* **Notas Manuais:** Botão dedicado para capturar telas específicas com observações personalizadas.
* **Comentários de Passo:** Permite adicionar instruções que aparecerão acima do próximo print.
* **Organização Automática:** Cria pastas isoladas para cada projeto (`docs/NomeDoProjeto/`).

---

## 📂 Estrutura do Projeto

```text
Flow2Doc/
├── main.py                 # Arquivo Principal (Start)
├── config.py               # Configurações (Proxy, Pastas)
├── core/
│   ├── browser_js.py       # Lógica Frontend (Injeção JS, Listeners)
│   ├── generator.py        # Lógica Backend (Orquestrador)
│   └── file_manager.py     # Gestão de arquivos e limpeza
├── utils/
│   └── formatter.py        # Formatação do Markdown
└── docs/                   # Pasta de Saída
    └── NomeDoProjeto/      # Seu Manual Gerado
        ├── images/         # Prints (ex: Projeto_01.png)
        └── NomeDoProjeto.md
