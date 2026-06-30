"""Agrega todos os registradores de callbacks."""

from frontend.callbacks.answer_flow import register_answer_flow_callbacks
from frontend.callbacks.concepts import register_concept_callbacks
from frontend.callbacks.exercise_selection import register_exercise_selection_callbacks
from frontend.callbacks.free_classification import register_free_classification_callbacks
from frontend.callbacks.game_modes import register_game_mode_callbacks
from frontend.callbacks.render import register_render_callbacks
from frontend.callbacks.tree_interaction import register_tree_interaction_callbacks
from frontend.callbacks.upload_sequences import register_upload_sequence_callbacks


def register_callbacks(app):
    register_concept_callbacks(app)
    register_upload_sequence_callbacks(app)
    register_exercise_selection_callbacks(app)
    register_game_mode_callbacks(app)
    register_tree_interaction_callbacks(app)
    register_answer_flow_callbacks(app)
    register_free_classification_callbacks(app)
    register_render_callbacks(app)

