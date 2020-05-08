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
