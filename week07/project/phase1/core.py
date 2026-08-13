import json
import os
from datetime import datetime, timezone

from config import (
    AGENT_DECISIONS_DIR,
    BREAKPOINT_PERCENTILE,
    BUFFER_SIZE,
    CHUNKING_VERSION,
    CHUNKS_DIR,
    EMBEDDING_MODEL,
    MAX_TOKENS_PER_BATCH,
    ROUTING_AGENT_CONTEXT,
    ROUTING_AGENT_MAX_STEPS,
    ROUTING_AGENT_MODEL,
    ROUTING_AGENT_NUM_PREDICT,
    ROUTING_AGENT_SAMPLE_CHARS,
    ROUTING_AGENT_TEMPERATURE,
    ROUTING_AGENT_VERSION,
    TEXT_ENCODING,
)
from phase1.chunking import build_semantic_chunks
from phase1.embedding import (
    build_context_windows,
    detect_breakpoints,
    generate_and_normalize_embeddings,
)
from phase1.file_utils import (
    calculate_file_hash,
    calculate_text_hash,
    load_registry,
    save_registry,
)
from phase1.routing_agent import estimate_tokens, evaluate_document
from phase1.text_prep import (
    extract_sentences,
    prepare_paragraph_text,
    unload_stanza_pipeline,
)


def build_result(
    status: str,
    filename: str,
    chunks_file: str = "",
    reason: str = "",
) -> dict:
    return {
        "status": status,
        "filename": filename,
        "chunks_file": chunks_file,
        "reason": reason,
    }


def safe_name(value: str) -> str:
    return value.replace(":", "-").replace("/", "-").replace("\\", "-")


def get_agent_settings() -> dict:
    return {
        "routing_agent_model": ROUTING_AGENT_MODEL,
        "routing_agent_version": ROUTING_AGENT_VERSION,
        "routing_agent_sample_chars": ROUTING_AGENT_SAMPLE_CHARS,
        "routing_agent_max_steps": ROUTING_AGENT_MAX_STEPS,
        "routing_agent_context": ROUTING_AGENT_CONTEXT,
        "routing_agent_num_predict": ROUTING_AGENT_NUM_PREDICT,
        "routing_agent_temperature": ROUTING_AGENT_TEMPERATURE,
        "max_tokens_per_batch": MAX_TOKENS_PER_BATCH,
    }


def get_processing_settings(routing_action: str) -> dict:
    return {
        "embedding_model": EMBEDDING_MODEL,
        "breakpoint_percentile": BREAKPOINT_PERCENTILE,
        "buffer_size": BUFFER_SIZE,
        "chunking_version": CHUNKING_VERSION,
        **get_agent_settings(),
        "routing_action": routing_action,
    }


def settings_match(saved_settings: dict, expected_settings: dict) -> bool:
    return all(
        saved_settings.get(key) == value
        for key, value in expected_settings.items()
    )


def find_valid_completed_run(registry_entry: dict):
    expected_agent_settings = get_agent_settings()
    expected_phase1_settings = {
        "embedding_model": EMBEDDING_MODEL,
        "breakpoint_percentile": BREAKPOINT_PERCENTILE,
        "buffer_size": BUFFER_SIZE,
        "chunking_version": CHUNKING_VERSION,
        **expected_agent_settings,
    }

    for run in registry_entry.get("runs", []):
        saved_settings = run.get("processing_settings", {})
        chunks_file = run.get("chunks_file", "")

        if (
            run.get("processing_status") != "completed"
            or not settings_match(saved_settings, expected_phase1_settings)
            or not chunks_file
            or not os.path.exists(chunks_file)
        ):
            continue

        try:
            with open(chunks_file, "r", encoding=TEXT_ENCODING) as file:
                saved_text = file.read()

            if calculate_text_hash(saved_text) == run.get("chunks_sha256"):
                return run
        except (OSError, UnicodeError):
            continue

    return None


