import argparse
import time


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="WatchDog simulated agent")
    parser.add_argument("--duration", type=int, default=30)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    end_time = time.time() + args.duration
    while time.time() < end_time:
        time.sleep(1)


if __name__ == "__main__":
    main()
