import matplotlib.pyplot as plt
import numpy as np

anfe_model = (
    "g_500_100",
    "g_500_200",
    "g_500_300",
    "g_500_400",
    "g_500_500",
    "g_500_1000"
    )

anfe_model_2 = (
    "g_1000_100",
    "g_1000_200",
    "g_1000_300",
    "g_1000_400",
    "g_1000_500",
    "g_1000_1000"
    )

anfe_female = {
    'dlib ANFE (%)': (75.2, 77.8, 77, 76, 76, 75.4),
    'ArcFace ANFE (%)': (91.2, 90.8, 90.4, 91.8, 91.8, 92),
    'FaceNet512 ANFE (%)': (97, 97.6, 97.2, 97.2, 97.2, 97.2),
}

anfe_female_2 = {
    'dlib ANFE (%)': (76.6, 78.6, 77.9, 77.1, 77, 76.4),
    'ArcFace ANFE (%)': (91.9, 92.8, 92.4, 93, 93.1, 92),
    'FaceNet512 ANFE (%)': (96.8, 97.5, 97.1, 97.2, 97.2, 97.2),
}

x = np.arange(len(anfe_model))  # the label locations
width = 0.6  # the width of the bars
#x = np.arange(len(anfe_model_2))  # the label locations
#width = 0.9  # the width of the bars
multiplier = 0

fig, ax = plt.subplots(layout='constrained')

for attribute, measurement in anfe_female.items():
#for attribute, measurement in anfe_female_2.items():
    offset = width * multiplier
    rects = ax.bar(x * 2 + offset, measurement, width, label=attribute)
    #rects = ax.bar(x * 3 + offset, measurement, width, label=attribute)
    ax.bar_label(rects, padding=3)
    multiplier += 1

# Add some text for labels, title and custom x-axis tick labels, etc.
ax.set_ylabel('Accuracy (%)')
ax.set_title('Results of Female ANFE Models for 500 Samples')
ax.set_xticks(x * 2 + width, anfe_model)
#ax.set_title('Results of Female ANFE Models for 1000 Samples')
#ax.set_xticks(x * 3 + width, anfe_model_2)
ax.legend(loc='upper left', ncols=3)
ax.set_ylim(0, 120)

plt.show()