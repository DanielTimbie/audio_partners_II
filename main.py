from djassistant.core import run_app
import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--file", type=str, required=True, help="Path to audio file")
    args = parser.parse_args()

    run_app(args.file)
