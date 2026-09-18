from __future__ import absolute_import
from __future__ import print_function
from __future__ import division

import numpy as np

import random
import string
import dlib


def convert_norm(emb):
    return emb/np.linalg.norm(emb)


def generating_id(word_length=16):
    return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(word_length))


def set_label(descriptors, th_cwc):
    labels = [label for i, label in enumerate(dlib.chinese_whispers_clustering(descriptors, th_cwc))]
    uniq_labels = {lb: generating_id() for lb in list(set(labels))}
    return labels, uniq_labels


def face_distance(face_encodings, face_to_compare, distance_metric=0):
    if face_encodings.size == 0:
        return np.empty(0)

    if distance_metric == 0:  # Euclidian distance
        return np.linalg.norm(face_encodings - face_to_compare, axis=1)
    elif distance_metric == 1:  # Distance based on cosine similarity (face_encodings -- array list)
        return np.abs(np.dot(face_encodings, face_to_compare)) / (np.linalg.norm(face_encodings,
                                                                                 axis=1) * np.linalg.norm(face_to_compare))
    elif distance_metric == 2:  # Distance based on cosine similarity (face_encodings -- single)
        return np.abs(np.dot(face_encodings, face_to_compare)) / (np.linalg.norm(face_encodings) * np.linalg.norm(face_to_compare))


if __name__ == '__main__':
    print(generating_id())
