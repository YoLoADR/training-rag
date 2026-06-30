"""
Test Bug v1 At.07 — mauvais import du CallbackHandler Langfuse (v3 au lieu de v2)

Logique :
- Le projet utilise le SDK Langfuse v2 (langfuse==2.57.1) → l'import correct est
  `from langfuse.callback import CallbackHandler`.
- Le bug le remplace par `from langfuse.langchain import CallbackHandler` (= API v3),
  module qui N'EXISTE PAS en v2 → get_langfuse_handler lèverait ImportError dès que des
  clés sont présentes → plus aucune trace n'arrive dans Langfuse.
- Test d'analyse statique (déterministe, pas de réseau) : on vérifie le bon chemin d'import.
- Bug actif : import v3 → test ECHOUE.
- Corrigé : import v2 → test PASSE.

git apply ... bugs/v1.patch ; pytest ... test_v1.py (FAIL) ; reset ; pytest (PASS)
"""

import inspect
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../../"))


def test_callback_handler_import_v2():
    import homebutler.eval.tracing as tracing
    src = inspect.getsource(tracing.get_langfuse_handler)
    print(f"\nSource get_langfuse_handler :\n{src}")
    assert "from langfuse.callback import CallbackHandler" in src, (
        "Mauvais import du CallbackHandler.\n"
        "Le projet est sur Langfuse v2 (==2.57.1) : utilise "
        "`from langfuse.callback import CallbackHandler`.\n"
        "`from langfuse.langchain import CallbackHandler` est l'API v3 → ImportError en v2."
    )
    assert "langfuse.langchain" not in src, (
        "Import v3 (langfuse.langchain) détecté — incompatible avec langfuse v2."
    )
