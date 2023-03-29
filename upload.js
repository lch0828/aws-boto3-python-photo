window.onload = function () {
    // var image_upload = document.getElementById('image_upload');
    const sendbtn = document.getElementById('submit');
    const imgInp = document.querySelector('input[type="file"]');
    imgInp.onchange = evt => {
        blah.style.display = "inline"
        const [file] = imgInp.files
        if (file) {
          blah.src = URL.createObjectURL(file)
        }
      }

    sendbtn.onclick = function(){
      // fileInput is an HTMLInputElement: <input type="file" id="myfileinput" multiple>
      const label = document.getElementById('label').value;

      const img = imgInp.files[0]
      if (typeof img !== "undefined") {
        const formData = new FormData();
        formData.append('file', img);
  2
        console.log(img)

        const params = {
          'x-amz-meta-filename': img.name,
          'Content-Type': img.type,
          //'Content-Type':img.type,
          //'x-amz-meta-customLabels': customLabels.replace(/\s/g, '').trim(),
        }
        console.log(label.replace(/\s/g, '').trim())

        fetch('https://5o8mdgexka.execute-api.us-east-1.amazonaws.com/v5/upload', {
          method: 'PUT',
          headers: {
              'x-amz-meta-customLabels':label.replace(/\s/g, '').trim(),
              'x-amz-meta-filename': img.name,
              'Content-Type': img.type,
          },
          body: img
          })
          .then(response => {
              console.log(response)
              location.reload(true);
          })
          .catch(error => {
              console.log(error)
          });

    }

}

}
