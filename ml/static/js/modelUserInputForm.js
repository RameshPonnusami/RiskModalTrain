function generate_user_input_form(data,object_unique_data,SelectedfeaturesDetails,model_full_path,std_dev,low_risk_threshold,high_risk_threshold){
    // Create a form dynamically based on column info
    document.getElementById('dynamicFormContainer').innerHTML = '';
    const dynamicFormContainer = document.getElementById('dynamicFormContainer');

    const form = document.createElement('form');
    form.id = 'dynamicForm';
    form.method = 'POST';
    // Add hidden fields to the form
    const hiddenField1 = document.createElement('input');
    hiddenField1.type = 'hidden';
    hiddenField1.name = 'selectedcriteria';
    hiddenField1.value = JSON.stringify(SelectedfeaturesDetails);

    form.appendChild(hiddenField1);

    const hiddenField2 = document.createElement('input');
    hiddenField2.type = 'hidden';
    hiddenField2.name = 'model_full_path';
    hiddenField2.value = model_full_path;
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
            input.className='form-control';
            input.name = column;
            input.id = column;
            input.required = true;
            form.appendChild(input);

        } else if (data_type === 'float64' || data_type === 'int32') {
            const input = document.createElement('input');
            input.type = 'text';
            input.className='form-control';
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
                option.className='form-control';
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
            input.className='form-control';
            form.appendChild(input);
        }

        const lineBreak = document.createElement('br');
        form.appendChild(lineBreak);
    }

    const submitButton = document.createElement('button');
    submitButton.type = 'submit';
    submitButton.textContent = 'Submit';
    submitButton.className='btn btn-md btn-success';
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
    const predictedResult = document.getElementById('predictedResult');
    var csscolorClass = '';
    var cssMsg = '';
    var cssheadClass = '';
    if (Color==='Green'){
        csscolorClass = 'bg-lightgreen';
        cssMsg = 'Financials are sufficient';
        cssWarningClass = ' <div class="succes succes-animation icon-top"><i class="fa fa-check"></i></div>,'+
        '<div class="succes border-bottom"></div>';
    }else if(Color==='Red'){
        csscolorClass = 'bg-lightred';
        cssMsg = 'Financials are in-sufficient';
        cssWarningClass = '<div class="danger danger-animation icon-top"><i class="fa fa-times"></i></div>,'+
        '<div class="danger border-bottom"></div>';
    }else {
        csscolorClass = 'bg-lightyellow';
        cssMsg = 'Chance to consider';
        cssWarningClass = '<div class="danger danger-animation icon-top"><i class="fa fa-times"></i></div>,'+
        '<div class="danger border-bottom"></div>';
    }
    var cardString = ('<h2 class="text-center text-white border bg-primary rounded">Predicted Result:'+ Color+'</h2>');
    cardString += '<div class="custom-modal '+csscolorClass+'">,'+
                    cssWarningClass+
                    '<div class="content">,'+
                    '<p class="type">Score:'+Score +'</p>'+
                    cssMsg+
                    '</div>,'+
                    '</div>,'
    predictedResult.innerHTML = cardString;


}