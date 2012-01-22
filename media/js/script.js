$(document).ready(function(){
    // Cache the Window object
    $window = $(window);
    // Cache the Y offset and the speed of each sprite
    $('[data-type]').each(function() {
        // For each element that has a data-type attribute
        $('section[data-type="background"]').each(function(){
            // Store some variables based on where we are
            var $self = $(this),
            offsetCoords = $self.offset(),
            topOffset = offsetCoords.top;
            // When the window is scrolled...
            $(window).scroll(function() {
                // If this section is in view
                if ( ($window.scrollTop() + $window.height()) > (topOffset) &&
                    ( (topOffset + $self.height()) > $window.scrollTop() ) ) {
                        // Scroll the background at var speed
                        // the yPos is a negative value because we're scrolling it UP!
                        var yPos = -($window.scrollTop() / $self.data('speed'));
                        // If this element has a Y offset then add it on
                        if ($self.data('offsety')) {
                            yPos += $self.data('offsety');
                        }

                       // Put together our final background position
                       var coords = '50% '+ yPos + 'px';

                       // Move the background
                       $self.css({ backgroundPosition: coords });
                       
                       $('#side-nav li a').each(function(){
                           $(this).removeClass('active');
                           if($(this).html() == $self.attr('id')){
                                $(this).addClass('active');
                            }
                        });

                       // Check for other sprites in this section    
                       $('[data-type="sprite"]', $self).each(function() {
 
                           // Cache the sprite
                           var $sprite = $(this);

                           // Use the same calculation to work out how far to scroll the sprite
                           var yPos = ($window.scrollTop() / $sprite.data('speed'));
                           var coords = $sprite.data('xposition') + ' ' + (yPos + $sprite.data('offsety')) + 'px';

                           $sprite.css({ backgroundPosition: coords });                                                    

                       }); // sprites
                       
                        $('[data-type="horizontal-sprite"]', $self).each(function() {

                              // Cache the sprite
                              var $sprite = $(this);

                              // Use the same calculation to work out how far to scroll the sprite
                              var xPos = ($window.scrollLeft() / $sprite.data('speed'));                    
                              var coords = (xPos + $sprite.data('offsetx')) + 'px' + $sprite.data('yposition') + '40%';

                              $sprite.css({ backgroundPosition: coords });                                                    

                          }); // sprites
                    }
            });
        });
    });
}); // document ready

function fancyboxFormSubmit(){
    var func = arguments.callee;
    $('.fancybox form').submit(function(){
        $.fancybox.showActivity();
        var data = $(this).serialize();
        var url = $(this).attr('action');
        $.ajax({type: "POST", 
                url:url, 
                data:data, 
                success:function(msg){$.fancybox({content:msg,onComplete:func});}, 
                error:function(){$.fancybox.error();}
        });
        return false;
    });
}
$(".fancyboxForm").fancybox({onComplete: fancyboxFormSubmit, autoScale: false});