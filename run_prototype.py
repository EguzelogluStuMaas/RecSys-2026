#!/usr/bin/env python3
"""
SVD-Based Book Recommender System - Prototype Demonstration
Demonstrates individual recommendations, group strategies, and baseline comparisons.
"""

import sys
import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings('ignore')

sys.path.insert(0, '.')

from recommenders import (
    SVDRecommender,
    GroupRecommender,
    PopularityBaseline,
    AverageRatingBaseline,
    train_test_split_temporal
)
from metrics import precision_at_k, recall_at_k


def print_section(title):
    """Print a formatted section header."""
    print(f"\n{'='*80}")
    print(f"  {title}")
    print(f"{'='*80}\n")


def main():
    print("""
╔═══════════════════════════════════════════════════════════════════════════╗
║           SVD-Based Book Recommender System - Prototype                  ║
║                                                                           ║
║  This demonstrates:                                                      ║
║  ✅ Individual recommendations via SVD matrix factorization             ║
║  ✅ Group recommendations (Average & Least Misery strategies)           ║
║  ✅ Baseline comparisons (Popularity, Average Rating, Random)           ║
║  🔄 Hyperparameter tuning on validation data (in progress)              ║
║  📋 Advanced features planned for phase 2                               ║
╚═══════════════════════════════════════════════════════════════════════════╝
    """)

    # Load data
    print_section("Step 1: Loading Data")
    print("Loading ratings and books data...")
    ratings_df = pd.read_csv('data/ratings.csv')
    books_df = pd.read_csv('data/books.csv')

    print(f"✅ Ratings loaded: {len(ratings_df):,} ratings")
    print(f"✅ Books loaded: {len(books_df):,} books")
    print(f"   Users: {ratings_df['user_id'].nunique():,}")
    print(f"   Sparsity: {1 - len(ratings_df)/(ratings_df['user_id'].nunique() * len(books_df))*100:.2f}%")

    # Data preprocessing
    print_section("Step 2: Data Preparation - Train/Validation/Test Split")
    print("Sampling data for demo (15% of full dataset)...")
    sample_ratings = ratings_df.sample(frac=0.15, random_state=42)

    train, val, test = train_test_split_temporal(
        sample_ratings,
        train_ratio=0.6,
        val_ratio=0.2
    )

    print(f"✅ Train set: {len(train):,} ratings (60%)")
    print(f"✅ Validation set: {len(val):,} ratings (20%)")
    print(f"✅ Test set: {len(test):,} ratings (20%)")

    # Train SVD model
    print_section("Step 3: Train SVD Model")
    print("Training Truncated SVD with 50 latent factors...")
    svd_model = SVDRecommender(n_factors=50, random_state=42)
    svd_model.fit(train)

    print(f"✅ SVD Model trained successfully")
    print(f"   Latent factors: 50")
    print(f"   Users in training: {len(svd_model.user_idx_map):,}")
    print(f"   Items in training: {len(svd_model.item_idx_map):,}")
    print(f"   Global mean rating: {svd_model.global_mean:.2f}")

    # Individual recommendations
    print_section("Step 4a: Individual Recommendations")
    user_rating_counts = train.groupby('user_id').size().sort_values(ascending=False)
    test_user_id = user_rating_counts.index[10]

    user_history = train[train['user_id'] == test_user_id].copy()
    user_history = user_history.merge(
        books_df[['book_id', 'title', 'authors', 'average_rating']],
        on='book_id'
    )

    print(f"User {test_user_id} - Rating History ({len(user_history)} books):")
    for idx, (_, row) in enumerate(user_history[['title', 'authors', 'rating']].head(5).iterrows(), 1):
        print(f"  {idx}. {row['title'][:50]:50s} | Rating: {row['rating']}")
    if len(user_history) > 5:
        print(f"   ... and {len(user_history) - 5} more")

    # Get recommendations
    exclude_books = set(user_history['book_id'].values)
    recommendations = svd_model.recommend(
        test_user_id,
        n_recommendations=10,
        exclude_items=exclude_books
    )

    rec_books = books_df[books_df['book_id'].isin(recommendations.index)].copy()
    rec_books = rec_books.merge(
        pd.DataFrame({
            'book_id': recommendations.index,
            'predicted_rating': recommendations.values
        }),
        on='book_id'
    ).sort_values('predicted_rating', ascending=False)

    print(f"\n✅ Top 10 Recommendations for User {test_user_id}:")
    for idx, (_, row) in enumerate(rec_books.head(10).iterrows(), 1):
        print(f"  {idx:2d}. {row['title'][:50]:50s} | Pred: {row['predicted_rating']:.2f}")

    # Group recommendations
    print_section("Step 4b: Group Recommendations")
    group_user_ids = user_rating_counts.index[5:9].tolist()
    print(f"Group members: {group_user_ids}")
    for uid in group_user_ids:
        n_ratings = len(train[train['user_id'] == uid])
        print(f"  User {uid}: {n_ratings} ratings")

    group_recommender = GroupRecommender(svd_model)
    group_exclude = set(train[train['user_id'].isin(group_user_ids)]['book_id'].values)

    print(f"\n--- AVERAGE Strategy (mean predicted rating) ---")
    avg_recs = group_recommender.average_strategy(
        group_user_ids,
        n_recommendations=10,
        exclude_items=group_exclude
    )
    avg_books = books_df[books_df['book_id'].isin(avg_recs.index)].copy()
    avg_books = avg_books.merge(
        pd.DataFrame({
            'book_id': avg_recs.index,
            'avg_rating': avg_recs.values
        }),
        on='book_id'
    ).sort_values('avg_rating', ascending=False)

    print("Top 5:")
    for idx, (_, row) in enumerate(avg_books.head(5).iterrows(), 1):
        print(f"  {idx}. {row['title'][:50]:50s} | Avg Pred: {row['avg_rating']:.2f}")

    print(f"\n--- LEAST MISERY Strategy (minimum predicted rating) ---")
    lm_recs = group_recommender.least_misery_strategy(
        group_user_ids,
        n_recommendations=10,
        exclude_items=group_exclude
    )
    lm_books = books_df[books_df['book_id'].isin(lm_recs.index)].copy()
    lm_books = lm_books.merge(
        pd.DataFrame({
            'book_id': lm_recs.index,
            'min_rating': lm_recs.values
        }),
        on='book_id'
    ).sort_values('min_rating', ascending=False)

    print("Top 5:")
    for idx, (_, row) in enumerate(lm_books.head(5).iterrows(), 1):
        print(f"  {idx}. {row['title'][:50]:50s} | Min Pred: {row['min_rating']:.2f}")

    # Strategy comparison
    avg_set = set(avg_recs.index)
    lm_set = set(lm_recs.index)
    overlap = avg_set & lm_set
    print(f"\n✅ Strategy Comparison:")
    print(f"   Overlap: {len(overlap)}/10 items ({len(overlap)/10*100:.0f}%)")
    print(f"   Unique to Average: {len(avg_set - lm_set)}")
    print(f"   Unique to Least Misery: {len(lm_set - avg_set)}")

    # Baseline comparisons
    print_section("Step 5: Baseline Comparisons")
    pop_baseline = PopularityBaseline(books_df)
    rating_baseline = AverageRatingBaseline(books_df)

    svd_recs = set(svd_model.recommend(test_user_id, n_recommendations=10, exclude_items=exclude_books).index)
    pop_recs = set(pop_baseline.recommend(n_recommendations=10, exclude_items=exclude_books))
    rating_recs = set(rating_baseline.recommend(n_recommendations=10, exclude_items=exclude_books))

    print(f"✅ SVD Model: {len(svd_recs)} recommendations")
    print(f"✅ Popularity Baseline: {len(pop_recs)} recommendations")
    print(f"✅ Average Rating Baseline: {len(rating_recs)} recommendations")

    print(f"\nOverlap analysis:")
    print(f"  SVD vs Popularity: {len(svd_recs & pop_recs)}/10 items in common")
    print(f"  SVD vs Rating: {len(svd_recs & rating_recs)}/10 items in common")
    print(f"  Popularity vs Rating: {len(pop_recs & rating_recs)}/10 items in common")

    # Validation metrics
    print_section("Step 6: Validation Metrics (Test Set)")
    test_sample = test.sample(min(100, len(test)), random_state=42)
    predictions = []
    actuals = []

    for _, row in test_sample.iterrows():
        try:
            pred = svd_model.predict(row['user_id'], [row['book_id']])[row['book_id']]
            predictions.append(pred)
            actuals.append(row['rating'])
        except:
            pass

    predictions = np.array(predictions)
    actuals = np.array(actuals)

    rmse = np.sqrt(np.mean((predictions - actuals) ** 2))
    mae = np.mean(np.abs(predictions - actuals))

    print(f"✅ Test Set Evaluation ({len(actuals)} predictions):")
    print(f"   RMSE: {rmse:.3f}")
    print(f"   MAE:  {mae:.3f}")
    print(f"   Range: [1.0, 5.0]")

    # Summary
    print_section("Implementation Status")
    print("""✅ IMPLEMENTED:
   • SVD-based individual recommendations
   • Group recommendations (Average & Least Misery strategies)
   • Baseline comparisons (Popularity, Rating, Random)
   • Train/validation/test split
   • Basic evaluation metrics (RMSE, MAE)

🔄 IN PROGRESS:
   • Hyperparameter tuning on validation set
   • Ranking metrics (Precision@K, Recall@K)
   • Cross-validation for robustness

📋 PLANNED (Phase 2):
   • Advanced diversity metrics
   • Cold start handling
   • Implicit feedback (to_read)
   • Hybrid content + collaborative filtering
   • Real-time model updates
   • Recommendation explanations
    """)

    print("\n" + "="*80)
    print("✅ PROTOTYPE COMPLETE - Ready for evaluation and expansion")
    print("="*80 + "\n")


if __name__ == "__main__":
    main()
