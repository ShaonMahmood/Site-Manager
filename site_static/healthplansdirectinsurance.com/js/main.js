/*--------------------------------------------
 ---- Coder: Masud Chowdhury -----------------
 ---- Contact: maxbizbd@ymail.com ------------
 ---- Github: https://github.com/maxbizbd ----
 -------------------------------------------*/
//debounce function when resize windows
function debouncer( func , timeout ) {
    var timeoutID , timeout = timeout || 200;
    return function () {
        var scope = this , args = arguments;
        clearTimeout( timeoutID );
        timeoutID = setTimeout( function () {
            func.apply( scope , Array.prototype.slice.call( args ) );
        } , timeout );
    }
}
/********** Document Ready Function ************/
$(document).ready(function(){

    /*$( "#dataForm" ).submit(function(event) {
        var url = "http://shared.hicleads.com/receive";
        var posting = $.post( url,$("#dataForm").serialize());
        posting.done(function(data) {
            if(data.toLowerCase()=='ok'){
                window.location.href = 'thankyou.php';
            }
            else{
                alert(data);
                return false;
            }

        });
        // Stop form from submitting normally
        event.preventDefault();
    });*/

    jQuery(document).on('click', '.msScrollTo', function() {
        var go_to = $(this).attr('href') || $(this).data('href') || '#';
        if($(go_to).length > 0){$('html, body').animate({scrollTop:$(go_to).position().top}, 1500);}
        return false;
    });
    
});

/********** Window load complete *************/
$(window).load(function(){
    
});

/************** Window resize ***************/
$(window).resize(debouncer(function(){
    
}));