def find_cached_agent_check(registry_entry: dict):
    expected_settings = get_agent_settings()

    for agent_check in reversed(registry_entry.get("agent_checks", [])):
        if settings_match(
            agent_check.get("agent_settings", {}),
            expected_settings,
        ):
            return agent_check

    return None


def build_chunk_signature(routing_action: str) -> str:
    return (
        f"{safe_name(EMBEDDING_MODEL)}_buf{BUFFER_SIZE}_"
        f"p{int(BREAKPOINT_PERCENTILE)}_v{CHUNKING_VERSION}_"
        f"agent-{safe_name(ROUTING_AGENT_MODEL)}_"
        f"a{ROUTING_AGENT_VERSION}_t{MAX_TOKENS_PER_BATCH}_"
        f"{routing_action}"
    )


def build_chunks_file_path(
    filename: str,
    input_sha256: str,
    routing_action: str,
) -> str:
    stem = os.path.splitext(filename)[0]
    short_hash = input_sha256[:6]
    signature = build_chunk_signature(routing_action)
    return os.path.join(
        CHUNKS_DIR,
        f"{stem}_{short_hash}_chunks_{signature}.json",
    )


def save_agent_check(
    filename: str,
    input_sha256: str,
    registry: dict,
    registry_entry: dict,
    agent_result: dict,
) -> dict:
    checked_at = datetime.now(timezone.utc).isoformat(timespec="seconds")
    short_hash = input_sha256[:6]
    decision = agent_result["decision"]
    agent_check = {
        "checked_at_utc": checked_at,
        "agent_settings": get_agent_settings(),
        "metrics": agent_result["metrics"],
        "model_called": agent_result.get("model_called", True),
        "raw_response": agent_result.get("raw_response", ""),
        "agent_trace": agent_result.get("agent_trace", []),
        "sample_used": agent_result.get("sample_used", False),
        "decision": decision,
    }
    os.makedirs(AGENT_DECISIONS_DIR, exist_ok=True)
    decision_filename = (
        f"{os.path.splitext(filename)[0]}_{short_hash}_routing_"
        f"{safe_name(ROUTING_AGENT_MODEL)}_v{ROUTING_AGENT_VERSION}.json"
    )
    decision_path = os.path.join(AGENT_DECISIONS_DIR, decision_filename)
    decision_output = {
        "source_filename": filename,
        "input_sha256": input_sha256,
        **agent_check,
    }

    with open(decision_path, "w", encoding=TEXT_ENCODING) as file:
        json.dump(decision_output, file, indent=2, ensure_ascii=False)

    agent_check["decision_file"] = decision_path
    registry_entry.setdefault("agent_checks", []).append(agent_check)
    save_registry(registry)
    return agent_check


def build_single_chunk(text: str) -> list:
    return [
        {
            "chunk_number": 1,
            "first_sentence_position": None,
            "final_sentence_position": None,
            "sentence_count": None,
            "character_count": len(text),
            "estimated_token_count": estimate_tokens(text),
            "text": text,
        }
    ]


def save_chunks_result(
    filename: str,
    input_sha256: str,
    registry: dict,
    registry_entry: dict,
    routing_action: str,
    agent_check: dict,
    chunks: list,
    total_sentence_count,
) -> str:
    chunks_file_path = build_chunks_file_path(
        filename,
        input_sha256,
        routing_action,
    )
    processing_settings = get_processing_settings(routing_action)
    chunks_data = {
        "source_filename": filename,
        "input_sha256": input_sha256,
        "routing_agent": {
            "checked_at_utc": agent_check.get("checked_at_utc"),
            "agent_settings": agent_check.get("agent_settings", {}),
            "decision": agent_check.get("decision", {}),
        },
        "processing_settings": processing_settings,
        "total_sentence_count": total_sentence_count,
        "total_chunk_count": len(chunks),
        "chunks": chunks,
    }
    chunks_json_text = json.dumps(
        chunks_data,
        indent=2,
        ensure_ascii=False,
    )
    chunks_sha256 = calculate_text_hash(chunks_json_text)
    os.makedirs(CHUNKS_DIR, exist_ok=True)

    with open(chunks_file_path, "w", encoding=TEXT_ENCODING) as file:
        file.write(chunks_json_text)

    registry_entry.setdefault("runs", []).append(
        {
            "processing_status": "completed",
            "routing_action": routing_action,
            "chunk_signature": build_chunk_signature(routing_action),
            "chunks_file": chunks_file_path,
            "chunks_sha256": chunks_sha256,
            "processed_at_utc": datetime.now(timezone.utc).isoformat(
                timespec="seconds"
            ),
            "processing_settings": processing_settings,
        }
    )
    save_registry(registry)
    return chunks_file_path


