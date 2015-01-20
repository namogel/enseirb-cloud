// ajoute la propriété pour le drop et le transfert de données
$.event.props.push('dataTransfer');
 
$(document).ready(function() {
    var i, $this;
    var DJANGO_SERV = 'http://localhost:8000/';
 
    $('#table tr').on({
        // on commence le drag
        dragstart: function(e) {
            $this = $(this);
            i = $this.index();
            $this.css('opacity', '0.5');
            
            // on garde l'id en mémoire 
            e.dataTransfer.setData('id', $this.attr('id'));
            // e.dataTransfer.setData('location', $('#table').attr('location'));
            // console.log($('#table').attr('location'));
            // DEBUG
            //e.dataTransfer.setData('id', '333');
        },

        // on passe sur un élément draggable
        dragenter: function(e) {
            // on augmente la taille pour montrer le draggable
            $(this).animate({
                width: '90px'
            }, 'fast');
            e.preventDefault();
        },

        // on quitte un élément draggable
        dragleave: function() {
            // on remet la taille par défaut
            $(this).animate({
                width: '75px'
            }, 'fast');
        },
        
        // déclenché tant qu on a pas lâché l élément
        dragover: function(e) {
            e.preventDefault();
        },

        // on lâche l élément
        drop: function(e) {
            // si l élément sur lequel on drop n'est pas l'élément de départ
            if (i !== $(this).index()) {
                
                var data_get = {
                    'location': $('#table').attr('location'),
                    'field': {
                        'dragged_file_id' : e.dataTransfer.getData('id'),
                        // DEBUG
                        'dropped_file_id' : $(this).attr('id'),
                        //'dropped_file_id' : '666',
                    },
                }
                $.post(DJANGO_SERV + "tree/update/move" , data_get);
                console.log(data_get);

            }
            // on remet la taille par défaut
            $(this).animate({
                width: '75px'
            }, 'fast');
        },
        
        // fin du drag (même sans drop)
        dragend: function() {
            $(this).css('opacity', '1');
        },
        
        // au clic sur un élément
        click: function() {
            //alert($(this).text());
        }
    });
});
