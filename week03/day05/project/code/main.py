# main.py
import glob
from config import STANZA_LANG
from nlp_core import init_stanza_pipeline
from phase1_prep import process_file_phase1
from phase2_summary import process_file_phase2

def main():
    """Main execution workflow for processing multiple local .txt files."""
    input_files = glob.glob("inputs/*.txt")
    
    if not input_files:
        print("No .txt files found in 'inputs/' directory.")
        return

    print("Initializing Stanza NLP pipeline...")
    stanza_pipeline = init_stanza_pipeline(STANZA_LANG)

    for filepath in input_files:
        print(f"\n--- Processing {filepath} ---")
        try:
            phase1_success = process_file_phase1(filepath, stanza_pipeline)
            if phase1_success:
                process_file_phase2(filepath)
        except Exception as e:
            print(f"Error processing {filepath}: {e}")

if __name__ == "__main__":
    main()