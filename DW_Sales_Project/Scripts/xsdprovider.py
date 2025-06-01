#!/usr/bin/env python3
"""
XML to XSD Generator Script

This script analyzes an XML file and generates a corresponding XSD (XML Schema Definition) file.
It handles elements, attributes, data types, and basic cardinality rules.
"""

import xml.etree.ElementTree as ET
from collections import defaultdict, Counter
import argparse
import os
import re


class XSDGenerator:
    def __init__(self):
        self.elements = defaultdict(dict)
        self.element_children = defaultdict(set)
        self.element_attributes = defaultdict(set)
        self.element_text_types = defaultdict(list)
        self.element_counts = defaultdict(Counter)
        self.target_namespace = None
        
    def analyze_xml(self, xml_file):
        """Analyze XML file to extract structure information."""
        try:
            tree = ET.parse(xml_file)
            root = tree.getroot()
            
            # Extract namespace if present
            if root.tag.startswith('{'):
                self.target_namespace = root.tag[1:root.tag.find('}')]
            
            self._analyze_element(root, None)
            return True
        except ET.ParseError as e:
            print(f"Error parsing XML file: {e}")
            return False
        except FileNotFoundError:
            print(f"Error: XML file '{xml_file}' not found.")
            return False
    
    def _analyze_element(self, element, parent_tag):
        """Recursively analyze XML elements."""
        # Clean tag name (remove namespace)
        tag = self._clean_tag(element.tag)
        
        # Track parent-child relationships
        if parent_tag:
            parent_clean = self._clean_tag(parent_tag)
            self.element_children[parent_clean].add(tag)
            self.element_counts[parent_clean][tag] += 1
        
        # Analyze attributes
        for attr_name, attr_value in element.attrib.items():
            attr_clean = self._clean_tag(attr_name)
            attr_type = self._infer_type(attr_value)
            self.element_attributes[tag].add((attr_clean, attr_type))
        
        # Analyze text content
        if element.text and element.text.strip():
            text_type = self._infer_type(element.text.strip())
            self.element_text_types[tag].append(text_type)
        
        # Analyze child elements
        for child in element:
            self._analyze_element(child, element.tag)
    
    def _clean_tag(self, tag):
        """Remove namespace from tag name."""
        if tag.startswith('{'):
            return tag[tag.find('}')+1:]
        return tag
    
    def _infer_type(self, value):
        """Infer XSD data type from value."""
        if not value or not isinstance(value, str):
            return "xs:string"
        
        value = value.strip()
        
        # Boolean
        if value.lower() in ('true', 'false'):
            return "xs:boolean"
        
        # Integer
        if re.match(r'^-?\d+$', value):
            return "xs:int"
        
        # Decimal/Float
        if re.match(r'^-?\d*\.\d+$', value):
            return "xs:decimal"
        
        # Date (basic patterns)
        if re.match(r'^\d{4}-\d{2}-\d{2}$', value):
            return "xs:date"
        
        # DateTime (basic patterns)
        if re.match(r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}', value):
            return "xs:dateTime"
        
        # Default to string
        return "xs:string"
    
    def _get_most_common_type(self, types_list):
        """Get the most common type from a list of types."""
        if not types_list:
            return "xs:string"
        
        type_counter = Counter(types_list)
        return type_counter.most_common(1)[0][0]
    
    def _determine_cardinality(self, parent, child):
        """Determine minOccurs and maxOccurs for child elements."""
        # element_counts[parent][child] is an integer count, not a list
        count = self.element_counts[parent][child]
        
        if count == 0:
            return "0", "1"
        elif count == 1:
            return "1", "1"
        else:
            return "1", "unbounded"
    
    def generate_xsd(self, output_file=None):
        """Generate XSD content."""
        xsd_lines = []
        
        # XML declaration and schema root
        xsd_lines.append('<?xml version="1.0" encoding="UTF-8"?>')
        
        schema_attrs = ['xmlns:xs="http://www.w3.org/2001/XMLSchema"']
        if self.target_namespace:
            schema_attrs.append(f'targetNamespace="{self.target_namespace}"')
            schema_attrs.append(f'xmlns="{self.target_namespace}"')
        schema_attrs.append('elementFormDefault="qualified"')
        
        xsd_lines.append(f'<xs:schema {" ".join(schema_attrs)}>')
        
        # Find root elements (elements that are not children of other elements)
        all_children = set()
        for children in self.element_children.values():
            all_children.update(children)
        
        root_elements = set(self.element_children.keys()) - all_children
        if not root_elements and self.element_children:
            # If no clear root, take the first element
            root_elements = {next(iter(self.element_children.keys()))}
        
        # Generate element definitions
        processed_elements = set()
        
        # Process root elements first
        for root_element in sorted(root_elements):
            self._generate_element_definition(root_element, xsd_lines, processed_elements, indent=1)
        
        # Process remaining elements
        for element in sorted(self.element_children.keys()):
            if element not in processed_elements:
                self._generate_element_definition(element, xsd_lines, processed_elements, indent=1)
        
        xsd_lines.append('</xs:schema>')
        
        xsd_content = '\n'.join(xsd_lines)
        
        if output_file:
            try:
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(xsd_content)
                print(f"XSD file generated successfully: {output_file}")
            except IOError as e:
                print(f"Error writing XSD file: {e}")
                return None
        
        return xsd_content
    
    def _generate_element_definition(self, element_name, xsd_lines, processed_elements, indent=1):
        """Generate XSD element definition."""
        if element_name in processed_elements:
            return
        
        processed_elements.add(element_name)
        indent_str = "  " * indent
        
        xsd_lines.append(f'{indent_str}<xs:element name="{element_name}">')
        
        # Check if element has children or attributes
        has_children = element_name in self.element_children and self.element_children[element_name]
        has_attributes = element_name in self.element_attributes and self.element_attributes[element_name]
        has_text = element_name in self.element_text_types and self.element_text_types[element_name]
        
        if has_children or has_attributes:
            xsd_lines.append(f'{indent_str}  <xs:complexType>')
            
            # Handle mixed content (elements with both text and child elements)
            if has_text and has_children:
                xsd_lines.append(f'{indent_str}    <xs:sequence>')
                # Generate child elements
                for child in sorted(self.element_children[element_name]):
                    min_occurs, max_occurs = self._determine_cardinality(element_name, child)
                    occurs_attr = ""
                    if min_occurs != "1" or max_occurs != "1":
                        occurs_attr = f' minOccurs="{min_occurs}" maxOccurs="{max_occurs}"'
                    xsd_lines.append(f'{indent_str}      <xs:element ref="{child}"{occurs_attr}/>')
                xsd_lines.append(f'{indent_str}    </xs:sequence>')
            
            elif has_children:
                xsd_lines.append(f'{indent_str}    <xs:sequence>')
                # Generate child elements
                for child in sorted(self.element_children[element_name]):
                    min_occurs, max_occurs = self._determine_cardinality(element_name, child)
                    occurs_attr = ""
                    if min_occurs != "1" or max_occurs != "1":
                        occurs_attr = f' minOccurs="{min_occurs}" maxOccurs="{max_occurs}"'
                    xsd_lines.append(f'{indent_str}      <xs:element ref="{child}"{occurs_attr}/>')
                xsd_lines.append(f'{indent_str}    </xs:sequence>')
            
            elif has_text:
                # Simple content with attributes
                text_type = self._get_most_common_type(self.element_text_types[element_name])
                xsd_lines.append(f'{indent_str}    <xs:simpleContent>')
                xsd_lines.append(f'{indent_str}      <xs:extension base="{text_type}">')
                # Generate attributes
                for attr_name, attr_type in sorted(self.element_attributes[element_name]):
                    xsd_lines.append(f'{indent_str}        <xs:attribute name="{attr_name}" type="{attr_type}"/>')
                xsd_lines.append(f'{indent_str}      </xs:extension>')
                xsd_lines.append(f'{indent_str}    </xs:simpleContent>')
            
            # Generate attributes for complex types
            if has_attributes and not (has_text and not has_children):
                for attr_name, attr_type in sorted(self.element_attributes[element_name]):
                    xsd_lines.append(f'{indent_str}    <xs:attribute name="{attr_name}" type="{attr_type}"/>')
            
            xsd_lines.append(f'{indent_str}  </xs:complexType>')
        
        elif has_text:
            # Simple element with text content only
            text_type = self._get_most_common_type(self.element_text_types[element_name])
            xsd_lines.append(f'{indent_str}  <xs:complexType>')
            xsd_lines.append(f'{indent_str}    <xs:simpleContent>')
            xsd_lines.append(f'{indent_str}      <xs:extension base="{text_type}"/>')
            xsd_lines.append(f'{indent_str}    </xs:simpleContent>')
            xsd_lines.append(f'{indent_str}  </xs:complexType>')
        
        xsd_lines.append(f'{indent_str}</xs:element>')


def main():
    parser = argparse.ArgumentParser(description='Generate XSD file from XML file')
    parser.add_argument('xml_file', help='Input XML file path')
    parser.add_argument('-o', '--output', help='Output XSD file path (default: input_file.xsd)')
    parser.add_argument('--print', action='store_true', help='Print XSD to console instead of saving to file')
    
    args = parser.parse_args()
    
    # Determine output file path
    if args.output:
        output_file = args.output
    else:
        base_name = os.path.splitext(args.xml_file)[0]
        output_file = f"{base_name}.xsd"
    
    # Generate XSD
    generator = XSDGenerator()
    
    if not generator.analyze_xml(args.xml_file):
        return 1
    
    if args.print:
        xsd_content = generator.generate_xsd()
        if xsd_content:
            print(xsd_content)
    else:
        generator.generate_xsd(output_file)
    
    return 0


if __name__ == "__main__":
    exit(main())