"""Compatibilidade temporária com o antigo nome ViberShell.

A interface oficial agora se chama Vibash. Novos imports devem usar
``modules.shell.vibash``.
"""
from modules.shell.vibash import (
    ShellInput,
    VibashApp,
    VibashScreen,
    run_vibash,
)

# Aliases legados para branches/plugins ainda não atualizados.
ViberShellApp = VibashApp
ViberShellScreen = VibashScreen
run_shell = run_vibash

__all__ = [
    "ShellInput", "VibashApp", "VibashScreen", "run_vibash",
    "ViberShellApp", "ViberShellScreen", "run_shell",
]
