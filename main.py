from pathlib import Path
from xml.etree.ElementTree import Element, SubElement, tostring

DEFAULT_FONT_FAMILY = "Times New Roman, Times, serif"
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


def _measure_text_tk(text: str, font_family: str, font_size: int) -> dict:
    """
    Измеряет текст через tkinter.font.
    Возвращает ширину, высоту, ascent, descent.
    """
    if not text:
        text = " "

    import tkinter as tk
    import tkinter.font as tkfont

    root = None
    try:
        root = tk.Tk()
        root.withdraw()

        # Для tkinter лучше использовать одно имя семейства.
        # Если передать строку с fallback через запятую, tkinter может понять это не так, как SVG.
        tk_family = font_family.split(",")[0].strip()

        font = tkfont.Font(root=root, family=tk_family, size=font_size)

        text_width = int(font.measure(text))
        ascent = int(font.metrics("ascent"))
        descent = int(font.metrics("descent"))
        text_height = ascent + descent

        return {
            "text_width": text_width,
            "text_height": text_height,
            "ascent": ascent,
            "descent": descent,
        }
    finally:
        if root is not None:
            root.destroy()


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
    font_family: str = "Times New Roman, Times, serif",
    title_font_size: int = 20,
    type_font_size: int = 20,
    description_font_size: int = 20,
    title_padding_x: int = 16,
    title_padding_y: int = 8,
    type_padding_x: int = 16,
    type_padding_y: int = 8,
    description_padding_x: int = 16,
    description_padding_y: int = 8,
    stroke_width: int = 1,
    text_color: str = "black",
    box_fill: str = "none",
    box_stroke: str = "black",
    background: str | None = None,
    outer_padding: int = 10,
    vertical_gap: int = 0,
    fit_to_max_width: bool = True,
    as_single_cell: bool = True,
) -> dict:
    """
    Создает SVG-карточку из 3 строк:
    1) название
    2) тип данных
    3) описание

    По умолчанию карточка рисуется как единая ячейка:
    общий внешний прямоугольник + внутренние разделители строк.
    """

    # Принудительно рендерим карточку как единый прямоугольник.
    fit_to_max_width = True
    as_single_cell = True
    vertical_gap = 0

    title = title if title else " "
    data_type = data_type if data_type else " "
    description = description if description else " "

    title_metrics = _measure_text_tk(title, font_family, title_font_size)
    type_metrics = _measure_text_tk(data_type, font_family, type_font_size)
    description_metrics = _measure_text_tk(description, font_family, description_font_size)

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

        # Горизонтальные разделители между строками.
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
        # Режим старого поведения: отдельная рамка на каждую строку.
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
        "title_box": {
            "width": title_width,
            "height": title_height,
            "text_width": title_metrics["text_width"],
        },
        "type_box": {
            "width": type_width,
            "height": type_height,
            "text_width": type_metrics["text_width"],
        },
        "description_box": {
            "width": description_width,
            "height": description_height,
            "text_width": description_metrics["text_width"],
        },
    }


def generate_field_card_svg(
    title_text: str,
    data_type_text: str,
    description_text: str,
    output_path: str = "card_3_lines.svg",
) -> dict:
    """
    Промышленный фасад для генерации карточки из 3 строк.

    Вход:
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
        font_family=DEFAULT_FONT_FAMILY,
        title_font_size=DEFAULT_FONT_SIZE,
        type_font_size=DEFAULT_FONT_SIZE,
        description_font_size=DEFAULT_FONT_SIZE,
        title_padding_x=DEFAULT_TITLE_PADDING[0],
        title_padding_y=DEFAULT_TITLE_PADDING[1],
        type_padding_x=DEFAULT_TYPE_PADDING[0],
        type_padding_y=DEFAULT_TYPE_PADDING[1],
        description_padding_x=DEFAULT_DESCRIPTION_PADDING[0],
        description_padding_y=DEFAULT_DESCRIPTION_PADDING[1],
        stroke_width=DEFAULT_STROKE_WIDTH,
        text_color=DEFAULT_TEXT_COLOR,
        box_fill=DEFAULT_BOX_FILL,
        box_stroke=DEFAULT_BOX_STROKE,
        background=None,
        outer_padding=DEFAULT_OUTER_PADDING,
        vertical_gap=DEFAULT_VERTICAL_GAP,
        fit_to_max_width=DEFAULT_FIT_TO_MAX_WIDTH,
        as_single_cell=DEFAULT_AS_SINGLE_CELL,
    )


if __name__ == "__main__":
    result = generate_field_card_svg(
        title_text="Название поля",
        data_type_text="string",
        description_text="Описание поля",
        output_path="card_3_lines.svg",
    )

    print("Успех: card_3_lines.svg")
    print("Размер SVG:", result["width"], "x", result["height"])
