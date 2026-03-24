from pathlib import Path
from xml.etree.ElementTree import Element, SubElement, tostring


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


def _add_text_box(
    parent,
    x: int,
    y: int,
    text: str,
    font_family: str,
    font_size: int,
    padding_x: int,
    padding_y: int,
    stroke_width: int,
    text_color: str,
    box_fill: str,
    box_stroke: str,
) -> dict:
    """
    Добавляет в SVG одну рамку с текстом.
    x, y — верхний левый угол всего блока.
    Возвращает размеры блока.
    """
    if not text:
        text = " "

    metrics = _measure_text_tk(text, font_family, font_size)
    text_width = metrics["text_width"]
    text_height = metrics["text_height"]
    ascent = metrics["ascent"]

    width = text_width + padding_x * 2 + stroke_width
    height = text_height + padding_y * 2 + stroke_width

    inner_left = x + stroke_width / 2
    inner_top = y + stroke_width / 2
    inner_width = width - stroke_width
    inner_height = height - stroke_width

    text_x = inner_left + inner_width / 2
    text_y = inner_top + (inner_height - text_height) / 2 + ascent

    SubElement(
        parent,
        "rect",
        {
            "x": str(x + stroke_width / 2),
            "y": str(y + stroke_width / 2),
            "width": str(width - stroke_width),
            "height": str(height - stroke_width),
            "fill": box_fill,
            "stroke": box_stroke,
            "stroke-width": str(stroke_width),
        },
    )

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

    return {
        "width": width,
        "height": height,
        "text_width": text_width,
        "text_height": text_height,
        "text_x": text_x,
        "text_y": text_y,
    }


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
    vertical_gap: int = 8,
    fit_to_max_width: bool = False,
) -> dict:
    """
    Создает SVG-карточку из 3 строк:
    1) название
    2) тип данных
    3) описание

    Каждая строка помещается в свою рамку.
    Блоки располагаются вертикально.

    Если fit_to_max_width=True:
        все три рамки получают одинаковую ширину = ширине самого широкого блока.
    Если fit_to_max_width=False:
        каждая рамка подстраивается только под свою строку.
    """

    title = title if title else " "
    data_type = data_type if data_type else " "
    description = description if description else " "

    title_metrics = _measure_text_tk(title, font_family, title_font_size)
    type_metrics = _measure_text_tk(data_type, font_family, type_font_size)
    description_metrics = _measure_text_tk(description, font_family, description_font_size)

    title_width = title_metrics["text_width"] + title_padding_x * 2 + stroke_width
    title_height = title_metrics["text_height"] + title_padding_y * 2 + stroke_width

    type_width = type_metrics["text_width"] + type_padding_x * 2 + stroke_width
    type_height = type_metrics["text_height"] + type_padding_y * 2 + stroke_width

    description_width = (
        description_metrics["text_width"] + description_padding_x * 2 + stroke_width
    )
    description_height = (
        description_metrics["text_height"] + description_padding_y * 2 + stroke_width
    )

    if fit_to_max_width:
        common_width = max(title_width, type_width, description_width)
        title_width = common_width
        type_width = common_width
        description_width = common_width

    total_width = max(title_width, type_width, description_width) + outer_padding * 2
    total_height = (
        title_height
        + type_height
        + description_height
        + vertical_gap * 2
        + outer_padding * 2
    )

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

    current_y = outer_padding

    # Заголовок
    x_title = outer_padding + (total_width - outer_padding * 2 - title_width) / 2
    title_inner_left = x_title + stroke_width / 2
    title_inner_top = current_y + stroke_width / 2
    title_inner_width = title_width - stroke_width
    title_inner_height = title_height - stroke_width
    title_text_x = title_inner_left + title_inner_width / 2
    title_text_y = (
        title_inner_top
        + (title_inner_height - title_metrics["text_height"]) / 2
        + title_metrics["ascent"]
    )

    SubElement(
        svg,
        "rect",
        {
            "x": str(x_title + stroke_width / 2),
            "y": str(current_y + stroke_width / 2),
            "width": str(title_width - stroke_width),
            "height": str(title_height - stroke_width),
            "fill": box_fill,
            "stroke": box_stroke,
            "stroke-width": str(stroke_width),
        },
    )
    title_el = SubElement(
        svg,
        "text",
        {
            "x": str(title_text_x),
            "y": str(title_text_y),
            "font-family": font_family,
            "font-size": str(title_font_size),
            "fill": text_color,
            "text-anchor": "middle",
            "xml:space": "preserve",
        },
    )
    title_el.text = title

    current_y += title_height + vertical_gap

    # Тип данных
    x_type = outer_padding + (total_width - outer_padding * 2 - type_width) / 2
    type_inner_left = x_type + stroke_width / 2
    type_inner_top = current_y + stroke_width / 2
    type_inner_width = type_width - stroke_width
    type_inner_height = type_height - stroke_width
    type_text_x = type_inner_left + type_inner_width / 2
    type_text_y = (
        type_inner_top
        + (type_inner_height - type_metrics["text_height"]) / 2
        + type_metrics["ascent"]
    )

    SubElement(
        svg,
        "rect",
        {
            "x": str(x_type + stroke_width / 2),
            "y": str(current_y + stroke_width / 2),
            "width": str(type_width - stroke_width),
            "height": str(type_height - stroke_width),
            "fill": box_fill,
            "stroke": box_stroke,
            "stroke-width": str(stroke_width),
        },
    )
    type_el = SubElement(
        svg,
        "text",
        {
            "x": str(type_text_x),
            "y": str(type_text_y),
            "font-family": font_family,
            "font-size": str(type_font_size),
            "fill": text_color,
            "text-anchor": "middle",
            "xml:space": "preserve",
        },
    )
    type_el.text = data_type

    current_y += type_height + vertical_gap

    # Описание
    x_description = outer_padding + (total_width - outer_padding * 2 - description_width) / 2
    description_inner_left = x_description + stroke_width / 2
    description_inner_top = current_y + stroke_width / 2
    description_inner_width = description_width - stroke_width
    description_inner_height = description_height - stroke_width
    description_text_x = description_inner_left + description_inner_width / 2
    description_text_y = (
        description_inner_top
        + (description_inner_height - description_metrics["text_height"]) / 2
        + description_metrics["ascent"]
    )

    SubElement(
        svg,
        "rect",
        {
            "x": str(x_description + stroke_width / 2),
            "y": str(current_y + stroke_width / 2),
            "width": str(description_width - stroke_width),
            "height": str(description_height - stroke_width),
            "fill": box_fill,
            "stroke": box_stroke,
            "stroke-width": str(stroke_width),
        },
    )
    description_el = SubElement(
        svg,
        "text",
        {
            "x": str(description_text_x),
            "y": str(description_text_y),
            "font-family": font_family,
            "font-size": str(description_font_size),
            "fill": text_color,
            "text-anchor": "middle",
            "xml:space": "preserve",
        },
    )
    description_el.text = description

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


