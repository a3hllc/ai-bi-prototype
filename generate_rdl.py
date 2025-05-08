# generate_rdl.py - with dynamic Fields section for SSRS upload validation
# Copyright A3H LLC

from jinja2 import Template
import os
import uuid
from nlp_template_selector import classify_template_intent  # ✅ Required for dynamic template selection

# Generate <TablixColumn> tags for each column
def build_tablix_columns(columns):
    return "\n".join([f"<TablixColumn><Width>2in</Width></TablixColumn>" for _ in columns])

# Generate <TablixRow> with a <Textbox> for each column
def build_tablix_rows(columns):
    cells = "\n".join([
        f"""
        <TablixCell>
          <CellContents>
            <Textbox Name='Textbox_{col}'>
              <CanGrow>true</CanGrow>
              <KeepTogether>true</KeepTogether>
              <Paragraphs>
                <Paragraph>
                  <TextRuns>
                    <TextRun>
                      <Value>=Fields!{col}.Value</Value>
                      <Style />
                    </TextRun>
                  </TextRuns>
                  <Style />
                </Paragraph>
              </Paragraphs>
              <rd:DefaultName>Textbox_{col}</rd:DefaultName>
              <Style />
            </Textbox>
          </CellContents>
        </TablixCell>""" for col in columns
    ])
    return f"<TablixRow><Height>0.25in</Height><TablixCells>{cells}</TablixCells></TablixRow>"

# Generate one <TablixMember> per column for column hierarchy
def build_column_members(columns):
    return "\n".join(["<TablixMember />" for _ in columns])

# Default row hierarchy is one <TablixMember>
def build_row_members():
    return "<TablixMember />"

# Generates the <Fields> block under <DataSet>
def build_fields_section(columns):
    field_tags = []
    for col in columns:
        field_tags.append(f"""
        <Field Name="{col}">
          <DataField>{col}</DataField>
          <rd:TypeName>System.String</rd:TypeName>
        </Field>""")
    return "\n".join(field_tags)

# ✅ Main function for report generation
def generate_rdl(report_title, dataset_name, sql_query, output_file, columns, layout_command="use tabular view"):
    """
    Generates a .rdl report file based on user input and layout intent.
    Arguments:
        report_title:     str - The report title
        dataset_name:     str - The name of the SQL data set
        sql_query:        str - SQL to be embedded in the report
        output_file:      str - Output .rdl file path
        columns:          list - List of column names from SQL result
        layout_command:   str - Optional NLP input like "use KPI cards"
    """
    # 🔍 NLP-based template path selection
    template_file = classify_template_intent(layout_command)

    # 📄 Load and compile the selected Jinja2 template
    with open(template_file, 'r', encoding='utf-8') as file:
        template = Template(file.read())

    # 🔧 Build template sections
    tablix_columns = build_tablix_columns(columns)
    tablix_rows = build_tablix_rows(columns)
    tablix_column_members = build_column_members(columns)
    tablix_row_members = build_row_members()
    dataset_fields = build_fields_section(columns)
    report_id = str(uuid.uuid4())

    # 🧪 Render final RDL XML using all sections
    rendered_rdl = template.render(
        report_title=report_title,
        dataset_name=dataset_name,
        sql_query=sql_query.strip(),
        tablix_columns=tablix_columns,
        tablix_rows=tablix_rows,
        tablix_column_members=tablix_column_members,
        tablix_row_members=tablix_row_members,
        dataset_fields=dataset_fields,
        report_id=report_id,
        columns=columns  # ✅ Fix: ensure Jinja2 receives columns list
    )

    # 💾 Save to .rdl file
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(rendered_rdl)

    print(f"✅ Report generated: {output_file}")
