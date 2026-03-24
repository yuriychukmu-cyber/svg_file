from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import TYPE_CHECKING
from xml.etree.ElementTree import Element, SubElement, tostring

if TYPE_CHECKING:
    from PyQt5.QtWidgets import QApplication

DEFAULT_FONT_FAMILY = "Times New Roman"
DEFAULT_FONT_SIZE = 20
DEFAULT_STROKE_WIDTH = 1
DEFAULT_TEXT_COLOR = "black"
DEFAULT_BOX_FILL = "none"
DEFAULT_BOX_STROKE = "black"
DEFAULT_OUTER_PADDING = 10
DEFAULT_VERTICAL_GAP = 0
DEFAULT_FIT_TO_MAX_WIDTH = True
DEFAULT_AS_SINGLE_CELL = True
DEFAULT_TITLE_PADDING = (16, 8)
DEFAULT_TYPE_PADDING = (16, 8)
DEFAULT_DESCRIPTION_PADDING = (16, 8)


def _ensure_qt_app():
    """Возвращает существующий QApplication или создает новый в offscreen-режиме."""
    from PyQt5.QtWidgets import QApplication

    app = QApplication.instance()
    if app is not None:
        return app

    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    return QApplication(sys.argv[:1])


def _measure_text_qt(text: str, font_family: str, font_size: int) -> dict:
    """Измеряет текст через PyQt5 QFontMetrics."""
    if not text:
        text = " "

    from PyQt5.QtGui import QFont, QFontMetrics

    _ensure_qt_app()

    font = QFont(font_family, font_size)
    metrics = QFontMetrics(font)

    text_width = int(metrics.horizontalAdvance(text))
    ascent = int(metrics.ascent())
    descent = int(metrics.descent())
    text_height = int(metrics.height())

    return {
        "text_width": text_width,
        "text_height": text_height,
        "ascent": ascent,
        "descent": descent,
    }


def _draw_row_text(
    parent,
    x: float,
    y: float,
    width: float,
    height: float,
    text: str,
    font_family: str,
    font_size: int,
    metrics: dict,
    text_color: str,
) -> None:
    """Рисует текст по центру указанной строки."""
    text_x = x + width / 2
    text_y = y + (height - metrics["text_height"]) / 2 + metrics["ascent"]

    text_el = SubElement(
        parent,
        "text",
        {
            "x": str(text_x),
            "y": str(text_y),
            "font-family": font_family,
            "font-size": str(font_size),
            "fill": text_color,
            "text-anchor": "middle",
            "xml:space": "preserve",
        },
    )
    text_el.text = text


