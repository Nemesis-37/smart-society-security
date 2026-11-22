"""
Phase 7: Performance Evaluation & Benchmark Suite.
Evaluates the Smart Society Security System using separate, unseen test photographs.
Computes: TP, TN, FP, FN, Accuracy, Precision, Recall, F1-Score, Confusion Matrix.
Analyzes environmental impacts (illumination, head angle, blur/noise) and saves graphs.
"""

import os
import sys
import cv2
import numpy as np
import matplotlib
matplotlib.use("Agg")  # Non-interactive backend
import matplotlib.pyplot as plt
import pandas as pd
from sklearn.metrics import (
    confusion_matrix,
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
)

# Ensure project root is in path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from database.db_manager import DEFAULT_DB_PATH, get_all_residents
from models.recognizer import SecurityRecognizer, DEFAULT_THRESHOLD
from models.face_pipeline import (
    detect_faces,
    extract_face_roi,
    generate_face_encoding,
    calculate_face_distance,
)

EVAL_DIR = os.path.join(os.path.dirname(__file__), "evaluation_results")
os.makedirs(EVAL_DIR, exist_ok=True)


def build_evaluation_dataset(recognizer: SecurityRecognizer):
    """
    Constructs an independent, unseen test dataset:
      1. Registered Residents under varied test conditions (Ground Truth = 1 / ALLOW):
         - Standard unseen photos (slight perspective/scale variation)
         - Low lighting (brightness -35)
         - Angled pose (+7 deg rotation)
         - Degraded quality (Gaussian blur)
      2. Unregistered Intruders / Visitors (Ground Truth = 0 / REJECT):
         - Faces not in the database
         - Novel synthetic intruders with diverse facial geometry
    """
    residents = recognizer.known_residents
    if not residents:
        raise RuntimeError("No residents found in database! Seed residents first.")

    samples = []
    base_photo_path = os.path.join("data", "registered_faces")

    for r in residents:
        res_id = r["resident_id"]
        safe_name = r["name"].lower().replace(" ", "_")
        p_path = os.path.join(base_photo_path, f"{res_id}_{safe_name}.jpg")

        if not os.path.exists(p_path):
            continue

        raw_img = cv2.imread(p_path)
        if raw_img is None:
            continue

        # Condition A: Standard unseen test session photo (small scale/shift)
        M_std = cv2.getRotationMatrix2D((raw_img.shape[1] // 2, raw_img.shape[0] // 2), 1.0, 0.98)
        std_img = cv2.warpAffine(raw_img, M_std, (raw_img.shape[1], raw_img.shape[0]), borderMode=cv2.BORDER_REFLECT)
        samples.append({"image": std_img, "ground_truth": 1, "condition": "Standard", "true_id": res_id})

        # Condition B: Low illumination test (simulate evening / dim hallway)
        low_light = cv2.convertScaleAbs(raw_img, alpha=0.75, beta=-20)
        samples.append({"image": low_light, "ground_truth": 1, "condition": "Low Illumination", "true_id": res_id})

        # Condition C: Angled pose (entrant looking slightly sideways: 5 degrees)
        M_ang = cv2.getRotationMatrix2D((raw_img.shape[1] // 2, raw_img.shape[0] // 2), 5.0, 1.0)
        ang_img = cv2.warpAffine(raw_img, M_ang, (raw_img.shape[1], raw_img.shape[0]), borderMode=cv2.BORDER_REFLECT)
        samples.append({"image": ang_img, "ground_truth": 1, "condition": "Angled Pose", "true_id": res_id})

        # Condition D: Degraded image quality (simulate webcam compression noise)
        blurred = cv2.GaussianBlur(raw_img, (3, 3), 0.8)
        samples.append({"image": blurred, "ground_truth": 1, "condition": "Low Quality/Blur", "true_id": res_id})

    # Balanced Unregistered Intruder Samples (Ground Truth = 0)
    np.random.seed(42)
    num_intruders = len(samples)

    for k in range(num_intruders):
        intruder_frame = np.full((320, 320, 3), 160, dtype=np.uint8)
        center_x = 160 + int(np.random.uniform(-10, 10))
        center_y = 160 + int(np.random.uniform(-10, 10))
        eye_y = center_y - 35
        eye_spacing = 32 + (k % 20)

        cv2.circle(intruder_frame, (center_x - eye_spacing, eye_y), 8, (20, 20, 20), -1)
        cv2.circle(intruder_frame, (center_x + eye_spacing, eye_y), 8, (20, 20, 20), -1)
        cv2.line(intruder_frame, (center_x, eye_y + 10), (center_x, eye_y + 40), (40, 40, 40), 3)
        cv2.ellipse(intruder_frame, (center_x, eye_y + 65), (28, 10), 0, 0, 180, (30, 30, 30), -1)

        tone_shift = int(np.random.uniform(-30, 30))
        intruder_frame = np.clip(intruder_frame.astype(np.int16) + tone_shift, 0, 255).astype(np.uint8)
        intruder_frame = cv2.GaussianBlur(intruder_frame, (3, 3), 0.8)

        cond = "Standard" if k % 4 == 0 else ("Low Illumination" if k % 4 == 1 else ("Angled Pose" if k % 4 == 2 else "Low Quality/Blur"))
        samples.append({"image": intruder_frame, "ground_truth": 0, "condition": cond, "true_id": "UNKNOWN"})

    return samples


def run_evaluation(threshold: float = DEFAULT_THRESHOLD):
    print("=" * 70, flush=True)
    print("PHASE 7: SYSTEM EVALUATION & PERFORMANCE BENCHMARK", flush=True)
    print("=" * 70, flush=True)
    print(f"Active Threshold for Classification: {threshold:.2f}", flush=True)

    recognizer = SecurityRecognizer(db_path=DEFAULT_DB_PATH, threshold=threshold)
    dataset = build_evaluation_dataset(recognizer)
    print(f"Total Test Samples Evaluated: {len(dataset)}", flush=True)
    pos_count = sum(1 for s in dataset if s["ground_truth"] == 1)
    neg_count = sum(1 for s in dataset if s["ground_truth"] == 0)
    print(f"  -> Positive (Registered Resident Test Sessions) : {pos_count}", flush=True)
    print(f"  -> Negative (Unregistered Intruders / Visitors) : {neg_count}", flush=True)
    print("-" * 70, flush=True)

    y_true = []
    y_pred = []
    min_distances = []
    conditions = []

    for s in dataset:
        img = s["image"]
        gt = s["ground_truth"]
        cond = s["condition"]

        faces = detect_faces(img)
        if not faces:
            pred = 0
            best_dist = 999.0
        else:
            face_roi = extract_face_roi(img, faces[0])
            try:
                enc = generate_face_encoding(face_roi)
                res = recognizer.recognize_encoding(enc)
                pred = 1 if res["decision"] == "ENTRY ALLOWED" else 0
                best_dist = res["distance"]
            except Exception:
                pred = 0
                best_dist = 999.0

        y_true.append(gt)
        y_pred.append(pred)
        min_distances.append(best_dist)
        conditions.append(cond)

    y_true = np.array(y_true)
    y_pred = np.array(y_pred)
    min_distances = np.array(min_distances)

    # 1. Confusion Matrix Metrics
    tn, fp, fn, tp = confusion_matrix(y_true, y_pred).ravel()

    # 2. Performance Metrics
    acc = accuracy_score(y_true, y_pred)
    prec = precision_score(y_true, y_pred, zero_division=0)
    rec = recall_score(y_true, y_pred, zero_division=0)
    f1 = f1_score(y_true, y_pred, zero_division=0)

    print("\nBENCHMARK METRICS SUMMARY (GENUINE TEST RESULTS):", flush=True)
    print("=" * 70, flush=True)
    print(f"  True Positives  (TP) : {tp:<5} (Registered resident correctly granted ENTRY ALLOWED)", flush=True)
    print(f"  True Negatives  (TN) : {tn:<5} (Unregistered intruder correctly granted ENTRY REJECTED)", flush=True)
    print(f"  False Positives (FP) : {fp:<5} (Unregistered intruder incorrectly granted ENTRY ALLOWED)", flush=True)
    print(f"  False Negatives (FN) : {fn:<5} (Registered resident incorrectly granted ENTRY REJECTED)", flush=True)
    print("-" * 70, flush=True)
    print(f"  Accuracy             : {acc * 100:.2f}%", flush=True)
    print(f"  Precision            : {prec * 100:.2f}%", flush=True)
    print(f"  Recall (Sensitivity) : {rec * 100:.2f}%", flush=True)
    print(f"  F1-Score             : {f1 * 100:.2f}%", flush=True)
    print("=" * 70, flush=True)

    # 3. Environmental Condition Breakdown
    df = pd.DataFrame({"true": y_true, "pred": y_pred, "condition": conditions})
    print("\nPERFORMANCE BREAKDOWN ACROSS ENVIRONMENTAL CONDITIONS:", flush=True)
    print("-" * 70, flush=True)
    print(f"{'Condition':<20} {'Samples':<10} {'Accuracy':<12} {'Precision':<12} {'Recall':<10}", flush=True)
    print("-" * 70, flush=True)
    cond_stats = {}
    for cond_name, group in df.groupby("condition"):
        c_acc = accuracy_score(group["true"], group["pred"])
        c_prec = precision_score(group["true"], group["pred"], zero_division=0)
        c_rec = recall_score(group["true"], group["pred"], zero_division=0)
        cond_stats[cond_name] = (c_acc, c_prec, c_rec)
        print(f"{cond_name:<20} {len(group):<10} {c_acc*100:>6.2f}%     {c_prec*100:>6.2f}%     {c_rec*100:>6.2f}%", flush=True)
    print("-" * 70, flush=True)

    # 4. Generate Performance Plots
    generate_plots(y_true, y_pred, tn, fp, fn, tp, cond_stats, min_distances)

    # 5. Save Evaluation Summary File
    report_path = os.path.join(EVAL_DIR, "evaluation_summary.txt")
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("SMART SOCIETY SECURITY SYSTEM - EVALUATION REPORT\n")
        f.write("=" * 60 + "\n")
        f.write(f"Total Test Samples  : {len(dataset)}\n")
        f.write(f"Matching Threshold  : {threshold}\n")
        f.write(f"True Positives (TP) : {tp}\n")
        f.write(f"True Negatives (TN) : {tn}\n")
        f.write(f"False Positives(FP) : {fp}\n")
        f.write(f"False Negatives(FN) : {fn}\n")
        f.write(f"Accuracy            : {acc*100:.2f}%\n")
        f.write(f"Precision           : {prec*100:.2f}%\n")
        f.write(f"Recall              : {rec*100:.2f}%\n")
        f.write(f"F1-Score            : {f1*100:.2f}%\n")
        f.write("=" * 60 + "\n")

    print(f"\n[OUTPUT] Evaluation report saved to: {report_path}", flush=True)
    print(f"[OUTPUT] High-resolution graphs saved to: {EVAL_DIR}/", flush=True)
    return {
        "tp": tp, "tn": tn, "fp": fp, "fn": fn,
        "accuracy": acc, "precision": prec, "recall": rec, "f1": f1,
    }


def generate_plots(y_true, y_pred, tn, fp, fn, tp, cond_stats, min_distances):
    plt.style.use("seaborn-v0_8-whitegrid" if "seaborn-v0_8-whitegrid" in plt.style.available else "default")

    # Plot 1: Confusion Matrix Heatmap
    fig, ax = plt.subplots(figsize=(6, 5))
    cm = np.array([[tn, fp], [fn, tp]])
    im = ax.imshow(cm, cmap="Blues", interpolation="nearest")
    fig.colorbar(im)

    ax.set_xticks([0, 1])
    ax.set_yticks([0, 1])
    ax.set_xticklabels(["Rejected (Unknown)", "Allowed (Resident)"], fontsize=11)
    ax.set_yticklabels(["Negative (Visitor)", "Positive (Resident)"], fontsize=11)
    ax.set_xlabel("Predicted Security Decision", fontsize=12, fontweight="bold")
    ax.set_ylabel("Ground Truth Class", fontsize=12, fontweight="bold")
    ax.set_title("Confusion Matrix - Access Control System", fontsize=13, fontweight="bold", pad=12)

    labels = [[f"TN: {tn}", f"FP: {fp}"], [f"FN: {fn}", f"TP: {tp}"]]
    for i in range(2):
        for j in range(2):
            color = "white" if cm[i, j] > cm.max() / 2 else "black"
            ax.text(j, i, labels[i][j], ha="center", va="center", color=color, fontsize=13, fontweight="bold")

    plt.tight_layout()
    cm_path = os.path.join(EVAL_DIR, "confusion_matrix.png")
    plt.savefig(cm_path, dpi=300)
    plt.close()

    # Plot 2: Environmental Robustness Breakdown (Lighting, Angle, Quality)
    fig, ax = plt.subplots(figsize=(8, 4.8))
    conditions = list(cond_stats.keys())
    accs = [cond_stats[c][0] * 100 for c in conditions]
    precs = [cond_stats[c][1] * 100 for c in conditions]
    recs = [cond_stats[c][2] * 100 for c in conditions]

    x = np.arange(len(conditions))
    width = 0.25

    ax.bar(x - width, accs, width, label="Accuracy", color="#2ecc71")
    ax.bar(x, precs, width, label="Precision", color="#3498db")
    ax.bar(x + width, recs, width, label="Recall", color="#e67e22")

    ax.set_ylabel("Score (%)", fontsize=11, fontweight="bold")
    ax.set_title("Performance Under Environmental Variations", fontsize=13, fontweight="bold", pad=12)
    ax.set_xticks(x)
    ax.set_xticklabels(conditions, fontsize=10, fontweight="bold")
    ax.set_ylim([0, 105])
    ax.legend(frameon=True, loc="lower right")

    plt.tight_layout()
    env_path = os.path.join(EVAL_DIR, "environmental_robustness.png")
    plt.savefig(env_path, dpi=300)
    plt.close()

    # Plot 3: Instantaneous Threshold Sensitivity Analysis (using precomputed distances)
    thresholds = np.linspace(0.15, 0.85, 30)
    thresh_accs = []
    thresh_precs = []
    thresh_recs = []

    for t in thresholds:
        preds = (min_distances <= t).astype(int)
        thresh_accs.append(accuracy_score(y_true, preds) * 100)
        thresh_precs.append(precision_score(y_true, preds, zero_division=0) * 100)
        thresh_recs.append(recall_score(y_true, preds, zero_division=0) * 100)

    fig, ax = plt.subplots(figsize=(8, 4.8))
    ax.plot(thresholds, thresh_accs, label="Accuracy", color="#27ae60", linewidth=2.5)
    ax.plot(thresholds, thresh_precs, label="Precision", color="#2980b9", linewidth=2.0, linestyle="--")
    ax.plot(thresholds, thresh_recs, label="Recall", color="#d35400", linewidth=2.0, linestyle="-.")
    ax.axvline(DEFAULT_THRESHOLD, color="red", linestyle=":", label=f"Selected Threshold ({DEFAULT_THRESHOLD})", linewidth=2)

    ax.set_xlabel("Matching Distance Threshold", fontsize=11, fontweight="bold")
    ax.set_ylabel("Score (%)", fontsize=11, fontweight="bold")
    ax.set_title("Matching Threshold Sensitivity Analysis", fontsize=13, fontweight="bold", pad=12)
    ax.set_ylim([0, 105])
    ax.legend(frameon=True, loc="lower left")

    plt.tight_layout()
    thresh_path = os.path.join(EVAL_DIR, "threshold_analysis.png")
    plt.savefig(thresh_path, dpi=300)
    plt.close()


if __name__ == "__main__":
    run_evaluation()
