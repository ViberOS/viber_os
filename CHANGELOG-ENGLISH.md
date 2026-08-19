# Changelog - ViberOS

All notable changes to ViberOS will be documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

---

## [1.2.0] - 2026-08-19

### Added
- Textual-based main runtime.
- New **Vibash** shell inspired by Bash, with command history and basic autocomplete.
- **[6] Vibash** main-menu entry and empty-line `Q` shortcut to return to the menu.
- Automatic playlist with shuffle, no immediate repeats, and fade-out/fade-in transitions.
- Persistent audio/system behavior settings and rotating logs.
- Settings, music, changelog, and log commands.
- Textual first-run setup, masked-password login, and age-restriction screens.
- User-local date and time in the main menu header, including the OS-detected UTC offset.
- A new animated Textual ViberAI hidden experience; its command intentionally remains undocumented.
- Automated tests for core logic, filesystem, Textual CSS/lifecycle, authentication, audio, and hidden experiences.
- 5 New Musics and authorial

### Changed
- Boot/loading, post-login welcome flow, and shutdown migrated to Textual.
- Classic ViberOS menu recreated in Textual while preserving its visual identity.
- Calendar, Music Library, Achievements, Vibegotchi, and Vibe Invaders now open as screens inside the same `ViberOSApp`.
- Vibe Invaders keeps Rich renderables while using the Textual runtime.
- `ViberShell` renamed to **Vibash**; old aliases remain for compatibility only.
- Existing hidden experiences now use Textual Screens with shared lifecycle and cleanup.
- Virtual filesystem blocks escaping outside the ViberOS home area.
- JSON saves/settings use resilient reads and atomic writes.
- New passwords use salted PBKDF2-SHA256; legacy plaintext profiles migrate after a valid login.
- Direct dependencies reviewed for the official stack: Textual 8.2.8, Rich 15.0.0, and pygame-ce 2.5.8.
- `BOSS_WAVE` remains 10 by default and can be overridden for tests through `VIBEROS_BOSS_WAVE`.

### Fixed
- ViberOS private Textual state is namespaced with the `_viber_` prefix.
- Hidden screens now share centralized timer cleanup.
- Removed the hidden path that could start another Textual runtime inside Vibash.
- Textual failures no longer auto-launch the legacy Rich menu; legacy mode stays opt-in through `VIBEROS_LEGACY_SHELL=1`.
- Textual runtimes start with `mouse=False`, preventing raw mouse/ANSI sequences from leaking after abnormal exits.
- Hardened the Music Library against audio/render failures.
- Fixed a fade timer race where the final fade-out callback could set volume to zero after the next track had already started.
- Direct track changes now invalidate stale transition callbacks, preventing playback from remaining muted.
- Re-centered the Vibegotchi name-creation field inside its setup card.
- `whoami` is the canonical command; `whoiam` remains a legacy alias.
- Fixed invalid Vibegotchi Textual CSS and terminal focus/state loss caused by nested Textual runtimes.
- Correctly restores menu/Vibash input focus after closing integrated screens.

---

## [1.1.0] - 2026-05-27

### Rebranding
- VibeOS → ViberOS.

### Added
- Achievement system.
- 5 original music tracks.
- Changelog available in PT-BR and English.

### Vibe Invaders Update
- New final boss: Vibe Destroyer.
- Complete visual overhaul.
- New RETRO / VIBE style system.

#### RETRO Style
- Classic v1.0 appearance.
- Easy difficulty.

#### VIBE Style
- New v1.1 appearance.
- Hard difficulty.
- New abilities during the boss fight.

### Achievements
- 10 achievements added in total.
- 3 unlocked through ViberOS usage.
- 3 through Vibe Invaders.
- 3 through Vibegotchi.
- 1 through Calendar.

### Changed
- Reworked application navigation.
- Applications moved to arrow-key and `Enter` navigation.

### Removed
- Viber API temporarily removed due to leaks and security issues.
- 11 tracks (Vibe 01-11) removed due to copyright risk.

---

## [1.0.0] - 2026-05-11

### Added
- Retro monochromatic green terminal.
- Simulated filesystem with `ls`, `cd`, `mkdir`, `rmdir`, `touch`, `rm`, `cat`, and `echo`.
- System commands including `clear`, `whoami`, `pwd`, `hostname`, `uname`, `help`, and `shutdown`.
- Built-in `viber` AI assistant.
- Mathematical expression support.
- Calendar, music library, Vibegotchi, and Vibe Invaders.
- Undocumented secret commands.
