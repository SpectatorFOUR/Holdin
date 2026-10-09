document.addEventListener('DOMContentLoaded', function () {
    var list = document.getElementById('history-list');
    if (!list) return;

    var nextPage = list.dataset.nextPage;
    var loading = false;
    var version = 0;

    function loadMore() {
        if (!nextPage || loading) return;
        loading = true;
        var myVersion = version;

        fetch(list.dataset.url + '?page=' + nextPage)
            .then(function (response) { return response.json(); })
            .then(function (data) {
                if (myVersion !== version) return;
                list.insertAdjacentHTML('beforeend', data.html);
                nextPage = data.next_page;
                loading = false;
                fillIfShort();
            })
            .catch(function () { loading = false; });
    }

    function nearBottom() {
        return list.scrollTop + list.clientHeight >= list.scrollHeight - 100;
    }

    function fillIfShort() {
        if (nextPage && list.scrollHeight <= list.clientHeight) {
            loadMore();
        }
    }

    list.addEventListener('scroll', function () {
        if (nearBottom()) loadMore();
    });

    window.holdinHistory = {
        reset: function (html, next) {
            version += 1;
            loading = false;
            list.innerHTML = html || '<p class="empty">No transactions yet.</p>';
            nextPage = next;
            list.scrollTop = 0;
            fillIfShort();
        }
    };

    fillIfShort();
});


