import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from app.domain.entities import InferenceResult
from app.shared.formatting import format_seconds


CANVAS_WIDTH = 960
CANVAS_HEIGHT = 520
FPS = 8
PIPE_ORDER = ["P1", "P2", "P3", "T1", "T2", "T3"]
PIPE_GRID_POSITIONS = {
    "P1": (0, 0),
    "P2": (0, 1),
    "P3": (1, 0),
    "T1": (1, 1),
    "T2": (2, 0),
    "T3": (2, 1),
}
PIPE_COLORS = {
    "P1": "#ff9a3c",
    "P2": "#ffbf3c",
    "P3": "#ffd94a",
    "T1": "#ff7e5f",
    "T2": "#7dcfb6",
    "T3": "#4aaed8",
}

SHEET_WIDTH = 1400
SHEET_TOP_PADDING = 48
SHEET_SIDE_PADDING = 52
SHEET_HEADER_HEIGHT = 220
SHEET_LEGEND_HEIGHT = 116
SHEET_ROW_HEIGHT = 300
SHEET_ROW_GAP = 20
SHEET_ROWS_PER_PAGE = 4


def load_font(size):
    candidates = [
        "C:/Windows/Fonts/segoeui.ttf",
        "C:/Windows/Fonts/georgia.ttf",
        "C:/Windows/Fonts/trebuc.ttf",
    ]
    for candidate in candidates:
        font_path = Path(candidate)
        if font_path.is_file():
            return ImageFont.truetype(str(font_path), size=size)
    return ImageFont.load_default()


TITLE_FONT = load_font(28)
BODY_FONT = load_font(18)
SMALL_FONT = load_font(15)
LABEL_FONT = load_font(20)
SHEET_TITLE_FONT = load_font(42)
SHEET_SUBTITLE_FONT = load_font(24)
SHEET_SECTION_FONT = load_font(26)
SHEET_ROW_TITLE_FONT = load_font(22)


def parse_active_labels(label_text):
    normalized = str(label_text).strip()
    if normalized == "" or normalized.lower() == "silence":
        return set()
    return {label.strip() for label in normalized.split(",") if label.strip()}


def get_current_segment(segments, current_time):
    if not segments:
        return None
    for segment in segments:
        if segment.start_second <= current_time < segment.end_second:
            return segment
    return segments[-1]


def draw_background(draw):
    draw.rectangle((0, 0, CANVAS_WIDTH, CANVAS_HEIGHT), fill="#f5ead8")
    draw.ellipse((-80, -60, 300, 220), fill="#ead3b1")
    draw.ellipse((680, 280, 1100, 640), fill="#e5c18f")
    draw.rectangle((0, 430, CANVAS_WIDTH, CANVAS_HEIGHT), fill="#d6b07e")


def draw_qeej_grid(draw, frame_box, inner_box, active_labels, circle_radius, font):
    draw.rounded_rectangle(frame_box, radius=34, fill="#6d4a2e", outline="#4a2f1f", width=4)
    draw.rounded_rectangle(inner_box, radius=26, fill="#f7e7c8", outline="#c9a473", width=3)

    inner_left, inner_top, inner_right, inner_bottom = inner_box
    inner_width = inner_right - inner_left
    inner_height = inner_bottom - inner_top
    col_centers = [
        inner_left + inner_width * 0.28,
        inner_left + inner_width * 0.72,
    ]
    row_centers = [
        inner_top + inner_height * 0.2,
        inner_top + inner_height * 0.5,
        inner_top + inner_height * 0.8,
    ]

    for pipe_name in PIPE_ORDER:
        row_idx, col_idx = PIPE_GRID_POSITIONS[pipe_name]
        center_x = int(col_centers[col_idx])
        center_y = int(row_centers[row_idx])
        is_active = pipe_name in active_labels

        fill_color = PIPE_COLORS[pipe_name] if is_active else "#d7b488"
        outline_color = "#7a5232"
        label_color = "#2a1a10"

        if is_active:
            glow_box = (
                center_x - circle_radius - 12,
                center_y - circle_radius - 12,
                center_x + circle_radius + 12,
                center_y + circle_radius + 12,
            )
            draw.ellipse(glow_box, fill="#fff2b8")

        circle_box = (
            center_x - circle_radius,
            center_y - circle_radius,
            center_x + circle_radius,
            center_y + circle_radius,
        )
        draw.ellipse(circle_box, fill=fill_color, outline=outline_color, width=4)

        text_box = draw.textbbox((0, 0), pipe_name, font=font)
        text_width = text_box[2] - text_box[0]
        text_height = text_box[3] - text_box[1]
        draw.text(
            (center_x - text_width / 2, center_y - text_height / 2 - 2),
            pipe_name,
            fill=label_color,
            font=font,
        )


