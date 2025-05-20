import cv2
import mss
import numpy as np
import pyautogui
import pytesseract
from PyQt5.QtCore import QPoint, QRect
from PyQt5.QtWidgets import QApplication
from skimage.metrics import structural_similarity as ssim

from app import Workflow, WorkflowState


def ptToTuple(pt):
    x, y = pt.x(), pt.y()
    return (x, y)


def tupleToPt(arry):
    x, y = arry
    return QPoint(x, y)


def click(wkspace: Workflow, state: WorkflowState, **kwargs):
    tl, br = wkspace.getBBox()
    tl = ptToTuple(tl)
    br = ptToTuple(br)
    mid = (np.array(tl) + np.array(br)) / 2
    pyautogui.click(int(mid[0]), int(mid[1]))


def scan(wkspace: Workflow, state: WorkflowState, **kwargs):
    parent = kwargs["parent"]
    ptl, pbr = parent.window.getBBox()
    dim = pbr - ptl
    width, height = dim.x(), dim.y()

    numScans = kwargs["count"]
    dir = kwargs["dir"]
    task = kwargs["task"]
    task.setWorkspace(wkspace)

    savedGeometry = wkspace.window.geometry()
    bbox = wkspace.window.getBBox()
    tl, br = bbox
    tl, br = np.array(ptToTuple(tl)), np.array(ptToTuple(br))
    dim = br - tl
    error = np.array([0.0, 0.0])

    task.execute(state)
    if numScans == 1:
        return

    # We have (numScans - 1) * stepSz + windowLen = regionLen
    # Solve for stepSz given direction
    if dir == "vertical":
        windowLen = dim[1]
        regionLen = height
        yStep = 1.0 * (regionLen - windowLen) / (numScans - 1)
        ds = np.array([0.0, yStep])

    else:
        windowLen = dim[0]
        regionLen = width
        xStep = 1.0 * (regionLen - windowLen) / (numScans - 1)
        ds = np.array([xStep, 0.0])

    for i in range(numScans - 1):
        tl, br = tl + ds, br + ds
        tl, br = tl + error, br + error
        newTl = tl.astype(int)
        newBr = br.astype(int)

        error = tl - newTl

        newTl = tupleToPt(newTl)
        newBr = tupleToPt(newBr)

        wkspace.setGeometry(QRect(newTl, newBr))
        QApplication.processEvents()
        task.execute(state)

    wkspace.setGeometry(savedGeometry)


def scroll(wkspace: Workflow, state: WorkflowState, **kwargs):
    dir = kwargs["dir"]
    tl, br = wkspace.getBBox()
    tl = ptToTuple(tl)
    br = ptToTuple(br)

    scrollTime = 0.3
    scrollAnim = pyautogui.easeOutQuad
    scrollClick = "left"

    x1, y1 = tl
    x2, y2 = br
    if dir in ["up", "down"]:
        xmid = (x1 + x2) / 2
        if dir == "down":
            pyautogui.moveTo(xmid, y1)
            pyautogui.dragTo(xmid, y2, scrollTime, scrollAnim, button=scrollClick)
        else:
            pyautogui.moveTo(xmid, y2)
            pyautogui.dragTo(xmid, y1, scrollTime, scrollAnim, button=scrollClick)
    else:
        ymid = (y1 + y2) / 2
        if dir == "right":
            pyautogui.moveTo(x1, ymid)
            pyautogui.dragTo(x2, ymid, scrollTime, scrollAnim, button=scrollClick)
        else:
            pyautogui.moveTo(x2, ymid)
            pyautogui.dragTo(x1, ymid, scrollTime, scrollAnim, button=scrollClick)


def screenshot(region):
    with mss.mss() as sct:
        monitor = {
            "left": region[0],
            "top": region[1],
            "width": region[2],
            "height": region[3],
        }
        screenshot = sct.grab(monitor)
        return np.array(screenshot)[:, :, :3]


def combine_images_side_by_side_np(image1, image2):
    # Resize to the same height if necessary
    if image1.shape[0] != image2.shape[0]:
        new_height = min(image1.shape[0], image2.shape[0])
        image1 = cv2.resize(
            image1, (int(image1.shape[1] * new_height / image1.shape[0]), new_height)
        )
        image2 = cv2.resize(
            image2, (int(image2.shape[1] * new_height / image2.shape[0]), new_height)
        )

    # Combine horizontally
    combined_image = np.hstack((image1, image2))

    return combined_image


def imageMatch(wkspace: Workflow, state: WorkflowState, **kwargs):
    tl, br = wkspace.getBBox()
    frame = wkspace.window.frameGeometry()
    region = (tl.x(), tl.y(), frame.width(), frame.height())

    ss = screenshot(region)
    threshold = 0.8
    img = kwargs["img"]
    if "threshold" in kwargs:
        threshold = kwargs["threshold"]

    ss = alignImages(img, ss)
    score = computeSSIM(ss, img)

    tmp = state.getTemporaryState()
    tmp["result"] = score >= threshold


def filterNumbers(wkspace: Workflow, state: WorkflowState, **kwargs):
    tl, br = wkspace.getBBox()
    frame = wkspace.window.frameGeometry()
    region = (tl.x(), tl.y(), frame.width(), frame.height())

    image = screenshot(region)
    image = filterColor(image, rgbToHsv(kwargs["lBound"]), rgbToHsv(kwargs["uBound"]))

    # Denoise the image
    image = cv2.fastNlMeansDenoising(image, None, 30, 7, 21)
    _, image = cv2.threshold(image, 127, 255, cv2.THRESH_BINARY)
    contours, _ = cv2.findContours(image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    # Create a blank mask to draw on
    filtered_mask = np.zeros_like(image)

    # Filter contours by area
    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)  # Get the bounding box
        aspect_ratio = 1.0 * h / w
        if 1.2 <= aspect_ratio:
            cv2.drawContours(filtered_mask, [contour], -1, (255), thickness=cv2.FILLED)

    # Resulting image
    image = cv2.bitwise_and(image, filtered_mask)

    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    image = cv2.dilate(image, kernel, iterations=1)

    text = pytesseract.image_to_string(image, config="--psm 6 digits")
    try:
        count = int(text)
    except ValueError:
        count = 1

    return count


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


def filterColor(image, lower_bound, upper_bound):
    # Convert to HSV color space
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    # Create a mask for the specific color range
    mask = cv2.inRange(hsv, lower_bound, upper_bound)

    return mask


def rgbToHsv(rgb):
    rgb = np.uint8([[rgb]])  # Convert RGB into OpenCV format
    hsv = cv2.cvtColor(rgb, cv2.COLOR_RGB2HSV)
    return hsv[0][0]  # Extract the HSV values
