"""Small sample script to extract a table from a pdf (not any pdf!) and convert and dump it to xml data structure"""

from enum import StrEnum
from typing import TypeAlias
from xml.etree.ElementTree import Element, SubElement, tostring

import pdfplumber

class ERROR_MSG(StrEnum):
    """Collection of all error messages"""
    NO_TABLE = "There is no table"
    """"""

    EMPTY_TABLE = "Your table is empty"
    """"""

class ATTRIBUTE(StrEnum):
    """All expected attributes inside an element"""
    
    DATA_TYPE = "type"
    """The data type associated with the property."""

    FLAG = "flag"
    """A flag indicating property status."""

    INFO = "information"
    """Additional information or description."""

    UNKNOWN = "unknown"
    """If no value was found."""

# type Table_PDF = list[list[str | None]] | None  # for python >=3.12
Table_PDF: TypeAlias = list[list[str | None]] | None


def extract_table_from_pdf_file(filename: str, page_number: int) -> Table_PDF:
    """Extract a table from any given PDF file

    Args:
        filename (str): filename (with path) to your pdf e.g. path/to/my.pdf
        page_number (int): page number where you expect your table to find (page number starts by 0)

    Returns:
        Table_PDF: returns nested list of your table or None (if no table was found)
    """
    with pdfplumber.open(filename) as pdf:
        target_page = pdf.pages[page_number]
        return target_page.extract_table(table_settings={"vertical_strategy": "text"})


def build_xml_struct(table: Table_PDF, document_element_name: str) -> Element:
    """Build a XML structure (tree) based on your table

    Args:
        table (Table_PDF): table you want to transform into an XML structure
        document_element_name (str): name of your document element

    Raises:
        ValueError: There is no table
        ValueError: Your table is empty

    Returns:
        Element: your XML structure (tree)
    """
    if table is None:
        raise ValueError(ERROR_MSG.NO_TABLE)

    root = Element(document_element_name)
    header = table.pop(0)  # remove header

    if header is None:
        raise ValueError(ERROR_MSG.EMPTY_TABLE)

    for row in table:
        if any(element is None for element in row):
            continue

        # 'or "UNKNOWN"' is not necessary I think, but linter doesn't understand
        property = SubElement(root, row[0] or ATTRIBUTE.UNKNOWN)

        property.set(ATTRIBUTE.DATA_TYPE, row[1] or ATTRIBUTE.UNKNOWN)
        property.set(ATTRIBUTE.FLAG     , row[2] or ATTRIBUTE.UNKNOWN)
        property.set(ATTRIBUTE.INFO     , row[3] or ATTRIBUTE.UNKNOWN)

    return root


def export_xml_struct(xml_struct: Element, filename: str) -> None:
    """Dump your XML object to a file

    Args:
        xml_struct (Element): your XML structure
        filename (str): name of your XML file
    """
    xml_str = tostring(xml_struct)

    with open(filename, "wb") as f:
        f.write(xml_str)


def main() -> None:
    table = extract_table_from_pdf_file("res/cpt_bacnet.pdf", 55)
    xml_struct = build_xml_struct(table, "ANALOG_INPUT")
    export_xml_struct(xml_struct, "analog_input.xml")


if __name__ == "__main__":
    main()
