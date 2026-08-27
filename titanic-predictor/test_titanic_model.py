import tempfile
import unittest
from pathlib import Path

import pandas as pd

from titanic_model import FEATURE_COLUMNS, build_model, load_training_data, predict_one


class TitanicModelTests(unittest.TestCase):
    def make_data(self) -> pd.DataFrame:
        rows = []
        for index in range(20):
            rows.append(
                {
                    "PassengerId": index + 1,
                    "Survived": int(index % 2 == 0),
                    "Pclass": 1 if index % 3 == 0 else 3,
                    "Name": f"Passenger {index}",
                    "Sex": "female" if index % 2 == 0 else "male",
                    "Age": None if index == 2 else 20 + index,
                    "SibSp": 0,
                    "Parch": 0,
                    "Ticket": str(index),
                    "Fare": 10.0 + index,
                    "Cabin": None,
                    "Embarked": "S" if index % 2 else "C",
                }
            )
        return pd.DataFrame(rows)

    def test_pipeline_handles_missing_values_and_predicts(self) -> None:
        data = self.make_data()
        model = build_model()
        model.fit(data[FEATURE_COLUMNS], data["Survived"])
        prediction, probability = predict_one(
            model,
            {
                "Pclass": 1,
                "Sex": "female",
                "Age": None,
                "SibSp": 0,
                "Parch": 0,
                "Fare": 80,
                "Embarked": "C",
            },
        )
        self.assertIn(prediction, (0, 1))
        self.assertGreaterEqual(probability, 0.0)
        self.assertLessEqual(probability, 1.0)

    def test_csv_loader_reports_missing_columns(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "bad.csv"
            pd.DataFrame({"Survived": [0]}).to_csv(path, index=False)
            with self.assertRaises(ValueError):
                load_training_data(path)


if __name__ == "__main__":
    unittest.main()