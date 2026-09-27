import argparse
from pathlib import Path

import mlflow
import mlflow.pytorch
import torch
from torch import nn
from torch.utils.data import DataLoader
from torchvision import datasets, models, transforms

# __file__ is src/food11/train.py, so parents[2] is the repo root
ROOT = Path(__file__).resolve().parents[2]
DATASETS = {
    "processed": ROOT / "data" / "food11_processed",
    "mini": ROOT / "data" / "food11_processed_mini",
}
NUM_CLASSES = 11

# Images are already 128x128 from data.py: just convert to tensors and
# normalise with the ImageNet statistics the pretrained resnet18 expects
TRANSFORM = transforms.Compose([
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
])


def parse_args():
    parser = argparse.ArgumentParser(description="Train resnet18 on Food-11")
    parser.add_argument("--dataset", choices=["processed", "mini"], default="mini")
    parser.add_argument("--epochs", type=int, default=5)
    parser.add_argument("--lr", type=float, default=0.001)
    parser.add_argument("--batch-size", type=int, default=32)  # stored as args.batch_size
    return parser.parse_args()


def make_loader(split_dir, batch_size, shuffle):
    # ImageFolder labels each image by the name of its category subfolder
    dataset = datasets.ImageFolder(split_dir, transform=TRANSFORM)
    return DataLoader(dataset, batch_size=batch_size, shuffle=shuffle)


def build_model():
    # Pretrained resnet18 with its 1000-class ImageNet head swapped for an 11-class one
    model = models.resnet18(weights=models.ResNet18_Weights.DEFAULT)
    model.fc = nn.Linear(model.fc.in_features, NUM_CLASSES)
    return model


def train_one_epoch(model, loader, criterion, optimizer, device):
    model.train()
    total_loss, total = 0.0, 0
    for images, labels in loader:
        images, labels = images.to(device), labels.to(device)
        optimizer.zero_grad()
        loss = criterion(model(images), labels)
        loss.backward()
        optimizer.step()
        # loss is a batch mean, so weight it by batch size for a true epoch average
        total_loss += loss.item() * images.size(0)
        total += images.size(0)
    return total_loss / total


def evaluate(model, loader, criterion, device):
    model.eval()
    total_loss, correct, total = 0.0, 0, 0
    with torch.no_grad():  # no gradients needed when only evaluating
        for images, labels in loader:
            images, labels = images.to(device), labels.to(device)
            outputs = model(images)
            total_loss += criterion(outputs, labels).item() * images.size(0)
            correct += (outputs.argmax(dim=1) == labels).sum().item()
            total += images.size(0)
    return total_loss / total, correct / total


def main():
    args = parse_args()
    data_dir = DATASETS[args.dataset]
    device = "cuda" if torch.cuda.is_available() else "cpu"

    train_loader = make_loader(data_dir / "training", args.batch_size, shuffle=True)
    val_loader = make_loader(data_dir / "validation", args.batch_size, shuffle=False)
    test_loader = make_loader(data_dir / "evaluation", args.batch_size, shuffle=False)

    model = build_model().to(device)
    criterion = nn.CrossEntropyLoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=args.lr)

    # Where the tracking server is, and which experiment to log into
    mlflow.set_tracking_uri("http://127.0.0.1:5000")
    mlflow.set_experiment("food11")

    with mlflow.start_run():
        # Params: logged once at the start, fixed for the whole run
        mlflow.log_params(vars(args))

        for epoch in range(1, args.epochs + 1):
            train_loss = train_one_epoch(model, train_loader, criterion, optimizer, device)
            val_loss, val_accuracy = evaluate(model, val_loader, criterion, device)

            # Metrics: logged every epoch; step=epoch is the x-axis of the charts
            mlflow.log_metric("train_loss", train_loss, step=epoch)
            mlflow.log_metric("val_loss", val_loss, step=epoch)
            mlflow.log_metric("val_accuracy", val_accuracy, step=epoch)
            print(f"epoch {epoch}/{args.epochs}  train_loss={train_loss:.4f}  "
                  f"val_loss={val_loss:.4f}  val_accuracy={val_accuracy:.4f}")

        # Final score on the held-out "evaluation" split, then save the model
        _, test_accuracy = evaluate(model, test_loader, criterion, device)
        mlflow.log_metric("test_accuracy", test_accuracy)
        print(f"test_accuracy={test_accuracy:.4f}")

        mlflow.pytorch.log_model(model, "model", serialization_format="pickle")


# Only runs when executed directly, not when imported
if __name__ == "__main__":
    main()