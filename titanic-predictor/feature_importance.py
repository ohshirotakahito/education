"""Titanicモデルの特徴量重要度をPermutation Importanceで調べる。"""

import argparse
from pathlib import Path

import pandas as pd
from sklearn.inspection import permutation_importance
from sklearn.model_selection import train_test_split

from compare_models import build_candidates
from titanic_model import load_training_data


def analyze_feature_importance(csv_path: str | Path) -> pd.DataFrame:
    """XGBoostを学習し、元の特徴量単位の重要度を返す。"""
    features, target = load_training_data(csv_path)
    train_features, test_features, train_target, test_target = train_test_split(
        features, target, test_size=0.2, random_state=42, stratify=target
    )
    model = build_candidates()["XGBoost"]
    model.fit(train_features, train_target)
    result = permutation_importance(
        model,
        test_features,
        test_target,
        scoring="accuracy",
        n_repeats=30,
        random_state=42,
        n_jobs=-1,
    )
    importance = pd.DataFrame(
        {
            "feature": test_features.columns,
            "importance_mean": result.importances_mean,
            "importance_std": result.importances_std,
        }
    )
    return importance.sort_values("importance_mean", ascending=False).reset_index(drop=True)


def main() -> None:
    parser = argparse.ArgumentParser(description="Titanic特徴量重要度を分析")
    parser.add_argument("data", type=Path, help="Titanic-Dataset.csvのパス")
    args = parser.parse_args()
    importance = analyze_feature_importance(args.data)
    print("XGBoostのPermutation Importance（正解率の平均低下）")
    print(
        importance.to_string(
            index=False,
            formatters={
                "importance_mean": "{:.4f}".format,
                "importance_std": "{:.4f}".format,
            },
        )
    )


if __name__ == "__main__":
    main()