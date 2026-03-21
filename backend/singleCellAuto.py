import cv2
import numpy as np


def rule_to_map(rule_number: int) -> dict[tuple[int, int, int], int]:
    if not (0 <= rule_number <= 255):
        raise ValueError("rule_number must be between 0 and 255")
    
    # rule_number is converted to an 8-bit binary string, where each bit corresponds to a specific neighborhood configuration
    bits = f"{rule_number:08b}"
    neighborhoods = [
        (1, 1, 1),
        (1, 1, 0),
        (1, 0, 1),
        (1, 0, 0),
        (0, 1, 1),
        (0, 1, 0),
        (0, 0, 1),
        (0, 0, 0),
    ]
    return {n: int(bit) for n, bit in zip(neighborhoods, bits)}


def next_generation(row: np.ndarray, rule_map: dict[tuple[int, int, int], int], wrap: bool = False) -> np.ndarray:
    width = len(row)
    new_row = np.zeros_like(row)

    for i in range(width):
        if wrap:
            left = row[i - 1] if i > 0 else row[-1]
            center = row[i]
            right = row[i + 1] if i < width - 1 else row[0]
        else:
            left = row[i - 1] if i > 0 else 0
            center = row[i]
            right = row[i + 1] if i < width - 1 else 0

        new_row[i] = rule_map[(int(left), int(center), int(right))]

    return new_row


def render_grid(grid: np.ndarray, cell_size: int = 6) -> np.ndarray:
    img = np.where(grid == 1, 0, 255).astype(np.uint8)

    img = cv2.resize(
        img,
        (grid.shape[1] * cell_size, grid.shape[0] * cell_size),
        interpolation=cv2.INTER_NEAREST,
    )

    if len(img.shape) == 2:
        img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)

    return img


