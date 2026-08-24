import unittest

from recommender import recommend_size


class RecommenderTests(unittest.TestCase):
    def test_returns_all_sizes_in_rank_order(self):
        result = recommend_size(170, 90, 44, "標準")
        self.assertEqual(len(result), 5)
        self.assertLessEqual(result[0]["score"], result[1]["score"])

    def test_more_ease_does_not_recommend_smaller_size(self):
        order = {"S": 0, "M": 1, "L": 2, "XL": 3, "XXL": 4}
        fitted = recommend_size(170, 90, 44, "すっきり")[0]["size"]
        oversized = recommend_size(170, 90, 44, "オーバーサイズ")[0]["size"]
        self.assertGreaterEqual(order[oversized], order[fitted])

    def test_rejects_invalid_measurement(self):
        with self.assertRaises(ValueError):
            recommend_size(90, 90, 44, "標準")


if __name__ == "__main__":
    unittest.main()
