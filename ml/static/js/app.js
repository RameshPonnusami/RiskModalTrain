
$(document).ready(function() {
    // Variable to store the file path
    $("#myTabs").hide();
    $(".tab-content").hide();
    
    var columnsTypeData ;
    var uploadedFilePath = null;
    $('#uploadButton').click(function() {
        var fileInput = $('#fileInput')[0].files[0];
        console.log(fileInput);
        var formData = new FormData();
        formData.append('file', fileInput);
        
        $.ajax({
            url: '/upload',
            type: 'POST',
            data: formData,
            contentType: false,
            processData: false,
            success: function(response) {
        //        console.log('File uploaded successfully:', response);
                // Store the file path
                uploadedFilePath = response.data.file_path;
                // Update the UI with the first 10 records and column names
                updateUI(response.data);
                generateFillNaTableForm(response.data.column_types);
                
                // Show a form to select the target column
                showTargetColumnForm();
            },
            error: function(jqXHR, textStatus, errorThrown) {
                console.error('Error uploading file:', textStatus, errorThrown);
            }
        });
    });



    

    $('#selectTargetColumnButton1').click(function() {
        selectedOptionsList = GenerateFillNaForm();        
        var selectedTargetColumn = $('#targetColumnSelect').val();
        $("#loader").show();

        $.ajax({
            url: '/model_trainxx',
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({ target_column: selectedTargetColumn, file_path: uploadedFilePath ,column_changes:selectedOptionsList}),
            success: function(response) {
//                console.log('Target column selected successfully:',response);
                response = JSON.parse(response);
                // Assume you have received data for each step in the response
                var recordDetails = response.threshold;  
                var coef = response.coef;    
                var pvalue = response.pvalue;     
                var chartDetails = response.chartDetails;    
                var SelectedfeaturesDetails = response.selected_features_details;    
                var model_full_path = response.model_full_path;      
                var low_risk_threshold = response.low_risk_threshold;      
                var high_risk_threshold = response.high_risk_threshold;      
                var std_dev = response.std_dev;      
                var testdecile = response.testdecile;      
                var test_decile_chart = response.decile_chart;      
                var htmlTable = generateTable(coef);
                $('#coef').html(htmlTable);
                
                var pvhtmlTable = generateTable(pvalue);
                $('#pvalue').html(pvhtmlTable);
                document.getElementById('testdata-container').innerHTML = '';
                document.getElementById('traindata-container').innerHTML = '';
                document.getElementById('testdata-charts-container').innerHTML = '';
                document.getElementById('traindata-charts-container').innerHTML = '';
                document.getElementById('charts-container').innerHTML = '';
                var testdecilehtmlTable = generateTable(testdecile);
                $('#testdata-container').html(testdecilehtmlTable);
                var traindecilehtmlTable = generateTable(response.trainDecileWithScore);
                $('#traindata-container').html(traindecilehtmlTable);
                var dsahtmlTable = generateTable(response.dsa_dict);
                $('#dsa-container').html(dsahtmlTable);
                
                var containerDiv = document.getElementById('testdata-charts-container');
                var imgElement = document.createElement('img');
                imgElement.src = test_decile_chart;
                containerDiv.appendChild(imgElement);
                var traincontainerDiv = document.getElementById('traindata-charts-container');
                var imgElement = document.createElement('img');
                imgElement.src = response.trainDecileChart;
                traincontainerDiv.appendChild(imgElement);
                
                
                var corr_df_after_binhtmlTable = generateCorrTable(response.corr_df_after_bin);
                $('#after-corr-charts-container').html(corr_df_after_binhtmlTable);
                
                var corr_df_before_binhtmlTable = generateCorrTable(response.corr_df_before_bin);
                $('#before-corr-charts-container').html(corr_df_before_binhtmlTable);
                
                var thresholdTable = generateDictTable(response.threshold);
                
                
                
                // Key to remove from each dictionary
                const keyToRemove = 'criteria';
                
                // Create a new list by removing the specified key from each dictionary
                const modifiedList = SelectedfeaturesDetails.map(dict => removeKeyFromDict(dict, keyToRemove));
//                console.log(modifiedList);
                
                var SelectedfeaturesDetailsTable = generateTableWithOption(modifiedList);
                
                var selectedFeaturesList = generateList(response.selected_features);
                
                // Insert the HTML table and list into div elements with the IDs 'threshold-container' and 'selected-features-container'
                $('#threshold-container').html(thresholdTable);
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




    $('#selectTargetColumnButton').click(function() {
        selectedOptionsList = GenerateFillNaForm();
        var selectedTargetColumn = $('#targetColumnSelect').val();
        $("#loader").show();

        $.ajax({
            url: '/EDA',
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({ target_column: selectedTargetColumn, file_path: uploadedFilePath ,column_changes:selectedOptionsList}),
            success: function(response) {
//                console.log('Target column selected successfully:',response);
                response = JSON.parse(response);
                // Assume you have received data for each step in the response
                var recordDetails = response.threshold;

                var chartDetails = response.chartDetails;
                var SelectedfeaturesDetails = response.selected_features_details;


                document.getElementById('testdata-container').innerHTML = '';
                document.getElementById('traindata-container').innerHTML = '';
                document.getElementById('testdata-charts-container').innerHTML = '';
                document.getElementById('traindata-charts-container').innerHTML = '';
                document.getElementById('charts-container').innerHTML = '';

                var thresholdTable = generateDictTable(response.threshold);

                // Key to remove from each dictionary
                const keyToRemove = 'criteria';
                console.log('SelectedfeaturesDetails',SelectedfeaturesDetails);

//                // Create a new list by removing the specified key from each dictionary
//                const modifiedList = SelectedfeaturesDetails.map(dict => removeKeyFromDict(dict, keyToRemove));
//                console.log('modifiedList',modifiedList);

                var SelectedfeaturesDetailsTable = generateTableWithOption(SelectedfeaturesDetails);

                var selectedFeaturesList = generateList(response.selected_features);

                // Insert the HTML table and list into div elements with the IDs 'threshold-container' and 'selected-features-container'
                $('#threshold-container').html(thresholdTable);
                $('#selected-features-details-container').html(SelectedfeaturesDetailsTable);

                updateCharts(chartDetails,'line_chart') ;
                updateCharts(chartDetails,'bar_chart') ;

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


   $('#featureForm').submit(function(event) {

        event.preventDefault();


        // Collect data from the form
        var formData = collectFormData();

        // Now, you can send formData to the backend using an appropriate method, such as fetch or XMLHttpRequest.
        console.log('Form data:', formData);

        // For example, using fetch:
        selectedOptionsList = GenerateFillNaForm();
        var selectedTargetColumn = $('#targetColumnSelect').val();


        fetch('/model_train_n', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ target_column: selectedTargetColumn, file_path: uploadedFilePath ,column_changes:selectedOptionsList,updated_criteria:formData}),
        })
        .then(response => response.json())
        .then(data => {
        alert("Hello! I am SUCCESS!");

            console.log('Success:', data);

             response = data;
                // Assume you have received data for each step in the response
                var coef = response.coef;
                var pvalue = response.pvalue;
                var SelectedfeaturesDetails = response.selected_features_details;
                var model_full_path = response.model_full_path;
                var low_risk_threshold = response.low_risk_threshold;
                var high_risk_threshold = response.high_risk_threshold;
                var std_dev = response.std_dev;
                var testdecile = response.testdecile;
                var test_decile_chart = response.decile_chart;
                var htmlTable = generateTable(coef);
                $('#coef').html(htmlTable);

                var pvhtmlTable = generateTable(pvalue);
                $('#pvalue').html(pvhtmlTable);
                document.getElementById('testdata-container').innerHTML = '';
                document.getElementById('traindata-container').innerHTML = '';
                document.getElementById('testdata-charts-container').innerHTML = '';
                document.getElementById('traindata-charts-container').innerHTML = '';
                var testdecilehtmlTable = generateTable(testdecile);
                $('#testdata-container').html(testdecilehtmlTable);
                var traindecilehtmlTable = generateTable(response.trainDecileWithScore);
                $('#traindata-container').html(traindecilehtmlTable);
                var dsahtmlTable = generateTable(response.dsa_dict);
                $('#dsa-container').html(dsahtmlTable);

                var containerDiv = document.getElementById('testdata-charts-container');
                var imgElement = document.createElement('img');
                imgElement.src = test_decile_chart;
                containerDiv.appendChild(imgElement);
                var traincontainerDiv = document.getElementById('traindata-charts-container');
                var imgElement = document.createElement('img');
                imgElement.src = response.trainDecileChart;
                traincontainerDiv.appendChild(imgElement);


                var corr_df_after_binhtmlTable = generateCorrTable(response.corr_df_after_bin);
                $('#after-corr-charts-container').html(corr_df_after_binhtmlTable);

                var corr_df_before_binhtmlTable = generateCorrTable(response.corr_df_before_bin);
                $('#before-corr-charts-container').html(corr_df_before_binhtmlTable);

                var thresholdTable = generateDictTable(response.threshold);



                generate_user_input_form(response.column_info,response.object_unique_values,
                    SelectedfeaturesDetails,model_full_path,std_dev,low_risk_threshold,high_risk_threshold)

                $("#myTabs").show();
                $(".tab-content").show();
                $("#loader").hide();
                // Handle the response as needed

            // Handle success response from the backend
        })
        .catch((error) => {
        alert("Hello! I am an eRROR!!");

            console.error('Error:', error);
            // Handle error
        });

    });


});
