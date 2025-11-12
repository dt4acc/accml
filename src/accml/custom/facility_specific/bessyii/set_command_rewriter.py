from .liasion_translator_setup import load_managers
from ..bl.command_rewritter import CommandRewriter


def set_command_rewriter():
    _, lm, tm = load_managers()
    return CommandRewriter(liaison_manager=lm, translation_service=tm)
