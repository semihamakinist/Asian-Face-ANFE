import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

# Confusion matrix fonksiyonu (örnek değerler)
def confusion_matrix_2():
    # Burada:
    # - TP (True Positive): Gerçek 'Female' tahmin edilen 'Female'
    # - FN (False Negative): Gerçek 'Female' fakat 'Male' tahmin edilmiş
    # - FP (False Positive): Gerçek 'Male' fakat 'Female' tahmin edilmiş
    # - TN (True Negative): Gerçek 'Male' ve 'Male' tahmin edilmiş
    TP = 975  # True Female (Gerçek kadın ve kadın tahmin edilmiş)
    FN = 25   # False Negative (Gerçek kadın fakat erkek tahmin edilmiş)
    FP = 58   # False Positive (Gerçek erkek fakat kadın tahmin edilmiş)
    TN = 942  # True Male (Gerçek erkek ve erkek tahmin edilmiş)
    # Matrisi, satırlar gerçek değerler, sütunlar tahmin edilen değerler olarak düzenliyoruz.
    return np.array([[TP, FN], [FP, TN]])

if __name__ == '__main__':
    # Confusion matrix değerlerini al
    cm = confusion_matrix_2()

    # Her satırı normalize ederek yüzde değerlerini hesapla
    # Her satırdaki değerlerin toplamı, o sınıfa ait toplam örnek sayısıdır.
    cm_percent = cm.astype('float') / cm.sum(axis=1)[:, np.newaxis] * 100

    # Görselleştirme ayarları
    plt.figure(figsize=(6, 4))
    sns.set(font_scale=1.1)

    # Heatmap oluşturuluyor; annot=False olarak ayarlanıyor, çünkü sayıları elle ekleyeceğiz.
    # Renk paleti "YlGnBu" olarak değiştirildi.
    ax = sns.heatmap(cm,
                     annot=False,
                     cmap="YlGnBu",
                     xticklabels=["Predicted Female", "Predicted Male"],
                     yticklabels=["True Female", "True Male"],
                     cbar=False,
                     square=True)  # Hücrelerin kare olması için

    # Her hücreye hem sayı hem de yüzde değeri ekle
    for i in range(cm.shape[0]):
        for j in range(cm.shape[1]):
            ax.text(j + 0.5, i + 0.5,
                    f'{cm[i, j]}\n({cm_percent[i, j]:.1f}%)',
                    horizontalalignment='center', verticalalignment='center',
                    fontsize=16, weight='bold', color='white')

    # Grafik başlığı, etiketler ve boşluk ayarları
    plt.title('Confusion Matrix for FaceNet512 200-ANFE Gender Prediction', pad=20)
    plt.xlabel('Predicted Labels', fontsize=12)
    plt.ylabel('True Labels', fontsize=12)
    plt.tight_layout(pad=2.0)

    # Grafiği dosya olarak kaydet (images klasörünün var olduğundan emin olun)
    plt.savefig(r'images\gender_confusion_matrix.png', bbox_inches='tight')
    plt.show()
