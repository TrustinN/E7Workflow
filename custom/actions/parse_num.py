import cv2
import numpy as np
from skimage.metrics import structural_similarity as ssim


def filterNumbers(context, postAction):
    image = postAction["capture"]
    image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Denoise the image
    image = cv2.fastNlMeansDenoising(image, None, 30, 7, 21)
    _, image = cv2.threshold(image, 127, 255, cv2.THRESH_BINARY)
    contours, _ = cv2.findContours(image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Create a blank mask to draw on
    filteredMask = np.zeros_like(image)

    # Removing noisy regions and commas from image
    if len(contours) > 0:
        yMin = min(cv2.boundingRect(contour)[1] for contour in contours)
        yMax = max(
            cv2.boundingRect(contour)[1] + cv2.boundingRect(contour)[3]
            for contour in contours
        )
        yMid = (yMin + yMax) / 2

    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)  # Get the bounding box
        aspect = 1.0 * h / w
        if 1.2 <= aspect and y <= yMid:
            cv2.drawContours(filteredMask, [contour], -1, (255), thickness=cv2.FILLED)

    # Cleaned image
    image = cv2.bitwise_and(image, filteredMask)

    # Extract individual digits and match with digitIcon assets
    cnts = cv2.findContours(image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = cnts[0] if len(cnts) == 2 else cnts[1]
    cnts = sorted(cnts, key=lambda c: cv2.boundingRect(c)[0])
    count = 0
    if len(cnts) > 0:
        digits = []
        for c, num in zip(cnts, range(len(cnts))):
            x, y, w, h = cv2.boundingRect(c)
            ROI = 255 - image[y : y + h, x : x + w]
            maxScore = -np.inf
            digit = -1

            # Ensure image size is large enough for ssim
            if w < 7 or h < 7:
                continue

            for i in range(10):
                digitIcon = context[f"digit_{i}"]
                roi = cv2.resize(
                    ROI,
                    (digitIcon.shape[1], digitIcon.shape[0]),
                    interpolation=cv2.INTER_LANCZOS4,
                )

                simScore, _ = ssim(digitIcon, roi, full=True)
                if simScore > maxScore:
                    maxScore = simScore
                    digit = i

            digits.append(digit)

        count = int("".join(map(str, digits)))

    return count
