from __future__ import annotations


def close_current_view(widget) -> None:
    """Fecha a tela atual quando o widget está no ViberOS integrado.

    Mantém compatibilidade com os pequenos Apps standalone usados para testes:
    se o App não expuser ``close_active_screen``, encerra o App normalmente.
    """
    app = widget.app
    close = getattr(app, "close_active_screen", None)
    if callable(close):
        close()
    else:
        app.exit()
