"""Titanicの生存者を予測する機械学習モデル。"""

import argparse
import pickle
from pathlib import Path
from typing import Any

import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder


FEATURE_COLUMNS = [
    "Pclass",
    "Sex",
    "Age",
    "SibSp",
    "Parch",
    "Fare",
    "Embarked",
]
TARGET_COLUMN = "Survived"


def find_default_data_path() -> Path | None:
    """よく使われる場所からTitanic CSVを探す。"""
    candidates = [
        Path(__file__).resolve().parent / "Titanic-Dataset.csv",
        Path.home() / "Downloads" / "archive (1)" / "Titanic-Dataset.csv",
    ]
    return next((path for path in candidates if path.exists()), None)


def build_preprocessor() -> ColumnTransformer:
    """Titanic特徴量用の欠損値処理とカテゴリ変換を返す。"""
    numeric_features = ["Pclass", "Age", "SibSp", "Parch", "Fare"]
    categorical_features = ["Sex", "Embarked"]

    numeric_pipeline = Pipeline(
        steps=[("imputer", SimpleImputer(strategy="median"))]
    )
    categorical_pipeline = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="most_frequent")),
            ("onehot", OneHotEncoder(handle_unknown="ignore")),
        ]
    )
    preprocessor = ColumnTransformer(
        transformers=[
            ("numeric", numeric_pipeline, numeric_features),
            ("categorical", categorical_pipeline, categorical_features),
        ]
    )
    return ColumnTransformer(
        transformers=[
            ("numeric", numeric_pipeline, numeric_features),
            ("categorical", categorical_pipeline, categorical_features),
        ]
    )


def build_model() -> Pipeline:
    """既定のRandom Forestモデルを返す。"""
    classifier = RandomForestClassifier(
        n_estimators=300,
        max_depth=6,
        min_samples_leaf=2,
        random_state=42,
        class_weight="balanced",
        n_jobs=-1,
    )
    return Pipeline(steps=[("preprocessor", build_preprocessor()), ("classifier", classifier)])


def load_training_data(csv_path: str | Path) -> tuple[pd.DataFrame, pd.Series]:
    """CSVを読み込み、学習用の特徴量と目的変数を返す。"""
    data = pd.read_csv(csv_path)
    required_columns = set(FEATURE_COLUMNS + [TARGET_COLUMN])
    missing_columns = required_columns.difference(data.columns)
    if missing_columns:
        missing = ", ".join(sorted(missing_columns))
        raise ValueError(f"CSVに必要な列がありません: {missing}")
    return data[FEATURE_COLUMNS].copy(), data[TARGET_COLUMN].astype(int)


def train_and_evaluate(
    csv_path: str | Path, model_path: str | Path | None = None
) -> dict[str, Any]:
    """モデルを学習し、ホールドアウトデータで評価する。"""
    features, target = load_training_data(csv_path)
    train_features, test_features, train_target, test_target = train_test_split(
        features,
        target,
        test_size=0.2,
        random_state=42,
        stratify=target,
    )
    model = build_model()
    model.fit(train_features, train_target)
    predictions = model.predict(test_features)
    result = {
        "model": model,
        "accuracy": accuracy_score(test_target, predictions),
        "confusion_matrix": confusion_matrix(test_target, predictions),
        "classification_report": classification_report(
            test_target, predictions, target_names=["Not survived", "Survived"]
        ),
        "test_size": len(test_target),
    }
    if model_path is not None:
        with Path(model_path).open("wb") as file:
            pickle.dump(model, file)
    return result


def predict_one(model: Pipeline, passenger: dict[str, Any]) -> tuple[int, float]:
    """1人分の乗客データから予測クラスと生存確率を返す。"""
    features = pd.DataFrame([passenger], columns=FEATURE_COLUMNS)
    prediction = int(model.predict(features)[0])
    probability = float(model.predict_proba(features)[0][1])
    return prediction, probability


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Titanic Survived予測モデル")
    parser.add_argument(
        "data",
        type=Path,
        nargs="?",
        help="学習に使うTitanic-Dataset.csv（省略時は自動検索）",
    )
    parser.add_argument(
        "--model-out",
        type=Path,
        default=Path("titanic_model.pkl"),
        help="学習済みモデルの保存先（既定: titanic_model.pkl）",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    data_path = args.data or find_default_data_path()
    if data_path is None:
        raise SystemExit(
            "Titanic-Dataset.csvが見つかりません。CSVのパスを指定してください。"
        )
    result = train_and_evaluate(data_path, args.model_out)
    print(f"データ: {data_path}")
    print(f"テストデータ: {result['test_size']}件")
    print(f"正解率: {result['accuracy']:.3f}")
    print("\n混同行列（行: 実際、列: 予測）")
    print(result["confusion_matrix"])
    print("\n分類レポート")
    print(result["classification_report"])
    print(f"学習済みモデルを保存しました: {args.model_out}")


if __name__ == "__main__":
    main()