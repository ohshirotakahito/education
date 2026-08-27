"""複数の機械学習アルゴリズムを比較し、最良モデルを保存する。"""

import argparse
import pickle
from pathlib import Path

import pandas as pd
from lightgbm import LGBMClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.calibration import CalibratedClassifierCV
from sklearn.model_selection import StratifiedKFold, cross_validate
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from xgboost import XGBClassifier

from titanic_model import build_preprocessor, load_training_data


def build_candidates() -> dict[str, Pipeline]:
    """比較する分類器を同じ前処理パイプラインに組み込む。"""
    classifiers = {
        "Logistic Regression": LogisticRegression(
            max_iter=1000, class_weight="balanced", random_state=42
        ),
        "Random Forest": RandomForestClassifier(
            n_estimators=300,
            max_depth=6,
            min_samples_leaf=2,
            class_weight="balanced",
            random_state=42,
            n_jobs=-1,
        ),
        "SVM": CalibratedClassifierCV(
            SVC(C=1.0, kernel="rbf", class_weight="balanced", random_state=42),
            cv=3,
        ),
        "XGBoost": XGBClassifier(
            n_estimators=300,
            max_depth=3,
            learning_rate=0.05,
            subsample=0.8,
            colsample_bytree=0.8,
            eval_metric="logloss",
            random_state=42,
            n_jobs=-1,
        ),
        "LightGBM": LGBMClassifier(
            n_estimators=300,
            learning_rate=0.03,
            num_leaves=15,
            max_depth=5,
            subsample=0.8,
            colsample_bytree=0.8,
            reg_lambda=1.0,
            verbosity=-1,
            random_state=42,
            n_jobs=-1,
        ),
    }
    return {
        name: Pipeline(
            steps=[("preprocessor", build_preprocessor()), ("classifier", classifier)]
        )
        for name, classifier in classifiers.items()
    }


def compare_models(csv_path: str | Path, metric: str = "accuracy") -> pd.DataFrame:
    """5分割交差検証で比較し、指標の平均値を返す。"""
    features, target = load_training_data(csv_path)
    cross_validation = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    rows = []
    for name, model in build_candidates().items():
        scores = cross_validate(
            model,
            features,
            target,
            cv=cross_validation,
            scoring=["accuracy", "precision", "recall", "f1"],
        )
        rows.append(
            {
                "model": name,
                "accuracy": scores["test_accuracy"].mean(),
                "precision": scores["test_precision"].mean(),
                "recall": scores["test_recall"].mean(),
                "f1": scores["test_f1"].mean(),
                "accuracy_std": scores["test_accuracy"].std(),
            }
        )
    return pd.DataFrame(rows).sort_values(metric, ascending=False).reset_index(drop=True)


def main() -> None:
    parser = argparse.ArgumentParser(description="Titanicモデルを複数アルゴリズムで比較")
    parser.add_argument("data", type=Path, help="Titanic-Dataset.csvのパス")
    parser.add_argument(
        "--metric",
        choices=["accuracy", "f1", "precision", "recall"],
        default="accuracy",
        help="最良モデルを決める指標（既定: accuracy）",
    )
    parser.add_argument(
        "--model-out",
        type=Path,
        default=Path("best_titanic_model.pkl"),
        help="最良モデルの保存先",
    )
    args = parser.parse_args()
    results = compare_models(args.data, args.metric)
    print("5分割交差検証による比較")
    print(results.to_string(index=False, formatters={
        column: "{:.3f}".format
        for column in ["accuracy", "precision", "recall", "f1", "accuracy_std"]
    }))

    best_name = results.iloc[0]["model"]
    best_model = build_candidates()[best_name]
    features, target = load_training_data(args.data)
    best_model.fit(features, target)
    with args.model_out.open("wb") as file:
        pickle.dump(best_model, file)
    print(f"\n最良モデル（{args.metric}基準）: {best_name}")
    print(f"学習済みモデルを保存しました: {args.model_out}")


if __name__ == "__main__":
    main()