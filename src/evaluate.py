import json
from typing import Dict, Any, Union


def calculate_metrics(
        tp: int = None,
        fn: int = None,
        tn: int = None,
        fp: int = None,
        json_path: str = None
) -> Dict[str, Union[float, int]]:
    """
    Model sınıflandırma metriklerini (Accuracy, Precision, Recall, F1-Score) hesaplar.

    Parametreler:
        tp (int): True Positive (Doğru Kadın / Pozitif)
        fn (int): False Negative (Yanlış Erkek Tahmini)
        tn (int): True Negative (Doğru Erkek / Negatif)
        fp (int): False Positive (Yanlış Kadın Tahmini)
        json_path (str, opsiyonel): DeepFace test JSON dosyası yolu

    Dönüş:
        dict: Metrikleri ve ham sayıları içeren sözlük.
    """
    # Eğer JSON dosyası verildiyse metrikleri doğrudan JSON içerisinden çıkar
    if json_path:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        tp = fn = tn = fp = 0

        # DeepFace JSON formatı kontrolü
        info = data.get("deepface", {}).get("image_info", {})

        for item in info.get("female", []):
            if item.get("case") is True or item.get("guess_gender") == "female":
                tp += 1
            else:
                fn += 1

        for item in info.get("male", []):
            if item.get("case") is True or item.get("guess_gender") == "male":
                tn += 1
            else:
                fp += 1

    total = tp + fn + tn + fp
    if total == 0:
        raise ValueError("Hesaplama için geçerli veri bulunamadı.")

    # Temel Metrik Formülleri
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    f1_score = (2 * precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0
    accuracy = (tp + tn) / total

    female_acc = (tp / (tp + fn) * 100) if (tp + fn) > 0 else 0.0
    male_acc = (tn / (tn + fp) * 100) if (tn + fp) > 0 else 0.0

    return {
        "Total_Samples": total,
        "TP": tp,
        "FN": fn,
        "TN": tn,
        "FP": fp,
        "Female_Acc_pct": round(female_acc, 2),
        "Male_Acc_pct": round(male_acc, 2),
        "Precision": round(precision, 4),
        "Recall": round(recall, 4),
        "F1_Score": round(f1_score, 4),
        "Accuracy": round(accuracy, 4)
    }


# ==========================================
# ÖRNEK KULLANIM:
# ==========================================
if __name__ == "__main__":
    # 1. ArcFace 200-ANFE (Tablo 5 değerleri ile)
    arcface_metrics = calculate_metrics(tp=928, fn=72, tn=901, fp=99)
    print("--- ArcFace 200-ANFE Sonuçları ---")
    print(f"Female Acc: %{arcface_metrics['Female_Acc_pct']}")
    print(f"Male Acc  : %{arcface_metrics['Male_Acc_pct']}")
    print(f"Precision : {arcface_metrics['Precision']:.2f}")
    print(f"Recall    : {arcface_metrics['Recall']:.2f}")
    print(f"F1-Score  : {arcface_metrics['F1_Score']:.2f}")
    print(f"Accuracy  : {arcface_metrics['Accuracy']:.2f}\n")

    # 2. FaceNet512 200-ANFE (Tablo 5 değerleri ile)
    facenet_metrics = calculate_metrics(tp=975, fn=25, tn=942, fp=58)
    print("--- FaceNet512 200-ANFE Sonuçları ---")
    print(f"Precision : {facenet_metrics['Precision']:.2f}")
    print(f"Recall    : {facenet_metrics['Recall']:.2f}")
    print(f"F1-Score  : {facenet_metrics['F1_Score']:.2f}")
    print(f"Accuracy  : {facenet_metrics['Accuracy']:.2f}\n")

    # 3. JSON Dosyasından Doğrudan Okuma (Örnek)
    # json_metrics = calculate_metrics(json_path="gender_deepface_asian_famous_test_1000.json")
    # print("DeepFace JSON Accuracy:", json_metrics["Accuracy"])