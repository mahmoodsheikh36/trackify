function $(selector) {
    return document.querySelector(selector)
}

function toggleMenu() {
    let menuButton = $("#topnav")
    if (menuButton.className === "topnav") {
        menuButton.className += " responsive"
    } else {
        menuButton.className = "topnav"
    }
}

function highlightCurrentNavbarTab() {
    // the element that contains the name of the tab in the navbar to be selected
    let elementWithValue = $('#navbar_value')
    if (elementWithValue) {
        let value = elementWithValue.value
        let navbars = [$('#topnav_left'), $('#topnav_right')];
        navbars.forEach(navbar => {
            for (let i = 0; i < navbar.children.length; ++i) {
                navbarTab = navbar.children[i]
                if (navbarTab.innerHTML === value) {
                    navbarTab.className += 'active'
                }
            }
        })
    }
}

function showMessage(msg, timeout) {
    $('.message').innerHTML = msg
    $('.message').style.display = "block"
    if (timeout !== undefined) {
        setTimeout(function() {
            $('.message').style.display = 'none'
        }, timeout * 1000);
    }
}
function hideMessage() {
    $('.message').style.display = 'none'
}

function fetchAPIData(backend) {
}
