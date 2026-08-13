import json
import os
import re
import subprocess
import sys
import time
import uuid
from pathlib import Path

import ollama
import streamlit as st

import config


RUN_LOCK_PATH = os.path.join(config.BASE_DIR, ".streamlit_pipeline.lock")


def inject_page_styles() -> None:
    st.markdown(
        """
        <style>
        [data-testid="stAppViewContainer"],
        [data-testid="stSidebar"] {
            direction: ltr;
        }
        [data-testid="stCode"],
        textarea,
        code {
            direction: ltr;
            text-align: left;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def build_runtime_settings() -> dict:
    with st.sidebar:
        st.header("Runtime Settings")

        st.subheader("Local Models")
        embedding_model = st.text_input(
            "Embedding model",
            value=config.EMBEDDING_MODEL,
        ).strip()
        summarization_model = st.text_input(
            "Summarization model",
            value=config.SUMMARIZATION_MODEL,
        ).strip()
        ollama_keep_alive = st.text_input(
            "Ollama keep-alive duration",
            value=config.OLLAMA_KEEP_ALIVE,
        ).strip()

        st.subheader("Routing Agent")
        routing_agent_model = st.text_input(
            "Routing agent model",
            value=config.ROUTING_AGENT_MODEL,
        ).strip()
        routing_agent_version = st.number_input(
            "Routing agent version",
            min_value=1,
            value=int(config.ROUTING_AGENT_VERSION),
            step=1,
        )
        routing_agent_sample_chars = st.number_input(
            "Maximum document sample characters",
            min_value=1000,
            value=int(config.ROUTING_AGENT_SAMPLE_CHARS),
            step=1000,
        )
        with st.expander("Agent protocol settings"):
            routing_agent_max_steps = st.number_input(
                "Maximum agent steps",
                min_value=1,
                value=int(config.ROUTING_AGENT_MAX_STEPS),
                step=1,
            )
            routing_agent_context = st.number_input(
                "Agent context window",
                min_value=1024,
                value=int(config.ROUTING_AGENT_CONTEXT),
                step=1024,
            )
            routing_agent_num_predict = st.number_input(
                "Maximum response tokens per step",
                min_value=1,
                value=int(config.ROUTING_AGENT_NUM_PREDICT),
                step=10,
            )
        routing_agent_temperature = st.number_input(
            "Routing agent temperature",
            min_value=0.0,
            max_value=2.0,
            value=float(config.ROUTING_AGENT_TEMPERATURE),
            step=0.1,
        )

        st.subheader("Phase 1 Settings")
        stanza_language = st.text_input(
            "Stanza language",
            value=config.STANZA_LANGUAGE,
        ).strip()
        stanza_use_gpu = st.checkbox(
            "Use GPU with Stanza",
            value=config.STANZA_USE_GPU,
        )
        breakpoint_percentile = st.number_input(
            "Breakpoint percentile",
            min_value=0.0,
            max_value=100.0,
            value=float(config.BREAKPOINT_PERCENTILE),
            step=1.0,
        )
        buffer_size = st.number_input(
            "Buffer size",
            min_value=0,
            value=int(config.BUFFER_SIZE),
            step=1,
        )
        chunking_version = st.number_input(
            "Chunking version",
            min_value=1,
            value=int(config.CHUNKING_VERSION),
            step=1,
        )

        st.subheader("Phase 2 Settings")
        max_tokens_per_batch = st.number_input(
            "Maximum estimated tokens per batch",
            min_value=1,
            value=int(config.MAX_TOKENS_PER_BATCH),
            step=100,
        )
        max_reduce_rounds = st.number_input(
            "Maximum Reduce rounds",
            min_value=1,
            value=int(config.MAX_REDUCE_ROUNDS),
            step=1,
        )

        with st.expander("Fixed Project Paths"):
            st.code(
                "\n".join(
                    [
                        f"inputs: {config.INPUT_DIR}",
                        f"chunks: {config.CHUNKS_DIR}",
                        f"agent decisions: {config.AGENT_DECISIONS_DIR}",
                        f"summaries: {config.SUMMARIES_DIR}",
                        f"registry: {config.REGISTRY_PATH}",
                        f"encoding: {config.TEXT_ENCODING}",
                    ]
                )
            )

    return {
        "EMBEDDING_MODEL": embedding_model,
        "SUMMARIZATION_MODEL": summarization_model,
        "OLLAMA_KEEP_ALIVE": ollama_keep_alive,
        "ROUTING_AGENT_MODEL": routing_agent_model,
        "ROUTING_AGENT_VERSION": int(routing_agent_version),
        "ROUTING_AGENT_SAMPLE_CHARS": int(routing_agent_sample_chars),
        "ROUTING_AGENT_MAX_STEPS": int(routing_agent_max_steps),
        "ROUTING_AGENT_CONTEXT": int(routing_agent_context),
        "ROUTING_AGENT_NUM_PREDICT": int(routing_agent_num_predict),
        "ROUTING_AGENT_TEMPERATURE": float(routing_agent_temperature),
        "STANZA_LANGUAGE": stanza_language,
        "STANZA_USE_GPU": stanza_use_gpu,
        "BREAKPOINT_PERCENTILE": float(breakpoint_percentile),
        "BUFFER_SIZE": int(buffer_size),
        "CHUNKING_VERSION": int(chunking_version),
        "MAX_TOKENS_PER_BATCH": int(max_tokens_per_batch),
        "MAX_REDUCE_ROUNDS": int(max_reduce_rounds),
    }


def validate_settings(settings: dict) -> list:
    errors = []

    for setting_name in (
        "EMBEDDING_MODEL",
        "SUMMARIZATION_MODEL",
        "ROUTING_AGENT_MODEL",
        "OLLAMA_KEEP_ALIVE",
        "STANZA_LANGUAGE",
    ):
        if not str(settings[setting_name]).strip():
            errors.append(f"The {setting_name} setting cannot be empty.")

    return errors


def get_local_ollama_model_names() -> set:
    response = ollama.list()

    if isinstance(response, dict):
        models = response.get("models", [])
    else:
        models = getattr(response, "models", [])

    model_names = set()

    for model in models:
        if isinstance(model, dict):
            model_name = model.get("model") or model.get("name")
        else:
            model_name = getattr(model, "model", None) or getattr(
                model,
                "name",
                None,
            )

        if model_name:
            model_names.add(str(model_name).strip().lower())

    return model_names


def model_is_available(requested_model: str, local_models: set) -> bool:
    requested_model = requested_model.strip().lower()

    if requested_model in local_models:
        return True

    if ":" not in requested_model:
        return f"{requested_model}:latest" in local_models

    return False


def validate_ollama_models(settings: dict) -> list:
    try:
        local_models = get_local_ollama_model_names()
    except Exception as error:
        return [
            "Could not connect to the local Ollama service. Make sure it is "
            f"running and try again. Details: {error}"
        ]

    errors = []

    for label, setting_name in (
        ("Embedding model", "EMBEDDING_MODEL"),
        ("Summarization model", "SUMMARIZATION_MODEL"),
        ("Routing agent model", "ROUTING_AGENT_MODEL"),
    ):
        model_name = settings[setting_name]

        if not model_is_available(model_name, local_models):
            errors.append(
                f"{label} is not installed locally or its name is incorrect: "
                f"{model_name}"
            )

    return errors


def validate_uploaded_files(uploaded_files: list) -> tuple:
    valid_files = []
    errors = []

    for uploaded_file in uploaded_files or []:
        safe_name = Path(uploaded_file.name).name

        if not safe_name.lower().endswith(config.INPUT_FILE_EXTENSION.lower()):
            errors.append(f"The file is not a TXT file: {safe_name}")
            continue

        file_bytes = uploaded_file.getvalue()

        try:
            file_bytes.decode(config.TEXT_ENCODING)
        except UnicodeDecodeError:
            errors.append(f"The file is not valid UTF-8 text: {safe_name}")
            continue

        if not file_bytes.strip():
            errors.append(f"The text file is empty: {safe_name}")
            continue

        valid_files.append((safe_name, file_bytes))

    return valid_files, errors


def save_uploaded_files(valid_files: list) -> list:
    os.makedirs(config.INPUT_DIR, exist_ok=True)
    saved_messages = []

    for safe_name, file_bytes in valid_files:
        destination = os.path.join(config.INPUT_DIR, safe_name)
        existed = os.path.isfile(destination)
        previous_bytes = Path(destination).read_bytes() if existed else None

        if previous_bytes == file_bytes:
            saved_messages.append(
                f"The file already exists with the same content: {safe_name}"
            )
            continue

        Path(destination).write_bytes(file_bytes)

        if existed:
            saved_messages.append(f"Updated the existing file: {safe_name}")
        else:
            saved_messages.append(f"Saved the file: {safe_name}")

    return saved_messages


def list_input_text_files() -> list:
    if not os.path.isdir(config.INPUT_DIR):
        return []

    return sorted(
        os.path.join(config.INPUT_DIR, filename)
        for filename in os.listdir(config.INPUT_DIR)
        if filename.lower().endswith(config.INPUT_FILE_EXTENSION.lower())
        and os.path.isfile(os.path.join(config.INPUT_DIR, filename))
    )


def process_is_running(process_id: int) -> bool:
    try:
        os.kill(process_id, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True

    return True


def acquire_run_lock() -> str:
    lock_token = uuid.uuid4().hex

    for _ in range(2):
        try:
            descriptor = os.open(
                RUN_LOCK_PATH,
                os.O_CREAT | os.O_EXCL | os.O_WRONLY,
            )
        except FileExistsError:
            try:
                lock_data = json.loads(Path(RUN_LOCK_PATH).read_text("utf-8"))
                process_id = int(lock_data.get("process_id", 0))
                created_at = float(lock_data.get("created_at", 0))
                lock_is_old = time.time() - created_at > 86400
            except (OSError, ValueError, TypeError, json.JSONDecodeError):
                process_id = 0
                lock_is_old = True

            if not lock_is_old and process_id and process_is_running(process_id):
                return ""

            try:
                os.unlink(RUN_LOCK_PATH)
            except FileNotFoundError:
                pass

            continue

        with os.fdopen(descriptor, "w", encoding="utf-8") as lock_file:
            json.dump(
                {
                    "token": lock_token,
                    "process_id": os.getpid(),
                    "created_at": time.time(),
                },
                lock_file,
            )

        return lock_token

    return ""


def update_run_lock_process(lock_token: str, process_id: int) -> None:
    try:
        lock_data = json.loads(Path(RUN_LOCK_PATH).read_text("utf-8"))
    except (OSError, json.JSONDecodeError):
        return

    if lock_data.get("token") != lock_token:
        return

    lock_data["process_id"] = process_id
    Path(RUN_LOCK_PATH).write_text(
        json.dumps(lock_data),
        encoding="utf-8",
    )


def release_run_lock(lock_token: str) -> None:
    try:
        lock_data = json.loads(Path(RUN_LOCK_PATH).read_text("utf-8"))
    except (OSError, json.JSONDecodeError):
        return

    if lock_data.get("token") != lock_token:
        return

    try:
        os.unlink(RUN_LOCK_PATH)
    except FileNotFoundError:
        pass


def build_pipeline_environment(settings: dict) -> dict:
    environment = os.environ.copy()

    for setting_name, value in settings.items():
        environment[f"{config.ENV_PREFIX}{setting_name}"] = str(value)

    return environment


def run_pipeline_with_progress(
    settings: dict,
    input_count: int,
    progress_bar,
    status_placeholder,
    log_placeholder,
) -> tuple:
    command = [sys.executable, "-u", os.path.join(config.BASE_DIR, "main.py")]
    environment = build_pipeline_environment(settings)
    lock_token = acquire_run_lock()

    if not lock_token:
        return False, "Another pipeline run is active. Wait for it to finish."

    logs = []
    routing_completed = 0
    phase1_completed = 0
    phase1_total = 0
    phase2_started = 0
    phase2_completed = 0
    phase2_total = 0
    current_batch_total = 0

    try:
        process = subprocess.Popen(
            command,
            cwd=config.BASE_DIR,
            env=environment,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding=config.TEXT_ENCODING,
            errors="replace",
            bufsize=1,
        )
        update_run_lock_process(lock_token, process.pid)

        if process.stdout is None:
            process.terminate()
            return False, "Could not read the pipeline process output."

        for raw_line in process.stdout:
            line = raw_line.rstrip()

            if not line:
                continue

            logs.append(line)
            log_placeholder.code("\n".join(logs[-250:]), language="text")

            if line.startswith("Starting routing agent pass for "):
                progress_bar.progress(5)
                status_placeholder.info(
                    f"Routing agent: starting inspection of {input_count} "
                    "input file(s)."
                )

            elif line.startswith("Routing pass progress: "):
                match = re.search(
                    r"Routing pass progress: (\d+) of (\d+)",
                    line,
                )

                if match:
                    routing_completed = int(match.group(1))
                    routing_total = int(match.group(2))
                else:
                    routing_total = input_count

                remaining = max(routing_total - routing_completed, 0)
                routing_ratio = routing_completed / max(routing_total, 1)
                progress_bar.progress(int(5 + (20 * routing_ratio)))
                status_placeholder.info(
                    f"Routing agent: inspected {routing_completed} of "
                    f"{routing_total}; {remaining} remaining."
                )

            elif line.startswith("Starting routing agent for "):
                status_placeholder.info(
                    f"Routing agent: inspecting file "
                    f"{min(routing_completed + 1, input_count)} of "
                    f"{input_count}."
                )

            elif line.startswith("Routing agent decision reused for "):
                status_placeholder.info(
                    "Routing agent: reusing a cached decision for this hash."
                )

            elif line.startswith("Starting Phase 1 processing pass for "):
                match = re.search(
                    r"Starting Phase 1 processing pass for (\d+)",
                    line,
                )
                phase1_total = int(match.group(1)) if match else 0
                progress_bar.progress(50 if phase1_total == 0 else 25)
                status_placeholder.info(
                    f"Phase 1 processing: {phase1_total} routed file(s) "
                    "require new processing."
                )

            elif line.startswith("Starting Phase 1 processing "):
                match = re.search(
                    r"Starting Phase 1 processing (\d+) of (\d+)",
                    line,
                )
                current_file = int(match.group(1)) if match else 0
                total_files = int(match.group(2)) if match else phase1_total
                status_placeholder.info(
                    f"Phase 1 processing: file {current_file} of "
                    f"{total_files}."
                )

            elif line.startswith("Phase 1 processing progress: "):
                match = re.search(
                    r"Phase 1 processing progress: (\d+) of (\d+)",
                    line,
                )

                if match:
                    phase1_completed = int(match.group(1))
                    phase1_total = int(match.group(2))

                remaining = max(phase1_total - phase1_completed, 0)
                phase1_ratio = phase1_completed / max(phase1_total, 1)
                progress_bar.progress(int(25 + (25 * phase1_ratio)))
                status_placeholder.info(
                    f"Phase 1 processing: completed {phase1_completed} of "
                    f"{phase1_total}; {remaining} remaining."
                )

            elif (
                line.startswith("Starting Phase 2 for ")
                and "eligible chunks file" in line
            ):
                match = re.search(
                    r"Starting Phase 2 for (\d+) eligible chunks file",
                    line,
                )
                phase2_total = int(match.group(1)) if match else 0
                progress_bar.progress(50)
                status_placeholder.info(
                    f"Phase 2 started for {phase2_total} chunks file(s)."
                )

            elif line.startswith("Starting Phase 2 for "):
                phase2_started += 1
                current_batch_total = 0
                remaining = max(phase2_total - phase2_completed, 0)
                status_placeholder.info(
                    f"Phase 2: file {phase2_started} of "
                    f"{max(phase2_total, phase2_started)}; "
                    f"{remaining} remaining."
                )

            elif line.startswith("Created ") and "summarization batches" in line:
                match = re.search(r"Created (\d+) summarization batches", line)
                current_batch_total = int(match.group(1)) if match else 0

            elif line.startswith("Summarizing batch "):
                match = re.search(r"Summarizing batch (\d+)", line)
                current_batch = int(match.group(1)) if match else 0
                remaining_batches = max(current_batch_total - current_batch, 0)
                denominator = max(phase2_total, phase2_started, 1)
                batch_ratio = current_batch / max(current_batch_total, 1)
                file_ratio = (phase2_completed + (0.8 * batch_ratio)) / denominator
                progress_bar.progress(min(int(50 + (45 * file_ratio)), 94))
                status_placeholder.info(
                    f"Map: batch {current_batch} of "
                    f"{max(current_batch_total, current_batch)}; "
                    f"{remaining_batches} remaining."
                )

            elif line.startswith("Starting Reduce round "):
                match = re.search(r"Starting Reduce round (\d+)", line)
                reduce_round = match.group(1) if match else "?"
                status_placeholder.info(
                    f"Reduce: processing round {reduce_round}."
                )

            elif "Phase 2 successfully completed for" in line:
                phase2_completed += 1
                denominator = max(phase2_total, phase2_completed, 1)
                progress_bar.progress(
                    min(int(50 + (45 * phase2_completed / denominator)), 95)
                )
                remaining = max(phase2_total - phase2_completed, 0)
                status_placeholder.info(
                    f"Phase 2: completed {phase2_completed} of {denominator}; "
                    f"{remaining} remaining."
                )

        return_code = process.wait()
        st.session_state["last_run_log"] = "\n".join(logs)

        if return_code == 0:
            progress_bar.progress(100)
            status_placeholder.success(
                "All pipeline phases completed successfully."
            )
            return True, "The pipeline completed successfully."

        status_placeholder.error(
            f"The pipeline stopped with exit code {return_code}. "
            "Review the execution log."
        )
        return False, f"The pipeline stopped with exit code {return_code}."

    except Exception as error:
        st.session_state["last_run_log"] = "\n".join(logs)
        status_placeholder.error(f"Could not run the pipeline: {error}")
        return False, f"Could not run the pipeline: {error}"
    finally:
        release_run_lock(lock_token)


def list_files(directory: str, suffix: str = "") -> list:
    if not os.path.isdir(directory):
        return []

    return sorted(
        (
            os.path.join(directory, filename)
            for filename in os.listdir(directory)
            if (not suffix or filename.endswith(suffix))
            and os.path.isfile(os.path.join(directory, filename))
        ),
        key=os.path.getmtime,
        reverse=True,
    )


def load_json_file(file_path: str):
    with open(file_path, "r", encoding=config.TEXT_ENCODING) as file:
        return json.load(file)


def format_field_name(field_name) -> str:
    text = str(field_name)

    if len(text) == 64 and all(character in "0123456789abcdefABCDEF" for character in text):
        return f"SHA-256: {text[:8]}...{text[-8:]}"

    if "." in text or "/" in text or "\\" in text:
        return text

    return text.replace("_", " ").strip().title()


def format_field_value(value) -> str:
    if value is None:
        return "—"

    if isinstance(value, bool):
        return "Yes" if value else "No"

    if isinstance(value, list):
        return ", ".join(str(item) for item in value) if value else "—"

    return str(value)


def show_key_value_table(data: dict) -> None:
    rows = [
        {
            "Field": format_field_name(key),
            "Value": format_field_value(value),
        }
        for key, value in data.items()
        if not isinstance(value, (dict, list))
        or isinstance(value, list)
        and all(not isinstance(item, (dict, list)) for item in value)
    ]

    if rows:
        st.table(rows)


def show_structured_data(data, depth: int = 0) -> None:
    if isinstance(data, dict):
        show_key_value_table(data)

        for key, value in data.items():
            if not isinstance(value, (dict, list)):
                continue

            if isinstance(value, list) and all(
                not isinstance(item, (dict, list)) for item in value
            ):
                continue

            label = format_field_name(key)

            with st.expander(label, expanded=depth == 0):
                if (
                    isinstance(key, str)
                    and len(key) == 64
                    and all(
                        character in "0123456789abcdefABCDEF"
                        for character in key
                    )
                ):
                    st.caption("Complete SHA-256 hash")
                    st.code(key)

                show_structured_data(value, depth + 1)

    elif isinstance(data, list):
        if not data:
            st.caption("No entries")
            return

        for index, item in enumerate(data, start=1):
            if isinstance(item, (dict, list)):
                with st.expander(f"Item {index}", expanded=depth == 0):
                    show_structured_data(item, depth + 1)
            else:
                st.write(f"{index}. {format_field_value(item)}")

    else:
        st.write(format_field_value(data))


def show_download_button(file_path: str, key: str) -> None:
    st.download_button(
        "Download file",
        data=Path(file_path).read_bytes(),
        file_name=os.path.basename(file_path),
        mime="application/octet-stream",
        key=key,
    )


def show_chunks_view() -> None:
    chunks_files = list_files(config.CHUNKS_DIR, ".json")

    if not chunks_files:
        st.info("No chunks files are available yet.")
        return

    selected_file = st.selectbox(
        "Select a chunks file",
        chunks_files,
        format_func=os.path.basename,
        key="chunks_file_selector",
    )

    try:
        data = load_json_file(selected_file)
    except (OSError, json.JSONDecodeError) as error:
        st.error(f"Could not read the chunks file: {error}")
        return

    show_download_button(selected_file, "download_chunks")
    column1, column2, column3 = st.columns(3)
    column1.metric("Sentences", data.get("total_sentence_count", 0))
    column2.metric("Chunks", data.get("total_chunk_count", 0))
    column3.metric("Source file", data.get("source_filename", "-"))

    st.subheader("Source Details")
    show_key_value_table(
        {
            "source_filename": data.get("source_filename"),
            "input_sha256": data.get("input_sha256"),
        }
    )

    st.subheader("Processing Settings")
    show_key_value_table(data.get("processing_settings", {}))

    routing_agent = data.get("routing_agent", {})

    if routing_agent:
        st.subheader("Routing Agent Decision")
        show_key_value_table(routing_agent.get("decision", {}))

    st.subheader("Semantic Chunks")

    for chunk in data.get("chunks", []):
        chunk_number = chunk.get("chunk_number", "?")

        with st.expander(f"Chunk {chunk_number}"):
            show_key_value_table(
                {
                    key: value
                    for key, value in chunk.items()
                    if key != "text"
                }
            )
            st.text_area(
                "Text",
                value=chunk.get("text", ""),
                height=220,
                disabled=True,
                key=f"chunk_text_{os.path.basename(selected_file)}_{chunk_number}",
            )


def show_registry_view() -> None:
    if not os.path.isfile(config.REGISTRY_PATH):
        st.info("The processing registry is not available yet.")
        return

    try:
        registry = load_json_file(config.REGISTRY_PATH)
    except (OSError, json.JSONDecodeError) as error:
        st.error(f"Could not read the processing registry: {error}")
        return

    show_download_button(config.REGISTRY_PATH, "download_registry")
    source_count = len(registry) if isinstance(registry, dict) else 0
    st.metric("Tracked source files", source_count)

    if isinstance(registry, dict):
        for source_name, source_data in registry.items():
            with st.expander(str(source_name), expanded=True):
                show_structured_data(source_data)
    else:
        show_structured_data(registry)


def show_agent_decisions_view() -> None:
    files = list_files(config.AGENT_DECISIONS_DIR, ".json")

    if not files:
        st.info("No routing agent decisions are available yet.")
        return

    selected_file = st.selectbox(
        "Select a routing agent decision",
        files,
        format_func=os.path.basename,
        key="agent_decision_selector",
    )

    try:
        data = load_json_file(selected_file)
    except (OSError, json.JSONDecodeError) as error:
        st.error(f"Could not read the routing agent decision: {error}")
        return

    show_download_button(selected_file, "download_agent_decision")
    decision = data.get("decision", {})
    metrics = data.get("metrics", {})
    column1, column2, column3 = st.columns(3)
    column1.metric("Action", decision.get("action", "-"))
    column2.metric(
        "Meaningful",
        "Yes" if decision.get("is_meaningful") else "No",
    )
    column3.metric(
        "Estimated Tokens",
        metrics.get("estimated_token_count", 0),
    )

    st.subheader("Source Details")
    show_key_value_table(
        {
            "source_filename": data.get("source_filename"),
            "input_sha256": data.get("input_sha256"),
            "checked_at_utc": data.get("checked_at_utc"),
        }
    )
    st.subheader("Decision")
    show_key_value_table(decision)
    st.subheader("Document Metrics")
    show_key_value_table(metrics)
    st.subheader("Agent Settings")
    show_key_value_table(data.get("agent_settings", {}))

    agent_trace = data.get("agent_trace", [])

    if agent_trace:
        with st.expander("Validated Agent Steps"):
            show_structured_data(agent_trace)


def show_partial_summaries_view() -> None:
    files = [
        file_path
        for file_path in list_files(config.SUMMARIES_DIR, ".json")
        if file_path.endswith("_partial_summaries.json")
    ]

    if not files:
        st.info("No partial summaries are available yet.")
        return

    selected_file = st.selectbox(
        "Select a partial summaries file",
        files,
        format_func=os.path.basename,
        key="partial_file_selector",
    )

    try:
        data = load_json_file(selected_file)
    except (OSError, json.JSONDecodeError) as error:
        st.error(f"Could not read the partial summaries file: {error}")
        return

    show_download_button(selected_file, "download_partial")
    st.caption(f"Source chunks file: {data.get('source_chunks_file', '-')}")
    st.caption(
        f"Model: {data.get('summarization_model', '-')} | "
        f"Total batches: {data.get('total_batch_count', 0)}"
    )

    for summary in data.get("partial_summaries", []):
        batch_id = summary.get("batch_id", "?")

        with st.expander(f"Batch {batch_id} Summary", expanded=True):
            st.caption(
                f"Source chunks: {summary.get('source_chunk_numbers', [])} | "
                "Estimated source tokens: "
                f"{summary.get('estimated_source_token_count', 0)}"
            )
            st.write(summary.get("summary", ""))


def show_full_summaries_view() -> None:
    files = [
        file_path
        for file_path in list_files(config.SUMMARIES_DIR, ".txt")
        if file_path.endswith("_full_summary.txt")
    ]

    if not files:
        st.info("No full summaries are available yet.")
        return

    selected_file = st.selectbox(
        "Select a full summary file",
        files,
        format_func=os.path.basename,
        key="full_file_selector",
    )
    summary_text = Path(selected_file).read_text(config.TEXT_ENCODING)
    show_download_button(selected_file, "download_full")
    st.text_area(
        "Full Summary",
        value=summary_text,
        height=420,
        disabled=True,
    )


def render_app() -> None:
    st.set_page_config(
        page_title="Local Text Summarizer",
        page_icon="📝",
        layout="wide",
    )
    inject_page_styles()

    if "pipeline_running" not in st.session_state:
        st.session_state["pipeline_running"] = False

    if "last_run_log" not in st.session_state:
        st.session_state["last_run_log"] = ""

    settings = build_runtime_settings()
    settings_errors = validate_settings(settings)

    st.title("Local Text Summarizer")
    st.caption(
        "Runs locally with Stanza and Ollama. It does not download models or "
        "connect to an external summarization service."
    )

    (
        run_tab,
        agent_tab,
        chunks_tab,
        registry_tab,
        partial_tab,
        full_tab,
    ) = st.tabs(
        [
            "Run",
            "Routing Agent",
            "Chunks",
            "Processing Registry",
            "Partial Summaries",
            "Full Summary",
        ]
    )

    with run_tab:
        st.subheader("Upload Text Files")
        uploaded_files = st.file_uploader(
            "Upload one or more TXT files",
            accept_multiple_files=True,
            help="Only UTF-8 encoded TXT files are accepted.",
        )
        valid_files, upload_errors = validate_uploaded_files(uploaded_files)

        for error_message in upload_errors:
            st.error(error_message)

        existing_inputs = list_input_text_files()
        st.caption(
            f"TXT files currently in inputs: {len(existing_inputs)} | "
            f"Valid files selected now: {len(valid_files)}"
        )

        run_disabled = bool(
            st.session_state["pipeline_running"]
            or upload_errors
            or settings_errors
        )
        run_clicked = st.button(
            "Run Pipeline",
            type="primary",
            disabled=run_disabled,
            use_container_width=True,
        )

        for error_message in settings_errors:
            st.error(error_message)

        progress_bar = st.progress(0)
        status_placeholder = st.empty()
        log_placeholder = st.empty()

        if st.session_state["last_run_log"]:
            with st.expander("Last Execution Log"):
                st.code(st.session_state["last_run_log"], language="text")

        if run_clicked:
            st.session_state["pipeline_running"] = True

            try:
                for message in save_uploaded_files(valid_files):
                    st.info(message)

                input_files = list_input_text_files()

                if not input_files:
                    status_placeholder.error(
                        "No TXT files were found in the inputs directory: "
                        f"{config.INPUT_DIR}"
                    )
                else:
                    model_errors = validate_ollama_models(settings)

                    if model_errors:
                        for error_message in model_errors:
                            st.error(error_message)
                    else:
                        progress_bar.progress(5)
                        status_placeholder.info(
                            "Local models verified. The pipeline has started."
                        )
                        success, message = run_pipeline_with_progress(
                            settings,
                            len(input_files),
                            progress_bar,
                            status_placeholder,
                            log_placeholder,
                        )

                        if success:
                            st.success(message)
                        else:
                            st.error(message)
            finally:
                st.session_state["pipeline_running"] = False

    with agent_tab:
        show_agent_decisions_view()

    with chunks_tab:
        show_chunks_view()

    with registry_tab:
        show_registry_view()

    with partial_tab:
        show_partial_summaries_view()

    with full_tab:
        show_full_summaries_view()


if __name__ == "__main__":
    render_app()
