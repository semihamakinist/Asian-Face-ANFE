
from skimage import transform as trans
import numpy as np
import math
import sys
import cv2

#<--left profile
src1 = np.array([[51.642, 50.115],
                 [57.617, 49.990],
                 [35.740, 69.007],
                 [51.157, 89.050],
                 [57.025, 89.702]],
                dtype=np.float32)
#<--left
src2 = np.array([[45.031, 50.118],
                 [65.568, 50.872],
                 [39.677, 68.111],
                 [45.177, 86.190],
                 [64.246, 86.758]],
                dtype=np.float32)

#---frontal
src3 = np.array([[39.730, 51.138],
                 [72.270, 51.138],
                 [56.000, 68.493],
                 [42.463, 87.010],
                 [69.537, 87.010]],
                dtype=np.float32)

#-->right
src4 = np.array([[46.845, 50.872],
                 [67.382, 50.118],
                 [72.737, 68.111],
                 [48.167, 86.758],
                 [67.236, 86.190]],
                dtype=np.float32)

#-->right profile
src5 = np.array([[54.796, 49.990],
                 [60.771, 50.115],
                 [76.673, 69.007],
                 [55.388, 89.702],
                 [61.257, 89.050]],
                dtype=np.float32)

src = np.array([src1, src2, src3, src4, src5])
src_map = {112: src, 224: src * 2}

arcface_src = np.array(
    [[38.2946, 51.6963],
     [73.5318, 51.5014],
     [56.0252, 71.7366],
     [41.5493, 92.3655],
     [70.7299, 92.2041]],
    dtype=np.float32)

arcface_src = np.expand_dims(arcface_src, axis=0)
MAX_IMG_SIZE = 1024 * 1024


def resize_if_big(im_cv):
    """
    Max allowed buffer to enroll is 1024 KB, resize to smaller size if needed
    """
    height, width, channels = im_cv.shape
    img_size = width * height * channels
    print(f"{width} x {height} x {channels} - {img_size > MAX_IMG_SIZE}")

    if channels != 3:
        print("image must be bgr24")
        sys.exit(1)

    if img_size > MAX_IMG_SIZE:
        scale = math.sqrt(MAX_IMG_SIZE / img_size)
        im_cv = cv2.resize(im_cv, (0, 0), fx=scale, fy=scale)
        # height, width, channels = im_cv.shape
        # img_size_kb = int(width * height * channels/1024)
        # print(f"Scale_value: {scale}-{MAX_IMG_SIZE}-{img_size},
        # Scaled down to {width}x{height} ({img_size_kb} KB)
        # to fit max size")
    return im_cv


# lmk is prediction; src is template
def estimate_norm(lmk, image_size=112, mode='arcface'):
    assert lmk.shape == (5, 2)
    tform = trans.SimilarityTransform()
    lmk_tran = np.insert(lmk, lmk.shape[1], values=np.ones(lmk.shape[0]), axis=1)
    min_M = []
    min_index = []
    min_angle = float('inf')
    min_lnd = []
    if mode == 'arcface':
        assert image_size == 112
        src = arcface_src
    else:
        src = src_map[image_size]

    for i in np.arange(src.shape[0]):
        tform.estimate(lmk, src[i])
        M = tform.params[0:2, :]
        results = np.dot(M, lmk_tran.T)
        results = results.T
        # print(f"{results[2][0] }x{src[i][2][0]} -- sag_sol: {results[2][0] - src[i][2][0]}")
        # print(f"{results[2][1] }x{src[i][2][1]} -- yukari_asagi: {results[2][1] - src[i][2][1]}")

        angle = np.sum(np.sqrt(np.sum((results - src[i])**2, axis=1)))
        if angle < min_angle:
            min_angle = angle
            min_M = M
            min_index = i
            min_lnd = results
    return min_M, min_index, min_angle, min_lnd


def norm_crop(img, landmark, image_size=112, mode='arcface'):
    M, pose_index, angle, n_landmark = estimate_norm(landmark, image_size, mode)
    warped = cv2.warpAffine(img, M, (image_size, image_size), borderValue=0.0)
    return warped, angle, n_landmark


def square_crop(im, S):
    if im.shape[0] > im.shape[1]:
        height = S
        width = int(float(im.shape[1]) / im.shape[0] * S)
        scale = float(S) / im.shape[0]
    else:
        width = S
        height = int(float(im.shape[0]) / im.shape[1] * S)
        scale = float(S) / im.shape[1]
    resized_im = cv2.resize(im, (width, height))
    det_im = np.zeros((S, S, 3), dtype=np.uint8)
    det_im[:resized_im.shape[0], :resized_im.shape[1], :] = resized_im
    return det_im, scale


def transform(data, center, output_size, scale, rotation):
    scale_ratio = scale
    rot = float(rotation) * np.pi / 180.0
    #translation = (output_size/2-center[0]*scale_ratio, output_size/2-center[1]*scale_ratio)
    t1 = trans.SimilarityTransform(scale=scale_ratio)
    cx = center[0] * scale_ratio
    cy = center[1] * scale_ratio
    t2 = trans.SimilarityTransform(translation=(-1 * cx, -1 * cy))
    t3 = trans.SimilarityTransform(rotation=rot)
    t4 = trans.SimilarityTransform(translation=(output_size / 2,
                                                output_size / 2))
    t = t1 + t2 + t3 + t4
    M = t.params[0:2]
    cropped = cv2.warpAffine(data,
                             M, (output_size, output_size),
                             borderValue=0.0)
    return cropped, M


def trans_points2d(pts, M):
    new_pts = np.zeros(shape=pts.shape, dtype=np.float32)
    for i in range(pts.shape[0]):
        pt = pts[i]
        new_pt = np.array([pt[0], pt[1], 1.], dtype=np.float32)
        new_pt = np.dot(M, new_pt)
        #print('new_pt', new_pt.shape, new_pt)
        new_pts[i] = new_pt[0:2]

    return new_pts


def trans_points3d(pts, M):
    scale = np.sqrt(M[0][0] * M[0][0] + M[0][1] * M[0][1])
    #print(scale)
    new_pts = np.zeros(shape=pts.shape, dtype=np.float32)
    for i in range(pts.shape[0]):
        pt = pts[i]
        new_pt = np.array([pt[0], pt[1], 1.], dtype=np.float32)
        new_pt = np.dot(M, new_pt)
        #print('new_pt', new_pt.shape, new_pt)
        new_pts[i][0:2] = new_pt[0:2]
        new_pts[i][2] = pts[i][2] * scale

    return new_pts


def trans_points(pts, M):
    if pts.shape[1] == 2:
        return trans_points2d(pts, M)
    else:
        return trans_points3d(pts, M)
