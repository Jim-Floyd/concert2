let checkboxes = document.querySelectorAll('.checkboxes');


checkboxes.forEach((checkbox, index) => {
    checkbox.addEventListener('change', () => {
        fetch('/set_artist/' + checkbox.dataset.id, {
            method: "POST",
            body: JSON.stringify({
                "user_checkbox": checkbox.checked
            }),
            headers: {
                'Content-Type': 'application/json'
            }
        })
    })
})