def make_svg_card_3_lines(
    title: str,
    data_type: str,
    description: str,
    output_path: str = "card_3_lines.svg",
    font_family: str = DEFAULT_FONT_FAMILY,
    title_font_size: int = DEFAULT_FONT_SIZE,
    type_font_size: int = DEFAULT_FONT_SIZE,
    description_font_size: int = DEFAULT_FONT_SIZE,
    title_padding_x: int = DEFAULT_TITLE_PADDING[0],
    title_padding_y: int = DEFAULT_TITLE_PADDING[1],
    type_padding_x: int = DEFAULT_TYPE_PADDING[0],
    type_padding_y: int = DEFAULT_TYPE_PADDING[1],
    description_padding_x: int = DEFAULT_DESCRIPTION_PADDING[0],
    description_padding_y: int = DEFAULT_DESCRIPTION_PADDING[1],
    stroke_width: int = DEFAULT_STROKE_WIDTH,
    text_color: str = DEFAULT_TEXT_COLOR,
    box_fill: str = DEFAULT_BOX_FILL,
    box_stroke: str = DEFAULT_BOX_STROKE,
    background: str | None = None,
    outer_padding: int = DEFAULT_OUTER_PADDING,
    vertical_gap: int = DEFAULT_VERTICAL_GAP,
    fit_to_max_width: bool = DEFAULT_FIT_TO_MAX_WIDTH,
    as_single_cell: bool = DEFAULT_AS_SINGLE_CELL,
) -> dict:
    """Создает SVG-карточку из 3 строк."""

    title = title if title else " "
    data_type = data_type if data_type else " "
    description = description if description else " "

    title_metrics = _measure_text_qt(title, font_family, title_font_size)
    type_metrics = _measure_text_qt(data_type, font_family, type_font_size)
    description_metrics = _measure_text_qt(description, font_family, description_font_size)

    title_width = title_metrics["text_width"] + title_padding_x * 2
    title_height = title_metrics["text_height"] + title_padding_y * 2

    type_width = type_metrics["text_width"] + type_padding_x * 2
    type_height = type_metrics["text_height"] + type_padding_y * 2

    description_width = description_metrics["text_width"] + description_padding_x * 2
    description_height = description_metrics["text_height"] + description_padding_y * 2

    if fit_to_max_width:
        common_width = max(title_width, type_width, description_width)
        title_width = common_width
        type_width = common_width
        description_width = common_width

    content_width = max(title_width, type_width, description_width)
    content_height = title_height + type_height + description_height + vertical_gap * 2

    total_width = content_width + outer_padding * 2 + stroke_width
    total_height = content_height + outer_padding * 2 + stroke_width

    svg = Element(
        "svg",
        {
            "xmlns": "http://www.w3.org/2000/svg",
            "width": str(total_width),
            "height": str(total_height),
            "viewBox": f"0 0 {total_width} {total_height}",
        },
    )

    if background is not None:
        SubElement(
            svg,
            "rect",
            {
                "x": "0",
                "y": "0",
                "width": str(total_width),
                "height": str(total_height),
                "fill": background,
            },
        )

    x = outer_padding + stroke_width / 2
    y = outer_padding + stroke_width / 2

    if as_single_cell:
        SubElement(
            svg,
            "rect",
            {
                "x": str(x),
                "y": str(y),
                "width": str(content_width),
                "height": str(content_height),
                "fill": box_fill,
                "stroke": box_stroke,
                "stroke-width": str(stroke_width),
            },
        )

        sep1_y = y + title_height + vertical_gap
        sep2_y = sep1_y + type_height + vertical_gap
        SubElement(
            svg,
            "line",
            {
                "x1": str(x),
                "y1": str(sep1_y),
                "x2": str(x + content_width),
                "y2": str(sep1_y),
                "stroke": box_stroke,
                "stroke-width": str(stroke_width),
            },
        )
        SubElement(
            svg,
            "line",
            {
                "x1": str(x),
                "y1": str(sep2_y),
                "x2": str(x + content_width),
                "y2": str(sep2_y),
                "stroke": box_stroke,
                "stroke-width": str(stroke_width),
            },
        )

        row1_y = y
        row2_y = sep1_y + vertical_gap
        row3_y = sep2_y + vertical_gap

        _draw_row_text(
            svg,
            x,
            row1_y,
            content_width,
            title_height,
            title,
            font_family,
            title_font_size,
            title_metrics,
            text_color,
        )
        _draw_row_text(
            svg,
            x,
            row2_y,
            content_width,
            type_height,
            data_type,
            font_family,
            type_font_size,
            type_metrics,
            text_color,
        )
        _draw_row_text(
            svg,
            x,
            row3_y,
            content_width,
            description_height,
            description,
            font_family,
            description_font_size,
            description_metrics,
            text_color,
        )
    else:
        current_y = y
        rows = [
            (title, title_metrics, title_font_size, title_height),
            (data_type, type_metrics, type_font_size, type_height),
            (description, description_metrics, description_font_size, description_height),
        ]
        for idx, (text, metrics, font_size, row_h) in enumerate(rows):
            SubElement(
                svg,
                "rect",
                {
                    "x": str(x),
                    "y": str(current_y),
                    "width": str(content_width),
                    "height": str(row_h),
                    "fill": box_fill,
                    "stroke": box_stroke,
                    "stroke-width": str(stroke_width),
                },
            )
            _draw_row_text(
                svg,
                x,
                current_y,
                content_width,
                row_h,
                text,
                font_family,
                font_size,
                metrics,
                text_color,
            )
            current_y += row_h
            if idx < 2:
                current_y += vertical_gap

    svg_bytes = tostring(svg, encoding="utf-8", xml_declaration=True)
    svg_text = svg_bytes.decode("utf-8")
    Path(output_path).write_text(svg_text, encoding="utf-8")

    return {
        "svg": svg_text,
        "width": total_width,
        "height": total_height,
    }


def generate_field_card_svg(
    title_text: str,
    data_type_text: str,
    description_text: str,
    output_path: str = "card_3_lines.svg",
) -> dict:
    """
    Производственный фасад с 3 параметрами.

    1) title_text — текст 1 прямоугольника
    2) data_type_text — текст 2 прямоугольника (без квадратных скобок)
    3) description_text — текст 3 прямоугольника
    """
    normalized_type = (data_type_text or "").strip()
    if normalized_type.startswith("[") and normalized_type.endswith("]"):
        normalized_type = normalized_type[1:-1].strip()
    data_type_in_brackets = f"[{normalized_type}]" if normalized_type else "[]"

    return make_svg_card_3_lines(
        title=title_text,
        data_type=data_type_in_brackets,
        description=description_text,
        output_path=output_path,
    )


if __name__ == "__main__":
    result = generate_field_card_svg(
        title_text="Название поля",
        data_type_text="string",
        description_text="Описание поля",
        output_path="card_3_lines_pyqt.svg",
    )

    print("Успех: card_3_lines_pyqt.svg")
    print("Размер SVG:", result["width"], "x", result["height"])
