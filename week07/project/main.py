import os

from config import (
    AGENT_DECISIONS_DIR,
    CHUNKS_DIR,
    INPUT_DIR,
    INPUT_FILE_EXTENSION,
    SUMMARIES_DIR,
)
from phase1.core import process_routed_file, route_file
from phase2.core import process_chunks_file


def create_project_directories() -> None:
    os.makedirs(INPUT_DIR, exist_ok=True)
    os.makedirs(CHUNKS_DIR, exist_ok=True)
    os.makedirs(SUMMARIES_DIR, exist_ok=True)
    os.makedirs(AGENT_DECISIONS_DIR, exist_ok=True)


def list_input_files() -> list:
    return sorted(
        os.path.join(INPUT_DIR, filename)
        for filename in os.listdir(INPUT_DIR)
        if filename.lower().endswith(INPUT_FILE_EXTENSION.lower())
        and os.path.isfile(os.path.join(INPUT_DIR, filename))
    )


def run_routing_pass(input_files: list) -> list:
    routing_plans = []
    total_files = len(input_files)

    print(f"Starting routing agent pass for {total_files} input file(s)...")

    for index, file_path in enumerate(input_files, start=1):
        print(f"Routing file {index} of {total_files}: {file_path}...")
        routing_plans.append(route_file(file_path))
        print(
            f"Routing pass progress: {index} of {total_files} "
            "files inspected."
        )

    routed_count = sum(
        plan["status"] == "routed" for plan in routing_plans
    )
    ready_count = sum(
        plan["status"] == "ready" for plan in routing_plans
    )
    skipped_count = sum(
        plan["status"] == "skipped" for plan in routing_plans
    )
    failed_count = sum(
        plan["status"] == "failed" for plan in routing_plans
    )
    print(
        f"Routing agent pass completed: {routed_count} routed for new "
        f"Phase 1 processing, {ready_count} already ready, "
        f"{skipped_count} skipped, and {failed_count} failed."
    )
    return routing_plans


def run_phase1(input_files: list) -> dict:
    routing_plans = run_routing_pass(input_files)
    routed_plans = [
        plan for plan in routing_plans if plan["status"] == "routed"
    ]
    processed_results = {}
    total_routed = len(routed_plans)

    print(
        f"Starting Phase 1 processing pass for {total_routed} "
        "routed file(s)..."
    )

    for index, routing_plan in enumerate(routed_plans, start=1):
        file_path = routing_plan["filepath"]
        print(
            f"Starting Phase 1 processing {index} of {total_routed} "
            f"for {file_path}..."
        )
        processed_results[file_path] = process_routed_file(routing_plan)
        print(
            f"Phase 1 processing progress: {index} of {total_routed} "
            "routed files completed."
        )

    ready_chunks_files = []
    skipped_count = 0
    failed_count = 0

    for routing_plan in routing_plans:
        if routing_plan["status"] == "routed":
            result = processed_results[routing_plan["filepath"]]
        else:
            result = process_routed_file(routing_plan)

        if result["status"] == "ready":
            ready_chunks_files.append(result["chunks_file"])
        elif result["status"] == "skipped":
            skipped_count += 1
        else:
            failed_count += 1

    print(
        f"Phase 1 completed: {len(ready_chunks_files)} ready, "
        f"{skipped_count} skipped by the routing agent, "
        f"and {failed_count} failed."
    )

    return {
        "ready_chunks_files": list(dict.fromkeys(ready_chunks_files)),
        "skipped_count": skipped_count,
        "failed_count": failed_count,
    }


def run_phase2_for_files(chunks_files: list) -> bool:
    successful_count = 0

    for chunks_file_path in chunks_files:
        if process_chunks_file(chunks_file_path):
            successful_count += 1

    print(
        f"Phase 2 completed: {successful_count} of "
        f"{len(chunks_files)} files succeeded."
    )

    return successful_count == len(chunks_files)


def main() -> int:
    create_project_directories()
    input_files = list_input_files()

    if not input_files:
        print(f"No {INPUT_FILE_EXTENSION} files were found in: {INPUT_DIR}")
        return 1

    print(f"Found {len(input_files)} input file(s).")

    phase1_result = run_phase1(input_files)

    if phase1_result["failed_count"]:
        print("Phase 2 was not started because Phase 1 did not complete successfully.")
        return 1

    chunks_files = phase1_result["ready_chunks_files"]

    if not chunks_files:
        print(
            "No input files require summarization. "
            "Phase 2 was skipped successfully."
        )
        return 0

    print(
        f"Starting Phase 2 for {len(chunks_files)} eligible chunks file(s)..."
    )

    if not run_phase2_for_files(chunks_files):
        print("The project finished with one or more Phase 2 failures.")
        return 1

    print("All project phases completed successfully.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
