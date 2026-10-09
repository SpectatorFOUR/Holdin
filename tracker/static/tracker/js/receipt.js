document.addEventListener('DOMContentLoaded', function () {
    var list = document.getElementById('history-list');
    var modal = document.getElementById('receipt-modal');
    if (!list || !modal) return;

    var closeBtn = document.getElementById('receipt-close');
    var typeEl = document.getElementById('r-type');
    var amountEl = document.getElementById('r-amount');
    var detailsEl = document.getElementById('r-details');
    var lastFocused = null;

    function addRow(label, value) {
        var dt = document.createElement('dt');
        dt.textContent = label;
        var dd = document.createElement('dd');
        dd.textContent = value;
        detailsEl.appendChild(dt);
        detailsEl.appendChild(dd);
    }

    function openReceipt(btn) {
        var d = btn.dataset;
        typeEl.textContent = d.type;
        typeEl.className = 'receipt-badge ' + d.kind;
        amountEl.textContent = 'Rs. ' + d.amount;

        detailsEl.innerHTML = '';
        addRow('Title', d.title);
        addRow(d.accountLabel, d.account);
        addRow(d.partyLabel, d.party);
        addRow('Date and time', d.datetime);
        if (d.description) addRow('Description', d.description);
        addRow('Receipt no.', '#' + d.id);

        lastFocused = btn;
        modal.hidden = false;
        closeBtn.focus();
    }

    function closeReceipt() {
        modal.hidden = true;
        if (lastFocused) lastFocused.focus();
    }

    list.addEventListener('click', function (event) {
        var btn = event.target.closest('.row-menu');
        if (btn) openReceipt(btn);
    });

    closeBtn.addEventListener('click', closeReceipt);

    modal.addEventListener('click', function (event) {
        if (event.target === modal) closeReceipt();
    });

    document.addEventListener('keydown', function (event) {
        if (event.key === 'Escape' && !modal.hidden) closeReceipt();
    });
});

