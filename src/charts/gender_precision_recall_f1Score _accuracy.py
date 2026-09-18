from sklearn.metrics import precision_score, recall_score, f1_score, accuracy_score

my_accuracy_score = lambda TP, FN, FP, TN: (TP + TN)/(TP + FN + FP + TN)
my_precision_score = lambda TP, FP: TP/(TP+FP)
my_recall_score = lambda TP, FN: TP/(TP + FN)
my_f1_score = lambda precision, recall: 2 * ((precision * recall)/(precision + recall))

if __name__ == '__main__':
    # Gerçek etiketler (Kadın: 0, Erkek: 1)
    y_true = [0, 1, 1, 0, 1, 0, 1, 1, 0, 1]

    # Modelin tahmin ettiği etiketler
    y_pred = [0, 1, 0, 0, 1, 1, 1, 0, 0, 1]

    # Precision, Recall, F1-score ve Accuracy hesaplamaları
    """precision = precision_score(y_true, y_pred)
    recall = recall_score(y_true, y_pred)
    f1 = f1_score(y_true, y_pred)
    accuracy = accuracy_score(y_true, y_pred)"""
    """# AsianWiki: FaceNet512 200-ANFE cinsiyet vektor model sonuclari
    TP = 975  # F -> F: Gerçek negatifler
    FN = 25  # F -> M: Yanlış pozitifler
    TN = 942  # M -> M: Gerçek pozitifler
    FP = 58  # M -> F: Yanlış negatifler"""

    """# AsianWiki: deepface cinsiyet tespit modeli
    TP = 887  # F -> F: Gerçek negatifler
    FN = 113  # F -> M: Yanlış pozitifler
    TN = 968  # M -> M: Gerçek pozitifler
    FP = 32   # M -> F: Yanlış negatifler

    precision = my_precision_score(TP, FP)
    recall = my_recall_score(TP, FN)
    f1 = my_f1_score(precision, recall)
    accuracy = my_accuracy_score(TP, FN, FP, TN)

    print(f"Precision: {precision:.2f}")
    print(f"Recall: {recall:.2f}")
    print(f"F1 Score: {f1:.2f}")
    print(f"Accuracy: {accuracy:.2f}")"""

    """# AsianWiki: imdb-centerface cinsiyet tespit modeli
    TP = 622  # F -> F: Gerçek negatifler
    FN = 378  # F -> M: Yanlış pozitifler
    TN = 888  # M -> M: Gerçek pozitifler
    FP = 112  # M -> F: Yanlış negatifler

    precision = my_precision_score(TP, FP)
    recall = my_recall_score(TP, FN)
    f1 = my_f1_score(precision, recall)
    accuracy = my_accuracy_score(TP, FN, FP, TN)

    print(f"Precision: {precision:.2f}")
    print(f"Recall: {recall:.2f}")
    print(f"F1 Score: {f1:.2f}")
    print(f"Accuracy: {accuracy:.2f}")"""

    """
    # AsianWiki: imdb-tensorflow cinsiyet tespit modeli
    TP = 880  # F -> F: Gerçek negatifler
    FN = 120  # F -> M: Yanlış pozitifler
    TN = 800  # M -> M: Gerçek pozitifler
    FP = 200  # M -> F: Yanlış negatifler

    precision = my_precision_score(TP, FP)
    recall = my_recall_score(TP, FN)
    f1 = my_f1_score(precision, recall)
    accuracy = my_accuracy_score(TP, FN, FP, TN)

    print(f"Precision: {precision:.2f}")
    print(f"Recall: {recall:.2f}")
    print(f"F1 Score: {f1:.2f}")
    print(f"Accuracy: {accuracy:.2f}")"""


    """
    # AsianWiki: ArcFace ANFE-200 cinsiyet tespit modeli
    TP = 972  # F -> F: Gerçek negatifler
    FN = 28  # F -> M: Yanlış pozitifler
    TN = 941  # M -> M: Gerçek pozitifler
    FP = 59  # M -> F: Yanlış negatifler

    precision = my_precision_score(TP, FP)
    recall = my_recall_score(TP, FN)
    f1 = my_f1_score(precision, recall)
    accuracy = my_accuracy_score(TP, FN, FP, TN)

    print(f"Precision: {precision:.2f}")
    print(f"Recall: {recall:.2f}")
    print(f"F1 Score: {f1:.2f}")
    print(f"Accuracy: {accuracy:.2f}")
    """
    # AsianWiki: small-vggface-16 cinsiyet tespit modeli
    TP = 964  # F -> F: Gerçek negatifler
    FN = 36  # F -> M: Yanlış pozitifler
    TN = 733  # M -> M: Gerçek pozitifler
    FP = 267  # M -> F: Yanlış negatifler

    precision = my_precision_score(TP, FP)
    recall = my_recall_score(TP, FN)
    f1 = my_f1_score(precision, recall)
    accuracy = my_accuracy_score(TP, FN, FP, TN)

    print(f"Precision: {precision:.2f}")
    print(f"Recall: {recall:.2f}")
    print(f"F1 Score: {f1:.2f}")
    print(f"Accuracy: {accuracy:.2f}")
