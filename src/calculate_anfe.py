#from units.set_face import set_bbox
from units.set_face import set_deepface_bbox
from deepface import DeepFace
from datetime import datetime
import numpy as np
import random
import glob
#import json
import os
#from deepface.commons import functions, realtime, distance as dst
from deepface.modules.verification import find_distance
from units.set_files import ReadJsonData, WriteJsonData

#face_recognation_models = ['VGG-Face', 'Facenet', 'Facenet512', 'OpenFace', 'DeepFace', 'DeepID', 'ArcFace', 'Dlib', 'SFace']
#face_detect_models = ['opencv', 'ssd', 'dlib', 'mtcnn', 'retinaface', 'mediapipe', 'yolov8', 'yunet', 'fastmtcnn']

face_recognation_models = [
    'VGG-Face', 'Facenet',
    'Facenet512', 'OpenFace',
    'DeepFace', 'DeepID',
    'ArcFace', 'Dlib',
    'SFace', 'GhostFaceNet',
]

face_detect_models = [
    'opencv', 'ssd', 'dlib', 'mtcnn', 'fastmtcnn',
    'retinaface', 'mediapipe', 'yolov8', 'yunet', 'centerface',
]
normalizations = ['base', 'raw', 'Facenet', 'Facenet2018', 'VGGFace', 'VGGFace2', 'ArcFace']
distance_metrics = ['cosine', 'euclidean', 'euclidean_l2']

gender_embeds = {
            'dlib': {
                'image_info': {'female': [], 'male': []},
                'average': {
                    100: {'female': [], 'male': []},
                    200: {'female': [], 'male': []},
                    300: {'female': [], 'male': []},
                    400: {'female': [], 'male': []},
                    500: {'female': [], 'male': []},
                    1000: {'female': [], 'male': []},
                },
                'models_analysis': {
                    100: {'female': [], 'male': []},
                    200: {'female': [], 'male': []},
                    300: {'female': [], 'male': []},
                    400: {'female': [], 'male': []},
                    500: {'female': [], 'male': []},
                    1000: {'female': [], 'male': []},
                },
                'correct_gender': {
                    100: {'female': 0, 'male': 0},
                    200: {'female': 0, 'male': 0},
                    300: {'female': 0, 'male': 0},
                    400: {'female': 0, 'male': 0},
                    500: {'female': 0, 'male': 0},
                    1000: {'female': 0, 'male': 0},
                },
            },
            'arcface': {
                'image_info': {'female': [], 'male': []},
                'average': {
                    100: {'female': [], 'male': []},
                    200: {'female': [], 'male': []},
                    300: {'female': [], 'male': []},
                    400: {'female': [], 'male': []},
                    500: {'female': [], 'male': []},
                    1000: {'female': [], 'male': []},
                },
                'models_analysis': {
                    100: {'female': [], 'male': []},
                    200: {'female': [], 'male': []},
                    300: {'female': [], 'male': []},
                    400: {'female': [], 'male': []},
                    500: {'female': [], 'male': []},
                    1000: {'female': [], 'male': []},
                },
                'correct_gender': {
                    100: {'female': 0, 'male': 0},
                    200: {'female': 0, 'male': 0},
                    300: {'female': 0, 'male': 0},
                    400: {'female': 0, 'male': 0},
                    500: {'female': 0, 'male': 0},
                    1000: {'female': 0, 'male': 0},
                },
            },
            'facenet512': {
                'image_info': {'female': [], 'male': []},
                'average': {
                    100: {'female': [], 'male': []},
                    200: {'female': [], 'male': []},
                    300: {'female': [], 'male': []},
                    400: {'female': [], 'male': []},
                    500: {'female': [], 'male': []},
                    1000: {'female': [], 'male': []},
                },
                'models_analysis': {
                    100: {'female': [], 'male': []},
                    200: {'female': [], 'male': []},
                    300: {'female': [], 'male': []},
                    400: {'female': [], 'male': []},
                    500: {'female': [], 'male': []},
                    1000: {'female': [], 'male': []},
                },
                'correct_gender': {
                    100: {'female': 0, 'male': 0},
                    200: {'female': 0, 'male': 0},
                    300: {'female': 0, 'male': 0},
                    400: {'female': 0, 'male': 0},
                    500: {'female': 0, 'male': 0},
                    1000: {'female': 0, 'male': 0},
                },
            }
        }


def calculateDistance(img1_embed, img2_embed, distance_metric):
    return find_distance(img1_embed, img2_embed, distance_metric)


def getFaceInfo(
        img_path,
        recognation_model,
        face_detect_model,
        normalizasyon
):
    try:
        objs = DeepFace.represent(
            img_path,
            model_name=recognation_model,
            enforce_detection=False,
            detector_backend=face_detect_model,
            align=True,
            normalization=normalizasyon  # ArcFace
        )
        return objs
    except Exception as ex:
        return {}