def build_routing_plan(
    status: str,
    filepath: str,
    filename: str,
    input_sha256: str = "",
    chunks_file: str = "",
    routing_action: str = "",
    agent_check=None,
    reason: str = "",
) -> dict:
    return {
        "status": status,
        "filepath": filepath,
        "filename": filename,
        "input_sha256": input_sha256,
        "chunks_file": chunks_file,
        "routing_action": routing_action,
        "agent_check": agent_check or {},
        "reason": reason,
    }


def route_file(filepath: str) -> dict:
    filename = os.path.basename(filepath)

    if not os.path.exists(filepath) or not filepath.lower().endswith(".txt"):
        message = "Invalid file type or missing file."
        print(f"Routing failed for {filepath}: {message}")
        return build_routing_plan(
            "failed",
            filepath,
            filename,
            reason=message,
        )

    input_sha256 = calculate_file_hash(filepath)
    short_hash = input_sha256[:6]
    registry = load_registry()
    registry.setdefault(filename, {})
    registry[filename].setdefault(
        input_sha256,
        {"runs": [], "agent_checks": []},
    )
    registry_entry = registry[filename][input_sha256]
    registry_entry.setdefault("runs", [])
    registry_entry.setdefault("agent_checks", [])

    valid_run = find_valid_completed_run(registry_entry)

    if valid_run:
        signature = valid_run.get("chunk_signature", "current settings")
        print(
            f"Phase 1 validated for {filename} (Hash: {short_hash}) with "
            f"settings [{signature}]. Skipping routing agent and Phase 1."
        )
        return build_routing_plan(
            "ready",
            filepath,
            filename,
            input_sha256=input_sha256,
            chunks_file=valid_run["chunks_file"],
        )

    try:
        with open(
            filepath,
            "r",
            encoding=TEXT_ENCODING,
            errors="replace",
        ) as file:
            raw_text = file.read()
    except OSError as error:
        message = f"The file could not be read: {error}"
        print(f"Routing failed for {filepath}: {message}")
        return build_routing_plan(
            "failed",
            filepath,
            filename,
            input_sha256=input_sha256,
            reason=message,
        )

    cached_agent_check = find_cached_agent_check(registry_entry)

    try:
        if cached_agent_check:
            agent_check = cached_agent_check
            print(
                f"Routing agent decision reused for {filename} "
                f"(Hash: {short_hash})."
            )
        else:
            print(
                f"Starting routing agent for {filename} "
                f"(Hash: {short_hash})..."
            )
            agent_result = evaluate_document(raw_text)
            agent_check = save_agent_check(
                filename,
                input_sha256,
                registry,
                registry_entry,
                agent_result,
            )

        decision = agent_check["decision"]
        routing_action = decision["action"]
        print(f"Routing agent decision for {filename}: {routing_action}.")
        print(f"Routing reason: {decision.get('reason', 'No reason provided.')}")

        if routing_action == "skip_file":
            print(
                f"File skipped for {filename} by the routing agent. "
                "No summarization is required."
            )
            return build_routing_plan(
                "skipped",
                filepath,
                filename,
                input_sha256=input_sha256,
                routing_action=routing_action,
                agent_check=agent_check,
                reason=decision.get("reason", "Skipped by routing agent."),
            )

        return build_routing_plan(
            "routed",
            filepath,
            filename,
            input_sha256=input_sha256,
            routing_action=routing_action,
            agent_check=agent_check,
            reason=decision.get("reason", ""),
        )

    except Exception as error:
        print(f"Routing failed for {filename}: {error}")
        return build_routing_plan(
            "failed",
            filepath,
            filename,
            input_sha256=input_sha256,
            reason=str(error),
        )


