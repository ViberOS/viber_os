# ViberOS

Pseudo-sistema operacional inspirado em terminais retrô de tela verde, estética de nostalgia digital e computadores clássicos.

O ViberOS combina uma interface TUI moderna construída com **Textual**, renderização Rich, um terminal próprio inspirado em Bash, aplicativos internos, jogos, música e comandos secretos.

---

## ✅ Versão atual: 1.2.0

A versão **1.2.0 foi lançada em 19/08/2026** e representa a maior migração estrutural do ViberOS até agora.

### Destaques da 1.2.0

- Runtime principal migrado para **Textual**
- Boot, criação de usuário, login, boas-vindas e desligamento em Textual
- Menu clássico preservado visualmente, agora dentro do Textual
- Novo terminal **Vibash**, inspirado em Bash
- `Q` com a linha vazia retorna do Vibash para o menu principal
- Calendário, Biblioteca, Conquistas, Vibegotchi e Vibe Invaders integrados ao mesmo runtime Textual
- Playlist automática com shuffle, fade-out/fade-in e retomada depois de apps com trilha própria
- Histórico de comandos e autocomplete básico no Vibash
- Sistema de arquivos virtual mais isolado e seguro
- Saves/configurações JSON com leitura tolerante e escrita atômica
- Senhas armazenadas com PBKDF2-SHA256; usuários antigos são migrados automaticamente no login
- Logs rotativos do sistema
- Data e hora local do usuário no menu principal, incluindo o offset UTC detectado pelo sistema
- Lifecycle das telas revisado para o Textual atual: apps e segredos fecham por `Screen.dismiss()` e devolvem foco ao menu/Vibash sem iniciar runtimes aninhados
- 5 Músicas novas e autorais.

---

## 🖥️ Fluxo do sistema

```text
Boot Textual
    ↓
Primeiro acesso / Login Textual
    ↓
Boas-vindas
    ↓
Menu clássico do ViberOS
    ├─ Calendário
    ├─ Biblioteca de músicas
    ├─ Vibegotchi
    ├─ Vibe Invaders
    ├─ Conquistas
    ├─ Vibash
    ├─ Ajuda
    └─ Desligar
```

No primeiro acesso, o ViberOS solicita **idade, nome de usuário e senha** através de um wizard Textual. A senha é mascarada durante a digitação e armazenada localmente apenas em formato derivado por hash.

---

## 💻 Vibash

O **Vibash** é o shell do ViberOS, inspirado em comandos e convenções do Bash.

Ele mantém a proposta de terminal do projeto sem transformar a interface principal em apenas uma linha de comando.

Alguns comandos disponíveis:

- `ls`
- `cd`
- `mkdir`
- `rmdir`
- `touch`
- `rm`
- `cat`
- `echo`
- `pwd`
- `whoami` (o alias histórico `whoiam` também funciona)
- `hostname`
- `uname`
- `help`
- `man`
- `clear`
- `shutdown`
- `menu`
- `music status`
- `music next`
- `settings`
- `changelog`

O Vibash possui histórico com `↑` / `↓`, autocomplete básico com `Tab` e retorno ao menu com **Q quando a linha de comando está vazia**.

---

## 🎮 Aplicativos integrados

| Aplicativo | Descrição |
|---|---|
| `calendar` | Calendário do sistema |
| `music` | Biblioteca de músicas |
| `vibegotchi` | Mascote virtual do ViberOS |
| `vibe_invaders` | Arcade retrô com modos RETRO / VIBE e boss final |
| `achievements` | Central de conquistas |
| `vibash` | Shell inspirado em Bash |

Os aplicativos principais compartilham o mesmo `ViberOSApp`, evitando iniciar múltiplos loops Textual e preservando corretamente foco, navegação e retorno ao menu.

### Controles rápidos

| Tela | Controles |
|---|---|
| Calendário | `←/→` ou `A/D` muda o mês, `G` vai para uma data, `Q/Esc` volta |
| Biblioteca | `↑/↓` navega, `Enter` toca, `N` próxima, `M` mudo, `Q/Esc` volta |
| Vibegotchi | `↑/↓` navega, `Enter` confirma, `Q/Esc` volta; na criação `Esc` cancela |
| Vibe Invaders | `A/←` e `D/→` movem, `Espaço` atira; `Q/Esc` volta pelo menu do jogo |
| Conquistas | `Q/Esc` volta |
| Vibash | `↑/↓` histórico, `Tab` autocomplete, `Ctrl+L` limpa, `Q` vazio ou `Esc` volta |

