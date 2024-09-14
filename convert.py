import csv
import os

mutation_operators = {
        "ACM": "Argument Change of overloaded Method call",
        "AOR": "Assignment Operator Replacement",
        "BCRD": "Break and Continue Replacement and Deletion",
        "BLR": "Boolean Literal Replacement",
        "BOR": "Binary Operator Replacement",
        "CBD": "Catch Block Deletion",
        "CSC": "Conditional Statement Change",
        "ER": "Enum Replacement",
        "ECS": "Explicit Conversion to Smaller type",
        "HLR": "Hexadecimal Literal Replacement",
        "ICM": "Increments Mirror",
        "ILR": "Integer Literal Replacement",
        "LCS": "Loop Statement Change",
        "OLFD": "Overloaded Function Deletion",
        "ORFD": "Overridden Function Deletion",
        "SKI": "Super Keyword Insertion",
        "SKD": "Super Keyword Deletion",
        "SLR": "String Literal Replacement",
        "UORD": "Unary Operator Replacement and Deletion",
        "AVR": "Address Value Replacement",
        "CCD": "Contract Constructor Deletion",
        "DLR": "Data Location Keyword Replacement",
        "DOD": "Delete Operator Deletion",
        "ETR": "Ether Transfer function Replacement",
        "EED": "Event Emission Deletion",
        "EHC": "Exception Handling Change",
        "FVR": "Function Visibility Replacement",
        "GVR": "Global Variable Replacement",
        "MCR": "Mathematical and Cryptographic function Replacement",
        "MOD": "Modifier Deletion",
        "MOI": "Modifier Insertion",
        "MOC": "Modifier Order Change",
        "MOR": "Modifier Replacement",
        "OMD": "Overridden Modifier Deletion",
        "PKD": "Payable Keyword Deletion",
        "RSD": "Return Statement Deletion",
        "RVS": "Return Values Swap",
        "SFD": "Selfdestruct Deletion",
        "SFI": "Selfdestruct Insertion",
        "SFR": "SafeMath Function Replacement",
        "SCEC": "Switch Call Expression Casting",
        "TOR": "Transaction Origin Replacement",
        "VUR": "Variable Unit Replacement",
        "VVR": "Variable Visibility Replacement"
}


