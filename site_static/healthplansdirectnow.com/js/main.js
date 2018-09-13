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

    //Mobile responsive menu
    $('#mainMenu').slicknav({
        'label' : ''
    });

    //open popup form
    $('#homeZipButtonJS').click(function(){
        var homeZip = parseInt($('#homeZipJS').val());
        if(isNaN(homeZip) || homeZip.toString().length!= 5){
            alert('Invelid Zip')
        }
        else{
            $('body').addClass('formOpenJS');
            $('#InputZip').val(homeZip);
        }
    });
    $('.closeBtn').click(function(){
        $('body').removeClass('formOpenJS');
    });
    $('.seePlansJs').click(function(){
        $('body').addClass('formOpenJS');
    });

    // Datepicker
    $('[data-toggle="datepicker"]').datepicker();


    $('.faqHeading').click(function(){
        $(this).next().stop().slideToggle();
    })

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