if __name__ == "__main__":
    result = make_svg_card_3_lines(
        title="Название поля",
        data_type="[string]",
        description="Описание поля",
        output_path="card_3_lines.svg",
        font_family="Times New Roman, Times, serif",
        title_font_size=20,
        type_font_size=20,
        description_font_size=20,
        title_padding_x=16,
        title_padding_y=8,
        type_padding_x=16,
        type_padding_y=8,
        description_padding_x=16,
        description_padding_y=8,
        stroke_width=1,
        text_color="black",
        box_fill="none",
        box_stroke="black",
        background=None,
        outer_padding=10,
        vertical_gap=8,
        fit_to_max_width=False,  # True, если нужны одинаковые ширины рамок
    )

    print("Успех: card_3_lines.svg")
    print("Размер SVG:", result["width"], "x", result["height"])





# from pathlib import Path
# from xml.etree.ElementTree import Element, SubElement, tostring


# def make_svg_text_box_tk_anchor_center(
#     text: str,
#     output_path: str = "text_box_tk_anchor_center.svg",
#     font_family: str = "Times New Roman, Times, serif",
#     font_size: int = 32,
#     padding_x: int = 16,
#     padding_y: int = 10,
#     stroke_width: int = 2,
#     text_color: str = "black",
#     box_fill: str = "none",
#     box_stroke: str = "black",
#     background: str | None = None,
# ) -> dict:
#     """
#     Создаёт SVG с текстом в рамке.
#     Горизонтальное центрирование делается через text-anchor="middle".
#     Вертикальное — через ascent/descent.
#     """
#     if not text:
#         text = " "

#     import tkinter as tk
#     import tkinter.font as tkfont

#     root = None
#     try:
#         root = tk.Tk()
#         root.withdraw()

#         font = tkfont.Font(root=root, family=font_family, size=font_size)

#         text_width = int(font.measure(text))
#         ascent = int(font.metrics("ascent"))
#         descent = int(font.metrics("descent"))
#         text_height = ascent + descent

#         width = text_width + padding_x * 2 + stroke_width
#         height = text_height + padding_y * 2 + stroke_width

#         inner_left = stroke_width / 2
#         inner_top = stroke_width / 2
#         inner_width = width - stroke_width
#         inner_height = height - stroke_width

#         text_x = inner_left + inner_width / 2
#         text_y = inner_top + (inner_height - text_height) / 2 + ascent

#         svg = Element(
#             "svg",
#             {
#                 "xmlns": "http://www.w3.org/2000/svg",
#                 "width": str(width),
#                 "height": str(height),
#                 "viewBox": f"0 0 {width} {height}",
#             },
#         )

#         if background is not None:
#             SubElement(
#                 svg,
#                 "rect",
#                 {
#                     "x": "0",
#                     "y": "0",
#                     "width": str(width),
#                     "height": str(height),
#                     "fill": background,
#                 },
#             )

#         SubElement(
#             svg,
#             "rect",
#             {
#                 "x": str(stroke_width / 2),
#                 "y": str(stroke_width / 2),
#                 "width": str(width - stroke_width),
#                 "height": str(height - stroke_width),
#                 "fill": box_fill,
#                 "stroke": box_stroke,
#                 "stroke-width": str(stroke_width),
#             },
#         )

#         text_el = SubElement(
#             svg,
#             "text",
#             {
#                 "x": str(text_x),
#                 "y": str(text_y),
#                 "font-family": font_family,
#                 "font-size": str(font_size),
#                 "fill": text_color,
#                 "text-anchor": "middle",
#                 "xml:space": "preserve",
#             },
#         )
#         text_el.text = text

#         svg_bytes = tostring(svg, encoding="utf-8", xml_declaration=True)
#         svg_text = svg_bytes.decode("utf-8")

#         Path(output_path).write_text(svg_text, encoding="utf-8")

#         return {
#             "svg": svg_text,
#             "width": width,
#             "height": height,
#             "text_width": text_width,
#             "text_height": text_height,
#             "text_x": text_x,
#             "text_y": text_y,
#         }

#     finally:
#         if root is not None:
#             root.destroy()


# if __name__ == "__main__":
#     result = make_svg_text_box_tk_anchor_center(
#         text="КУСОК SVG, работай, ибо я тебя придумал!!!!",
#         output_path="text_box_tk_anchor_center.svg",
#         font_family="Times New Roman, Times, serif",
#         font_size=32,
#         padding_x=20,
#         padding_y=12,
#         stroke_width=2,
#     )

#     print("Успех:", "text_box_tk_anchor_center.svg")