def generate_html_from_csv(csv_file_path, output_html_path):
    # Dictionary to store the rows grouped by filenames and line numbers
    file_data = {}
    operators = set()

    # Define colors for different statuses
    status_colors = {
        "killed": "green",
        "live": "red",
        "stillborn": "yellow"
    }

    # Open the CSV file
    with open(csv_file_path, 'r') as csv_file:
        reader = csv.DictReader(csv_file)

        mutants = {'killed': 0, 'live': 0, 'stillborn': 0}
        
        # Collect rows by filename and line number, and gather all operators
        for row in reader:
            file_path = row['File']
            filename = os.path.basename(file_path)
            operator = row['Operator']
            start_line = int(row['StartLine'])
            end_line = int(row['EndLine'])

            operators.add(operator)
            if filename not in file_data:
                file_data[filename] = {'path': file_path}

            if start_line not in file_data[filename]:
                file_data[filename][start_line] = {}
            file_data[filename][start_line][operator] = {
                'status': row['Status'].lower(),
                'original': row['Original'],
                'replacement': row['Replacement']
            }
            mutants[row['Status'].lower()] = mutants[row['Status'].lower()] + 1


        # Start HTML structure
        html_content = """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>SuMo run results</title>
            <style>
                body { font-family: Arial, sans-serif; background-color: #f4f4f4; }
                table { width: 100%; border-collapse: collapse; margin-bottom: 40px; }
                table, th, td { border: 1px solid #ddd; }
                .status-line {  height: 10px; }
                .status-line.high, .high .cover-fill { background:rgb(77,146,33) }
                td:nth-child(odd) { background-color: #fff }
                th, td { text-align: left; }
                th { background-color: #f4f4f4; }
                .file-header { font-weight: bold; margin-bottom: 10px; }
                .killed { background-color: green; color: white; }
                .live { background-color: red; color: white; }
                .stillborn { background-color: yellow; color: black; }
                .unchanged { background-color: transparent; color: black; }
                .legend { margin-bottom: 20px; }
                .legend span { margin-right: 15px; padding: 3px; border-radius: 3px; font-weight: bold; }
                .tooltip { position: relative; cursor: pointer; }
                .tooltip .tooltiptext { 
                    visibility: hidden;
                    width: 350px;
                    background-color: #f9f9f9;
                    color: #333;
                    text-align: left;
                    padding: 5px;
                    border-radius: 6px;
                    border: 1px solid #ddd;
                    position: absolute;
                    z-index: 1;
                    bottom: 125%; 
                    left: 50%; 
                    margin-left: -100px; 
                    opacity: 0;
                    transition: opacity 0.3s;
                }
                .tooltip .tooltiptextbelow { 
                    visibility: hidden;
                    width: 200px;
                    background-color: #f9f9f9;
                    color: #333;
                    text-align: left;
                    padding: 5px;
                    border-radius: 6px;
                    border: 1px solid #ddd;
                    position: absolute;
                    z-index: 1;
                    top: 150%; 
                    left: 150%; 
                    margin-left: -100px; 
                    opacity: 0;
                    transition: opacity 0.3s;
                }
                .tooltip:hover .tooltiptext {
                    visibility: visible;
                    opacity: 1;
                }
                .tooltip:hover .tooltiptextbelow {
                    visibility: visible;
                    opacity: 1;
                }
                th.sticky, td.sticky {
                    position: sticky;
                    background-color: #f4f4f4;
                    z-index: 2;
                }
                th.sticky {
                    top: 0;
                }
                td.sticky {
                    left: 0;
                    z-index: 1;
                    background-color: #fff;
                    border-right: 1px solid #ddd;
                }
                .line-content {
                    width: 50%;
                    white-space: nowrap;
                    overflow: hidden;
                    text-overflow: ellipsis;
                }
                .status-summary {
                    white-space: nowrap;
                    text-align: center;
                }
                col.line-number { width: 5%; }
                col.status-summary { width: 15%; }
                col.line-content { width: 50%; }
                col.operator-status { width: 10%; }
                
                /* Alternating row colors */
                tr:nth-child(even) { background-color: #f2f2f2; }
                tr:nth-child(odd) { background-color: #ffffff; }

                /* Keep the first three columns the same color */
                tr:nth-child(even) td:nth-child(1) { background-color: #f2f2f2; }
                tr:nth-child(even) td:nth-child(2) { background-color: #f2f2f2; }
                tr:nth-child(even) td:nth-child(3) { background-color: #f2f2f2; }
                tr:nth-child(odd) td:nth-child(2) { background-color: #ffffff; }

                /* Alternating column colors for the rest of the columns within rows */
                tr:nth-child(odd) td:nth-child(n+4):nth-child(even) { background-color: #f2f2f2; }
                tr:nth-child(even) td:nth-child(n+4):nth-child(odd) { background-color: #f2f2f2; }
                tr:nth-child(even) td:nth-child(n+4):nth-child(even) { background-color: #dddddd; }

                /* Ensure that the headers have a consistent background */
                th { background-color: #cccccc; }

            </style>
        </head>
        <body>
        <div class="legend">
        """

        # Add the legend as colored labels next to each other
        for status, color in status_colors.items():
            text_color = "white" if color in ["green", "red"] else "black"
            html_content += f'<span style="background-color:{color};color:{text_color};">{status} : {mutants[status]}</span>'
        
        html_content += "</div>"

        # Process each file
        for filename, lines in file_data.items():
            if os.path.exists(file_data[filename]['path']):
                filename = file_data[filename]['path']	
            if os.path.exists(filename):
                with open(filename, 'r') as file:
                    file_lines = file.readlines()

                    # Start table structure
                    html_content += f"""
                    <div class="file-container">
                        <div class="file-header">{file_data[filename]['path']}</div>
                        <div class="status-line high"></div>
                        <table>
                            <colgroup>
                                <col class="line-number">
                                <col class="status-summary">
                                <col class="line-content">
                                {"".join([f"<col class='operator-status'>" for _ in sorted(operators)])}
                            </colgroup>
                            <thead>
                                <tr>
                                    <th class="sticky">#</th>
                                    <th class="sticky">Mutants</th>
                                    <th class="sticky"></th>
                                    {"".join([f"<th class='sticky tooltip'>{operator}<span class='tooltiptextbelow'>{mutation_operators[operator]}</span></th>" for operator in sorted(operators)])}
                                </tr>
                            </thead>
                            <tbody>
                    """

                    # Format the lines and add them to the table
                    for i, r_line in enumerate(file_lines):
                        line_number = i + 1
                        line = r_line.replace('\t', '&nbsp;&nbsp;&nbsp;&nbsp;').replace(' ', '&nbsp;')
                        formatted_line = line.strip()  # Strip trailing newlines from the original line
                        line_data = lines.get(line_number, {})

                        # Calculate the summary for this line
                        summary_counts = {"killed": 0, "live": 0, "stillborn": 0}
                        for operator, data in line_data.items():
                            summary_counts[data['status']] += 1

                        summary_text = ""

                        if summary_counts['killed'] > 0:
                            summary_text = f"<span class=\"killed\">{summary_counts['killed']}</span>&nbsp;"

                        if summary_counts['live'] > 0:
                            summary_text = f"{summary_text}<span class=\"live\">{summary_counts['live']}</span>&nbsp;"

                        if summary_counts['stillborn'] > 0:
                            summary_text = f"{summary_text}<span class=\"stillborn\">{summary_counts['stillborn']}</span>"

                        
                        # Prepare cells for each operator
                        operator_cells = ""
                        for operator in sorted(operators):
                            if operator in line_data:
                                status = line_data[operator]['status']
                                original = line_data[operator]['original']
                                replacement = line_data[operator]['replacement']
                                if replacement == "":
                                    replacement = f"<i>*nothing*</i>"
                                color_class = status.lower()  # Use lowercase status as the CSS class name
                                if len(original) + len(replacement) < 30:
                                    tooltip = f"{original}&nbsp;&nbsp;&rarr;&nbsp;&nbsp;{replacement}"
                                else:
                                    tooltip = f"{original}<br>&nbsp;&nbsp;&nbsp;&nbsp;&darr;<br>{replacement}"
                                operator_cells += f"""
                                <td class="tooltip" style="background-color: {status_colors[status.lower()]}">
                                    <span class="tooltiptext">{tooltip}</span>
                                </td>
                                """
                            else:
                                operator_cells += "<td></td>"  # Empty cell if no data for this operator

                        html_content += f"""
                        <tr>
                            <td class="sticky">{line_number}</td>
                            <td class="sticky status-summary">{summary_text}</td>
                            <td class="sticky line-content">{formatted_line}</td>
                            {operator_cells}
                        </tr>
                        """

                    # Close table structure
                    html_content += """
                            </tbody>
                        </table>
                    </div>
                    """

        # End HTML structure
        html_content += """
        </body>
        </html>
        """

        # Write the HTML content to the output file
        with open(output_html_path, 'w') as html_file:
            html_file.write(html_content)

        print(f"HTML page generated successfully: {output_html_path}")

csv_file_path = 'results.csv'  # Use 'results.csv' as the input CSV file
output_html_path = 'output.html'  # Output HTML file path

generate_html_from_csv(csv_file_path, output_html_path)
