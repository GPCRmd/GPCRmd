function openPage(url) {
    window.open(url, '_blank');
}

function getInfo() {
    const button = document.getElementById('getInfo');
    button.disabled = true;
    button.innerText = 'Updating...';

    fetch('/admin_panel/get_info', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
    })
    .then(response => response.json())
    .then(data => {
        console.log(data);
        button.disabled = false;
        button.innerText = 'Update';
    })
    .catch(error => {
        console.error('Error:', error);
        button.disabled = false;
        button.innerText = 'Update';
    });
}

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}