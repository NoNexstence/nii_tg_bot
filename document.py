from docx import Document
from docxtpl import DocxTemplate

def create_doc(data):
    years = data.get('years')
    params = []
    seen = set()
    for y in years:
        for p in data[y].keys():
            if p not in seen:
                seen.add(p)
                params.append(p)

    last_year = years[0]
    year = years[1]

    context = {
        'data': data,
        'last_year': last_year,
        'year': year,
        'params': params,
    }

    tpl = DocxTemplate("files/test.docx")
    tpl.render(context)
    tpl.save("files/result.docx")


    # ====================/ ТУТ КОНЕЧНО КУСТАРЩИНА С УДАЛЕНИЕМ ПОСЛЕДНЕЙ /==================== #
    # ====================/ СТРОКИ В ТАБЛИЦЕ, НО ПОКА ЧТО КАК ЕСТЬ       /==================== #

    final_doc = Document("files/result.docx")
    for table in final_doc.tables:
        if len(table.rows) > 1:
            table._tbl.remove(table.rows[-1]._tr)

    final_doc.save("files/final_result.docx")

    print("Saved final_result.docx")