def animate_rule(
    rule_number: int = 110, width: int = 151, steps: int = 120, cell_size: int = 6,
    fps: int = 10, output_path: str = "rule110.mp4", wrap: bool = False, show_preview: bool = True,
    ) -> None:

    rule_map = rule_to_map(rule_number)
    row = np.zeros(width, dtype=np.uint8)
    row[width // 2] = 1

    grid = np.zeros((steps, width), dtype=np.uint8)
    grid[0] = row

    frame_width = width * cell_size
    frame_height = steps * cell_size

    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    writer = cv2.VideoWriter(output_path, fourcc, fps, (frame_width, frame_height))

    for t in range(steps):
        if t > 0:
            row = next_generation(row, rule_map, wrap=wrap)
            grid[t] = row

        frame = render_grid(grid[: t + 1], cell_size=cell_size)

        if frame.shape[0] < frame_height:
            pad_height = frame_height - frame.shape[0]
            pad = np.full((pad_height, frame_width, 3), 255, dtype=np.uint8)
            frame = np.vstack([frame, pad])

        writer.write(frame)

        if show_preview:
            cv2.imshow(f"Rule {rule_number}", frame)
            key = cv2.waitKey(int(1000 / fps))
            if key == 27:
                break

    writer.release()
    cv2.destroyAllWindows()
    print(f"Saved video to {output_path}")

RULE110_ETHER = "00010011011111"
RULE110_GLIDER = "0001110111"


def pattern_to_array(pattern: str) -> np.ndarray:
    bits = [int(ch) for ch in pattern if ch in "01"]
    if not bits:
        raise ValueError("pattern must contain at least one binary digit")
    return np.array(bits, dtype=np.uint8)

# ether is a repeating background pattern that can support gliders
# this is necessary for computiation to have a preset patter. 
def build_ether_row(width: int, tile: str = RULE110_ETHER) -> np.ndarray:
    tile_bits = pattern_to_array(tile)
    repeats = (width + len(tile_bits) - 1) // len(tile_bits)
    return np.tile(tile_bits, repeats)[:width].copy()


def place_pattern(row: np.ndarray, pattern: str, start: int) -> np.ndarray:
    bits = pattern_to_array(pattern)
    row = row.copy()
    left = max(start, 0)
    right = min(start + len(bits), len(row))
    if left >= right:
        return row

    src_left = left - start
    src_right = src_left + (right - left)
    row[left:right] = bits[src_left:src_right]
    return row


def simulate_rule_grid(rule_number: int, initial_row: np.ndarray, steps: int, wrap: bool = False,) -> np.ndarray:
    if steps < 1:
        raise ValueError("steps must be at least 1")

    rule_map = rule_to_map(rule_number)
    row = initial_row.astype(np.uint8).copy()
    grid = np.zeros((steps, len(row)), dtype=np.uint8)
    grid[0] = row

    for t in range(1, steps):
        row = next_generation(row, rule_map, wrap=wrap)
        grid[t] = row

    return grid


def add_inputs(a: int, b: int) -> int:
    if a < 0 or b < 0:
        raise ValueError("addition demo expects non-negative integers")
    return a + b


def build_initial_row(preset: str, width: int, rule_number: int, a: int = 3, b: int = 5,) -> tuple[np.ndarray, list[str]]:
    # Single seed starts from the first row and builds
    if preset == "single_seed":
        row = np.zeros(width, dtype=np.uint8)
        row[width // 2] = 1
        return row, [f"Rule {rule_number} single-seed evolution"]

    # Rule 110 glider showcase stats with a pattern that will produce a glider 
    if preset == "rule110_glider":
        row = build_ether_row(width)
        start = max(0, (width - len(RULE110_GLIDER)) // 2)
        row = place_pattern(row, RULE110_GLIDER, start)
        return row, [
            "Rule 110 glider showcase",
            f"Ether: {RULE110_ETHER}",
            f"Localized pattern: {RULE110_GLIDER}",
        ]

    # Makes two gliders that will collide
    if preset == "rule110_collision":
        row = build_ether_row(width)
        first = width // 4
        second = (2 * width) // 3
        row = place_pattern(row, RULE110_GLIDER, first)
        row = place_pattern(row, RULE110_GLIDER, second)
        return row, [
            "Rule 110 collision showcase",
            f"Two glider seeds embedded in ether: {RULE110_ETHER}",
        ]

    if preset == "rule110_addition":
        total = add_inputs(a, b)
        row = build_ether_row(width)
        encoded_a = format(a, "b")
        encoded_b = format(b, "b")
        encoded_sum = format(total, "b")
        spacer = RULE110_ETHER * 2
        separator = RULE110_GLIDER + RULE110_ETHER
        payload = spacer.join(
            [
                encoded_a.replace("1", RULE110_GLIDER).replace("0", RULE110_ETHER),
                separator,
                encoded_b.replace("1", RULE110_GLIDER).replace("0", RULE110_ETHER),
                separator,
                encoded_sum.replace("1", RULE110_GLIDER).replace("0", RULE110_ETHER),
            ]
        )
        start = max(0, (width - len(payload)) // 2)
        row = place_pattern(row, payload, start)
        return row, [
            "Rule 110 addition showcase",
            f"A={a} ({encoded_a})  B={b} ({encoded_b})  Sum={total} ({encoded_sum})",
            "The row encodes inputs and expected output on a Rule 110 ether background.",
        ]

    raise ValueError(f"unknown preset: {preset}")


def annotate_frame(frame: np.ndarray, lines: list[str]) -> np.ndarray:
    if not lines:
        return frame

    top_pad = 24 + (20 * len(lines))
    annotated = cv2.copyMakeBorder(frame,top_pad,0,0,0,cv2.BORDER_CONSTANT,value=(245, 245, 245),)

    for index, line in enumerate(lines):
        y = 22 + (index * 20)
        cv2.putText(annotated,line,(12, y),cv2.FONT_HERSHEY_SIMPLEX,0.5,(20, 20, 20),1,cv2.LINE_AA,)

    return annotated


def animate_preset(
    preset: str = "rule110_glider",
    rule_number: int = 110,
    width: int = 220,
    steps: int = 160,
    cell_size: int = 6,
    fps: int = 10,
    output_path: str = "rule110_showcase.mp4",
    wrap: bool = False,
    show_preview: bool = False,
    a: int = 3,
    b: int = 5,
) -> None:
    initial_row, labels = build_initial_row(preset, width, rule_number, a=a, b=b)
    grid = simulate_rule_grid(rule_number, initial_row, steps, wrap=wrap)

    base_frame_width = width * cell_size
    base_frame_height = steps * cell_size
    sample_frame = annotate_frame(render_grid(grid[:1], cell_size=cell_size), labels)
    frame_width = sample_frame.shape[1]
    frame_height = sample_frame.shape[0]

    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    writer = cv2.VideoWriter(output_path, fourcc, fps, (frame_width, frame_height))

    for t in range(steps):
        frame = render_grid(grid[: t + 1], cell_size=cell_size)

        if frame.shape[0] < base_frame_height:
            pad_height = base_frame_height - frame.shape[0]
            pad = np.full((pad_height, base_frame_width, 3), 255, dtype=np.uint8)
            frame = np.vstack([frame, pad])

        frame = annotate_frame(frame, labels)
        writer.write(frame)

        if show_preview:
            cv2.imshow(f"Rule {rule_number} - {preset}", frame)
            key = cv2.waitKey(int(1000 / fps))
            if key == 27:
                break

    writer.release()
    cv2.destroyAllWindows()
    print(f"Saved video to {output_path}")


def main():
    animate_rule(
        rule_number=90,
        width=100,
        steps=120,
        cell_size=6,
        fps=10,
        output_path="rule110.mp4",
        wrap=False,
        show_preview=True,
    import argparse

    parser = argparse.ArgumentParser(
        description="Render elementary cellular automata, including Rule 110 showcases."
    )
    parser.add_argument(
        "--preset",
        choices=[
            "single_seed",
            "rule110_glider",
            "rule110_collision",
            "rule110_addition",
        ],
        default="rule110_glider",
        help="Initial-condition showcase to render.",
    )
    parser.add_argument("--rule", type=int, default=110, help="Elementary CA rule number.")
    parser.add_argument("--width", type=int, default=220, help="Number of cells in each row.")
    parser.add_argument("--steps", type=int, default=160, help="Number of generations to render.")
    parser.add_argument("--cell-size", type=int, default=6, help="Pixel size for each cell.")
    parser.add_argument("--fps", type=int, default=10, help="Frames per second for the video.")
    parser.add_argument("--output", default="", help="Output video path.")
    parser.add_argument("--wrap", action="store_true", help="Use wraparound boundary conditions.")
    parser.add_argument("--preview", action="store_true", help="Show a live OpenCV preview window.")
    parser.add_argument("--a", type=int, default=3, help="First integer input for addition showcase.")
    parser.add_argument("--b", type=int, default=5, help="Second integer input for addition showcase.")
    args = parser.parse_args()

    output_path = args.output or f"{args.preset}_rule{args.rule}.mp4"
    animate_preset(
        preset=args.preset,
        rule_number=args.rule,
        width=args.width,
        steps=args.steps,
        cell_size=args.cell_size,
        fps=args.fps,
        output_path=output_path,
        wrap=args.wrap,
        show_preview=args.preview,
        a=args.a,
        b=args.b,
    )
if __name__ == "__main__":
    main()