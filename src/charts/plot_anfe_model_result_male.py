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
    'dlib ANFE (%)': (71.8, 70.4, 71.4, 72.8, 71.6, 72.2),
    'ArcFace ANFE (%)': (88.4, 86.6, 87.2, 87.8, 87.4, 88.4),
    'FaceNet512 ANFE (%)': (93.8, 94.4, 94, 94.2, 94.2, 94.2),
}

anfe_female_2 = {
    'dlib ANFE (%)': (74, 72.8, 73.7, 74.8, 73.8, 74.3),
    'ArcFace ANFE (%)': (90.1, 90.1, 89.8, 89.6, 89.6, 90.2),
    'FaceNet512 ANFE (%)': (93.7, 94.2, 94.1, 94.1, 94.1, 94.1),
}

#x = np.arange(len(anfe_model))  # the label locations
#width = 0.6  # the width of the bars
x = np.arange(len(anfe_model_2))  # the label locations
width = 0.9  # the width of the bars
multiplier = 0

fig, ax = plt.subplots(layout='constrained')

#for attribute, measurement in anfe_female.items():
for attribute, measurement in anfe_female_2.items():
    offset = width * multiplier
    #rects = ax.bar(x * 2 + offset, measurement, width, label=attribute)
    rects = ax.bar(x * 3 + offset, measurement, width, label=attribute)
    ax.bar_label(rects, padding=3)
    multiplier += 1

# Add some text for labels, title and custom x-axis tick labels, etc.
ax.set_ylabel('Accuracy (%)')
#ax.set_title('Results of Male ANFE Models for 500 Samples')
#ax.set_xticks(x * 2 + width, anfe_model)
ax.set_title('Results of Male ANFE Models for 1000 Samples')
ax.set_xticks(x * 3 + width, anfe_model_2)
ax.legend(loc='upper left', ncols=3)
ax.set_ylim(0, 120)

plt.show()