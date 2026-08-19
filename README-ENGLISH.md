# ViberOS

A pseudo-operating system inspired by retro green-screen terminals, digital nostalgia, and classic computers.

ViberOS combines a modern **Textual** TUI, Rich renderables, a Bash-inspired shell, integrated applications, games, music, and hidden commands.

---

## ✅ Current version: 1.2.0

Version **1.2.0 was released on 2026-08-19** and is the biggest structural migration of ViberOS so far.

### 1.2.0 highlights

- Main runtime migrated to **Textual**
- Textual boot, user setup, login, welcome flow, and shutdown
- Classic ViberOS menu visually preserved inside Textual
- New **Vibash** terminal inspired by Bash
- Pressing `Q` on an empty Vibash command line returns to the main menu
- Calendar, Music Library, Achievements, Vibegotchi, and Vibe Invaders integrated into the same Textual runtime
- Automatic playlist with shuffle, fade-out/fade-in, and playback recovery after apps with their own soundtrack
- Command history and basic autocomplete in Vibash
- Safer isolated virtual filesystem
- Resilient JSON saves/settings with atomic writes
- PBKDF2-SHA256 password storage with automatic migration of legacy plaintext profiles
- Rotating system logs
- User-local date and time in the main menu, including the UTC offset detected by the system
- Screen lifecycle reviewed for the current Textual runtime: apps and secrets close through `Screen.dismiss()` and return focus to the menu/Vibash without nested runtimes
- 5 New Musics and authorial

---

## 🖥️ System flow

```text
Textual Boot
    ↓
First-run Setup / Textual Login
    ↓
Welcome Screen
    ↓
Classic ViberOS Menu
    ├─ Calendar
    ├─ Music Library
    ├─ Vibegotchi
    ├─ Vibe Invaders
    ├─ Achievements
    ├─ Vibash
    ├─ Help
    └─ Shutdown
```

On first run, ViberOS asks for **age, username, and password** through a Textual setup wizard. Password input is masked and only a derived password hash is stored locally.

---

## 💻 Vibash

**Vibash** is the ViberOS shell, inspired by Bash commands and conventions.

Available commands include:

- `ls`
- `cd`
- `mkdir`
- `rmdir`
- `touch`
- `rm`
- `cat`
- `echo`
- `pwd`
- `whoami` (the historical `whoiam` alias also works)
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

Vibash supports `↑` / `↓` command history, basic `Tab` autocomplete, and **Q to return to the main menu when the command line is empty**.

---

## 🎮 Integrated applications

| Application | Description |
|---|---|
| `calendar` | System calendar |
| `music` | Music library |
| `vibegotchi` | ViberOS virtual pet |
| `vibe_invaders` | Retro arcade game with RETRO / VIBE modes and a final boss |
| `achievements` | Achievement center |
| `vibash` | Bash-inspired system shell |

The main applications share the same `ViberOSApp`, preventing nested Textual event loops and preserving focus/navigation when returning to the menu.

### Quick controls

| Screen | Controls |
|---|---|
| Calendar | `←/→` or `A/D` changes month, `G` jumps to a date, `Q/Esc` goes back |
| Music Library | `↑/↓` navigates, `Enter` plays, `N` next, `M` mute, `Q/Esc` goes back |
| Vibegotchi | `↑/↓` navigates, `Enter` confirms, `Q/Esc` goes back; `Esc` cancels name setup |
| Vibe Invaders | `A/←` and `D/→` move, `Space` fires; `Q/Esc` returns from the game menu |
| Achievements | `Q/Esc` goes back |
| Vibash | `↑/↓` history, `Tab` autocomplete, `Ctrl+L` clears, empty `Q` or `Esc` goes back |

---

## 👾 Vibe Invaders

### RETRO
- Classic visuals
- More accessible difficulty
- Original minimal aesthetic

### VIBE
- Alternate visuals
- Higher difficulty
- Additional boss mechanics

Vibe Invaders uses Textual for runtime events/timers while preserving Rich renderables where they remain useful.

---

## 🎵 Music

ViberOS includes its own music library and an automatic playback system.

The playlist can:

- shuffle tracks;
- avoid immediate repeats;
- automatically start another track when one ends;
- use fade-out/fade-in transitions scheduled by the Textual event loop in the main runtime;
- pause while an application owns the soundtrack;
- resume system playback after returning.

Most of the current soundtrack was created specifically for the project. The temporary main track `ViberOS.mp3` is still planned to be replaced by a fully original composition.

---

## 🥚 Hidden experiences

Not everything is shown in the menu or command documentation.

Some internal secrets now run as native Textual screens, including ASCII video, animations, and special sequences, returning to ViberOS without leaving the main runtime.

Some secrets are meant to be discovered. 👀

---

## 🏆 Achievements

Achievements are connected to ViberOS usage, Vibe Invaders, Vibegotchi, Calendar, and hidden system experiences.

---

## ➗ Mathematical expressions

Vibash supports simple expressions such as:

- `5 + 5`
- `10 * 8`
- `(4 + 2) ** 2`
- `25 % 4`

Supported operators: `+`, `-`, `*`, `/`, `//`, `%`, `**`, and `()`.

---

## 🔐 Local data and security

- The virtual filesystem is contained inside the ViberOS home area.
- New passwords use **PBKDF2-SHA256** with a salt.
- Legacy plaintext-password profiles are migrated after a valid login.
- Critical JSON files use atomic writes and corruption fallbacks.
- Logs avoid recording full command arguments.

---

## 🛠️ Running and testing

Install dependencies:

```bash
pip install -r requirements.txt
```

Run ViberOS:

```bash
python main.py
```

Run tests:

```bash
pip install -r requirements-dev.txt
pytest -q
```

The official 1.2.0 UI layer uses **Textual 8.2.8 + Rich 15.0.0**. Rich is intentionally kept as a rendering layer inside Textual widgets where it simplifies the code; it is not a competing second runtime.

For quick boss testing:

```bash
VIBEROS_BOSS_WAVE=2 python main.py
```

The normal boss wave remains wave 10.

---

## 🎨 Aesthetic

Green screen. Command line. Retro music. ASCII. Minimal interface.

As if a forgotten computer from another era were still running somewhere.

---

## ⚠️ Notice

Not every command is documented.
Some are meant to be discovered.
