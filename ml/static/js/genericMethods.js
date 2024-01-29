function generateTable(data) {
    var table = '<table  class="table table-bordered table-striped" border="1"><thead><tr>';

    // Create table header
    for (var key in data[0]) {
        table += '<th>' + key + '</th>';
    }
    table += '</tr></thead><tbody>';

    // Create table rows
    for (var i = 0; i < data.length; i++) {
        table += '<tr>';
        for (var key in data[i]) {
            table += '<td>' + data[i][key] + '</td>';
        }
        table += '</tr>';
    }

    table += '</tbody></table>';
    return table;
}

function generateTableFromDF(columns,records )
    {
        // Update the UI with the first 10 records as a table
        var tableHtml = '<table class="table table-bordered table-striped table-responsive" border="1"><thead><tr>';

        // Generate table header from column names
        columns.forEach(column => {
            tableHtml += `<th>${column}</th>`;
        });

        tableHtml += '</tr></thead><tbody>';

        // Generate table rows from records
        records.forEach(record => {
            tableHtml += '<tr>';
            columns.forEach(column => {
                tableHtml += `<td>${record[column]}</td>`;
            });
            tableHtml += '</tr>';
        });

        tableHtml += '</tbody></table>';
    return tableHtml;
    }






function showTargetColumnForm() {
    $('#targetColumnForm').show();
}

function generateList(data) {
    var list = '<ul>';
    for (var i = 0; i < data.length; i++) {
        list += '<li>' + data[i] + '</li>';
    }
    list += '</ul>';
    return list;
}

    // Function to generate HTML table for a dictionary
function generateDictTable(data) {
    var table = '<table class="table table-bordered table-striped table-responsive"  border="1"><thead><tr><th>Attribute</th><th>Value</th></tr></thead><tbody>';
    for (var key in data) {
        table += '<tr><td>' + key + '</td><td>' + data[key] + '</td></tr>';
    }
    table += '</tbody></table>';
    return table;
}

// Function to remove a specific key from a dictionary
const removeKeyFromDict = (dict, keyToRemove) => {
    const { [keyToRemove]: removedKey, ...rest } = dict;
    return rest;
};