def process_routed_file(routing_plan: dict) -> dict:
    status = routing_plan.get("status", "failed")
    filename = routing_plan.get("filename", "")
    filepath = routing_plan.get("filepath", "")

    if status != "routed":
        return build_result(
            status,
            filename,
            chunks_file=routing_plan.get("chunks_file", ""),
            reason=routing_plan.get("reason", ""),
        )

    input_sha256 = routing_plan.get("input_sha256", "")
    routing_action = routing_plan.get("routing_action", "")
    agent_check = routing_plan.get("agent_check", {})
    short_hash = input_sha256[:6]

    try:
        if not os.path.isfile(filepath):
            raise ValueError("The file disappeared after the routing pass.")

        current_sha256 = calculate_file_hash(filepath)

        if current_sha256 != input_sha256:
            raise ValueError(
                "The file changed after the routing pass. Run the pipeline "
                "again so the agent can inspect the new content."
            )

        with open(
            filepath,
            "r",
            encoding=TEXT_ENCODING,
            errors="replace",
        ) as file:
            raw_text = file.read()

        prepared_text = prepare_paragraph_text(raw_text)

        if not prepared_text:
            raise ValueError("File contains no valid text after preparation.")

        signature = build_chunk_signature(routing_action)
        registry = load_registry()

        try:
            registry_entry = registry[filename][input_sha256]
        except KeyError as error:
            raise ValueError(
                "The routing decision is missing from the processing registry."
            ) from error

        if routing_action == "single_chunk":
            print(
                f"Semantic chunking is not required for {filename}. "
                "Creating one chunk for Phase 2..."
            )
            chunks = build_single_chunk(prepared_text)
            chunks_file_path = save_chunks_result(
                filename,
                input_sha256,
                registry,
                registry_entry,
                routing_action,
                agent_check,
                chunks,
                total_sentence_count=None,
            )
            print(
                f"Phase 1 routing successfully completed for {filename} "
                f"({signature})."
            )
            return build_result(
                "ready",
                filename,
                chunks_file=chunks_file_path,
            )

        if routing_action != "semantic_chunking":
            raise ValueError(
                f"Unsupported routed action: {routing_action or 'empty'}"
            )

        print(
            f"Starting Phase 1 data preparation for {filename} "
            f"(Hash: {short_hash}) with settings [{signature}]..."
        )
        sentences = extract_sentences(prepared_text)
        unload_stanza_pipeline()
        windows = build_context_windows(sentences)
        embeddings = generate_and_normalize_embeddings(windows)
        breakpoints = detect_breakpoints(embeddings)
        semantic_chunks = build_semantic_chunks(sentences, breakpoints)
        chunks_file_path = save_chunks_result(
            filename,
            input_sha256,
            registry,
            registry_entry,
            routing_action,
            agent_check,
            semantic_chunks,
            total_sentence_count=len(sentences),
        )
        print(f"Phase 1 successfully completed for {filename} ({signature}).")
        return build_result(
            "ready",
            filename,
            chunks_file=chunks_file_path,
        )

    except Exception as error:
        print(f"Phase 1 failed for {filename}: {error}")
        return build_result("failed", filename, reason=str(error))


def process_file(filepath: str) -> dict:
    """Process one file while preserving the original single-file API."""
    return process_routed_file(route_file(filepath))
