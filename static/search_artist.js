function search_artist() {

    let input = document.getElementById('inputSearchName').value

    input = input.toLowerCase();

    let x = document.getElementsByClassName('searching');
    console.log(input)


    for (i = 0; i < x.length; i++) {

        if (!x[i].innerHTML.toLowerCase().includes(input)) {

            x[i].style.display = "none";

        }

        else {

            x[i].style.display = "list-item";

        }

    }
}