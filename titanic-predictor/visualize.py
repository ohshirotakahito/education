"""Titanicデータと学習モデルの評価結果を画像に可視化する。"""

import argparse
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import pandas as pd
from sklearn.model_selection import train_test_split

from titanic_model import build_model, load_training_data, train_and_evaluate


def plot_survival_rate(data: pd.DataFrame, column: str, axis: plt.Axes) -> None:
    rates = data.groupby(column, observed=True)["Survived"].mean().mul(100)
    rates.plot(kind="bar", ax=axis, color="#2f80ed")
    axis.set_title(f"Survival rate by {column}")
    axis.set_ylabel("Survival rate (%)")
    axis.set_ylim(0, 100)
    axis.tick_params(axis="x", rotation=0)
    for index, value in enumerate(rates):
        axis.text(index, value + 2, f"{value:.1f}%", ha="center")


def plot_age_distribution(data: pd.DataFrame, axis: plt.Axes) -> None:
    axis.hist(
        [data.loc[data["Survived"] == 0, "Age"].dropna(), data.loc[data["Survived"] == 1, "Age"].dropna()],
        bins=20,
        label=["Not survived", "Survived"],
        color=["#e76f51", "#2a9d8f"],
        alpha=0.75,
    )
    axis.set_title("Age distribution")
    axis.set_xlabel("Age")
    axis.set_ylabel("Passengers")
    axis.legend()


def plot_confusion_matrix(matrix, axis: plt.Axes) -> None:
    image = axis.imshow(matrix, cmap="Blues")
    axis.set_title("Confusion matrix")
    axis.set_xlabel("Predicted")
    axis.set_ylabel("Actual")
    axis.set_xticks([0, 1])
    axis.set_xticklabels(["Not survived", "Survived"])
    axis.set_yticks([0, 1])
    axis.set_yticklabels(["Not survived", "Survived"])
    for row in range(2):
        for column in range(2):
            axis.text(column, row, matrix[row, column], ha="center", va="center")
    axis.figure.colorbar(image, ax=axis, fraction=0.046, pad=0.04)


def plot_feature_importance(model, axis: plt.Axes) -> None:
    preprocessor = model.named_steps["preprocessor"]
    classifier = model.named_steps["classifier"]
    names = preprocessor.get_feature_names_out()
    importance = pd.Series(classifier.feature_importances_, index=names).sort_values()
    importance.tail(10).plot(kind="barh", ax=axis, color="#9b5de5")
    axis.set_title("Top feature importance")
    axis.set_xlabel("Importance")
    axis.tick_params(axis="y", labelsize=8)


def create_visualization(csv_path: str | Path, output_path: str | Path) -> None:
    data = pd.read_csv(csv_path)
    features, target = load_training_data(csv_path)
    train_features, _, train_target, _ = train_test_split(
        features, target, test_size=0.2, random_state=42, stratify=target
    )
    model = build_model()
    model.fit(train_features, train_target)
    result = train_and_evaluate(csv_path)

    figure, axes = plt.subplots(2, 3, figsize=(18, 10))
    figure.suptitle(
        f"Titanic analysis | accuracy: {result['accuracy']:.3f} | test size: {result['test_size']}",
        fontsize=16,
    )
    plot_survival_rate(data, "Sex", axes[0, 0])
    plot_survival_rate(data, "Pclass", axes[0, 1])
    plot_age_distribution(data, axes[0, 2])
    plot_confusion_matrix(result["confusion_matrix"], axes[1, 0])
    plot_feature_importance(model, axes[1, 1])
    axes[1, 2].axis("off")
    figure.tight_layout()
    figure.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close(figure)


def main() -> None:
    parser = argparse.ArgumentParser(description="Titanicデータを可視化します")
    parser.add_argument("data", type=Path, help="Titanic-Dataset.csvのパス")
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("titanic_visualizations.png"),
        help="出力画像のパス（既定: titanic_visualizations.png）",
    )
    args = parser.parse_args()
    create_visualization(args.data, args.output)
    print(f"可視化画像を保存しました: {args.output}")


if __name__ == "__main__":
    main()