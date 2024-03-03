import requests
from CatalogParser import CatalogParser


def download_html():
    catalog_parser = CatalogParser()
    for id in catalog_parser.get_id_list():
        response = requests.get("https://www.graduate.technion.ac.il/Subjects.Heb/?SUB=" + id)
        with open("HTML Courses/" + id + ".html", "w") as HTML_file:
            HTML_file.write(response.text)
            HTML_file.close()
        print(id + " downloaded!")
