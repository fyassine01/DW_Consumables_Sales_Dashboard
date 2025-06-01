#!/bin/bash

# Set root project folder
PROJECT_DIR="DW_Sales_Project"
mkdir -p "$PROJECT_DIR"

echo "[+] Creating folders..."
# Create folders
mkdir -p "$PROJECT_DIR/PowerBI"
mkdir -p "$PROJECT_DIR/SSMS"
mkdir -p "$PROJECT_DIR/SSIS/projetBI"
mkdir -p "$PROJECT_DIR/SSIS/bin/Development"
mkdir -p "$PROJECT_DIR/SSIS/obj/Development"
mkdir -p "$PROJECT_DIR/DataSources"
mkdir -p "$PROJECT_DIR/Scripts"

echo "[+] Moving PowerBI file..."
mv consumables_sales_dashboard_yassine_aziz.pbix "$PROJECT_DIR/PowerBI/"

echo "[+] Moving SSMS files..."
mv database_schema_and_data.sql "$PROJECT_DIR/SSMS/"
mv customers_database.json "$PROJECT_DIR/SSMS/"

echo "[+] Moving SSIS files..."
mv projetBI.sln "$PROJECT_DIR/SSIS/"
mv projetBI/Package.dtsx "$PROJECT_DIR/SSIS/projetBI/"
mv projetBI/Project.params "$PROJECT_DIR/SSIS/projetBI/"
mv projetBI/projetBI.database "$PROJECT_DIR/SSIS/projetBI/"
mv projetBI/projetBI.dtproj "$PROJECT_DIR/SSIS/projetBI/"
mv projetBI/projetBI.dtproj.user "$PROJECT_DIR/SSIS/projetBI/"
mv projetBI/bin/Development/projetBI.ispac "$PROJECT_DIR/SSIS/bin/Development/"
mv projetBI/obj/Development/* "$PROJECT_DIR/SSIS/obj/Development/"

echo "[+] Moving data source files..."
mv employees_directory.yaml "$PROJECT_DIR/DataSources/"
mv inventory_movements.tsv "$PROJECT_DIR/DataSources/"
mv marketing_campaigns.xml "$PROJECT_DIR/DataSources/"
mv products_inventory.csv "$PROJECT_DIR/DataSources/"
mv suppliers_and_analytics.xlsx "$PROJECT_DIR/DataSources/"
mv suppliers_and_analytics.xml "$PROJECT_DIR/DataSources/"
mv suppliers_and_analytics.xsd "$PROJECT_DIR/DataSources/"
# Copy customers_database.json again in DataSources for convenience
cp "$PROJECT_DIR/SSMS/customers_database.json" "$PROJECT_DIR/DataSources/"

echo "[+] Moving Python scripts..."
mv datagenerator.py "$PROJECT_DIR/Scripts/"
mv xsdprovider.py "$PROJECT_DIR/Scripts/"
mv exttoxml.py "$PROJECT_DIR/Scripts/"

echo "[+] Done. Project organized under $PROJECT_DIR/"

