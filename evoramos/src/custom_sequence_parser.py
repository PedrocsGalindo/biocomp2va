"""Parser de sequências importadas pelo usuário."""

from __future__ import annotations

import base64
import binascii
import re
from typing import Any


def build_uploaded_example(contents: str, filename: str | None, imported_example_id: str) -> dict[str, Any]:
    organisms = parse_sequence_text(decode_upload_contents(contents))
    source_name = filename or "arquivo TXT"
    return {
        "id": imported_example_id,
        "title": "Árvore importada",
        "difficulty": "Livre",
        "description": f"Árvore automática montada a partir de {len(organisms)} sequências de {source_name}.",
        "learning_goal": "Criar uma interpretação própria da árvore por similaridade genética.",
        "organisms": organisms,
        "expected_events": [],
        "explanation": "Esta árvore foi montada por similaridade. Relações especiais, como hibridização e transferência horizontal, devem ser anotadas manualmente.",
        "optional_edges": [],
        "tree_mode": "uploaded_similarity_tree",
    }


def decode_upload_contents(contents: str) -> str:
    if "," not in contents:
        raise ValueError("Conteúdo de upload inválido.")
    _metadata, encoded = contents.split(",", 1)
    try:
        raw = base64.b64decode(encoded)
    except (binascii.Error, ValueError) as exc:
        raise ValueError("Não foi possível ler o arquivo enviado.") from exc
    for encoding in ("utf-8-sig", "utf-8", "latin-1"):
        try:
            return raw.decode(encoding)
        except UnicodeDecodeError:
            continue
    raise ValueError("Use um arquivo TXT em UTF-8 ou Latin-1.")


def parse_sequence_text(text: str) -> list[dict[str, Any]]:
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    if not lines:
        raise ValueError("O arquivo não contém sequências.")

    entries = parse_fasta_lines(lines) if any(line.startswith(">") for line in lines) else parse_plain_sequence_lines(lines)
    if len(entries) < 2:
        raise ValueError("Envie pelo menos duas sequências para montar a árvore.")

    organisms = []
    expected_length: int | None = None
    for index, (name, sequence) in enumerate(entries, start=1):
        cleaned = normalize_sequence(sequence)
        if not cleaned:
            raise ValueError(f"A sequência {index} está vazia ou contém caracteres inválidos.")
        if expected_length is None:
            expected_length = len(cleaned)
        elif len(cleaned) != expected_length:
            raise ValueError("Todas as sequências precisam ter o mesmo tamanho para esta árvore.")
        organisms.append(
            {
                "id": f"upload_{index}",
                "name": name or f"Sequência {index}",
                "sequence": cleaned,
                "description": "Sequência importada pelo usuário.",
            }
        )
    return organisms


def parse_fasta_lines(lines: list[str]) -> list[tuple[str, str]]:
    entries: list[tuple[str, str]] = []
    current_name: str | None = None
    current_sequence: list[str] = []

    for line in lines:
        if line.startswith(">"):
            if current_name is not None:
                entries.append((current_name, "".join(current_sequence)))
            current_name = line[1:].strip() or f"Sequência {len(entries) + 1}"
            current_sequence = []
        else:
            current_sequence.append(line)
    if current_name is not None:
        entries.append((current_name, "".join(current_sequence)))
    return entries


def parse_plain_sequence_lines(lines: list[str]) -> list[tuple[str, str]]:
    entries: list[tuple[str, str]] = []
    for index, line in enumerate(lines, start=1):
        normalized_line = re.sub(r"[,;]", " ", line)
        if ":" in normalized_line:
            name, sequence = normalized_line.split(":", 1)
        else:
            parts = normalized_line.split()
            if len(parts) == 1:
                name, sequence = f"Sequência {index}", parts[0]
            else:
                name, sequence = " ".join(parts[:-1]), parts[-1]
        entries.append((name.strip(), sequence.strip()))
    return entries


def normalize_sequence(sequence: str) -> str:
    cleaned = re.sub(r"\s+", "", sequence).upper().replace("U", "T")
    if not re.fullmatch(r"[ACGTN]+", cleaned or ""):
        return ""
    return cleaned

