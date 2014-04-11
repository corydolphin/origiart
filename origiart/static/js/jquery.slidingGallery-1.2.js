/*
*       Developed by Justin Mead
*       ©2009 MeadMiracle
*       www.meadmiracle.com / meadmiracle@gmail.com
*       Version 1.0
*       Testing: IE7/Windows XP
*                Firefox/Windows XP
*       Licensed under the Creative Commons GPL http://creativecommons.org/licenses/GPL/2.0/
*
*       OPTIONS LISTING:
*           *Lheight, Lwidth            - the height and width to use for the center image
*           *startClass                 - the class label of the image to place in the center slot at the start of the gallery
*           *slideSpeed                 - the animation speed of sliding. use jQuery animation speed values
*           *gutterWidth                - the horizontal distance between each of the images. use a pixel value
*
*       All options have default values, and as such, are optional.  Check the 'options' JSON object below to see the defaults.
*/

(function($) {
    $.galleryUtility = {};
    $.galleryUtility.centerImage = {};
    $.galleryUtility.rightImage = {};
    $.galleryUtility.leftImage = {};
    $.galleryUtility.rightImageStorage = {};
    $.galleryUtility.leftImageStorage = {};
    $.galleryUtility.gallery = {};

    $.galleryUtility.Options = {
        container: null,
        Lheight: 400,
        Lwidth: 600,
        startClass: 'start',
        slideSpeed: 'normal',
        gutterWidth: 50
    };

    $.fn.slidingGallery = function(options) {
        //global settings
        $.extend($.galleryUtility.Options, options);
        //eliminate overflow
        $('body').css('overflow-x', 'hidden');
        var container = null;
        if (!$.galleryUtility.Options.container) {
            $.galleryUtility.Options.container = $('body');
        } else {
            $.galleryUtility.Options.container.css('position', 'relative');
        }
        $.galleryUtility.gallery = $(this).css('cursor', 'pointer');
        $.galleryUtility.definePositions();

        //setup existing images
        var lastIndex = 0;
        var gallerySize = $.galleryUtility.gallery.each(function(i) {
            $(this).attr({
                'index': i,
                'prev': (i - 1),
                'next': (i + 1)
            }).css('position', 'absolute');
            lastIndex = i;
        }).hide().size();

        $.galleryUtility.gallery.filter('[index=' + lastIndex + ']').attr('next', 0);
        $.galleryUtility.gallery.filter('[index=0]').attr('prev', lastIndex);

        //set images
        $.galleryUtility.setCenter($.galleryUtility.gallery.filter('.' + $.galleryUtility.Options.startClass).show());
        $.galleryUtility.setLeft($.galleryUtility.gallery.filter('[index=' + $.galleryUtility.centerImage.image.attr('prev') + ']').show());
        $.galleryUtility.setRight($.galleryUtility.gallery.filter('[index=' + $.galleryUtility.centerImage.image.attr('next') + ']').show());
        $.galleryUtility.setLeftStorage($.galleryUtility.gallery.filter('[index=' + $.galleryUtility.leftImage.image.attr('prev') + ']'));
        $.galleryUtility.setRightStorage($.galleryUtility.gallery.filter('[index=' + $.galleryUtility.rightImage.image.attr('next') + ']'));

        //bind events
        $.galleryUtility.leftImage.image.one('click', $.galleryUtility.slideRight);
        $.galleryUtility.rightImage.image.one('click', $.galleryUtility.slideLeft);
        $(window).resize(function() {
            $.galleryUtility.definePositions();
            $.galleryUtility.setCenter($.galleryUtility.centerImage.image);
            $.galleryUtility.setLeft($.galleryUtility.leftImage.image);
            $.galleryUtility.setRight($.galleryUtility.rightImage.image);
            $.galleryUtility.setLeftStorage($.galleryUtility.leftImageStorage.image);
            $.galleryUtility.setRightStorage($.galleryUtility.rightImageStorage.image);
        });

        //return the objects (for chaining purposes)
        return $(this);
    };

    $.galleryUtility.slideRight = function() {
        var liLeft = $.galleryUtility.leftImage.left($.galleryUtility.leftImageStorage.image, $.galleryUtility.leftImage.image);
        var riLeft = $.galleryUtility.rightImage.left($.galleryUtility.leftImage.image);
        var risLeft = $.galleryUtility.rightImageStorage.left($.galleryUtility.centerImage.image);

        $.galleryUtility.leftImageStorage.image.animate({
            'top': $.galleryUtility.leftImage.top,
            'left': liLeft,
            'opacity': 'show'
        },
        $.galleryUtility.Options.slideSpeed, 'linear', function() {
            $(this).one('click', $.galleryUtility.slideRight);
        });

        $.galleryUtility.leftImage.image.unbind().animate({
            'top': $.galleryUtility.centerImage.top,
            'left': $.galleryUtility.centerImage.left,
        });

        $.galleryUtility.centerImage.image.unbind().animate({
            'top': $.galleryUtility.rightImage.top,
            'left': riLeft,
        },
        $.galleryUtility.Options.slideSpeed, 'linear', function() {
            $(this).one('click', $.galleryUtility.slideLeft);
        });

        $.galleryUtility.rightImage.image.unbind().animate({
            'top': $.galleryUtility.rightImageStorage.top,
            'left': risLeft,
            'opacity': 'hide'
        },
        $.galleryUtility.Options.slideSpeed, 'linear');

        $.galleryUtility.rightImageStorage.image = $.galleryUtility.rightImage.image;
        $.galleryUtility.rightImage.image = $.galleryUtility.centerImage.image;
        $.galleryUtility.centerImage.image = $.galleryUtility.leftImage.image;
        $.galleryUtility.leftImage.image = $.galleryUtility.leftImageStorage.image;
        $.galleryUtility.setLeftStorage($.galleryUtility.gallery.filter('[index=' + $.galleryUtility.leftImageStorage.image.attr('prev') + ']'));
    };

    $.galleryUtility.slideLeft = function() {
        var riLeft = $.galleryUtility.rightImage.left($.galleryUtility.rightImage.image);
        var liLeft = $.galleryUtility.leftImage.left($.galleryUtility.centerImage.image, $.galleryUtility.rightImage.image);
        var lisLeft = $.galleryUtility.leftImageStorage.left($.galleryUtility.leftImage.image, $.galleryUtility.centerImage.image, $.galleryUtility.rightImage.image);

        $.galleryUtility.rightImageStorage.image.animate({
            'top': $.galleryUtility.rightImage.Ltop,
            'left': riLeft,
            'opacity': 'show'
        },
        $.galleryUtility.Options.slideSpeed, 'linear', function() {
            $(this).one('click', $.galleryUtility.slideLeft);
        });

        $.galleryUtility.rightImage.image.unbind().animate({
            'top': $.galleryUtility.centerImage.top,
            'left': $.galleryUtility.centerImage.left,
        });

        $.galleryUtility.centerImage.image.unbind().animate({
            'top': $.galleryUtility.leftImage.top,
            'left': liLeft,
            'height': $.galleryUtility.leftImage.height,
            'width': $.galleryUtility.leftImage.width
        },
        $.galleryUtility.Options.slideSpeed, 'linear', function() {
            $(this).one('click', $.galleryUtility.slideRight);
        });

        $.galleryUtility.leftImage.image.unbind().animate({
            'top': $.galleryUtility.leftImageStorage.top,
            'left': lisLeft, 
            'opacity': 'hide'
        },
        $.galleryUtility.Options.slideSpeed, 'linear');

        $.galleryUtility.leftImageStorage.image = $.galleryUtility.leftImage.image;
        $.galleryUtility.leftImage.image = $.galleryUtility.centerImage.image;
        $.galleryUtility.centerImage.image = $.galleryUtility.rightImage.image;
        $.galleryUtility.rightImage.image = $.galleryUtility.rightImageStorage.image;
        $.galleryUtility.setRightStorage($.galleryUtility.gallery.filter('[index=' + $.galleryUtility.rightImageStorage.image.attr('next') + ']'));
    };

    $.galleryUtility.setRightStorage = function(image) {
        $.galleryUtility.rightImageStorage.image = image;
        $.galleryUtility.rightImageStorage.image.hide().css({
            'top': $.galleryUtility.rightImageStorage.top,
        });
        $.galleryUtility.rightImageStorage.image.css('left', $.galleryUtility.rightImageStorage.left($.galleryUtility.rightImage.image));
    };

    $.galleryUtility.setLeftStorage = function(image) {
        $.galleryUtility.leftImageStorage.image = image;
        $.galleryUtility.leftImageStorage.image.hide().css({
            'top': $.galleryUtility.leftImageStorage.top,
        });
        $.galleryUtility.leftImageStorage.image
             .css('left', $.galleryUtility.leftImageStorage.left($.galleryUtility.leftImageStorage.image, $.galleryUtility.leftImage.image, $.galleryUtility.centerImage.image));
    };

    $.galleryUtility.setCenter = function(image) {
        $.galleryUtility.centerImage.image = image;
        $.galleryUtility.centerImage.image.css({
            'top': $.galleryUtility.centerImage.top,
            'left': $.galleryUtility.centerImage.left,
        });
    };

    $.galleryUtility.setRight = function(image) {
        $.galleryUtility.rightImage.image = image;
        $.galleryUtility.rightImage.image.css({
            'top': $.galleryUtility.rightImage.top,
        });
        $.galleryUtility.rightImage.image.css('left', $.galleryUtility.rightImage.left($.galleryUtility.centerImage.image));
    };

    $.galleryUtility.setLeft = function(image) {
        $.galleryUtility.leftImage.image = image;
        $.galleryUtility.leftImage.image.css({
            'top': $.galleryUtility.leftImage.top,
        });
        $.galleryUtility.leftImage.image.css('left', $.galleryUtility.leftImage.left($.galleryUtility.leftImage.image, $.galleryUtility.centerImage.image));
    };

    $.galleryUtility.definePositions = function() {
        var container = $.galleryUtility.Options.container;
        if (container[0].tagName == 'BODY') {
            container = $(window);
        }
        var Gheight = container.height();
        var Gwidth = container.width();

        $.galleryUtility.centerImage.height = $.galleryUtility.centerImage.clientHeight;
        $.galleryUtility.centerImage.width = $.galleryUtility.centerImage.clientWidth;
        $.galleryUtility.centerImage.top = Math.round(Gheight / 2) - ($.galleryUtility.centerImage.height / 2);
        $.galleryUtility.centerImage.left = Math.round(Gwidth / 2) - ($.galleryUtility.centerImage.width / 2);

        $.galleryUtility.leftImage.height = $.galleryUtility.leftImage.clientHeight;
        $.galleryUtility.leftImage.width = $.galleryUtility.leftImage.clientWidth;
        $.galleryUtility.leftImage.top = Math.round(Gheight / 2) - ($.galleryUtility.leftImage.height / 2);
        $.galleryUtility.leftImage.left = function(left, center) {
            return Math.round($.galleryUtility.centerImage.left - ($.galleryUtility.leftImage.width + $.galleryUtility.Options.gutterWidth));
        };

        $.galleryUtility.rightImage.height = $.galleryUtility.centerImage.clientHeight;
        $.galleryUtility.rightImage.width = $.galleryUtility.centerImage.clientWidth;
        $.galleryUtility.rightImage.top = Math.round(Gheight / 2) - ($.galleryUtility.rightImage.height / 2);
        $.galleryUtility.rightImage.left = function(center) {
            return Math.round($.galleryUtility.centerImage.left + ($.galleryUtility.centerImage.width + $.galleryUtility.Options.gutterWidth));
        };

        $.galleryUtility.leftImageStorage.height = $.galleryUtility.leftImageStorage.clientHeight;
        $.galleryUtility.leftImageStorage.width = $.galleryUtility.leftImageStorage.clientWidth;
        $.galleryUtility.leftImageStorage.top = Math.round(Gheight / 2) - ($.galleryUtility.leftImageStorage.height / 2);
        $.galleryUtility.leftImageStorage.left = function(leftStorage, left, center) {
            return Math.round($.galleryUtility.leftImage.left(left, center) - ($.galleryUtility.leftImageStorage.width + $.galleryUtility.Options.gutterWidth));
        };

        $.galleryUtility.rightImageStorage.height = $.galleryUtility.rightImageStorage.clientHeight;
        $.galleryUtility.rightImageStorage.width = $.galleryUtility.rightImageStorage.clientWidth;
        $.galleryUtility.rightImageStorage.top = Math.round(Gheight / 2) - ($.galleryUtility.rightImageStorage.height / 2);
        $.galleryUtility.rightImageStorage.left = function(right) {
            return Math.round($.galleryUtility.rightImage.left(right) + ($.galleryUtility.rightImage.width + $.galleryUtility.Options.gutterWidth));

        // $.galleryUtility.centerImage.Lheight = $.galleryUtility.Options.Lheight;
        // $.galleryUtility.centerImage.Lwidth = $.galleryUtility.Options.Lwidth;
        // $.galleryUtility.centerImage.Ltop = Math.round(Gheight / 2) - ($.galleryUtility.centerImage.Lheight / 2);
        // $.galleryUtility.centerImage.Lleft = Math.round(Gwidth / 2) - ($.galleryUtility.centerImage.Lwidth / 2);

        // $.galleryUtility.leftImage.Lheight = $.galleryUtility.centerImage.Lheight;
        // $.galleryUtility.leftImage.Lwidth = $.galleryUtility.centerImage.Lwidth;
        // $.galleryUtility.leftImage.Ltop = Math.round($.galleryUtility.centerImage.Ltop + (($.galleryUtility.centerImage.Lheight - $.galleryUtility.leftImage.Lheight) / 2));
        // $.galleryUtility.leftImage.left = function(left, center) {
            // return Math.round($.galleryUtility.centerImage.Lleft - ($.galleryUtility.leftImage.Lwidth + $.galleryUtility.Options.gutterWidth));
        // };

        // $.galleryUtility.rightImage.Lheight = $.galleryUtility.centerImage.Lheight;
        // $.galleryUtility.rightImage.Lwidth = $.galleryUtility.centerImage.Lwidth;
        // $.galleryUtility.rightImage.Ltop = Math.round($.galleryUtility.centerImage.Ltop + (($.galleryUtility.centerImage.Lheight - $.galleryUtility.rightImage.Lheight) / 2));
        // $.galleryUtility.rightImage.left = function(center) {
            // return Math.round($.galleryUtility.centerImage.Lleft + ($.galleryUtility.centerImage.Lwidth + $.galleryUtility.Options.gutterWidth));
        // };

        // $.galleryUtility.leftImageStorage.Lheight = $.galleryUtility.leftImage.Lheight;
        // $.galleryUtility.leftImageStorage.Lwidth = $.galleryUtility.leftImage.Lwidth;
        // $.galleryUtility.leftImageStorage.Ltop = Math.round($.galleryUtility.leftImage.Ltop + (($.galleryUtility.leftImage.Lheight - $.galleryUtility.leftImageStorage.Lheight) / 2));
        // $.galleryUtility.leftImageStorage.left = function(leftStorage, left, center) {
            // return Math.round($.galleryUtility.leftImage.left(left, center) - ($.galleryUtility.leftImageStorage.Lwidth + $.galleryUtility.Options.gutterWidth));
        // };

        // $.galleryUtility.rightImageStorage.Lheight = $.galleryUtility.rightImage.Lheight;
        // $.galleryUtility.rightImageStorage.Lwidth = $.galleryUtility.rightImage.Lwidth;
        // $.galleryUtility.rightImageStorage.Ltop = Math.round($.galleryUtility.rightImage.Ltop + (($.galleryUtility.rightImage.Lheight - $.galleryUtility.rightImageStorage.Lheight) / 2));
        // $.galleryUtility.rightImageStorage.left = function(right) {
            // return Math.round($.galleryUtility.rightImage.left(right) + ($.galleryUtility.rightImage.Lwidth + $.galleryUtility.Options.gutterWidth));    
        };
    };
})(jQuery);