const container = document.getElementById('container');
const registerBtn = document.getElementById('register');
const loginBtn = document.getElementById('login');

registerBtn.addEventListener('click', () => {
    container.classList.add("active");
});

loginBtn.addEventListener('click', () => {
    container.classList.remove("active");
});


    $('#confirmDeleteModal').on('show.bs.modal', function (event) {
        var button = $(event.relatedTarget);
        var form = button.closest('form');
        form.on('submit', function (e) {
            e.preventDefault();
        });
    });

    $('#confirmDeleteModal').on('hidden.bs.modal', function () {
        var form = $(this).find('form');
        form.off('submit');
    });