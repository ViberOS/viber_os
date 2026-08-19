# ViberOS 1.2.0 — Ajuda rápida

O ViberOS inicia no **menu principal**. Digite o número do aplicativo e pressione `Enter`.

- `1` — Calendário
- `2` — Biblioteca de músicas
- `3` — Vibegotchi
- `4` — Vibe Invaders
- `5` — Conquistas
- `6` — Vibash
- `7` — Ajuda
- `8` — Desligar

No **Vibash**, pressione `Q` com a linha vazia ou use `menu` para voltar ao menu principal.

---

# Comandos do Vibash

**clear:** Limpa o histórico visível do terminal.

**whoami:** Mostra o nome do usuário atual.
- O alias antigo `whoiam` continua funcionando por compatibilidade.

**pwd:** Mostra o diretório de trabalho atual dentro do filesystem virtual.

**hostname:** Mostra o nome da máquina virtual: `vibe-os`.

**uname:** Mostra a versão do kernel/sistema do ViberOS.

**ls [caminho]:** Lista arquivos e diretórios.
- Sem argumento, lista a pasta atual.
- Com um caminho, lista o conteúdo daquele diretório.

**cd <caminho>:** Troca o diretório atual.
- `cd ..` volta um nível.
- O filesystem virtual não permite escapar da área do ViberOS.

**mkdir <pasta1> [pasta2 ...]:** Cria uma ou mais pastas.

**touch <arquivo>:** Cria um arquivo vazio.

**rm <arquivo>:** Remove um arquivo após confirmação.

**rmdir <pasta1> [pasta2 ...]:** Remove uma ou mais pastas vazias.

**cat <arquivo>:** Mostra o conteúdo de um arquivo.

**echo <texto>:** Mostra um texto no terminal.
- Para escrever em arquivo: `echo texto > arquivo.txt`.

**man <comando>:** Mostra a parte deste manual referente ao comando informado.

**help:** Abre esta ajuda dentro do ViberOS.

**calendar:** Abre o Calendário.

**music:** Abre a Biblioteca de músicas.
- `music next` — toca a próxima faixa.
- `music mute` — silencia a trilha.
- `music unmute` — reativa a trilha.
- `music status` — mostra a faixa atual.

**vibegotchi:** Abre o Vibegotchi.

**vibe_invaders:** Abre o Vibe Invaders.

**achievements:** Abre a Central de Conquistas.

**settings:** Mostra as configurações globais atuais.
- `settings volume 0.5` — volume entre `0` e `1`.
- `settings fade 1600` — duração da transição em milissegundos.
- `settings shuffle on|off` — ativa/desativa embaralhamento.
- `settings autoplay on|off` — ativa/desativa reprodução automática.

**changelog:** Mostra o changelog do projeto dentro do Vibash.

**logs:** Mostra as últimas linhas de `logs/viber_os.log`.

**menu:** Volta ao menu principal.

**shutdown:** Desliga o ViberOS usando a tela de desligamento em Textual.

**viber <prompt>:** Nome reservado para o antigo assistente Viber.
- O assistente está desativado nesta versão.

---

# Controles dos aplicativos

**Calendário**
- `←` / `→` ou `A` / `D` — muda o mês.
- `G` — ir para uma data (`DD/MM/AAAA`).
- `Q` ou `Esc` — voltar.

**Biblioteca de músicas**
- `↑` / `↓` — navegar pelas faixas.
- `Enter` — tocar a faixa selecionada.
- `N` — próxima música.
- `M` — mutar/desmutar.
- `Q` ou `Esc` — voltar.

**Vibegotchi**
- Na criação: digite o nome e pressione `Enter`; `Esc` cancela e volta.
- `↑` / `↓` — navegar pelas ações.
- `Enter` — confirmar a ação.
- `Q` ou `Esc` — voltar.

**Vibe Invaders**
- Menu: `↑` / `↓` e `Enter`.
- `A` / `←` — esquerda.
- `D` / `→` — direita.
- `Espaço` — atirar.
- `Q` ou `Esc` no menu do jogo — voltar ao ViberOS.

**Conquistas**
- `Q` ou `Esc` — voltar.

---

# Vibash

- `↑` / `↓` — histórico de comandos.
- `Tab` — autocomplete básico.
- `Ctrl+L` — limpa o terminal.
- `Q` com a linha vazia — volta ao menu.
- `Esc` — volta ao menu.

---

# Expressões matemáticas

O Vibash também aceita cálculos simples, por exemplo:

- `5 + 5`
- `10 * 8`
- `(4 + 2) ** 2`
- `25 % 4`

Operadores aceitos: `+`, `-`, `*`, `/`, `//`, `%`, `**` e `()`.

---

Existem comandos e experiências secretas que não aparecem neste manual. 👀
