let inputDate = document.querySelector('.check_time');


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
})
