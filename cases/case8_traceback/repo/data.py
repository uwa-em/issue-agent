def load_scores(raw):
    scores = {}
    for line in raw.splitlines():
        name, score = line.split(",")
        scores[name] = int(score)
    return scores
