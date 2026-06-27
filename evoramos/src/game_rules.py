"""Regras e descrições dos eventos evolutivos do EvoRamos."""

from typing import Any


EVENT_DEFINITIONS = {
    "speciation": {
        "name": "Especiação",
        "description": "Uma linhagem ancestral origina duas linhagens distintas.",
    },
    "hybridization": {
        "name": "Hibridização",
        "description": "Duas linhagens contribuem para a origem de uma nova linhagem.",
    },
    "horizontal_transfer": {
        "name": "Transferência horizontal de genes",
        "description": "Material genético passa entre organismos sem relação direta de descendência.",
    },
    "none": {
        "name": "Não é evento especial",
        "description": "O elemento selecionado não representa um dos eventos especiais avaliados.",
    },
}


def describe_events(events: list[dict[str, Any]]) -> list[dict[str, str]]:
    """Retorna os dados de apresentação dos eventos esperados de um exemplo."""
    described_events = []
    for event in events:
        event_type = event.get("event_type")
        if event_type not in EVENT_DEFINITIONS:
            continue
        described_events.append(
            {
                "id": event["id"],
                "event_type": event_type,
                "label": event.get("label") or EVENT_DEFINITIONS[event_type]["name"],
                "description": event.get("explanation")
                or EVENT_DEFINITIONS[event_type]["description"],
                "target_id": event.get("target_id", ""),
                "target_type": event.get("target_type", ""),
            }
        )
    return described_events


def check_player_answer(
    example: dict[str, Any],
    selected_element: dict[str, str] | None,
    selected_event_type: str | None,
    submitted_answers: list[dict[str, Any]] | None = None,
    player_id: int | None = None,
) -> dict[str, Any]:
    """Confere a resposta do jogador e evita pontuação duplicada."""
    if not selected_element:
        return {
            "correct": False,
            "matched_event": None,
            "message": "Selecione um nó ou aresta antes de confirmar.",
            "points": 0,
            "answer_record": None,
        }

    if not selected_event_type:
        return {
            "correct": False,
            "matched_event": None,
            "message": "Escolha um tipo de evento antes de confirmar.",
            "points": 0,
            "answer_record": None,
        }

    submitted_answers = submitted_answers or []
    matched_event = next(
        (
            event
            for event in example["expected_events"]
            if selected_element["id"] == event["target_id"]
            and selected_element["type"] == event["target_type"]
        ),
        None,
    )

    is_correct = False
    if selected_event_type == "none":
        is_correct = matched_event is None
    elif matched_event:
        is_correct = selected_event_type == matched_event["event_type"]

    answer_record = {
        "element_id": selected_element["id"],
        "element_type": selected_element["type"],
        "selected_event_type": selected_event_type,
        "player_id": player_id,
        "correct": is_correct,
        "event_id": matched_event["id"] if matched_event else None,
    }

    if is_correct and _is_duplicate_score(submitted_answers, answer_record):
        event_name = EVENT_DEFINITIONS.get(selected_event_type, {}).get(
            "name", "Evento"
        )
        return {
            "correct": True,
            "matched_event": matched_event,
            "message": f"Você já havia pontuado este {event_name.lower()}.",
            "points": 0,
            "answer_record": answer_record,
        }

    if is_correct:
        if matched_event:
            return {
                "correct": True,
                "matched_event": matched_event,
                "message": matched_event.get("explanation")
                or "Resposta correta.",
                "points": 1,
                "answer_record": answer_record,
            }
        return {
            "correct": True,
            "matched_event": None,
            "message": "Correto: este elemento não representa um evento especial.",
            "points": 1,
            "answer_record": answer_record,
        }

    if matched_event:
        expected_name = EVENT_DEFINITIONS[matched_event["event_type"]]["name"]
        return {
            "correct": False,
            "matched_event": matched_event,
            "message": f"Dica: este elemento está ligado a {expected_name.lower()}.",
            "points": 0,
            "answer_record": answer_record,
        }

    return {
        "correct": False,
        "matched_event": None,
        "message": "Dica: este elemento não faz parte dos eventos especiais mapeados.",
        "points": 0,
        "answer_record": answer_record,
    }


def _is_duplicate_score(
    submitted_answers: list[dict[str, Any]], answer_record: dict[str, Any]
) -> bool:
    """Bloqueia pontuação repetida para o mesmo acerto."""
    for previous in submitted_answers:
        if not previous.get("correct"):
            continue
        if previous.get("element_id") != answer_record["element_id"]:
            continue
        if previous.get("element_type") != answer_record["element_type"]:
            continue
        if previous.get("selected_event_type") != answer_record["selected_event_type"]:
            continue
        if previous.get("player_id") != answer_record["player_id"]:
            continue
        return True
    return False
