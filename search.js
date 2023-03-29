
$(document).ready(function() {
    $(window).load(function() {

    function insertMessage() {
    const query = msg = $('.message-input').val();
    const params = { q: query };

    console.log(query)

    fetch('https://5o8mdgexka.execute-api.us-east-1.amazonaws.com/v5/search?q='.concat(query), {
        headers:{},
        method: 'GET',
        })
        .then(response => {
            response.json().then((data) => {
                console.log(data);
                const gallery = document.getElementById('image_display');
                gallery.innerHTML = '';
                data['results'].forEach(url => {
                    const img = document.createElement('img');
                    img.src = url;
                    gallery.appendChild(img);
            });

            }).catch((err) => {
                console.log(err);
            }) 
            //console.log(response.json()['results'])
        })
        .catch(error => {
            console.log(error)
        });
    
    }

    $(window).on('keydown', function(e) {
        if (e.which == 13) {
          insertMessage();
          return false;
        }
      })

    })
})