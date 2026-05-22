# Evaluation module for chatbot performance
# Uses confusion matrix (TP, FP, TN, FN) for accurate metrics.
#
# CSV format: timestamp, user_query, chatbot_response, feedback, user_email, confidence_score
#
# Ground truth (actual label):  feedback column   -> "yes" = Actual Positive, "no" = Actual Negative
# Predicted label:              confidence_score   -> >= THRESHOLD = Predicted Positive, < THRESHOLD = Predicted Negative
#
# Confusion Matrix:
#                        Predicted Positive          Predicted Negative
# Actual Positive        True Positive  (TP)        False Negative (FN)
# Actual Negative        False Positive (FP)        True Negative  (TN)

import os
import csv

FB_FILE = os.path.join(os.path.dirname(__file__), 'feedback.csv')
CONFIDENCE_THRESHOLD = 0.70  # 70% threshold for predicted yes/no


def evaluate():
    """
    Evaluate chatbot performance based on feedback.csv.
    Reads feedback (ground truth) and confidence_score (prediction).
    Returns dictionary with TP, FP, TN, FN counts and total.
    """
    if not os.path.exists(FB_FILE):
        return {"total": 0, "yes": 0, "no": 0, "tp": 0, "fp": 0, "tn": 0, "fn": 0}

    yes = 0       # total positive feedback
    no = 0        # total negative feedback
    total = 0
    tp = 0        # True Positives
    fp = 0        # False Positives
    tn = 0        # True Negatives
    fn = 0        # False Negatives

    with open(FB_FILE, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        if reader.fieldnames is None:
            return {"total": 0, "yes": 0, "no": 0, "tp": 0, "fp": 0, "tn": 0, "fn": 0}

        for row in reader:
            if not row:
                continue

            # --- Ground truth from user feedback ---
            feedback_val = (row.get('feedback') or '').strip().lower()
            if not feedback_val:
                continue

            # --- Confidence score from chatbot ---
            try:
                confidence = float(row.get('confidence_score', 0) or 0)
            except (ValueError, TypeError):
                confidence = 0.0

            total += 1

            # Determine actual label from feedback
            if feedback_val in ('yes', 'y', '1', 'true'):
                actual_positive = True
                yes += 1
            elif feedback_val in ('no', 'n', '0', 'false'):
                actual_positive = False
                no += 1
            else:
                continue  # skip unrecognised feedback values

            # Determine predicted label from confidence threshold
            predicted_positive = confidence >= CONFIDENCE_THRESHOLD

            # Populate confusion matrix
            if actual_positive and predicted_positive:
                tp += 1      # Correct: chatbot was confident AND user confirmed correct
            elif actual_positive and not predicted_positive:
                fn += 1      # Missed:  user said correct BUT chatbot was NOT confident
            elif not actual_positive and predicted_positive:
                fp += 1      # Wrong:   chatbot was confident BUT user said incorrect
            else:
                tn += 1      # Correct: chatbot was NOT confident AND user confirmed incorrect

    return {
        "total": total,
        "yes": yes,
        "no": no,
        "tp": tp,
        "fp": fp,
        "tn": tn,
        "fn": fn
    }


def metrics():
    """
    Compute accuracy, precision, recall, and F1 score
    using the confusion matrix (TP, FP, TN, FN).

    Accuracy  = (TP + TN) / (TP + TN + FP + FN)
    Precision = TP / (TP + FP)
    Recall    = TP / (TP + FN)
    F1        = 2 * Precision * Recall / (Precision + Recall)
    """
    results = evaluate()
    total = results["total"]
    tp = results["tp"]
    fp = results["fp"]
    tn = results["tn"]
    fn = results["fn"]

    if total == 0:
        return {"accuracy": 0, "precision": 0, "recall": 0, "f1": 0}

    # Accuracy: overall correctness
    accuracy = (tp + tn) / (tp + tn + fp + fn) if (tp + tn + fp + fn) > 0 else 0

    # Precision: of all predicted positives, how many were actually correct
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0

    # Recall: of all actual positives, how many were correctly predicted
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0

    # F1 Score: harmonic mean of precision and recall
    f1 = (2 * precision * recall) / (precision + recall) if (precision + recall) > 0 else 0

    return {
        "accuracy": round(accuracy, 4),
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "f1": round(f1, 4)
    }


# Backwards-compatible alias
evaluate_feedback_csv = evaluate
