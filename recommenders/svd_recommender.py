import numpy as np
import pandas as pd
from sklearn.decomposition import TruncatedSVD
from sklearn.model_selection import train_test_split


class SVDRecommender:
    """Matrix factorization recommender using Truncated SVD."""

    def __init__(self, n_factors=50, random_state=42):
        self.n_factors = n_factors
        self.random_state = random_state
        self.svd = TruncatedSVD(n_components=n_factors, random_state=random_state)
        self.user_factors = None
        self.item_factors = None
        self.user_idx_map = None
        self.item_idx_map = None
        self.global_mean = None
        self.user_bias = None
        self.item_bias = None

    def fit(self, ratings_df):
        """Fit SVD model on ratings data."""
        # Create user and item mappings
        self.user_idx_map = pd.Series(
            range(ratings_df["user_id"].nunique()),
            index=ratings_df["user_id"].unique()
        )
        self.item_idx_map = pd.Series(
            range(ratings_df["book_id"].nunique()),
            index=ratings_df["book_id"].unique()
        )

        # Create rating matrix
        n_users = len(self.user_idx_map)
        n_items = len(self.item_idx_map)

        user_idx = ratings_df["user_id"].map(self.user_idx_map)
        item_idx = ratings_df["book_id"].map(self.item_idx_map)

        rating_matrix = np.zeros((n_users, n_items))
        rating_matrix[user_idx, item_idx] = ratings_df["rating"].values

        # Calculate global mean and biases
        self.global_mean = ratings_df["rating"].mean()

        # Simple bias calculation
        user_means = {}
        item_means = {}
        for user_id in self.user_idx_map.index:
            user_ratings = ratings_df[ratings_df["user_id"] == user_id]["rating"]
            user_means[user_id] = user_ratings.mean() - self.global_mean if len(user_ratings) > 0 else 0

        for item_id in self.item_idx_map.index:
            item_ratings = ratings_df[ratings_df["book_id"] == item_id]["rating"]
            item_means[item_id] = item_ratings.mean() - self.global_mean if len(item_ratings) > 0 else 0

        self.user_bias = pd.Series(user_means)
        self.item_bias = pd.Series(item_means)

        # Fit SVD on rating matrix (ignoring zeros as implicit feedback)
        # For explicit feedback, we work with the matrix as-is
        self.svd.fit(rating_matrix)
        self.user_factors = self.svd.transform(rating_matrix)
        self.item_factors = self.svd.components_.T

    def predict(self, user_id, item_ids):
        """Predict ratings for a user and list of items."""
        if user_id not in self.user_idx_map.index:
            # Return global mean for unknown users
            return pd.Series(
                [self.global_mean] * len(item_ids),
                index=item_ids
            )

        user_idx = self.user_idx_map[user_id]
        user_factor = self.user_factors[user_idx]

        predictions = {}
        for item_id in item_ids:
            if item_id not in self.item_idx_map.index:
                predictions[item_id] = self.global_mean
            else:
                item_idx = self.item_idx_map[item_id]
                item_factor = self.item_factors[item_idx]
                pred = (self.global_mean +
                        self.user_bias.get(user_id, 0) +
                        self.item_bias.get(item_id, 0) +
                        np.dot(user_factor, item_factor))
                # Clip to valid rating range [1, 5]
                predictions[item_id] = np.clip(pred, 1, 5)

        return pd.Series(predictions)

    def recommend(self, user_id, n_recommendations=10, exclude_items=None):
        """Get top N recommendations for a user."""
        if exclude_items is None:
            exclude_items = set()

        # Get all items
        all_items = self.item_idx_map.index.tolist()

        # Filter out excluded items
        candidate_items = [item for item in all_items if item not in exclude_items]

        # Predict ratings
        predictions = self.predict(user_id, candidate_items)

        # Get top N
        top_items = predictions.nlargest(n_recommendations)

        return top_items


def train_test_split_temporal(ratings_df, train_ratio=0.6, val_ratio=0.2):
    """Split data into train, validation, and test sets."""
    # Sort by user and ensure we have enough data per set
    n_total = len(ratings_df)
    n_train = int(n_total * train_ratio)
    n_val = int(n_total * val_ratio)

    train = ratings_df.iloc[:n_train].copy()
    val = ratings_df.iloc[n_train:n_train + n_val].copy()
    test = ratings_df.iloc[n_train + n_val:].copy()

    return train, val, test
