$(document).ready(function() {
// Variable to store the file path
$("#myTabs").hide();
$(".tab-content").hide();

var columnsTypeData ;
    var uploadedFilePath = null;
    $('#uploadButton').click(function() {
        var fileInput = $('#fileInput')[0].files[0];

        var formData = new FormData();
        formData.append('file', fileInput);

        $.ajax({
            url: '/upload',
            type: 'POST',
            data: formData,
            contentType: false,
            processData: false,
            success: function(response) {
                console.log('File uploaded successfully:', response);
                // Store the file path
                uploadedFilePath = response.data.file_path;
                // Update the UI with the first 10 records and column names
                updateUI(response.data);

                // Show a form to select the target column
                showTargetColumnForm();
            },
            error: function(jqXHR, textStatus, errorThrown) {
                console.error('Error uploading file:', textStatus, errorThrown);
            }
        });
    });

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


   function updateUI(data) {

    tableHtml = generateTableFromDF(data.columns,data.first_10_records);
    $('#first10Records').html(tableHtml);

    // Update the UI with the list of columns for the target column selection
    var columnsHtml = data.columns.map(column => `<option value="${column}">${column}</option>`).join('');
    $('#targetColumnSelect').html(columnsHtml);

    createColumnOptions(data.column_types);
    columnsTypeData = data.column_types;
    document.getElementById('togglebutton').style.display = 'block';


}
// function showStep(step) {
//            $('.step').addClass('hidden');
//            $('#' + step).removeClass('hidden');
//        }




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
            radioLabel.className = 'radio-label'; // Added class for styling

            radioContainer.appendChild(radio);
            radioContainer.appendChild(radioLabel);

            return radioContainer;
        }

// Function to create options for each column
        function createColumnOptions(columnsData) {
            const columnOptionsContainer = document.getElementById('columnOptionsContainer');
            for (const [columnName, columnType] of Object.entries(columnsData)) {
                const optionDiv = document.createElement('div');
                optionDiv.className = 'mb-1 d-flex align-items-left'; // Added class for styling

                const radioNumeric = createRadio('Do nothing', columnName, 'Do nothing');

                const radioMean = (columnType === 'numeric') ? createRadio('mean', columnName, 'Mean') : null;
                const radioZero = (columnType === 'numeric') ? createRadio('zero', columnName, 'Zero') : null;
                const radioManualInput = createRadio('manual', columnName, 'Manual Input');

                optionDiv.appendChild(radioNumeric);
                if (radioMean) {
                    optionDiv.appendChild(radioMean);
                }
                if (radioZero) {
                    optionDiv.appendChild(radioZero);
                }

                optionDiv.appendChild(radioManualInput);

                const label = document.createElement('label');
                label.textContent = `Column: ${columnName}, Type: ${columnType}`;
                optionDiv.appendChild(label);

                const input = document.createElement('input');
                input.type = 'text';
                input.className = 'form-control'; // Adjust margin as needed
                input.name = columnName + '_manual_input';
                input.style.display = 'none'; // Initially hide the input field

                // Event listener to show/hide the input field based on the selected radio button
                radioManualInput.querySelector('input[type="radio"]').addEventListener('change', function () {
                    input.style.display = this.checked ? 'block' : 'none';
                });

                optionDiv.appendChild(input);
                columnOptionsContainer.appendChild(optionDiv);
            }
        }


     // Assuming you have a function to update content for each step
    function updateContent(step, content) {
        $('#' + 'step' + step + '-content').html(content);
    }



function updateCharts(jsonData,chart_type) {
//console.log(jsonData);
  // Loop through charts and display them
  for (var i = 0; i < jsonData[chart_type].length; i++) {
    var chartData = jsonData[chart_type][i];


    // Create a container div for each entry
    var entryContainerTable = $('<div>').addClass('table-container col-md-6');
    var entryContainerImg = $('<div>').addClass('chart-container col-md-4');

    var TableHtmlString = '';
var ImgHtmlString = '';

    if (chart_type === 'line_chart') {
      // Display line chart image
      var lineChartImage = $('<img>').attr('src', chartData.chart_path).addClass('img-fluid');
      var lineImg = document.createElement('img');
      lineImg.src = lineChartImage.attr('src');  // Get the image source
      entryContainerImg.append(lineImg);
     var lineTable= generateTable(chartData.table_data);
      entryContainerTable.append(lineTable);

        TableHtmlString = $(lineTable).prop('outerHTML');
 ImgHtmlString = $(lineImg).prop('outerHTML');

//      var chartContainer = $('<div>').addClass('chart-container col-md-6');
//        chartContainer.append(lineImg);
//
//    var tableContainer = $('<div>').addClass('table-container col-md-6');
//    tableContainer.append(lineTable);



    } else if (chart_type === 'bar_chart') {
      // Display bar chart image
      var barChartImage = $('<img>').attr('src', chartData.chart_path).addClass('img-fluid');
      var barImg = document.createElement('img');
      barImg.src = barChartImage.attr('src');  // Get the image source
      entryContainerImg.append(barImg);

      // Display bar chart table data
      var barTable = $('<table>').append('<tr><th>Decile Rank</th><th>Bad Loan Total</th><th>Total Records</th><th>ID Min</th><th>ID Max</th><th>ID Mean</th><th>Percentage Bad Loan</th></tr>');
       var barTable= generateTable(chartData.table_data);

     TableHtmlString = $(barTable).prop('outerHTML');
 ImgHtmlString = $(barImg).prop('outerHTML');

      entryContainerTable.append(barTable);

    }

    // Add entryContainer to the main container
//    $('#charts-container').append(childDiv);
console.log(entryContainerImg);
console.log(entryContainerImg.outerHTML);

//console.log('htmlString',htmlString);


    $('#charts-container').append('<div class="row"><div class="col-md-4"><div class="images mx-auto ">'+ImgHtmlString+'</div></div><div class="col-md-8">'+TableHtmlString+'</div></div>');
     //$('.charts-container-1').append(entryContainerImg);
    //$('.charts-container-2').append(entryContainerTable);

    //$('#charts-container').append('<br>');

    // Add break if not the last entry
//    if (i < jsonData.length - 1) {
//      $('#charts-container').append('<br>');
//      $('#charts-container').append('<br>');
//      console.log('addbreak;');
//    }
  }
}


function generate_user_input_form(data,object_unique_data,SelectedfeaturesDetails,model_full_path,std_dev,low_risk_threshold,high_risk_threshold){
console.log('data',model_full_path);
// Create a form dynamically based on column info
                const dynamicFormContainer = document.getElementById('dynamicFormContainer');
                const form = document.createElement('form');
                form.id = 'dynamicForm';
                form.method = 'POST';
//                form.action = '/api';  // Update with your form action URL

                // Add hidden fields to the form
                const hiddenField1 = document.createElement('input');
                hiddenField1.type = 'hidden';
                hiddenField1.name = 'selectedcriteria';
//                hiddenField1.setAttribute('readonly', true);
//                hiddenField1.setAttribute('disabled', true);
                hiddenField1.value = JSON.stringify(SelectedfeaturesDetails);

                form.appendChild(hiddenField1);

                const hiddenField2 = document.createElement('input');
                hiddenField2.type = 'hidden';
                hiddenField2.name = 'model_full_path';
                hiddenField2.value = model_full_path;
//                hiddenField2.setAttribute('readonly', true);
//                hiddenField2.setAttribute('disabled', true);
                form.appendChild(hiddenField2);


                const hiddenField3 = document.createElement('input');
                hiddenField3.type = 'hidden';
                hiddenField3.name = 'std_dev';
                hiddenField3.value = std_dev;
                form.appendChild(hiddenField3);

                const hiddenField4 = document.createElement('input');
                hiddenField4.type = 'hidden';
                hiddenField4.name = 'low_risk_threshold';
                hiddenField4.value = low_risk_threshold;
                form.appendChild(hiddenField4);
                console.log('low_risk_threshold',low_risk_threshold);
                const hiddenField5 = document.createElement('input');
                hiddenField5.type = 'hidden';
                hiddenField5.name = 'high_risk_threshold';
                hiddenField5.value = high_risk_threshold;
                form.appendChild(hiddenField5);



                for (const [column, data_type] of Object.entries(data)) {
                    const label = document.createElement('label');
                    label.for = column;
                    label.textContent = `${column}:`;
                    form.appendChild(label);

                    if (data_type === 'int64') {
                        const input = document.createElement('input');
                        input.type = 'number';
                        input.name = column;
                        input.id = column;
                        input.required = true;
                        form.appendChild(input);
                    } else if (data_type === 'float64' || data_type === 'int32') {
                        const input = document.createElement('input');
                        input.type = 'text';
                        input.pattern = '[0-9]+(\.[0-9]+)?';
                        input.name = column;
                        input.id = column;
                        input.required = true;
                        form.appendChild(input);
                    } else if (data_type === 'object') {
                           const select = document.createElement('select');
                             select.name =column;
                               select.id = column;
                                select.classList.add('form-control');
                                select.required = true;
                                child_data =object_unique_data[column];
                                child_data.forEach(cd => {
                                const option = document.createElement('option');
                                option.value = cd;
                                option.textContent = cd;
                                // Check if the grade is selected (you can replace 'selectedGrade' with the actual selected grade variable)
                                option.selected = 'selectedGrade' === cd;
                                select.appendChild(option);
                                form.appendChild(select);
                                });

                    } else {
                        const input = document.createElement('input');
                        input.type = 'text';
                        input.name = column;
                        input.id = column;
                        input.required = true;
                        form.appendChild(input);
                    }

                    const lineBreak = document.createElement('br');
                    form.appendChild(lineBreak);
                }

                const submitButton = document.createElement('button');
                submitButton.type = 'submit';
                submitButton.textContent = 'Submit';
                form.appendChild(submitButton);

                dynamicFormContainer.appendChild(form);

                // Add an event listener for form submission
                form.addEventListener('submit', function (event) {
                    event.preventDefault(); // Prevent the default form submission

                    // Collect form data
                    const formData = new FormData(form);

                    // Make an AJAX call using the fetch API
                    fetch('/model_test_with_user_input', {
                        method: 'POST',
                           headers: {
                                     'Content-Type': 'application/json', // Set the content type to JSON
                            },
                            body: JSON.stringify({
                                ...Object.fromEntries(formData),
                                jsonData: JSON.parse(formData.get('jsonData')) // Parse the JSON data separately
                            }),
                    })
                    .then(response => response.json()) // Assuming the response is in JSON format
                    .then(data => {
                        // Handle the response data as needed
                        console.log(data);
                        // Assume you have received data for each step in the response
                        var score = data.score;  // Replace with the actual key in your response
                        var risk_cat = data.risk_cat;
                        showPredictedScore(score,risk_cat);


                    })
                    .catch(error => {
                        console.error('Error:', error);
                    });
                });

    }


    function showPredictedScore(Score,Color){
        const dynamicFormContainer = document.getElementById('dynamicFormContainer');
        const paragraphId = 'scoreParagraph';
        const paragraph = document.getElementById(paragraphId);
        if (paragraph) {
                // If the <p> element with the specified ID exists, update its content
                paragraph.textContent = Score;
            } else {
                    const paragraph = document.createElement('p');
                    paragraph.id = paragraphId;
                     paragraph.textContent = Score;
                    // Append the <p> element to the existing <div>
                    dynamicFormContainer.appendChild(paragraph);
        }

        const colorparagraphId = 'colorParagraph';
        const colorParagraph = document.getElementById(colorparagraphId);
        if (colorParagraph) {
                // If the <p> element with the specified ID exists, update its content
                colorParagraph.textContent = Color;
            } else {
                    const colorParagraph = document.createElement('p');
                     colorParagraph.id = colorparagraphId;
                     colorParagraph.textContent = Color;
                    // Append the <p> element to the existing <div>
                    dynamicFormContainer.appendChild(colorParagraph);
                    }
        }


 // Function to remove a specific key from a dictionary
    const removeKeyFromDict = (dict, keyToRemove) => {
        const { [keyToRemove]: removedKey, ...rest } = dict;
        return rest;
    };
    $('#selectTargetColumnButton').click(function() {

            const form = document.getElementById('nanFillForm');
            const formData = new FormData(form);

            const selectedOptionsList = [];

            // Iterate over form data and handle selections for radio buttons only
            formData.forEach((value, name) => {
                // Check if it's a radio button (exclude input fields)
                if (!name.endsWith('_manual_input')) {
                    const columnName = name; // Keep the full column name
                    const selectedOption = (value === 'manual') ? 'manual' : (value === 'mean' && columnsTypeData[columnName] === 'numeric') ? 'mean' :(value === 'zero' && columnsTypeData[columnName] === 'numeric') ? 'zero' : 'do-nothing';

                    const selectedOptions = {
                        columnName: columnName,
                        columnType: columnsTypeData[columnName],
                        selectedOption: selectedOption,
                        textInput: (selectedOption === 'manual') ? formData.get(columnName + '_manual_input') : ''
                    };

                    selectedOptionsList.push(selectedOptions);
                }
            });

            console.log(selectedOptionsList);


        var selectedTargetColumn = $('#targetColumnSelect').val();
         $("#loader").show();

        $.ajax({
            url: '/model_train',
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({ target_column: selectedTargetColumn, file_path: uploadedFilePath ,column_changes:selectedOptionsList}),
            success: function(response) {
                console.log('Target column selected successfully:',response);
                 response = JSON.parse(response);
                 // Assume you have received data for each step in the response
                var recordDetails = response.threshold;  // Replace with the actual key in your response
                var coef = response.coef;    // Replace with the actual key in your response
                var pvalue = response.pvalue;      // Replace with the actual key in your response
                var chartDetails = response.chartDetails;      // Replace with the actual key in your response
                var SelectedfeaturesDetails = response.selected_features_details;      // Replace with the actual key in your response
                var model_full_path = response.model_full_path;      // Replace with the actual key in your response
                var low_risk_threshold = response.low_risk_threshold;      // Replace with the actual key in your response
                var high_risk_threshold = response.high_risk_threshold;      // Replace with the actual key in your response
                var std_dev = response.std_dev;      // Replace with the actual key in your response
                 var htmlTable = generateTable(coef);
                  $('#coef').html(htmlTable);

                  var pvhtmlTable = generateTable(pvalue);
                  $('#pvalue').html(pvhtmlTable);

                  var thresholdTable = generateDictTable(response.threshold);



                    // Key to remove from each dictionary
                    const keyToRemove = 'criteria';

                    // Create a new list by removing the specified key from each dictionary
                    const modifiedList = SelectedfeaturesDetails.map(dict => removeKeyFromDict(dict, keyToRemove));
                    console.log(modifiedList);

                  var SelectedfeaturesDetailsTable = generateTable(modifiedList);

                   var selectedFeaturesList = generateList(response.selected_features);

                  // Insert the HTML table and list into div elements with the IDs 'threshold-container' and 'selected-features-container'
                  $('#threshold-container').html(thresholdTable);
//                  $('#selected-features-container').html(selectedFeaturesList);
                  $('#selected-features-details-container').html(SelectedfeaturesDetailsTable);

                    updateCharts(chartDetails,'line_chart') ;
                    updateCharts(chartDetails,'bar_chart') ;
                    generate_user_input_form(response.column_info,response.object_unique_values,
                                    SelectedfeaturesDetails,model_full_path,std_dev,low_risk_threshold,high_risk_threshold)

                   $("#myTabs").show();
                   $(".tab-content").show();
                 $("#loader").hide();
                // Handle the response as needed
            },
            error: function(jqXHR, textStatus, errorThrown) {
                console.error('Error selecting target column:', textStatus, errorThrown);
                 $("#loader").hide();
            }

        });
    });
});