def calculateGenderDeepModel(
        img_path,
        data_average_embeddings,
        gender_name,
        model_name='arcface',
        recognation_model='ArcFace',
        normalizasyon='ArcFace'
):
    global gender_embeds
    det_th = 0.8
    face_size = 40
    face_detect_models_tmp = [
        face_detect_models[-1], face_detect_models[5],
        face_detect_models[6], face_detect_models[8],
        face_detect_models[4]
    ]

    for face_detect_model in face_detect_models_tmp:
        objs = getFaceInfo(img_path, recognation_model, face_detect_model, normalizasyon)
        if (len(objs) == 0
                or len(objs) > 1
                or (len(objs) == 1 and objs[0]['face_confidence'] <= det_th)):
            continue
        elif len(objs) == 1 and (objs[0]['face_confidence'] >= det_th):
            try:
                (left, top, right, bottom) = set_deepface_bbox(objs[0]['facial_area'])
                if ((objs[0]['face_confidence'] >= det_th)
                        and ((abs(top - bottom) >= face_size) or (abs(left - right) >= face_size))):
                    face_embed = objs[0]['embedding']
                    face_bbox = (left, top, right, bottom)
                    det_score = float(objs[0]['face_confidence'])
                    image_info_data = {
                        'img_path': img_path,
                        'bbox': face_bbox,
                        'det_score': det_score,
                        'detect_model': face_detect_model,
                        'face_emb': face_embed,
                    }
                    gender_embeds[model_name]['image_info'][gender_name].append(image_info_data)

                    for key, value in data_average_embeddings.items():
                        female_average_ambed = np.array(data_average_embeddings[key]['female'])
                        male_average_ambed = np.array(data_average_embeddings[key]['male'])
                        # distance_metrics[-1] -> euclidean_l2
                        f_dist = calculateDistance(female_average_ambed, face_embed, distance_metrics[-1])
                        m_dist = calculateDistance(male_average_ambed, face_embed, distance_metrics[-1])
                        g_gender = 'female' if f_dist < m_dist else 'male'
                        gender_case = True if g_gender == gender_name else False

                        gender_info = {
                            'img_path': img_path,
                            'f_dist': f_dist,
                            'm_dist': m_dist,
                            'correct_gender': gender_name,
                            'guess_gender': g_gender,
                            'case': gender_case
                        }
                        # print(f'gender_info: {gender_info}')
                        gender_embeds[model_name]['models_analysis'][int(key)][gender_name].append(gender_info)
                        if gender_case:
                            gender_embeds[model_name]['correct_gender'][int(key)][gender_name] += 1
                        """else:
                            print('Error_{0}_{1}: {2}'.format(model_name, key, img_path))"""
                    #return face_embed, face_bbox, det_score
                else:
                    print('Under40Px: {0} - det_th: {1} - {2}x{3}'
                          .format(img_path, objs[0]['face_confidence'],
                                  abs(top - bottom), abs(left - right)))
            except Exception as ex:
                print('Error setFaceDeepModel: {0} - img_path: {1}'.format(ex, img_path))
            break
        elif len(objs) > 1:
            print("ManyFace_image_path: {0}".format(img_path))
    #return [], (), 0


if __name__ == '__main__':
    data_path = r'data\embeddings\gender_average_embeds_asian_famous_dlib_arcface_facenet512_V3.json'
    data_average = ReadJsonData(data_path)
    data_dlib_average = data_average['dlib']['average']
    data_arcface_average = data_average['arcface']['average']
    data_facenet512_average = data_average['facenet512']['average']
    gender_embeds['dlib']['average'] = data_dlib_average
    gender_embeds['arcface']['average'] = data_arcface_average
    gender_embeds['facenet512']['average'] = data_facenet512_average

    genders = ['female', 'male']
    # genders = ['female']
    # genders = ['male']
    try:
        print("Start Time =", datetime.now().strftime("%H:%M:%S"))
        for gender in genders:
            image_main_path = r'dataset\asianwiki\gender\Test1000\version_1\{0}'.format(gender)
            image_path_list = glob.glob(os.path.join(image_main_path, '*', '*.*'))
            random.shuffle(image_path_list)
            loop_index = 0
            for image_path in image_path_list:
                print(f'image_path: {image_path}')
                # ArcFace
                calculateGenderDeepModel(image_path, data_arcface_average,
                                         gender, model_name='arcface',
                                         recognation_model=face_recognation_models[6], # arcface_model
                                         normalizasyon=normalizations[-1])
                # dlib
                calculateGenderDeepModel(image_path, data_dlib_average,
                                         gender, model_name='dlib',
                                         recognation_model=face_recognation_models[7], # dlib_model
                                         normalizasyon=normalizations[-1])

                # facenet512
                calculateGenderDeepModel(image_path, data_facenet512_average,
                                         gender, model_name='facenet512',
                                         recognation_model=face_recognation_models[2], # facenet512_model
                                         normalizasyon=normalizations[2])
                loop_index += 1
                if loop_index == 500:
                    break

        print("Finish Time =", datetime.now().strftime("%H:%M:%S"))
        #file_path = r"results/gender_average_embeds_asian_famous_test_dlib_arcface_facenet512_1000.json"
        file_path = r"results/gender_average_embeds_asian_famous_test_dlib_arcface_facenet512_500.json"
        WriteJsonData(file_path, gender_embeds)
        print('Finishing a job')
    except Exception as ex:
        print('Error reading: {0}'.format(str(ex)))
