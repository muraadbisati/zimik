
params_dict = {'pizza-size': ['large', 'small'], 'pizza-type': ['Pepperoni'], 'amount': [2.0, 1.0]}



def format_message_body(params_dict):
    # Define the mapping from parameter keys to column names
    column_mapping = {
        'pizza-type': 'Pizza',
        'pizza-size': 'Size',
        'amount': 'Qty'
    }

    # Initialize a dictionary to store the column values
    column_values = {column_name: [] for column_name in column_mapping.values()}

    # Populate the column values
    for key, values in params_dict.items():
        column_name = column_mapping.get(key)
        if column_name:
            column_values[column_name].extend(values)

    # Check if column_values is not empty
    if not column_values:
        return "No data available."

    # Get the maximum length of values in each column
    max_lengths = {column: max(len(str(value)) for value in values) for column, values in column_values.items()}

    # Create the header row
    header_row = '|' + '|'.join(f' {column_mapping[key]} ' for key in column_mapping) + '|'

    # Create the separator row
    separator_row = '|' + '|'.join('-' * (max_lengths[column] + 2) for column in column_values) + '|'

    # Create the data rows
    data_rows = []
    for i in range(max(len(values) for values in column_values.values())):
        row = []
        for column_name, values in column_values.items():
            value = values[i] if i < len(values) else ''
            row.append(f'{value:>{max_lengths[column_name]}}')
        data_rows.append('|' + '|'.join(' ' + cell + ' ' for cell in row) + '|')

    # Join the rows
    message_body = '\n'.join([header_row, separator_row] + data_rows)
    print(message_body)

    return message_body

format_message_body(params_dict)