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


def process_video(input_path, output_path, mosaic_scale=0.06):
    mp_face = mp.solutions.face_detection

    cap = cv2.VideoCapture(input_path)

    if not cap.isOpened():
        raise RuntimeError(f"Could not open video: {input_path}")

    fps = cap.get(cv2.CAP_PROP_FPS)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    writer = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

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

            if results.detections:
                for detection in results.detections:
                    bbox = detection.location_data.relative_bounding_box

                    x = int(bbox.xmin * width)
                    y = int(bbox.ymin * height)
                    w = int(bbox.width * width)
                    h = int(bbox.height * height)

                    # Add margin around face
                    margin = int(0.25 * max(w, h))
                    x = max(0, x - margin)
                    y = max(0, y - margin)
                    w = min(width - x, w + 2 * margin)
                    h = min(height - y, h + 2 * margin)

                    frame = mosaic_region(frame, x, y, w, h, scale=mosaic_scale)

            writer.write(frame)

    cap.release()
    writer.release()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("input", help="Input MP4 path")
    parser.add_argument("output", help="Output MP4 path")
    parser.add_argument("--scale", type=float, default=0.06, help="Smaller = stronger mosaic")

    args = parser.parse_args()
    process_video(args.input, args.output, args.scale)
