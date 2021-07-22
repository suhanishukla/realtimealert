function format(value1, value2) {
    return '<tr>'+
        '<td># of camels: </td>' +
      '<td>'+value1 +'</td>'+
    '</tr>'+
    '<tr>'+
        '<td># of zebras: </td>'+
      '<td>'+value2+'</td>'+
     '</td>';
}
$(document).ready(function () {
    var table = $('table.display').DataTable({
      "paging": false,
      "ordering": false,
      "info": false
    });

    // Add event listener for opening and closing details
    $('table.display').on('click', 'td.details-control', function () {
        var tr = $(this).closest('tr');
        var row = table.row(tr);

        if (row.child.isShown()) {
            // This row is already open - close it
            row.child.hide();
            tr.removeClass('shown');
        } else {
            // Open this row
            row.child(format(tr.data('child-value-1'), tr.data('child-value-2'))).show();
            tr.addClass('shown');
        }
    });
});
