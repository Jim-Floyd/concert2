let inputDate = document.querySelector('.check_time'),
    inputDateUser = document.querySelector('.check_time_user'),
    msgTrue = document.querySelector('.true'),
    msgFalse = document.querySelector('.false');

if (inputDate) {
    inputDate.addEventListener('change', () => {
        fetch('/check_date/' + inputDate.dataset.id, {
            method: "POST",
            body: JSON.stringify({
                "time_entered": inputDate.value
            }),
            headers: {
                'Content-Type': 'application/json'
            }
        })
            .then(function (response) {
                return response.json()

            })

            .then(function (jsonResponse) {
                console.log(jsonResponse['found'])
                if (jsonResponse['found']) {
                    msgTrue.style.cssText = 'display:block; color:red'
                    msgFalse.style.cssText = 'display:none;'
                } else if (!jsonResponse['found']) {
                    msgTrue.style.display = 'none'
                    msgFalse.style.cssText = 'display:block; color:green'
                } else {
                    msgTrue.style.display = 'none'
                    msgFalse.style.display = 'none'
                }
            })
    })
} else {
    inputDateUser.addEventListener('change', () => {
        fetch('/check_date_user/' + inputDateUser.dataset.id, {
            method: "POST",
            body: JSON.stringify({
                "time_entered": inputDateUser.value
            }),
            headers: {
                'Content-Type': 'application/json'
            }
        })
            .then(function (response) {
                return response.json()

            })

            .then(function (jsonResponse) {
                console.log(jsonResponse['found'])
                if (jsonResponse['found']) {
                    msgTrue.style.cssText = 'display:block; color:red'
                    msgFalse.style.cssText = 'display:none;'
                } else if (!jsonResponse['found']) {
                    msgTrue.style.display = 'none'
                    msgFalse.style.cssText = 'display:block; color:green'
                } else {
                    msgTrue.style.display = 'none'
                    msgFalse.style.display = 'none'
                }
            })
    })
}