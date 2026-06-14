import cv2
import mediapipe as mp
import argparse


def mosaic_region(img, x, y, w, h, scale=0.06):
    """Apply pixel mosaic to a rectangular region."""
    roi = img[y:y+h, x:x+w]

    if roi.size == 0:
        return img

    small_w = max(1, int(w * scale))
    small_h = max(1, int(h * scale))

    small = cv2.resize(roi, (small_w, small_h), interpolation=cv2.INTER_LINEAR)
    mosaic = cv2.resize(small, (w, h), interpolation=cv2.INTER_NEAREST)

    img[y:y+h, x:x+w] = mosaic
    return img


def best_detection_center(detections, width, height):
    """Pick the single most prominent face (largest area) and return its
    center and size in pixels. Assumes one subject per video."""
    best = None
    best_area = -1.0
    for d in detections:
        bbox = d.location_data.relative_bounding_box
        w = bbox.width * width
        h = bbox.height * height
        area = w * h
        if area > best_area:
            best_area = area
            cx = (bbox.xmin + bbox.width / 2.0) * width
            cy = (bbox.ymin + bbox.height / 2.0) * height
            best = (cx, cy, w, h)
    return best


def fill_missing_centers(centers):
    """Fill frames with no detection by linearly interpolating the face center
    from the nearest detected frames; leading/trailing gaps hold the nearest
    available center. Assumes a single, continuously-present face."""
    n = len(centers)
    known = [i for i, c in enumerate(centers) if c is not None]
    if not known:
        return centers

    filled = list(centers)

    # Leading gap: hold first known center.
    first = known[0]
    for i in range(first):
        filled[i] = centers[first]

    # Trailing gap: hold last known center.
    last = known[-1]
    for i in range(last + 1, n):
        filled[i] = centers[last]

    # Interior gaps: linear interpolation between bracketing detections.
    for a, b in zip(known, known[1:]):
        if b - a <= 1:
            continue
        (ax, ay), (bx, by) = centers[a], centers[b]
        for i in range(a + 1, b):
            t = (i - a) / (b - a)
            filled[i] = (ax + (bx - ax) * t, ay + (by - ay) * t)

    return filled


def process_video(input_path, output_path, mosaic_scale=0.06, margin_ratio=0.25):
    mp_face = mp.solutions.face_detection

    cap = cv2.VideoCapture(input_path)
    if not cap.isOpened():
        raise RuntimeError(f"Could not open video: {input_path}")

    fps = cap.get(cv2.CAP_PROP_FPS)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    # Pass 1: detect the single face in every frame.
    centers = []   # (cx, cy) per frame, or None when nothing was detected
    sizes = []     # (w, h) for frames where a face was found
    with mp_face.FaceDetection(
        model_selection=1,
        min_detection_confidence=0.5
    ) as face_detection:
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = face_detection.process(rgb)

            best = (best_detection_center(results.detections, width, height)
                    if results.detections else None)
            if best is not None:
                cx, cy, w, h = best
                centers.append((cx, cy))
                sizes.append((w, h))
            else:
                centers.append(None)
    cap.release()

    if not sizes:
        raise RuntimeError("No face detected in any frame; nothing to mosaic.")

    # The face stays roughly the same size, so use a single robust box size
    # (median) for every frame. This avoids size jitter and covers frames that
    # were filled by interpolation.
    sizes.sort(key=lambda s: s[0])
    box_w = sizes[len(sizes) // 2][0]
    sizes.sort(key=lambda s: s[1])
    box_h = sizes[len(sizes) // 2][1]

    centers = fill_missing_centers(centers)

    # Pass 2: re-read and mosaic a fixed-size box around the (filled) center.
    cap = cv2.VideoCapture(input_path)
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    writer = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

    margin_w = box_w * margin_ratio
    margin_h = box_h * margin_ratio

    idx = 0
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        center = centers[idx] if idx < len(centers) else None
        if center is not None:
            cx, cy = center
            x = int(round(cx - box_w / 2.0 - margin_w))
            y = int(round(cy - box_h / 2.0 - margin_h))
            w = int(round(box_w + 2 * margin_w))
            h = int(round(box_h + 2 * margin_h))

            x = max(0, x)
            y = max(0, y)
            w = min(width - x, w)
            h = min(height - y, h)

            frame = mosaic_region(frame, x, y, w, h, scale=mosaic_scale)

        writer.write(frame)
        idx += 1

    cap.release()
    writer.release()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("input", help="Input MP4 path")
    parser.add_argument("output", help="Output MP4 path")
    parser.add_argument("--scale", type=float, default=0.10, help="Smaller = stronger mosaic")
    parser.add_argument("--margin", type=float, default=0.2,
                        help="Box padding as a fraction of face size; smaller = tighter mosaic")

    args = parser.parse_args()
    process_video(args.input, args.output, args.scale, args.margin)
