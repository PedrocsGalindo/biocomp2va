"""Regras, correções e descrições dos eventos evolutivos do EvoRamos."""

from __future__ import annotations

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
        "name": "Transferência horizontal",
        "description": "Material genético passa entre organismos sem relação direta de descendência.",
    },
    "none": {
        "name": "Não é evento especial",
        "description": "O elemento selecionado não representa um dos eventos especiais avaliados.",
    },
}


def event_name(event_type: str | None) -> str:
    """Retorna o nome amigável de um tipo de resposta/evento."""
    if not event_type:
        return "Sem resposta"
    return EVENT_DEFINITIONS.get(event_type, {"name": event_type})["name"]


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
                "description": event.get("short_feedback")
                or event.get("explanation")
                or EVENT_DEFINITIONS[event_type]["description"],
                "target_id": event.get("primary_target_id") or event.get("target_id", ""),
                "target_type": event.get("primary_target_type") or event.get("target_type", ""),
            }
        )
    return described_events


def check_player_answer(
    example: dict[str, Any],
    selected_element: dict[str, Any] | None,
    selected_event_type: str | None,
    submitted_answers: list[dict[str, Any]] | None = None,
    player_id: int | None = None,
) -> dict[str, Any]:
    """Confere a resposta do jogador e devolve uma correção diagnóstica."""
    if not selected_element:
        return _empty_result("Selecione um nó ou aresta antes de confirmar.")

    if not selected_event_type:
        return _empty_result("Escolha um tipo de evento antes de confirmar.")

    submitted_answers = submitted_answers or []
    matched_event = find_event_for_element(example, selected_element)
    is_correct = _is_correct_answer(matched_event, selected_event_type)
    answer_record = build_answer_review(
        example=example,
        selected_element=selected_element,
        selected_event_type=selected_event_type,
        matched_event=matched_event,
        is_correct=is_correct,
        player_id=player_id,
        attempt_number=len(submitted_answers) + 1,
    )

    duplicate = is_correct and _is_duplicate_score(submitted_answers, answer_record)
    points = 0 if duplicate else int(is_correct)
    answer_record["points"] = points
    if duplicate:
        answer_record["short_feedback"] = "Você já pontuou essa relação anteriormente."
        answer_record["full_explanation"] = (
            "A resposta está correta, mas a mesma relação já foi registrada para este jogador. "
            "Por isso ela não soma ponto novamente."
        )

    return {
        "correct": is_correct,
        "matched_event": matched_event,
        "message": answer_record["short_feedback"],
        "points": points,
        "answer_record": answer_record,
        "highlight": answer_record["highlight"],
        "full_explanation": answer_record["full_explanation"],
        "correct_answer": answer_record["correct_answer"],
        "selected_event_type": selected_event_type,
    }


def find_event_for_element(
    example: dict[str, Any], selected_element: dict[str, Any]
) -> dict[str, Any] | None:
    """Localiza o evento esperado associado ao elemento selecionado."""
    return next(
        (
            event
            for event in example.get("expected_events", [])
            if selected_element.get("id")
            == (event.get("primary_target_id") or event.get("target_id"))
            and selected_element.get("type")
            == (event.get("primary_target_type") or event.get("target_type"))
        ),
        None,
    )


