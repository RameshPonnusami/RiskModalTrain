
function createRadio(value, name, description) {
    const radioContainer = document.createElement('div');
    radioContainer.className = 'option-container';

    const radio = document.createElement('input');
    radio.type = 'radio';
    radio.value = value;
    radio.name = name;
    radio.className = 'mr-2';

    const radioLabel = document.createElement('label');
    radioLabel.textContent = description;
    radioLabel.className = 'radio-label';

    radioContainer.appendChild(radio);
    radioContainer.appendChild(radioLabel);

    return radioContainer;
}


function createColumnOptions(columnsData, tableBodyId, columnType) {
    const tableBody = document.querySelector('#' + tableBodyId);
    for (const [columnName, columnTypeData] of Object.entries(columnsData)) {
        if (columnTypeData === columnType) {
            const row = document.createElement('tr');

            // Column name cell
            const columnNameCell = document.createElement('td');
            columnNameCell.textContent = columnName;
            row.appendChild(columnNameCell);

            // Radio buttons for Do Nothing, Mean, Zero
            const doNothingRadio = document.createElement('td');
            doNothingRadio.appendChild(createRadio('do_nothing', columnName, ''));
            row.appendChild(doNothingRadio);

            const meanRadio = columnType === 'numeric' ? document.createElement('td') : null;
            if (meanRadio) {
                meanRadio.appendChild(createRadio('mean', columnName, ''));
                row.appendChild(meanRadio);
            }

            const zeroRadio = columnType === 'numeric' ? document.createElement('td') : null;
            if (zeroRadio) {
                zeroRadio.appendChild(createRadio('zero', columnName, ''));
                row.appendChild(zeroRadio);
            }

            // Manual Input radio button and manual input field
            const manualInputRadio = document.createElement('td');
            manualInputRadio.appendChild(createRadio('manual', columnName, ''));
            row.appendChild(manualInputRadio);

            const manualInput = document.createElement('td');
            manualInput.setAttribute("id", "manual_input_text");
            manualInput.textContent = '';
            manualInput.style.display = 'none';
            manualInput.appendChild(document.createElement('input')); // Add input field inside the cell
            row.appendChild(manualInput);

            // Event listener to show/hide the manual input field
            manualInputRadio.querySelector('input[type="radio"]').addEventListener('change', function () {
                manualInput.style.display = this.checked ? 'block' : 'none';
                if (!this.checked) {
                    manualInput.querySelector('input[type="text"]').value = ''; // Updated selector
                    manualInput.querySelector('input[type="text"]').style.display = 'none';; // Updated selector
                }
            });

            tableBody.appendChild(row);
        }
    }
    }


// Load FillNa Values IN Table Form:
function generateFillNaTableForm(columnsData){
    createColumnOptions(columnsData, 'numeric-table-body', 'numeric');
    createColumnOptions(columnsData, 'categorical-table-body', 'categorical');
    const allRadioButtons = document.querySelectorAll('input[type="radio"]');

    allRadioButtons.forEach(function (radio) {
        radio.addEventListener('change', function () {
            const radioValue = this.value;
            const row = this.closest('tr');

            if (radioValue!='manual'){
                const cellToDisable = row.querySelector('#manual_input_text');;
                cellToDisable.style.display = 'none';
                cellToDisable.setAttribute('disabled', true); // For input elements
                cellToDisable.style.pointerEvents = 'none'; // For non-input elements
                cellToDisable.style.color = 'gray';
                //   row.querySelector('input').disabled = true
            }else{
                const cellToDisable = row.querySelector('#manual_input_text');;
                cellToDisable.style.display = 'block'; // Or 'table-cell' if it's a table cell
                cellToDisable.removeAttribute('disabled'); // Remove 'disabled' attribute for input elements
                cellToDisable.style.pointerEvents = 'auto'; // Revert pointer events for non-input elements
                cellToDisable.style.color = '';
            }

            if (!this.checked) {
                correspondingManualInput.querySelector('input').value = '';
            }
        });
    });
  }

function getSelectedOption(cells, columnType) {
    for (let i = 1; i <= 4; i++) {
        const radio = cells[i] && cells[i].querySelector('input[type="radio"]');
        if (radio && radio.checked) {
            return radio.value;
        }
    }
    return '';
}

function extractTableData(tableBodyId, columnType, jsonList) {
    const tableBody = document.getElementById(tableBodyId);
    const rows = tableBody.querySelectorAll('tr');

    // Iterate through each row
    rows.forEach(function (row) {
        const cells = row.querySelectorAll('td');
        const columnName = cells[0].textContent;
        // Check the selected radio button
        const selectedOption = getSelectedOption(cells, columnType);
        var  inputValue ;
        const manualInputCell = row.querySelector('#manual_input_text');
        if (manualInputCell) {
            // Access the input element within the cell
            const inputElement = manualInputCell.querySelector('input');
            // Check if the input element is found
            if (inputElement) {
                // Access the value of the input element
                inputValue = inputElement.value;
                // Now you can use the inputValue as needed
            }
        }

        // Adjust the index based on your structure
        // Create JSON object and push it to the list
        const jsonObject = {
            "columnName": columnName,
            "selectedOption": selectedOption,
            "textInput": inputValue,
            "columnType":columnType,
        };

        jsonList.push(jsonObject);
    });
}


function GenerateFillNaForm(){
    const jsonList = [];

    // Extract data from the numeric table
    extractTableData('numeric-table-body', 'numeric', jsonList);

    // Extract data from the categorical table
    extractTableData('categorical-table-body', 'categorical', jsonList);

    // Output the generated JSON list
    return jsonList;

}
