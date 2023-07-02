function openCamera() {
    // get the operating system and browser
    var OSName = "Unknown OS";
    if (navigator.appVersion.indexOf("Win") != -1) OSName = "Windows";
    if (navigator.appVersion.indexOf("Mac") != -1) OSName = "MacOS";
    if (navigator.appVersion.indexOf("X11") != -1) OSName = "UNIX";

    var browserName = navigator.appName;
    if (navigator.appVersion.indexOf("Edg") != -1) browserName = "Edge";
    if (navigator.appVersion.indexOf("Chrome") != -1) browserName = "Chrome";
    if (navigator.appVersion.indexOf("Safari") != -1) browserName = "Safari";

    // for chrome and windows we have to use the old method
    if (browserName == "Chrome" && OSName == "Windows") {
        navigator.mediaDevices.getUserMedia({ video: true }).then(gotMedia).catch(error =>
            console.error('getUserMedia() error:', error));
    } else if (browserName == "Safari" && OSName == "MacOS") {
        navigator.mediaDevices.getUserMedia({ video: true }).then(gotMedia).catch(error =>
            console.error('getUserMedia() error:', error));
    }


    function gotMedia(mediaStream) {
        const mediaStreamTrack = mediaStream.getVideoTracks()[0];

        // set imageCapture based on the browser and operating system
        if (browserName == "Chrome" && OSName == "Windows") {
            const imageCapture = new ImageCapture(mediaStreamTrack);
        } else if (browserName == "Safari" && OSName == "MacOS") {
            const imageCapture = new ImageCapture(mediaStreamTrack);
        }
        // const imageCapture = new ImageCapture(mediaStreamTrack);

        //console.log(imageCapture);

        function capture() {
            imageCapture.takePhoto().then(blob => {
                img = document.getElementById("img")
                img.src = URL.createObjectURL(blob);

                var fd = new FormData();
                fd.append('file', blob, 'screenshot.png');

                $.ajax({
                    type: 'POST',
                    url: '/upload',
                    data: fd,
                    processData: false,
                    contentType: false
                }).done(function (data) {
                    $('#result').text(data);
                    console.log(data);
                });

                img.onload = () => {
                    URL.revokeObjectURL(this.src);
                }
            }).catch(error => console.error('takePhoto() error:', error));
            window.setTimeout(capture, 100000)
        }

        capture();
    }
}