---

## 👾 Vibe Invaders

### RETRO
- Visual clássico
- Dificuldade mais acessível
- Estética minimalista original

### VIBE
- Visual alternativo
- Dificuldade maior
- Mecânicas adicionais durante o boss

O Vibe Invaders usa Textual como runtime de eventos/timers enquanto preserva renderables Rich onde eles continuam úteis.

---

## 🎵 Música

O ViberOS possui uma biblioteca própria de músicas e um sistema de reprodução automática.

A playlist pode:

- embaralhar as faixas;
- evitar repetição imediata;
- iniciar automaticamente uma nova música ao fim da anterior;
- aplicar fade-out/fade-in nas transições usando o event loop do Textual no runtime principal;
- pausar quando um app assume sua própria trilha;
- retomar a playlist do sistema ao retornar.

A maior parte da trilha atual foi criada especificamente para o projeto. A faixa principal temporária `ViberOS.mp3` ainda será substituída no futuro por uma composição autoral própria.

---

## 🥚 Segredos

Nem tudo aparece no menu ou na documentação de comandos.

Algumas experiências internas usam telas Textual próprias, incluindo vídeo ASCII, animações e sequências especiais. Elas retornam ao ViberOS sem abandonar o runtime principal.

Alguns segredos precisam ser descobertos. 👀

---

## 🏆 Conquistas

O sistema possui conquistas ligadas ao uso do ViberOS, Vibe Invaders, Vibegotchi, Calendário e segredos do sistema.

---

## ➗ Expressões matemáticas

<<<<<<< HEAD
O Vibash suporta cálculos simples, por exemplo:
=======
Os aplicativos internos do VibeOS utilizam um sistema de navegação inspirado em jogos retrô.

A navegação é feita utilizando as setas direcionais e a tecla `Enter`, proporcionando uma experiência mais fluida e imersiva dentro dos aplicativos.

O terminal principal do VibeOS permanece baseado em comandos tradicionais.

---

## Recursos

- Terminal retrô com interface monocromática verde
- Sistema de arquivos simulado
- Aplicativos integrados
- Suporte a expressões matemáticas
- Comandos secretos
- Atmosfera de nostalgia digital
- Sistema de jogos internos

---

## Aplicativos Integrados

| Aplicativo | Descrição |
|-------------|-----------|
| `calendar` | Calendário do sistema |
| `music` | Biblioteca de músicas do sistema |
| `vibegotchi` | Mascote virtual do sistema |
| `vibe_invaders` | Jogo arcade inspirado em clássicos retrô |
| `achievements` | Sistema de conquistas |

---

## Expressões Matemáticas

O terminal suporta cálculos simples:
>>>>>>> 5db42724172831ac21ea93508c343c39162ef64c

- `5 + 5`
- `10 * 8`
- `(4 + 2) ** 2`
- `25 % 4`

Operadores suportados: `+`, `-`, `*`, `/`, `//`, `%`, `**` e `()`.

---

## 🔐 Dados locais e segurança

- O filesystem virtual é limitado à área própria do ViberOS.
- Senhas novas utilizam **PBKDF2-SHA256** com salt.
- Perfis antigos com senha em texto puro são migrados após um login válido.
- Arquivos JSON críticos usam gravação atômica e fallback em caso de corrupção.
- Logs não registram argumentos completos dos comandos.

---

## 🛠️ Execução e testes

Instale as dependências:

```bash
pip install -r requirements.txt
```

Execute:

```bash
python main.py
```

Para testes:

```bash
pip install -r requirements-dev.txt
pytest -q
```

A camada de interface oficial da 1.2.0 usa **Textual 8.2.8 + Rich 15.0.0**. O Rich continua sendo usado intencionalmente como renderização dentro de widgets Textual onde isso simplifica o código; ele não é um segundo runtime concorrente.

Para chegar rapidamente ao boss durante testes:

```bash
VIBEROS_BOSS_WAVE=2 python main.py
```

No comportamento normal, o boss permanece na wave 10.

---

## 🎨 Estética

Tela verde. Linha de comando. Música retrô. ASCII. Interface minimalista.

Como se um computador esquecido no tempo ainda continuasse ligado em algum lugar.

---

## ⚠️ Aviso

Nem todos os comandos são documentados.
Alguns foram feitos para serem descobertos.
