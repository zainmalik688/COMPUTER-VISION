"""Match ORB features between an image and a rotated copy."""

from __future__ import annotations

import argparse
from pathlib import Path

import cv2
import matplotlib.pyplot as plt


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Match ORB features between an image and a rotated copy."
    )
    parser.add_argument("image", type=Path, help="Path to the input image")
    parser.add_argument(
        "--angle",
        type=float,
        default=45.0,
        help="Rotation angle in degrees (default: 45)",
    )
    parser.add_argument(
        "--max-matches",
        type=int,
        default=100,
        help="Maximum number of best matches to draw (default: 100)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("outputs/task-01-matches.png"),
        help=(
            "Path to save the match visualization "
            "(default: outputs/task-01-matches.png)"
        ),
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.max_matches < 1:
        print("Error: --max-matches must be at least 1.")
        return 2

    image = cv2.imread(str(args.image), cv2.IMREAD_GRAYSCALE)
    if image is None:
        print(f"Error: Could not read image: {args.image}")
        return 1

    rows, cols = image.shape
    rotation = cv2.getRotationMatrix2D((cols / 2, rows / 2), args.angle, 1.0)
    rotated = cv2.warpAffine(image, rotation, (cols, rows))

    detector = cv2.ORB_create(nfeatures=1500)
    keypoints_original, descriptors_original = detector.detectAndCompute(image, None)
    keypoints_rotated, descriptors_rotated = detector.detectAndCompute(rotated, None)

    if descriptors_original is None or descriptors_rotated is None:
        print("Error: No ORB descriptors were detected in one or both images.")
        return 1

    matcher = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
    matches = sorted(
        matcher.match(descriptors_original, descriptors_rotated),
        key=lambda match: match.distance,
    )
    selected_matches = matches[: args.max_matches]

    print(f"Total matches found: {len(matches)}")
    print(f"Matches displayed: {len(selected_matches)}")

    visualization = cv2.drawMatches(
        image,
        keypoints_original,
        rotated,
        keypoints_rotated,
        selected_matches,
        None,
        flags=cv2.DrawMatchesFlags_NOT_DRAW_SINGLE_POINTS,
    )
    visualization_rgb = cv2.cvtColor(visualization, cv2.COLOR_BGR2RGB)

    plt.figure(figsize=(15, 8))
    plt.imshow(visualization_rgb)
    plt.title(f"ORB Feature Matching (rotation: {args.angle:g} degrees)")
    plt.axis("off")
    plt.tight_layout()

    args.output.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(args.output, bbox_inches="tight")
    print(f"Visualization saved to: {args.output}")

    plt.show()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