def build_answer_review(
    example: dict[str, Any],
    selected_element: dict[str, Any],
    selected_event_type: str,
    matched_event: dict[str, Any] | None,
    is_correct: bool,
    player_id: int | None,
    attempt_number: int,
) -> dict[str, Any]:
    """Monta o registro detalhado de uma tentativa do jogador."""
    selected_id = selected_element.get("id", "")
    selected_type = selected_element.get("type", "")
    correct_answer = matched_event["event_type"] if matched_event else "none"
    correct_label = event_name(correct_answer)
    player_label = event_name(selected_event_type)
    selected_label = _selected_element_label(selected_element)

    highlight = _build_highlight(
        selected_id=selected_id,
        selected_type=selected_type,
        matched_event=matched_event,
        is_correct=is_correct,
        selected_event_type=selected_event_type,
    )

    if is_correct:
        if matched_event:
            short_feedback = matched_event.get("short_feedback") or f"Correto: {correct_label}."
            full_explanation = _event_explanation(matched_event)
        else:
            short_feedback = "Correto: este elemento não é um evento especial."
            full_explanation = (
                f"O elemento selecionado ({selected_label}) faz parte da estrutura normal da árvore. "
                "Ele não corresponde aos eventos avaliados neste jogo: especiação, hibridização ou transferência horizontal."
            )
    else:
        if matched_event:
            short_feedback = f"Ainda não. O correto para este elemento era: {correct_label}."
            full_explanation = _event_explanation(matched_event)
        else:
            short_feedback = "Ainda não. Esse elemento não é um evento especial."
            full_explanation = (
                f"Você marcou {player_label}, mas o elemento selecionado ({selected_label}) não está mapeado como "
                "especiação, hibridização ou transferência horizontal neste exemplo."
            )

    return {
        "attempt_id": f"attempt_{attempt_number:02d}_{selected_id}",
        "player_id": player_id,
        "selected_element_id": selected_id,
        "selected_element_type": selected_type,
        "selected_element_label": selected_label,
        "selected_event_type": selected_event_type,
        "selected_event_label": player_label,
        "player_answer": selected_event_type,
        "player_answer_label": player_label,
        "correct": is_correct,
        "is_correct": is_correct,
        "correct_answer": correct_answer,
        "correct_answer_label": correct_label,
        "event_id": matched_event["id"] if matched_event else None,
        "matched_event_id": matched_event["id"] if matched_event else None,
        "matched_event_label": matched_event.get("label") if matched_event else "Não é evento especial",
        "short_feedback": short_feedback,
        "full_explanation": full_explanation,
        "highlight": highlight,
        # Legacy keys used by existing counters.
        "element_id": selected_id,
        "element_type": selected_type,
    }


def _empty_result(message: str) -> dict[str, Any]:
    return {
        "correct": False,
        "matched_event": None,
        "message": message,
        "points": 0,
        "answer_record": None,
        "highlight": None,
        "full_explanation": message,
        "correct_answer": None,
    }


def _is_correct_answer(matched_event: dict[str, Any] | None, selected_event_type: str) -> bool:
    if selected_event_type == "none":
        return matched_event is None
    return bool(matched_event and selected_event_type == matched_event.get("event_type"))


def _selected_element_label(selected_element: dict[str, Any]) -> str:
    if selected_element.get("type") == "edge":
        source = selected_element.get("source", "origem")
        target = selected_element.get("target", "destino")
        return f"Ligação {source} → {target}"
    return selected_element.get("label") or selected_element.get("id", "Elemento selecionado")


def _event_explanation(event: dict[str, Any]) -> str:
    if event.get("full_explanation"):
        return event["full_explanation"]
    if event.get("event_type") == "speciation":
        return "Esse nó representa especiação porque uma linhagem ancestral se divide em duas ou mais linhagens descendentes."
    if event.get("event_type") == "hybridization":
        return "Esse organismo representa hibridização porque recebe contribuição de duas linhagens diferentes."
    if event.get("event_type") == "horizontal_transfer":
        return "Essa ligação representa transferência horizontal porque conecta ramos sem relação direta de ancestralidade."
    return event.get("explanation") or "Este elemento representa o evento esperado no grafo."


def _build_highlight(
    selected_id: str,
    selected_type: str,
    matched_event: dict[str, Any] | None,
    is_correct: bool,
    selected_event_type: str,
) -> dict[str, list[str]]:
    highlight = {
        "primary_nodes": [],
        "primary_edges": [],
        "related_nodes": [],
        "related_edges": [],
        "wrong_nodes": [],
        "wrong_edges": [],
        "missed_nodes": [],
        "missed_edges": [],
    }

    if matched_event:
        target_id = matched_event.get("primary_target_id") or matched_event.get("target_id")
        target_type = matched_event.get("primary_target_type") or matched_event.get("target_type")
        if target_type == "node":
            highlight["primary_nodes"].append(target_id)
        elif target_type == "edge":
            highlight["primary_edges"].append(target_id)
        highlight["related_nodes"].extend(matched_event.get("related_node_ids", []))
        highlight["related_edges"].extend(matched_event.get("related_edge_ids", []))

    if not is_correct:
        bucket = "wrong_edges" if selected_type == "edge" else "wrong_nodes"
        highlight[bucket].append(selected_id)
        if matched_event is None and selected_event_type != "none":
            # The selected element itself is the incorrect focus.
            return _dedupe_highlight(highlight)
        if matched_event:
            # Keep the correct relation visible as the answer the player missed.
            highlight["missed_nodes"].extend(highlight["primary_nodes"])
            highlight["missed_edges"].extend(highlight["primary_edges"])

    return _dedupe_highlight(highlight)


def _dedupe_highlight(highlight: dict[str, list[str]]) -> dict[str, list[str]]:
    return {key: list(dict.fromkeys(value)) for key, value in highlight.items()}


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
