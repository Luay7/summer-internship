import glob
import os

from config import INPUT_DIR

import phase1
import phase2


def main():
    os.makedirs(INPUT_DIR, exist_ok=True)

    input_files = sorted(
        glob.glob(os.path.join(INPUT_DIR, "*.txt"))
    )

    if not input_files:
        print(
            f"No .txt files found in "
            f"'{INPUT_DIR}' directory."
        )
        return

    ready_files = []

    print("--- BEGINNING PHASE 1 ---")

    for filepath in input_files:
        print(f"\nEvaluating Phase 1 for {filepath}")

        try:
            if phase1.process_file(filepath):
                ready_files.append(filepath)
        except Exception as error:
            print(
                f"Unexpected error during Phase 1 "
                f"for {filepath}: {error}"
            )

    if not ready_files:
        print(
            "\nNo files successfully completed "
            "Phase 1. Exiting."
        )
        return

    print("\n--- BEGINNING PHASE 2 ---")

    for filepath in ready_files:
        print(f"\nEvaluating Phase 2 for {filepath}")

        try:
            if not phase2.process_file(filepath):
                print(
                    f"Phase 2 was not completed "
                    f"for {filepath}."
                )
        except Exception as error:
            print(
                f"Unexpected error during Phase 2 "
                f"for {filepath}: {error}"
            )


if __name__ == "__main__":
    main()
