# Changelog - ViberOS

Todas as mudanças notáveis do ViberOS serão documentadas aqui.

O formato é baseado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.0.0/).

---

## [1.2.0] - 19-08-2026

### Adicionado
- Runtime principal baseado em Textual.
- Novo shell **Vibash**, inspirado em Bash, com histórico de comandos e autocomplete básico.
- Opção **[6] Vibash** no menu principal e atalho `Q` com linha vazia para retornar ao menu.
- Playlist automática com shuffle, fila sem repetição imediata e transições fade-out/fade-in.
- Configurações persistentes de áudio e comportamento do sistema.
- Logs rotativos em `logs/viber_os.log`.
- Comandos de configuração, música, changelog e logs.
- Wizard Textual de primeiro acesso, login com senha mascarada e tela de bloqueio etário.
- Data e hora local no cabeçalho do menu principal, com offset UTC detectado pelo sistema operacional.
- Nova experiência secreta animada em Textual envolvendo o ViberAI; o comando continua intencionalmente fora da documentação.
- 5 Músicas novas e autorais.
- Testes automatizados para core, filesystem, CSS Textual, lifecycle, autenticação, áudio e segredos.

### Alterado
- Boot/loading, boas-vindas e desligamento migrados para Textual.
- Menu clássico do ViberOS recriado em Textual, preservando sua identidade visual.
- Calendário, Biblioteca, Conquistas, Vibegotchi e Vibe Invaders agora abrem como telas do mesmo `ViberOSApp`.
- Vibe Invaders mantém renderização Rich integrada ao runtime Textual.
- `ViberShell` foi renomeado para **Vibash**; aliases antigos permanecem apenas para compatibilidade.
- Experiências secretas existentes foram migradas para Screens Textual com lifecycle e cleanup compartilhados.
- Sistema de arquivos virtual passou a bloquear fuga para caminhos externos ao home do ViberOS.
- Saves/configurações JSON passaram a usar leitura tolerante e gravação atômica.
- Senhas novas usam PBKDF2-SHA256 com salt; perfis antigos em texto puro são migrados após login válido.
- Dependências diretas revisadas para o stack oficial: Textual 8.2.8, Rich 15.0.0 e pygame-ce 2.5.8.
- `BOSS_WAVE` permanece em 10 por padrão e pode ser alterado para testes via `VIBEROS_BOSS_WAVE`.

### Corrigido
- Estado privado das classes Textual padronizado com prefixo `_viber_`.
- Removido caminho oculto que podia iniciar outro runtime Textual dentro do Vibash.
- Falhas do runtime Textual não iniciam automaticamente o menu Rich legado; modo legado continua opt-in via `VIBEROS_LEGACY_SHELL=1`.
- Runtime Textual inicia com `mouse=False`, evitando vazamento de sequências de mouse/ANSI após encerramentos anormais.
- Biblioteca de músicas reforçada para não derrubar o runtime em falhas de áudio/renderização.
- Corrigida uma corrida de timers no fade: o último passo do fade-out não pode mais zerar o volume depois que a nova faixa já começou.
- Trocas diretas de faixa invalidam callbacks de transições antigas, evitando música presa em volume zero.
- Campo de criação do Vibegotchi recentralizado e integrado ao cartão de criação.
- `whoami` passou a ser o comando oficial; `whoiam` permanece como alias legado.
- Corrigido o crash do Vibegotchi causado por CSS inválido e a perda de foco/estado causada por runtimes Textual aninhados.
- Restaurado corretamente o foco do menu/Vibash ao fechar telas internas.

---

## [1.1.0] - 27-05-2026

### Rebranding
- VibeOS → ViberOS

### Adicionado
- Sistema de conquistas.
- 5 músicas autorais inéditas.
- Changelog disponível em PT-BR e Inglês.

### Atualização do Vibe Invaders
- Novo boss final: Vibe Destroyer.
- Mudança visual completa.
- Novo sistema de estilos: RETRO / VIBE.

#### Estilo RETRO
- Aparência clássica da v1.0.
- Dificuldade fácil.

#### Estilo VIBE
- Aparência nova da v1.1.
- Dificuldade difícil.
- Novas habilidades durante a boss fight.

### Conquistas
- 10 conquistas adicionadas no total.
- 3 desbloqueadas usando o ViberOS.
- 3 jogando Vibe Invaders.
- 3 jogando Vibegotchi.
- 1 utilizando o Calendário.

### Alterado
- Sistema de navegação dos aplicativos reformulado.
- Aplicativos passaram a utilizar setas direcionais e `Enter`.

### Removido
- API do Viber removida temporariamente devido a vazamentos e problemas de segurança.
- 11 músicas (Vibe 01-11) removidas por risco de direitos autorais.

---

## [1.0.0] - 11-05-2026

### Adicionado
- Terminal retrô com visual verde monocromático.
- Sistema de arquivos simulado com `ls`, `cd`, `mkdir`, `rmdir`, `touch`, `rm`, `cat` e `echo`.
- Comandos de sistema como `clear`, `whoami`, `pwd`, `hostname`, `uname`, `help` e `shutdown`.
- Assistente de IA `viber` integrado ao terminal.
- Suporte a expressões matemáticas.
- Calendário, biblioteca de música, Vibegotchi e Vibe Invaders.
- Comandos secretos não documentados.
