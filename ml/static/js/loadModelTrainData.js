  function updateUI(data) {

        tableHtml = generateTableFromDF(data.columns,data.first_10_records);
        $('#first10Records').html(tableHtml);

        // Update the UI with the list of columns for the target column selection
        var columnsHtml = data.columns.map(column => `<option value="${column}">${column}</option>`).join('');
        $('#targetColumnSelect').html(columnsHtml);
        console.log(data.column_types);
        createColumnOptions(data.column_types);
        columnsTypeData = data.column_types;
        document.getElementById('togglebutton').style.display = 'block';

    }

     // Assuming you have a function to update content for each step
    function updateContent(step, content) {
        $('#' + 'step' + step + '-content').html(content);
    }



    function updateCharts(jsonData,chart_type) {
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


            $('#charts-container').append('<div class="row"><div class="col-md-4"><div class="images mx-auto ">'+ImgHtmlString+'</div></div><div class="col-md-8">'+TableHtmlString+'</div></div>');

        }
    }

