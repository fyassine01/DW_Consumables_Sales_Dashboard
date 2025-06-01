import pandas as pd
import xml.etree.ElementTree as ET
from xml.dom import minidom

def sanitize_column_name(col):
    """Convert column names to valid XML tags."""
    # Replace spaces and special characters with underscores
    sanitized = col.replace(' ', '_').replace('(', '').replace(')', '')
    sanitized = sanitized.replace('/', '_').replace('\\', '_').strip()
    # Ensure tag starts with a letter/underscore
    if not sanitized[0].isalpha():
        sanitized = f'_{sanitized}'
    return sanitized.lower()

def excel_to_xml(input_file, output_file):
    # Read Excel file
    df = pd.read_excel(input_file)
    
    # Clean column names for XML compatibility
    df.columns = [sanitize_column_name(col) for col in df.columns]
    
    # Create XML root
    root = ET.Element('data')
    
    # Add records
    for _, row in df.iterrows():
        record_elem = ET.SubElement(root, 'record')
        for col in df.columns:
            elem = ET.SubElement(record_elem, col)
            elem.text = str(row[col]) if pd.notna(row[col]) else ''
    
    # Create pretty XML
    xml_str = ET.tostring(root, encoding='utf-8')
    pretty_xml = minidom.parseString(xml_str).toprettyxml(indent='  ')
    
    # Write to file
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(pretty_xml)

if __name__ == '__main__':
    excel_to_xml('suppliers_and_analytics.xlsx', 'suppliers_and_analytics.xml')