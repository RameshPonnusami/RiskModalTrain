$(document).ready(function() {
// Variable to store the file path
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
  var table = '<table border="1"><thead><tr>';

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
        var tableHtml = '<table border="1"><thead><tr>';

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
    var table = '<table border="1"><thead><tr><th>Attribute</th><th>Value</th></tr></thead><tbody>';
    for (var key in data) {
      table += '<tr><td>' + key + '</td><td>' + data[key] + '</td></tr>';
    }
    table += '</tbody></table>';
    return table;
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
    var entryContainer = $('<div>');

    if (chart_type === 'line_chart') {
      // Display line chart image
      var lineChartImage = $('<img>').attr('src', chartData.chart_path);
      var lineImg = document.createElement('img');
      lineImg.src = lineChartImage.attr('src');  // Get the image source
      entryContainer.append(lineImg);

      // Display line chart table data
//      var lineTable = $('<table>').append('<tr><th>X</th><th>Y</th></tr>');

     var lineTable= generateTable(chartData.table_data);



      entryContainer.append(lineTable);
    } else if (chart_type === 'bar_chart') {
      // Display bar chart image
      var barChartImage = $('<img>').attr('src', chartData.chart_path);
      var barImg = document.createElement('img');
      barImg.src = barChartImage.attr('src');  // Get the image source
      entryContainer.append(barImg);

      // Display bar chart table data
      var barTable = $('<table>').append('<tr><th>Decile Rank</th><th>Bad Loan Total</th><th>Total Records</th><th>ID Min</th><th>ID Max</th><th>ID Mean</th><th>Percentage Bad Loan</th></tr>');
       var barTable= generateTable(chartData.table_data);

      entryContainer.append(barTable);
    }

    // Add entryContainer to the main container
    $('#charts-container').append(entryContainer);

    // Add break if not the last entry
    if (i < jsonData.length - 1) {
      $('#charts-container').append('<br>');
    }
  }
}




    $('#selectTargetColumnButton').click(function() {
        var selectedTargetColumn = $('#targetColumnSelect').val();

        $.ajax({
            url: '/model_train',
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({ target_column: selectedTargetColumn, file_path: uploadedFilePath }),
            success: function(response) {
                console.log('Target column selected successfully:',response);
                 response = JSON.parse(response);
                 // Assume you have received data for each step in the response
                var recordDetails = response.threshold;  // Replace with the actual key in your response
                var coef = response.coef;    // Replace with the actual key in your response
                var pvalue = response.pvalue;      // Replace with the actual key in your response
                var chartDetails = response.chartDetails;      // Replace with the actual key in your response
                var SelectedfeaturesDetails = response.selected_features_details;      // Replace with the actual key in your response
//                console.log('modelresponse',pvalue)
                 var htmlTable = generateTable(coef);
                  $('#coef').html(htmlTable);

                  var pvhtmlTable = generateTable(pvalue);
                  $('#pvalue').html(pvhtmlTable);

                  var thresholdTable = generateDictTable(response.threshold);

                  var SelectedfeaturesDetailsTable = generateTable(SelectedfeaturesDetails);

                   var selectedFeaturesList = generateList(response.selected_features);

                  // Insert the HTML table and list into div elements with the IDs 'threshold-container' and 'selected-features-container'
                  $('#threshold-container').html(thresholdTable);
//                  $('#selected-features-container').html(selectedFeaturesList);
                  $('#selected-features-details-container').html(SelectedfeaturesDetailsTable);

                    updateCharts(chartDetails,'line_chart') ;
                    updateCharts(chartDetails,'bar_chart') ;




                // Handle the response as needed
            },
            error: function(jqXHR, textStatus, errorThrown) {
                console.error('Error selecting target column:', textStatus, errorThrown);
            }
        });
    });
});
