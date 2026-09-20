from pathlib import Path
from PIL import Image

# Index position = the digit prefix in the filename (0_0.jpg -> "Bread")
categories = [
    "Bread",
    "Dairy product",
    "Dessert",
    "Egg",
    "Fried food",
    "Meat",
    "Noodles-Pasta",
    "Rice",
    "Seafood",
    "Soup",
    "Vegetable-Fruit",
]

data_splits = ["training", "evaluation", "validation"]
size = (128, 128)               # target size required
batch_per_category = 100         # small dev dataset

# parents[2] is the repo root.
# Resolving from the file (not the working directory) means the script runs correctly 
# no matter which folder you launch it from.
root = Path(__file__).resolve().parents[2]
raw = root / "data" / "food11_raw"
processed = root / "data" / "food11_processed"
mini = root / "data" / "food11_processed_mini"

def process_split(split):
    src = raw / split

    # Tracks how many images each category has contributed to the mini set
    counts = {name: 0 for name in categories}

    # Create the category subfolders up front, for both outputs.
    # one folder per class.
    for category in categories:
        (processed / split / category).mkdir(parents=True, exist_ok=True)
        (mini / split / category).mkdir(parents=True, exist_ok=True)

    # sorted() keeps the same order every time (run reproducible)
    for path in sorted(src.glob("*.jpg")):
        try:
            # "3_128.jpg" -> 3 -> "Egg"
            label = int(path.name.split("_")[0])
        except ValueError:
            print(f"skipping {path.name}: no category prefix")
            continue

        category = categories[label]
        
        with Image.open(path) as img:
            # convert("RGB") normalises grayscale/CMYK images that would
            # otherwise raise an error when saved as JPEG
            img = img.convert("RGB").resize(size, Image.BILINEAR)

            # Full processed dataset
            img.save(processed / split / category / path.name, quality=90)

            # Same resized image reused for the mini set
            if counts[category] < batch_per_category:
                img.save(mini / split / category / path.name, quality=90)
                counts[category] += 1

    total = sum(len(list((processed / split / c).glob("*.jpg"))) for c in categories)
    print(f"{split}: {total} images processed, {sum(counts.values())} in mini")

def main():
    for split in data_splits:
        process_split(split)

# Only runs when executed directly, not when imported by another module
if __name__ == "__main__":
    main()