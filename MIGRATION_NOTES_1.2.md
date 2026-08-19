# ViberOS 1.2.0 — Notas de migração

A versão 1.2.0 conclui a migração do runtime principal para Textual sem reescrever a lógica-base dos aplicativos. Rich permanece como camada de renderização onde é útil.

## Runtime

- Um único `ViberOSApp` controla menu, Vibash e aplicativos integrados.
- Screens internas encerram com `dismiss()` e devolvem foco somente após o lifecycle de retorno.
- Estado privado criado pelo ViberOS em classes Textual usa o prefixo `_viber_`.
- Timers dos easter eggs possuem cleanup centralizado.
- O modo Rich legado continua disponível apenas por `VIBEROS_LEGACY_SHELL=1`.
- Mouse tracking fica desativado porque a interface atual é controlada por teclado.

## Áudio

- `pygame.mixer.music` continua sendo o stream único de música do sistema.
- Transições são agendadas no event loop do Textual, sem worker threads.
- O último passo do fade-out é agendado antes da troca de faixa, eliminando a corrida que podia deixar a próxima música em volume zero.
- Uma troca direta invalida callbacks de transições anteriores.

## Interface

- Boot, criação de usuário, login, boas-vindas, menu principal e desligamento usam Textual.
- O menu mostra data e hora local do sistema, com offset UTC, sem dependência externa adicional.
- Vibegotchi, Biblioteca, Calendário, Conquistas e Vibe Invaders retornam ao mesmo runtime.
- Rich continua sendo usado para `Panel`, `Text`, `Align`, logs e renderables do Vibe Invaders.

## Dependências oficiais

- Textual 8.2.8
- Rich 15.0.0
- pygame-ce 2.5.8
- art 6.5
- numpy 2.4.4
- opencv-python 4.13.0.92
- simpleeval 1.0.7

## Release

Versão oficial: **1.2.0** — 13/08/2026.

## Validação da release

- `compileall`: OK
- `pytest`: 37/37 testes passando
- Smoke test do agendamento de fade com mixer simulado: volume final restaurado corretamente
- Smoke test de cancelamento de transição antiga: callbacks antigos não alteram a faixa nova
