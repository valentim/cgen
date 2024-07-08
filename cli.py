import argparse
import subprocess


def load_data(path):
    command = ["poetry", "run", "python", "src/load_data_trainings.py", "--path", path]

    subprocess.run(command)


def train_model(lines=None):
    command = ["poetry", "run", "python", "src/train_model.py"]
    if lines:
        command.append("--lines")
        command.append(str(lines))
    subprocess.run(command)


def summarize_results():
    command = ["poetry", "run", "python", "src/summarize_results.py"]
    subprocess.run(command)


def main():
    parser = argparse.ArgumentParser(description="Code Generation CLI")
    subparsers = parser.add_subparsers(dest="command")

    load_parser = subparsers.add_parser("load_data", help="Load data into the database")
    load_parser.add_argument(
        "--path", type=str, required=True, help="Path to the dataset file"
    )

    train_parser = subparsers.add_parser(
        "train_model", help="Run the training application"
    )
    train_parser.add_argument("--lines", type=int, help="Number of lines to process")

    subparsers.add_parser("summarize", help="Summarize the results")

    args = parser.parse_args()

    if args.command == "load_data":
        load_data(args.path)
    elif args.command == "train_model":
        train_model(args.lines)
    elif args.command == "summarize":
        summarize_results()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
