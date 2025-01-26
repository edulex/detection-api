def normalize_score(score, min_value, max_value):
    """
    Normalize a score to a 0-1 range.
    """
    return (score - min_value) / (max_value - min_value)

def fuzzy_classification(score):
    """
    Assign fuzzy membership based on normalized score.
    """
    if score >= 0.7:
        return 1.0  # Strong indication of dyslexia
    elif 0.3 <= score < 0.7:
        return 0.5  # Uncertain
    else:
        return 0.0  # No indication of dyslexia

def cumulative_assessment(results):
    """
    Perform the cumulative dyslexia assessment.
    
    Args:
        results (dict): A dictionary containing normalized test results.

    Returns:
        dict: Cumulative score and final classification.
    """
    # Base weights for each test
    weights = {
        "eye_tracking": 0.3,
        "handwriting": 0.25,
        "phonetics": 0.2,
        "questionnaire": 0.15,
        "dictation": 0.1,
    }
    
    # Step 1: Fuzzy classification and weighted voting
    fuzzy_scores = {test: fuzzy_classification(score) for test, score in results.items()}
    vote_1 = sum(weights[test] * score for test, score in fuzzy_scores.items())  # Dyslexia
    vote_0 = sum(weights[test] * (1 - score) for test, score in fuzzy_scores.items())  # No dyslexia

    dominant_class = 1 if vote_1 > vote_0 else 0

    # Step 2: Penalize inconsistent tests
    adjusted_weights = weights.copy()
    for test, score in fuzzy_scores.items():
        if (score > 0.5 and dominant_class == 0) or (score <= 0.5 and dominant_class == 1):
            adjusted_weights[test] *= 0.5  # Penalize inconsistent tests

    # Step 3: Recalculate cumulative score
    cumulative_score = sum(adjusted_weights[test] * results[test] for test in results.keys())

    # Step 4: Interpret cumulative score
    if cumulative_score >= 0.7:
        final_class = "Strong indication of dyslexia"
    elif cumulative_score >= 0.4:
        final_class = "Moderate indication of dyslexia"
    else:
        final_class = "No indication of dyslexia"

    return {
        "cumulative_score": cumulative_score,
        "final_class": final_class,
        "dominant_class": dominant_class,
    }