def draw_qeej(draw, active_labels):
    draw_qeej_grid(
        draw,
        frame_box=(300, 80, 740, 410),
        inner_box=(330, 110, 710, 380),
        active_labels=active_labels,
        circle_radius=48,
        font=LABEL_FONT,
    )


def draw_progress(draw, current_time, total_duration):
    bar_x0 = 60
    bar_x1 = CANVAS_WIDTH - 60
    bar_y0 = 470
    bar_y1 = 490
    draw.rounded_rectangle((bar_x0, bar_y0, bar_x1, bar_y1), radius=12, fill="#ecd5b3")
    progress = 0.0 if total_duration <= 0 else min(1.0, current_time / total_duration)
    filled_x = bar_x0 + int((bar_x1 - bar_x0) * progress)
    draw.rounded_rectangle((bar_x0, bar_y0, filled_x, bar_y1), radius=12, fill="#b25a2b")
    draw.text(
        (bar_x0, bar_y0 - 28),
        f"Thời gian: {format_seconds(current_time)}s / {format_seconds(total_duration)}s",
        fill="#4a311f",
        font=BODY_FONT,
    )


def render_frame(result, current_time, total_duration):
    image = Image.new("RGB", (CANVAS_WIDTH, CANVAS_HEIGHT), "#f5ead8")
    draw = ImageDraw.Draw(image)

    draw_background(draw)
    current_segment = get_current_segment(result.segments, current_time)
    active_labels = parse_active_labels(current_segment.label if current_segment else "")
    draw_qeej(draw, active_labels)
    draw_progress(draw, current_time, total_duration)
    return image


def render_guide_animation(result: InferenceResult, output_path: Path):
    last_segment_end = result.segments[-1].end_second if result.segments else 0.0
    total_duration = max(result.duration_seconds, last_segment_end, 1.0)
    frame_count = max(1, int(math.ceil(total_duration * FPS)))
    frame_duration_ms = max(80, int(1000 / FPS))

    frames = []
    for frame_index in range(frame_count):
        current_time = min(total_duration, frame_index / FPS)
        frames.append(render_frame(result, current_time, total_duration))

    frames[0].save(
        output_path,
        save_all=True,
        append_images=frames[1:],
        duration=[frame_duration_ms] * max(0, len(frames) - 1) + [900],
        loop=0,
    )


def draw_sheet_background(draw, width, height):
    draw.rectangle((0, 0, width, height), fill="#f5ead8")
    draw.ellipse((-120, -80, 340, 260), fill="#ead3b1")
    draw.ellipse((width - 420, height - 360, width + 120, height + 120), fill="#e5c18f")
    draw.rectangle((0, 0, width, 170), fill="#efe0c3")


def draw_sheet_header(draw, result):
    x = SHEET_SIDE_PADDING
    y = SHEET_TOP_PADDING
    draw.text((x, y), "Tài liệu hướng dẫn", fill="#3f2918", font=SHEET_TITLE_FONT)


def draw_legend(draw, y):
    x = SHEET_SIDE_PADDING
    draw.text((x, y), "Mã màu các ống khèn", fill="#3f2918", font=SHEET_SECTION_FONT)
    chip_y = y + 42
    chip_x = x
    for pipe_name in PIPE_ORDER:
        fill_color = PIPE_COLORS[pipe_name]
        text = pipe_name
        text_box = draw.textbbox((0, 0), text, font=BODY_FONT)
        text_width = text_box[2] - text_box[0]
        pill_width = text_width + 54
        draw.rounded_rectangle(
            (chip_x, chip_y, chip_x + pill_width, chip_y + 42),
            radius=21,
            fill="#fff8ef",
            outline="#d1ac82",
            width=2,
        )
        draw.ellipse((chip_x + 12, chip_y + 10, chip_x + 32, chip_y + 30), fill=fill_color, outline="#7a5232")
        draw.text((chip_x + 40, chip_y + 10), text, fill="#4a311f", font=BODY_FONT)
        chip_x += pill_width + 12


def draw_label_chips(draw, labels, x, y):
    chip_x = x
    for label in labels:
        text_box = draw.textbbox((0, 0), label, font=SMALL_FONT)
        text_width = text_box[2] - text_box[0]
        pill_width = text_width + 30
        draw.rounded_rectangle(
            (chip_x, y, chip_x + pill_width, y + 34),
            radius=17,
            fill=PIPE_COLORS.get(label, "#fff8ef"),
            outline="#7a5232",
            width=2,
        )
        draw.text((chip_x + 15, y + 8), label, fill="#2a1a10", font=SMALL_FONT)
        chip_x += pill_width + 10


