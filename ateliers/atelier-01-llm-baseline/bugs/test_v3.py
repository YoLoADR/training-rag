"""
Test Bug v3 — SystemMessage remplace par HumanMessage dans script_system.py

Analyse statique de script_system.py :
- Le bug remplace SystemMessage(content=SYSTEM_PROMPT) par HumanMessage(content=SYSTEM_PROMPT).
- En etat propre : SystemMessage(content=SYSTEM_PROMPT) doit etre present.

Ce test PASSE en etat propre.
Ce test ECHOUE quand le bug est actif.
"""

import pathlib

SCRIPT = pathlib.Path(__file__).parent.parent / "script_system.py"


def test_system_message_present():
    """
    En etat de reference, script_system.py doit contenir SystemMessage(content=SYSTEM_PROMPT).
    """
    source = SCRIPT.read_text(encoding="utf-8")
    assert "SystemMessage(content=SYSTEM_PROMPT)" in source, (
        "SystemMessage(content=SYSTEM_PROMPT) absent de script_system.py. "
        "Indice : le bug a remplace SystemMessage par HumanMessage pour le system prompt."
    )
