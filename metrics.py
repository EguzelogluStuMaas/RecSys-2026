#these are metrics to use for phase 1
def precision_at_k(recommended_items, relevant_items, k):
    recommended_at_k = recommended_items[:k]
    relevant_and_recommended = set(recommended_at_k) & set(relevant_items)
    return len(relevant_and_recommended) / k if k > 0 else 0

def recall_at_k(recommended_items, relevant_items, k):
    recommended_at_k = recommended_items[:k]
    relevant_and_recommended = set(recommended_at_k) & set(relevant_items)
    return len(relevant_and_recommended) / len(relevant_items) if relevant_items else 0,
