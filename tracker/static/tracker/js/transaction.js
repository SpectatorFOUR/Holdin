document.addEventListener('DOMContentLoaded', function () {
    var modal = document.getElementById('tx-modal');
    var form = document.getElementById('tx-form');
    if (!modal || !form) return;

    var box = document.getElementById('tx-box');
    var heading = document.getElementById('tx-heading');
    var accountLabel = document.getElementById('tx-account-label');
    var partyLabel = document.getElementById('tx-party-label');
    var formError = document.getElementById('tx-form-error');
    var saveBtn = document.getElementById('tx-save');
    var cancelBtn = document.getElementById('tx-cancel');
    var closeBtn = document.getElementById('tx-close');

    var kinds = {
        credit: { title: 'Add credit', account: 'Balance in', party: 'Source', url: form.dataset.creditUrl },
        debit: { title: 'Add debit', account: 'Balance from', party: 'Paid to', url: form.dataset.debitUrl }
    };
    var currentKind = null;
    var lastFocused = null;

    function nowLocal() {
        var d = new Date();
        d.setMinutes(d.getMinutes() - d.getTimezoneOffset());
        return d.toISOString().slice(0, 16);
    }

    function clearErrors() {
        formError.textContent = '';
        form.querySelectorAll('.field-error').forEach(function (el) { el.textContent = ''; });
    }

    function showErrors(errors) {
        Object.keys(errors).forEach(function (field) {
            var el = form.querySelector('.field-error[data-for="' + field + '"]');
            var text = errors[field].join(' ');
            if (el) {
                el.textContent = text;
            } else {
                formError.textContent = (formError.textContent + ' ' + text).trim();
            }
        });
    }

    function openModal(kind, trigger) {
        currentKind = kind;
        lastFocused = trigger;
        heading.textContent = kinds[kind].title;
        accountLabel.textContent = kinds[kind].account;
        partyLabel.textContent = kinds[kind].party;
        box.dataset.kind = kind;

        form.reset();
        clearErrors();
        form.elements['date_time'].value = nowLocal();

        modal.hidden = false;
        form.elements['title'].focus();
    }

    function closeModal() {
        modal.hidden = true;
        if (lastFocused) lastFocused.focus();
    }

    document.querySelectorAll('[data-open-tx]').forEach(function (btn) {
        btn.addEventListener('click', function () {
            openModal(btn.dataset.openTx, btn);
        });
    });

    closeBtn.addEventListener('click', closeModal);
    cancelBtn.addEventListener('click', closeModal);

    document.addEventListener('keydown', function (event) {
        if (event.key === 'Escape' && !modal.hidden) closeModal();
    });

    form.addEventListener('submit', function (event) {
        event.preventDefault();
        clearErrors();
        saveBtn.disabled = true;
        saveBtn.textContent = 'Saving...';

        fetch(kinds[currentKind].url, {
            method: 'POST',
            body: new FormData(form),
            headers: { 'X-Requested-With': 'XMLHttpRequest' }
        })
            .then(function (response) {
                return response.json().then(function (data) {
                    return { ok: response.ok, data: data };
                });
            })
            .then(function (result) {
                if (result.ok && result.data.ok) {
                    ['total', 'cash', 'bank', 'wallet'].forEach(function (key) {
                        document.getElementById('bal-' + key).textContent = 'Rs. ' + result.data.balances[key];
                    });
                    window.holdinHistory.reset(result.data.html, result.data.next_page);
                    closeModal();
                } else {
                    showErrors(result.data.errors || {});
                }
            })
            .catch(function () {
                formError.textContent = 'Something went wrong. Please try again.';
            })
            .then(function () {
                saveBtn.disabled = false;
                saveBtn.textContent = 'Save';
            });
    });
});


