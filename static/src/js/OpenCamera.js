navigator.mediaDevices.getUserMedia({video: true}).then(gotMedia).catch(error =>
    console.error('getUserMedia() error:', error));

function gotMedia(mediaStream) {
    const mediaStreamTrack = mediaStream.getVideoTracks()[0];
    const imageCapture = new ImageCapture(mediaStreamTrack);

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
                console.log(data);
            });

            img.onload = () => {
                URL.revokeObjectURL(this.src);
            }
        }).catch(error => console.error('takePhoto() error:', error));
        window.setTimeout(capture, 100000)
    }

    capture()
}