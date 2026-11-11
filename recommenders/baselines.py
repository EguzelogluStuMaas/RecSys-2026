import pandas as pd
import numpy as np


class PopularityBaseline:
    """Recommend most popular items by rating count."""

    def __init__(self, books_df):
        self.books_df = books_df

    def recommend(self, n_recommendations=10, exclude_items=None):
        """Get top N items by popularity (ratings count)."""
        if exclude_items is None:
            exclude_items = set()

        candidates = self.books_df[~self.books_df["book_id"].isin(exclude_items)].copy()
        top_items = candidates.nlargest(n_recommendations, "ratings_count")

        return top_items["book_id"].tolist()


class AverageRatingBaseline:
    """Recommend items with highest average ratings."""

    def __init__(self, books_df):
        self.books_df = books_df

    def recommend(self, n_recommendations=10, exclude_items=None):
        """Get top N items by average rating."""
        if exclude_items is None:
            exclude_items = set()

        candidates = self.books_df[~self.books_df["book_id"].isin(exclude_items)].copy()
        top_items = candidates.nlargest(n_recommendations, "average_rating")

        return top_items["book_id"].tolist()


class RandomBaseline:
    """Recommend random items."""

    def __init__(self, books_df, random_state=42):
        self.books_df = books_df
        self.random_state = random_state

    def recommend(self, n_recommendations=10, exclude_items=None):
        """Get N random items."""
        if exclude_items is None:
            exclude_items = set()

        candidates = self.books_df[~self.books_df["book_id"].isin(exclude_items)].copy()
        random_items = candidates.sample(
            n=min(n_recommendations, len(candidates)),
            random_state=self.random_state
        )

        return random_items["book_id"].tolist()
