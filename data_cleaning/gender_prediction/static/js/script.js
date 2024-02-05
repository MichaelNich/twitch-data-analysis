document.getElementById("saveButton").addEventListener("click", function() {

    saveButton.disabled = true;
    var checkedNames = [];
    var checkboxes = document.querySelectorAll('input[type="checkbox"]:checked');
    checkboxes.forEach(function(checkbox) {
        checkedNames.push(checkbox.value);
    });

    // Send an HTTP request to the server with the checked names
    var xhr = new XMLHttpRequest();
    xhr.open('POST', '/save_names', true);
    xhr.setRequestHeader('Content-Type', 'application/json');
    xhr.send(JSON.stringify({ names: checkedNames }));

    // Uncheck all checkboxes
    checkboxes.forEach(function(checkbox) {
        checkbox.checked = false;
    });

    alert('Names saved successfully!');
});