from data import load_scores

def top_scorer(raw):
    scores = load_scores(raw)
    return max(scores, key=scores.get)
