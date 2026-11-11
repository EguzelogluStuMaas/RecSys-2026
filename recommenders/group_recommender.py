import numpy as np
import pandas as pd


class GroupRecommender:
    """Group recommendation strategies for combining individual preferences."""

    def __init__(self, individual_recommender):
        self.recommender = individual_recommender

    def average_strategy(self, user_ids, n_recommendations=10, exclude_items=None):
        """Average aggregation: rank items by mean predicted rating."""
        if exclude_items is None:
            exclude_items = set()

        # Get all items
        all_items = self.recommender.item_idx_map.index.tolist()
        candidate_items = [item for item in all_items if item not in exclude_items]

        # Collect predictions from all users
        all_predictions = {}
        for user_id in user_ids:
            preds = self.recommender.predict(user_id, candidate_items)
            for item_id, rating in preds.items():
                if item_id not in all_predictions:
                    all_predictions[item_id] = []
                all_predictions[item_id].append(rating)

        # Calculate average ratings
        avg_ratings = {}
        for item_id, ratings in all_predictions.items():
            avg_ratings[item_id] = np.mean(ratings)

        # Get top N
        avg_series = pd.Series(avg_ratings)
        top_items = avg_series.nlargest(n_recommendations)

        return top_items

    def least_misery_strategy(self, user_ids, n_recommendations=10, exclude_items=None):
        """Least Misery aggregation: rank items by minimum predicted rating."""
        if exclude_items is None:
            exclude_items = set()

        # Get all items
        all_items = self.recommender.item_idx_map.index.tolist()
        candidate_items = [item for item in all_items if item not in exclude_items]

        # Collect predictions from all users
        all_predictions = {}
        for user_id in user_ids:
            preds = self.recommender.predict(user_id, candidate_items)
            for item_id, rating in preds.items():
                if item_id not in all_predictions:
                    all_predictions[item_id] = []
                all_predictions[item_id].append(rating)

        # Calculate minimum ratings
        min_ratings = {}
        for item_id, ratings in all_predictions.items():
            min_ratings[item_id] = np.min(ratings)

        # Get top N
        min_series = pd.Series(min_ratings)
        top_items = min_series.nlargest(n_recommendations)

        return top_items

    def most_pleasure_strategy(self, user_ids, n_recommendations=10, exclude_items=None):
        """Most Pleasure aggregation: rank items by maximum predicted rating."""
        if exclude_items is None:
            exclude_items = set()

        # Get all items
        all_items = self.recommender.item_idx_map.index.tolist()
        candidate_items = [item for item in all_items if item not in exclude_items]

        # Collect predictions from all users
        all_predictions = {}
        for user_id in user_ids:
            preds = self.recommender.predict(user_id, candidate_items)
            for item_id, rating in preds.items():
                if item_id not in all_predictions:
                    all_predictions[item_id] = []
                all_predictions[item_id].append(rating)

        # Calculate maximum ratings
        max_ratings = {}
        for item_id, ratings in all_predictions.items():
            max_ratings[item_id] = np.max(ratings)

        # Get top N
        max_series = pd.Series(max_ratings)
        top_items = max_series.nlargest(n_recommendations)

        return top_items
