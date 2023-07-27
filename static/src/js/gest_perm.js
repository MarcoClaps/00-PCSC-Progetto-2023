$(document).ready(function () {
    // Aggiungi un gestore di eventi al pulsante
    $('.delete_button').click(function () {
        var p = $(this).data('p');
        var n = $(this).data('n');
        var nn = n.replace(/_/g, ' ');
        // Mostra la finestra popup di conferma
        if (confirm('Sei sicuro di voler cancellare ' + nn + '?')) {
            // Se l'utente ha cliccato su "OK", esegui il codice qui
            console.log('L\'utente ha cliccato su OK');
            // Esempio: reindirizza l'utente a una nuova pagina
            $.ajax({
                url: '/dashboard/gest_perm/delete/' + p,
                type: 'POST',
                data: {
                    csrfmiddlewaretoken: '{{ csrf_token }}'
                },
                success: function (response) {
                    console.log(response);
                    window.location.reload();
                },
                error: function (response) {
                    console.log(response);
                }
            });
        } else {
            // Se l'utente ha cliccato su "Annulla", esegui il codice qui
            console.log('L\'utente ha cliccato su Annulla');
        }
    });
});