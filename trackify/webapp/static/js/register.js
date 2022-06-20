function validateEmail(email) {
    var re = /^(([^<>()\[\]\\.,;:\s@"]+(\.[^<>()\[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/
    return re.test(String(email).toLowerCase())
}

function validate() {
    let password = $('#password').value
    let verifiedPassword = $('#verified_password').value
    let username = $('#username').value
    let email = $('#email').value
    if (username === '') {
        $('#error_message').innerHTML = 'username cant be empty'
        return false
    }
    if (password === '') {
        $('#error_message').innerHTML = 'password cant be empty'
        return false
    }
    if (!(password === verifiedPassword)) {
        $('#error_message').innerHTML = 'passwords do not match'
        return false
    }
    if (email == '') {
        $('#error_message').innerHTML = 'email cant be empty'
        return false
    }
    if (!validateEmail(email)) {
        $('#error_message').innerHTML = 'entered email is incorrect'
        return false
    }
    return true
}
