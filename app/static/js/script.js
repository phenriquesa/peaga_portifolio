<<<<<<< HEAD
/* ================================================================ */

function formatar(mascara, documento){
  var i = documento.value.length;
  var saida = mascara.substring(0,1);
  var texto = mascara.substring(i)

  if (texto.substring(0,1) != saida){
            documento.value += texto.substring(0,1);
  }

};
/* ================================================================ */
function BlockLetters(e){
    var tecla=(window.event)?event.keyCode:e.which;
    if((tecla>47 && tecla<58)) return true;
    else{
    	if (tecla==8 || tecla==0) return true;
	else  return false;
    }
};
/* ================================================================ */
=======
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
>>>>>>> dfcd81a (Atualização de arquivos)
