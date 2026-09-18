from units.set_generel_tools import generating_id
from insightface.model_zoo import get_model
from insightface.utils import face_align
import numpy as np
import cv2
import os


def get_face_model(model_name, ctx_id=-1, nms=0.4):
    face_model = get_model(model_name)
    if nms == -0.00000000001:
        face_model.prepare(ctx_id=ctx_id)
    else:
        face_model.prepare(ctx_id=ctx_id, nms=nms)
    return face_model


def set_crop_face(f_location, img_size, margin=10):
    (left, top, right, bottom) = f_location
    left = int(np.maximum(left - margin / 2, 0))
    top = int(np.maximum(top - margin / 2, 0))
    right = int(np.minimum(right + margin / 2, img_size[1]))
    bottom = int(np.minimum(bottom + margin / 2, img_size[0]))
    return left, top, right, bottom


# bbo normalizasyonu
def set_bbox(f_location):
    (left, top, right, bottom) = f_location
    return np.max([left, 0]), np.max([top, 0]), np.max([right, 0]), np.max([bottom, 0])

def set_deepface_bbox(facial_area):
    bbox = np.array([facial_area['x'], facial_area['y'], facial_area['w'], facial_area['h']])
    (left, top, w, h) = set_bbox(bbox.astype(np.int32).flatten())
    right = left + w
    bottom = top + h
    return int(left), int(top), int(right), int(bottom)


# https://github.com/ageitgey/face_recognition/blob/master/face_recognition/api.py
def face_distance(face_encodings, face_to_compare):
    if len(face_encodings) == 0:
        return np.empty(0)
    return np.linalg.norm(face_encodings - face_to_compare, axis=1)


# insightface -- face similarity
def face_similarity_1(emb1, emb2):
    if len(emb1) == 0 or len(emb2) == 0:
        return np.empty(0)
    return np.dot(emb1, emb2)/(np.linalg.norm(emb1) * np.linalg.norm(emb2))


# my_method -- face similarity
def cosine_similarity(emb_list, compare_emb):
    return np.dot(emb_list, compare_emb) / (np.linalg.norm(emb_list, axis=1) * np.linalg.norm(compare_emb))


def face_distance_all(face_encodings, face_to_compare, distance_metric=0):
    if len(face_encodings) == 0:
        return np.empty(0)

    if distance_metric == 0:  # Euclidian distance
        return np.linalg.norm(face_encodings - face_to_compare, axis=1)

    elif distance_metric == 1:  # Distance based on cosine similarity (face_encodings -- array list)
        return np.abs(np.dot(face_encodings, face_to_compare)) / (np.linalg.norm(face_encodings,
                                                                                 axis=1) * np.linalg.norm(face_to_compare))
    elif distance_metric == 2:  # Distance based on cosine similarity (face_encodings -- single)
        return np.abs(np.dot(face_encodings, face_to_compare)) / (np.linalg.norm(face_encodings) * np.linalg.norm(face_to_compare))


def convert_norm(emb):
    embedding_norm = np.linalg.norm(emb)
    normed_embedding = emb / embedding_norm
    return normed_embedding


def extract_embed_list(model_detect, model_embed, confidence_val, know_person_image_path_list, face_size):
    know_person_embeds = []
    know_person_labels = []

    for root_path, file_name in know_person_image_path_list:
        # read image
        image_file_path = os.path.join(root_path, file_name)
        know_person_label, _ = file_name.split(".jpg")
        know_person_embed, know_person_label = extract_embed_single(model_detect, model_embed,
                                                                    confidence_val,
                                                                    image_file_path,
                                                                    face_size,
                                                                    file_name)

        know_person_embeds.extend(know_person_embed)
        know_person_labels.extend(know_person_label)

    return know_person_embeds, know_person_labels


def extract_embed_single(model_detect, model_embed, confidence_val, image_file_path, face_size, file_name=None):
    know_person_embeds = []
    know_person_labels = []
    try:
        # read
        img = cv2.imread(image_file_path)

        # bboxes_scores -- (bbox, score)
        bboxes_scores, landmarks = model_detect.detect(img)

        if bboxes_scores.size > 0:
            landmark = landmarks[0]
            bbox = bboxes_scores[0]

            (left, top, right, bottom) = set_bbox(bbox[0:4].astype(np.int).flatten())

            # confidence_val --> bbox[4]
            # print(f"know_person_label: {know_person_label} - score: {bbox[4]} - face_size: {abs(top - bottom)}x{abs(left - right)}")
            if bbox[4] >= confidence_val and abs(top - bottom) >= face_size and abs(left - right) >= face_size:
                # crop_img -- crop face and resize face (112x112)
                crop_face_img = face_align.norm_crop(img, landmark=landmark)
                face_emb = model_embed.get_embedding(crop_face_img).flatten()

                # normalization process for face embeding (0 - 1.5)
                normed_embedding = convert_norm(face_emb)

                know_person_embeds.append(normed_embedding)
                if file_name:
                    know_person_labels.append(file_name)
                else:
                    know_person_labels.append(generating_id())

    except Exception as e:
        print(f"error code: {e}")
        print(f"Error image_file_path: {image_file_path}")
    # break
    return know_person_embeds, know_person_labels
