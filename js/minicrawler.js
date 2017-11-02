var crawler = {};

crawler.limit = 300;
crawler.pagination = {};
crawler.intervals = {};
crawler.fails = {},

/*
 * Get entry point crawlers
 */
crawler.getList = function(suc, err) {
    $.ajax({
        url : '/crawler',
        type : 'GET',
        contentType : 'application/json',
        dataType : 'json',
        success : suc,
        error : err
    });
};

/*
 * Get crawler result for a given ID using pagination
 */
crawler.getById = function(id, start, suc, err) {
    $.ajax({
        url : '/crawler/' + id + '?start=' + start + '&limit=' + crawler.limit,
        type : 'GET',
        contentType : 'application/json',
        dataType : 'json',
        success : suc,
        error : err
    });
};

/*
 * Update DataTable content
 */
crawler.updateDataTable = function(id, table) {
    var start = crawler.pagination[id] || 0;
    crawler.getById(id, start, function(result) {
        var data = [];
        $.each(result.refs, function(key, url) {
            data.push([url]);
        });

        // Empty page received
        //
        // It may be because all data was already received or
        // because there was not enough time to crawler creates new entries
        //
        // Stop the interval loop only after 5 failures
        if (data.length == 0) {
            failures = crawler.fails[id] || 0;
            if (failures + 1 >= 5)
                clearInterval(crawler.intervals[id]);
            else
                crawler.fails[id] = failures + 1;
        } else {
            table.rows.add(data).draw(false);
            crawler.pagination[id] = start + data.length;
        }
    }, function(jqXHR, textStatus, errorThrown) {
        // Failed to get content
        error = crawler.getErrorHtml(jqXHR.responseJSON.message);
        content.prepend(error);
    });
};

/*
 * Return HTML to display error
 */
crawler.getErrorHtml = function(msg) {
    return "<p class='error'>" +
        "<i class='fa fa-exclamation' aria-hidden='true'></i>" + msg + "</p>";
};

/*
 * Main function
 */
crawler.main = function() {
    var content = $('#content');

    // Build UI
    crawler.getList(function(result) {
        $.each(result, function(key, entry) {
            content.append('<h3>' + entry.url + '</h3>');
            content.append('<table class="display" width="100%" cellspacing="0" id="table-' + entry._id + '">' +
                           '<thead><tr><th></th></tr></thead></table>');
        
            var table = $('#table-' + entry._id).DataTable({"ordering": false});
            crawler.updateDataTable(entry._id, table);
            var interval = setInterval(function() {
                crawler.updateDataTable(entry._id, table);
            }, 5000);
            crawler.intervals[entry._id] = interval;

        });
    }, function(jqXHR, textStatus, errorThrown) {
        // Failed to get content
        error = crawler.getErrorHtml(jqXHR.responseJSON.message);
        content.prepend(error);
    });
};