def draw_segment_row(draw, segment, row_index, y):
    x0 = SHEET_SIDE_PADDING
    x1 = SHEET_WIDTH - SHEET_SIDE_PADDING
    y1 = y + SHEET_ROW_HEIGHT

    draw.rounded_rectangle(
        (x0, y, x1, y1),
        radius=28,
        fill="#fffaf4",
        outline="#d6b07e",
        width=2,
    )

    text_x = x0 + 28
    text_y = y + 24
    active_labels = sorted(
        parse_active_labels(segment.label),
        key=lambda label: PIPE_ORDER.index(label) if label in PIPE_ORDER else len(PIPE_ORDER),
    )
    duration = max(0.0, segment.end_second - segment.start_second)

    draw.text((text_x, text_y), f"Đoạn {row_index + 1}", fill="#3f2918", font=SHEET_ROW_TITLE_FONT)
    draw.text(
        (text_x, text_y + 42),
        f"Khoảng thời gian: {format_seconds(segment.start_second)}s - {format_seconds(segment.end_second)}s",
        fill="#4a311f",
        font=BODY_FONT,
    )
    draw.text(
        (text_x, text_y + 76),
        f"Độ dài đoạn: {format_seconds(duration)}s",
        fill="#4a311f",
        font=BODY_FONT,
    )
    draw.text((text_x, text_y + 110), "Các ống đang hoạt động", fill="#6d4a2e", font=BODY_FONT)
    if active_labels:
        draw_label_chips(draw, active_labels, text_x, text_y + 144)
    else:
        draw.text((text_x, text_y + 146), "Khong co thao tac", fill="#6d4a2e", font=BODY_FONT)

    diagram_x0 = x1 - 420
    diagram_y0 = y + 18
    diagram_x1 = x1 - 28
    diagram_y1 = y1 - 18
    draw_qeej_grid(
        draw,
        frame_box=(diagram_x0, diagram_y0, diagram_x1, diagram_y1),
        inner_box=(diagram_x0 + 22, diagram_y0 + 18, diagram_x1 - 22, diagram_y1 - 18),
        active_labels=set(active_labels),
        circle_radius=34,
        font=BODY_FONT,
    )


def _build_guide_sheet_page(result, page_segments, page_number, total_pages):
    row_count = max(1, len(page_segments))
    page_height = (
        SHEET_TOP_PADDING
        + SHEET_HEADER_HEIGHT
        + SHEET_LEGEND_HEIGHT
        + row_count * SHEET_ROW_HEIGHT
        + max(0, row_count - 1) * SHEET_ROW_GAP
        + SHEET_TOP_PADDING
    )

    image = Image.new("RGB", (SHEET_WIDTH, page_height), "#f5ead8")
    draw = ImageDraw.Draw(image)

    draw_sheet_background(draw, SHEET_WIDTH, page_height)
    draw_sheet_header(draw, result)
    page_text = f"Trang {page_number}/{total_pages}"
    page_text_box = draw.textbbox((0, 0), page_text, font=BODY_FONT)
    draw.text(
        (SHEET_WIDTH - SHEET_SIDE_PADDING - (page_text_box[2] - page_text_box[0]), SHEET_TOP_PADDING + 12),
        page_text,
        fill="#6d4a2e",
        font=BODY_FONT,
    )
    legend_y = SHEET_TOP_PADDING + SHEET_HEADER_HEIGHT
    draw_legend(draw, legend_y)

    first_row_y = legend_y + SHEET_LEGEND_HEIGHT
    if page_segments:
        row_offset = (page_number - 1) * SHEET_ROWS_PER_PAGE
        for row_index, segment in enumerate(page_segments):
            row_y = first_row_y + row_index * (SHEET_ROW_HEIGHT + SHEET_ROW_GAP)
            draw_segment_row(draw, segment, row_offset + row_index, row_y)
    else:
        empty_box = (
            SHEET_SIDE_PADDING,
            first_row_y,
            SHEET_WIDTH - SHEET_SIDE_PADDING,
            first_row_y + SHEET_ROW_HEIGHT,
        )
        draw.rounded_rectangle(empty_box, radius=28, fill="#fffaf4", outline="#d6b07e", width=2)
        draw.text(
            (SHEET_SIDE_PADDING + 28, first_row_y + 42),
            "Không phát hiện ống nào được kích hoạt.",
            fill="#3f2918",
            font=SHEET_ROW_TITLE_FONT,
        )

    return image


def render_guide_sheet(result: InferenceResult, output_path: Path):
    active_segments = result.active_segments or [
        segment for segment in result.segments if segment.label.lower() != "silence"
    ]
    page_chunks = [
        active_segments[index : index + SHEET_ROWS_PER_PAGE]
        for index in range(0, len(active_segments), SHEET_ROWS_PER_PAGE)
    ] or [[]]
    total_pages = len(page_chunks)
    pages = [
        _build_guide_sheet_page(result, page_segments, page_number, total_pages)
        for page_number, page_segments in enumerate(page_chunks, start=1)
    ]

    pages[0].save(
        output_path,
        "PDF",
        resolution=100.0,
        save_all=True,
        append_images=pages[1:],
    )
