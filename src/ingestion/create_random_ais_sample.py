import csv
import random
import zipfile
from pathlib import Path


ZIP_PATH = Path("data/raw/public_ais/AIS_2024_01_01.zip")
ZIP_MEMBER = "AIS_2024_01_01.csv"
OUTPUT_PATH = Path("data/raw/public_ais/AIS_2024_01_01_random_sample_500k.csv")

SAMPLE_SIZE = 500_000
RANDOM_SEED = 42


def main() -> None:
    rng = random.Random(RANDOM_SEED)
    reservoir = []

    total_rows = 0

    with zipfile.ZipFile(ZIP_PATH) as zip_file:
        with zip_file.open(ZIP_MEMBER, "r") as compressed_file:
            text_file = (line.decode("utf-8") for line in compressed_file)
            reader = csv.DictReader(text_file)

            fieldnames = reader.fieldnames

            if fieldnames is None:
                raise ValueError("CSV header not found.")

            for row in reader:
                total_rows += 1

                if len(reservoir) < SAMPLE_SIZE:
                    reservoir.append(row)
                else:
                    replacement_index = rng.randint(0, total_rows - 1)

                    if replacement_index < SAMPLE_SIZE:
                        reservoir[replacement_index] = row

                if total_rows % 500_000 == 0:
                    print(f"Rows scanned: {total_rows}")

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    with OUTPUT_PATH.open("w", encoding="utf-8", newline="") as output_file:
        writer = csv.DictWriter(output_file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(reservoir)

    print(f"Random sample created: {OUTPUT_PATH}")
    print(f"Total rows scanned: {total_rows}")
    print(f"Sample rows written: {len(reservoir)}")
    print(f"Random seed: {RANDOM_SEED}")


if __name__ == "__main__":
    main()
