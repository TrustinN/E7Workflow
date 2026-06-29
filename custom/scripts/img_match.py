import cv2
import numpy as np
from skimage.metrics import structural_similarity as ssim


def alignImages(img1, img2):
    try:
        # Convert images to grayscale
        gray1 = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY) if len(img1.shape) == 3 else img1
        gray2 = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY) if len(img2.shape) == 3 else img2

        # Detect ORB keypoints and descriptors
        orb = cv2.ORB_create(nfeatures=5000)
        keypoints1, descriptors1 = orb.detectAndCompute(gray1, None)
        keypoints2, descriptors2 = orb.detectAndCompute(gray2, None)

        if descriptors1 is None or descriptors2 is None:
            raise ValueError("No features detected in one or both images.")

        # Match features using KNN matcher
        bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=False)
        matches = bf.knnMatch(descriptors1, descriptors2, k=2)

        # Apply Lowe's ratio test
        good_matches = [m for m, n in matches if m.distance < 0.75 * n.distance]

        if len(good_matches) < 4:
            raise ValueError("Not enough good matches to align images.")

        # Extract matched keypoints
        points1 = np.float32([keypoints1[m.queryIdx].pt for m in good_matches])
        points2 = np.float32([keypoints2[m.trainIdx].pt for m in good_matches])

        # Estimate affine transformation
        matrix, inliers = cv2.estimateAffinePartial2D(
            points2, points1, method=cv2.RANSAC
        )

        if matrix is None:
            raise ValueError("Failed to estimate transformation matrix.")

        # Align img2 to img1
        aligned_img2 = cv2.warpAffine(img2, matrix, (img1.shape[1], img1.shape[0]))

        return aligned_img2

    except ValueError:
        # Resize img2 to match img1 dimensions
        resized_img2 = cv2.resize(img2, (img1.shape[1], img1.shape[0]))
        return resized_img2


def computeSSIM(img1, img2):
    """
    Computes the Structural Similarity Index (SSIM) between two images.

    Args:
        img1 (np.ndarray): First image (grayscale or RGB).
        img2 (np.ndarray): Second image (grayscale or RGB).

    Returns:
        float: SSIM value (1.0 means identical, lower values indicate less similarity).
    """
    # Ensure images are grayscale for SSIM computation
    if len(img1.shape) == 3:
        img1 = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
    if len(img2.shape) == 3:
        img2 = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)

    # Resize images to match dimensions if needed
    if img1.shape != img2.shape:
        raise ValueError("Images must have the same dimensions for SSIM computation.")

    # Compute SSIM
    score, _ = ssim(img1, img2, full=True)

    return score


def condition(context):
    threshold = 0.8
    img = context["img"]
    img2 = context["img2"]

    img2 = alignImages(img, img2)
    score = computeSSIM(img2, img)
    return score >= threshold
