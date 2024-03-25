function generateTableWithOption(data) {
    var table = '<table class="table table-bordered table-striped" border="1"><thead><tr>';

    // Create table header
    for (var key in data[0]) {
        if (key === 'criteria') {
            table += '<th style="display:none;" >' + key + '</th>';
        } else {
            table += '<th>' + key.charAt(0).toUpperCase() + key.slice(1) + '</th>';
        }
    }

    // Add columns for Condition, Values, Selected Values, Add Condition, and Duplicate Row
    table += '<th>Add Condition</th><th>Condition</th><th>Values</th><th>Duplicate Row</th></tr></thead><tbody>';

    // Create table rows
    for (var i = 0; i < data.length; i++) {
        table += '<tr>';
        for (var key in data[i]) {
            if (key === 'criteria') {
                table += '<td style="display:none;" >' + data[i][key].join(', ') + '</td>';
            } else {
                table += '<td>' + data[i][key] + '</td>';
            }
        }

        // Add empty cells for Condition, Values, Selected Values, Add Condition, and Duplicate Row

        table += '<td><input type="checkbox" name="conditionCheckbox" onclick="enableImpactCriteria(this)"></td>';
       table += '<td></td><td></td>';
        table += '<td><input type="checkbox" name="duplicateCheckbox" onclick="duplicateRow(this)"></td>';
         table += '<td><button type="button" onclick="deleteRow(this)">Delete</button></td>';


        table += '</tr>';
    }

    table += '</tbody></table>';
    return table;
}

 function enableImpactCriteria(checkbox) {
        var rowIndex = checkbox.parentNode.parentNode.rowIndex;
        var table = document.querySelector('#selected-features-details-container table');
        var conditionCell = table.rows[rowIndex].cells[5];
        var valuesCell = table.rows[rowIndex].cells[6];
        var selectedValuesCell = table.rows[rowIndex].cells[7];

        if (checkbox.checked) {
            var type = table.rows[rowIndex].cells[1].innerText.trim().toLowerCase();
            var newConditionHTML = '<select onchange="handleConditionChange(this)">';
            if (type === 'numerical') {
                newConditionHTML += '<option value="lesser">Lesser Than</option><option value="lesser_equal">Lesser Than or Equal To</option><option value="greater">Greater Than</option><option value="between">Between</option>';
            } else if (type === 'categorical') {
                newConditionHTML += '<option value="contains">Contains</option>';
            }
            newConditionHTML += '</select>';

            var newValuesHTML = '';
            if (type === 'numerical') {
                newValuesHTML = '<input type="text" placeholder="Enter values">';
            } else if (type === 'categorical') {
                newValuesHTML = '<input type="text" placeholder="Enter values">';
            }

            conditionCell.innerHTML = newConditionHTML;
            valuesCell.innerHTML = newValuesHTML;
            var conditionCheckbox = table.rows[rowIndex].cells[7];
            conditionCheckbox.innerHTML = '<td><input type="checkbox" name="duplicateCheckbox" onclick="duplicateRow(this)"></td>';

        } else {
            conditionCell.innerHTML = '';
            valuesCell.innerHTML = '';
            selectedValuesCell.innerHTML = '';
        }
    }

    function handleConditionChange(selectElement) {
        var rowIndex = selectElement.parentNode.parentNode.rowIndex;
        var table = document.querySelector('#selected-features-details-container table');
        var valuesCell = table.rows[rowIndex].cells[6];

        if (selectElement.value === 'between') {
            var newValuesHTML = 'From: <input type="text" placeholder="Enter lower value"> To: <input type="text" placeholder="Enter upper value">';
            valuesCell.innerHTML = newValuesHTML;
        } else {
            var type = table.rows[rowIndex].cells[1].innerText.trim().toLowerCase();
            var newValuesHTML = '';
            if (type === 'numerical') {
                newValuesHTML = '<input type="text" placeholder="Enter values">';
            } else if (type === 'categorical') {
                newValuesHTML = '<select multiple onchange="updateSelectedValues(this)"><option value="value1">Value 1</option><option value="value2">Value 2</option><option value="value3">Value 3</option></select>';
            }
            valuesCell.innerHTML = newValuesHTML;
        }
    }

    function updateSelectedValues(selectElement) {
        var rowIndex = selectElement.parentNode.parentNode.rowIndex;
        var table = document.querySelector('#selected-features-details-container table');
        var selectedValuesCell = table.rows[rowIndex].cells[6];
        var selectedValues = Array.from(selectElement.selectedOptions).map(option => option.value).join(', ');

        selectedValuesCell.innerHTML = selectedValues;
    }

    function duplicateRow(checkbox) {
        if (checkbox.checked) {
            var rowIndex = checkbox.parentNode.parentNode.rowIndex;
            var table = document.querySelector('#selected-features-details-container table');
            var newRow = table.insertRow(rowIndex + 1);

            for (var i = 0; i < table.rows[rowIndex].cells.length; i++) {
                var newCell = newRow.insertCell(i);
                 // Clone the content of each cell
                if (table.rows[rowIndex].cells[i].style.display === 'none') {
                    // For hidden columns
                    newCell.style.display = 'none';
                }

            if (i===6){
                newValuesHTML = '<input type="text" placeholder="Enter values">';
                newCell.innerHTML=newValuesHTML;
            }
            else{
                newCell.innerHTML = table.rows[rowIndex].cells[i].innerHTML;
            }
             // Find the checkbox in the newly duplicated row and check it

            }
             var checkboxIndex = 4;
             newRow.cells[checkboxIndex].querySelector('input[type="checkbox"]').checked = true;




        }
    }

    // ----------------------



    function collectFormData() {
        var formData = {
            conditions: []
        };

        var table = document.querySelector('#selected-features-details-container table');
        var rows = table.getElementsByTagName('tr');

        for (var i = 1; i < rows.length; i++) { // Start from 1 to skip the header row
            var condition = {
                name: rows[i].cells[0].innerText.trim(),
                type: rows[i].cells[1].innerText.trim(),
                impactCriteria: rows[i].cells[2].innerText.trim(),
                conditionType: '',
                values: '',
                addCondition: false,
                duplicateRow: false
            };

            // Collect checkbox values
            var conditionCheckbox = rows[i].cells[4].querySelector('input[type="checkbox"]');
            condition.addCondition = conditionCheckbox ? conditionCheckbox.checked : false;

            var duplicateCheckbox = rows[i].cells[7].querySelector('input[type="checkbox"]');
            condition.duplicateRow = duplicateCheckbox ? duplicateCheckbox.checked : false;

            var conditionCell = rows[i].cells[5];
            if (conditionCell.children.length > 0) {
                var selectElement = conditionCell.children[0];
                condition.conditionType = selectElement.value;
            }

            var valuesCell = rows[i].cells[6];
            if (valuesCell.children.length > 0) {
                if (condition.type === 'numerical') {
                    if(condition.conditionType=='between'){
                    condition.values = valuesCell.children[0].value;
                    condition.values +=', '
                    condition.values += valuesCell.children[1].value;
                    }
                    else{
                    condition.values = valuesCell.children[0].value;
                    }
                } else if (condition.type === 'categorical') {
                     condition.values = valuesCell.children[0].value;
                }
            }

            formData.conditions.push(condition);
        }

        return formData;
    }

// Function to delete a row
    function deleteRow(button) {
        var row = button.parentNode.parentNode;
        row.parentNode.removeChild(row);
    }


