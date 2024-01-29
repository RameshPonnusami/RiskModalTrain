$(document).ready(function() {
    $('.tab-content').on('click', 'img', function() {
        // Your function logic for image click goes here
        $("#full-image").attr("src", $(this).attr("src"));
        $('#image-viewer').show();
    });

    // Event handler for tab click
    $("#myTabs a").on("click", function (e) {
        e.preventDefault();
        var tabId = $(this).attr("name");
        // Assuming the content for all tabs is already loaded, simply show the tab
        $('.fade').removeClass("show");
        $('.fade').removeClass("active");
        $('#'+tabId).addClass("show");
        $('#'+tabId).addClass("active");

        $(this).tab("show");
        //$(this).tab("active");
        //$('#'+tabId).addClass("active");

    });

    $("#image-viewer .close").click(function(){
        $('#image-viewer').hide();
    })
});
