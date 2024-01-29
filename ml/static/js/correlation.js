  function generateCorrTable(data) {
    var table = '<table>';

    // Create table header
    table += '<thead><tr><th></th>';
    for (var i = 0; i < data.length; i++) {
      table += '<th>' + data[i]['index'] + '</th>';
    }
    table += '</tr></thead><tbody>';

    // Create table rows
    for (var i = 0; i < data.length; i++) {
      table += '<tr>';
      // Add correlation index column
      table += '<td>' + data[i]['index'] + '</td>';
      for (var j = 0; j < data.length; j++) {
        var value = data[i][data[j]['index']];
        var colorClass = getColor(value);
        table += '<td class="' + colorClass + '">' + value.toFixed(2) + '</td>';
      }
      table += '</tr>';
    }

    table += '</tbody></table>';
    return table;
  }

  function getColor(value) {
    // You can customize this function to map values to color classes as per your requirements
    // For simplicity, this example uses predefined classes for different ranges
    if (value >= 0.8 ||  value <= -0.8)  {
      return 'heatmap-cell-1';
    } else if (value >= 0.6  ||  value <= -0.6) {
      return 'heatmap-cell-2';
    } else if (value >= 0.4  || value <= -0.4) {
      return 'heatmap-cell-3';
    } else if (value >= 0.2 || value <= -0.2) {
      return 'heatmap-cell-4';
    } else if (value >= -0.2) {
      return 'heatmap-cell-5';
    } else {
      return 'heatmap-cell-6';
    }
  }