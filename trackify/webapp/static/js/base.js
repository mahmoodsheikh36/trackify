function $(selector) {
    return document.querySelector(selector)
}

function navbarFunction() {
    var x = document.getElementById("topnav")
    console.log(x)
    if (x.className === "topnav") {
        x.className += " responsive"
    } else {
        x.className = "topnav"
    }
}

window.onload = function() {
    // the element that contains the name of the tab in the navbar to be selected
    let elementWithValue = $('#navbar_value')
    if (elementWithValue) {
        let value = elementWithValue.value
        let navbar = $('#topnav')
        for (let i = 0; i < navbar.children.length; ++i) {
            navbarTab = navbar.children[i]
            if (navbarTab.innerHTML === value) {
                console.log(value)
                navbarTab.className += 'active'
            }
        }
    }
}
