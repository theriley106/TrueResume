$(function(){

    var refreshFilenameList = function(data){
        return;
    };

    var fileUploadSuccess = function(data){
        console.log(data);
        window.location.href = data;
        var url = "/filenames";
        var promise = $.get(url);
        promise.then(refreshFilenameList);
    };

    var fileUploadFail = function(data){};

    var dragHandler = function(evt){
        evt.preventDefault();
    };

    var dropHandler = function(evt){
        evt.preventDefault();
        var files = evt.originalEvent.dataTransfer.files;

        var formData = new FormData();
        formData.append("file2upload", files[0]);

        var req = {
            url: "/sendfile",
            method: "post",
            processData: false,
            contentType: false,
            data: formData
        };

        var promise = $.ajax(req);
        promise.then(fileUploadSuccess, fileUploadFail);
    };

    var dropHandlerSet = {
        dragover: dragHandler,
        drop: dropHandler
    };

    $(".droparea").on(dropHandlerSet);

    //fileUploadSuccess(false); // called to ensure that we have initial data
});
