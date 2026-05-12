# Evaluation module for chatbot performance

import os
import csv

FB_FILE = os.path.join(os.path.dirname(__file__), 'feedback.csv')

def evaluate():
    """
    Evaluate chatbot performance based on feedback.csv.
    Counts 'helpful' vs 'not helpful' responses.
    Returns dictionary with totals.
    """
    if not os.path.exists(FB_FILE):
        return {"total": 0, "yes": 0, "no": 0}

    yes = 0
    no = 0
    total = 0

    with open(FB_FILE, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        if reader.fieldnames is None:
            return {"total": 0, "yes": 0, "no": 0}
        
        for row in reader:
            if not row:
                continue
            # Read feedback from 'feedback' column (case-insensitive)
            val = (row.get('feedback') or '').strip().lower()
            if not val:
                continue
            total += 1
            if val in ('yes', 'y', '1', 'true'):
                yes += 1
            elif val in ('no', 'n', '0', 'false'):
                no += 1

    return {"total": total, "yes": yes, "no": no}


def metrics():
    """
    Compute accuracy, precision, recall, and F1 score
    based on evaluation results.
    """
    results = evaluate()
    total = results["total"]
    yes = results["yes"]
    no = results["no"]

    if total == 0:
        return {"accuracy": 0, "precision": 0, "recall": 0, "f1": 0}

    # Treat 'yes' as positive, 'no' as negative
    accuracy = (yes + no) / total  # always 1 if only yes/no
    precision = yes / (yes + no) if (yes + no) > 0 else 0
    recall = yes / total if total > 0 else 0
    f1 = (2 * precision * recall) / (precision + recall) if (precision + recall) > 0 else 0

    return {
        "accuracy": round(accuracy, 4),
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "f1": round(f1, 4)
    }


# Backwards-compatible alias
evaluate_feedback_csv = evaluate
