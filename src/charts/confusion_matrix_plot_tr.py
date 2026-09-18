import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

# Confusion matrix fonksiyonu
def confusion_matrix(y_true, y_pred):
    TP = np.sum((y_true == 1) & (y_pred == 1))  # Gerçek pozitifler
    FP = np.sum((y_true == 0) & (y_pred == 1))  # Yanlış pozitifler
    TN = np.sum((y_true == 0) & (y_pred == 0))  # Gerçek negatifler
    FN = np.sum((y_true == 1) & (y_pred == 0))  # Yanlış negatifler
    return np.array([[TN, FP], [FN, TP]])

# Confusion matrix fonksiyonu
def confusion_matrix_2():
    TP = 975  # F -> F: Gerçek negatifler
    FN = 25   # F -> M: Yanlış pozitifler
    TN = 942  # M -> M: Gerçek pozitifler
    FP = 58   # M -> F: Yanlış negatifler
    return np.array([[TP, FN], [FP, TN]])

if __name__ == '__main__':
    # Örnek veriler: Gerçek cinsiyetler (0 = Kadın, 1 = Erkek)
    # Burada sadece örnek veriler kullandık. Gerçek verileri kendi verisetinizden alabilirsiniz.
    # y_true = np.array([1, 0, 1, 1, 0, 1, 0, 0, 1, 0, 1, 1, 0, 0, 1, 1, 0, 1, 0, 0])
    # y_pred = np.array([1, 0, 1, 0, 0, 1, 1, 0, 1, 0, 1, 1, 1, 0, 1, 1, 0, 0, 0, 0])

    # Confusion matrix hesapla
    # cm = confusion_matrix(y_true, y_pred)
    cm = confusion_matrix_2()

    # Her hücre için yüzdelik değerleri hesapla
    cm_percent = cm.astype('float') / cm.sum(axis=1)[:, np.newaxis] * 100  # Satır bazında normalize et


    # Alternatif olarak, Matplotlib ve Seaborn ile görselleştirme
    plt.figure(figsize=(6, 4))
    """sns.heatmap(cm, annot=True, fmt="d", cmap="Blues", xticklabels=["Tahmin Edilen Kadın (0)", "Tahmin Edilen Erkek (1)"],
                yticklabels=["Doğru Kadın (0)", "Doğru Erkek (1)"], cbar=False,
                annot_kws={"size": 12, 'weight': 'bold'}, cbar_kws={'label': 'Counts'})"""
    sns.set(font_scale=1.1)
    # Heatmap oluşturma, annot=False yaparak sayıları plotly text ile ekleyeceğiz
    sns.heatmap(cm, annot=False,
                annot_kws={"size": 16, 'weight': 'bold'},
                #fmt = 'd',
                #cmap="YlGnBu",
                #cmap=sns.color_palette("flare", as_cmap=True),
                cmap=sns.color_palette("dark:#5A9_r", as_cmap=True),
                xticklabels=["Kadın", "Erkek"],
                yticklabels=["Kadın", "Erkek"],
                cbar=False,
                square=True)

    # Yüzdeleri de aynı grafikte göstermek için:
    for i in range(cm.shape[0]):
        for j in range(cm.shape[1]):
            plt.text(j + 0.5, i + 0.5, f'{cm[i, j]}\n({cm_percent[i, j]:.1f}%)',
                     horizontalalignment='center', verticalalignment='center',
                     fontsize=16, weight='bold',
                     color='white')

    plt.title('FaceNet512 200-ANFE Cinsiyet Tahmini için Karışıklık Matrisi', pad=20)
    # Başlık sonrasında boşluk eklemek için aşağıdaki satırı ekliyoruz:
    #plt.subplots_adjust(top=0.85)  # Bu, başlık alanı için biraz daha boşluk ekler
    plt.tight_layout(pad=2.0)
    plt.xlabel('Tahmin Edilen Etiketler', fontsize=12)
    plt.ylabel('Gerçek Etiketler', fontsize=12)

    # Grafik dosyası olarak kaydediliyor
    plt.savefig(r'images\gender_confusion_matrix_tr.png', bbox_inches='tight')
    plt.show()

