from io import BytesIO
from typing import List, Any
import xlsxwriter


def generate_excel(column_labels: List[str], rows: List[Any]):
    file = BytesIO()

    workbook = xlsxwriter.Workbook(file, {"in_memory": True})
    worksheet = workbook.add_worksheet()

    header_row_format = workbook.add_format({"bold": True})

    worksheet.set_row(0, 100)
    worksheet.insert_image(
        0, 0, "static/resources/runners_logo.png", {"x_scale": 0.4, "y_scale": 0.4}
    )
    worksheet.write_row(1, 0, column_labels, header_row_format)
    for i in range(len(rows)):
        worksheet.write_row(i + 2, 0, rows[i])

    worksheet.autofit()
    workbook.close()

    file.seek(0, 0)
    return file
