/*************************************************
 *  Hugo Academic: an academic theme for Hugo.
 *  https://github.com/gcushen/hugo-academic
 **************************************************/

(function($){

  // Measure the closed mobile header, not the expanded navigation menu.
  function anchorOffset() {
    var navbar = $('#navbar-main');
    var height = navbar.outerHeight() || 0;
    if (navbar.find('.navbar-toggle').is(':visible')) {
      height = navbar.find('.navbar-header').outerHeight() || height;
      height += parseFloat(navbar.css('border-top-width')) || 0;
      height += parseFloat(navbar.css('border-bottom-width')) || 0;
    }
    var offset = Math.ceil(height) + 16;
    document.documentElement.style.setProperty('--homepage-anchor-offset', offset + 'px');
    return offset;
  }

  function sectionPosition(hash) {
    return hash === '#top' ? 0 : Math.max(0, $(hash).offset().top - anchorOffset());
  }

  function alignCurrentSection() {
    var hash = window.location.hash;
    // Restrict alignment to this homepage's section anchors.
    if ($('#homepage').length && /^#[a-z][a-z0-9-]*$/i.test(hash) && $(hash).length) {
      $('html, body').stop(true).scrollTop(sectionPosition(hash));
    }
  }

  anchorOffset();
  $(window).on('resize', anchorOffset);
  $(window).on('hashchange', alignCurrentSection);

  /* ---------------------------------------------------------------------------
   * Add smooth scrolling to all links inside the main navbar.
   * --------------------------------------------------------------------------- */

  $('#navbar-main li.nav-item a').on('click', function(event){

    // Store requested URL hash.
    var hash = this.hash;

    // If we are on the homepage and the navigation bar link is to a homepage section.
    if( hash && $(hash).length && ($("#homepage").length > 0)){
      // Prevent default click behavior
      event.preventDefault();

      // Update the URL without triggering a second native jump after animation.
      var nextHash = hash === '#top' ? '' : hash;
      if (window.location.hash !== nextHash) {
        window.history.pushState(null, '', window.location.pathname + window.location.search + nextHash);
      }
      $('html, body').stop(true).animate({
        scrollTop: sectionPosition(hash)
      }, 800);
    }
  });

  /* ---------------------------------------------------------------------------
   * Smooth scrolling for Back To Top link.
   * --------------------------------------------------------------------------- */

  $('#back_to_top').on('click', function(event){
    event.preventDefault();

    window.history.pushState(null, '', window.location.pathname + window.location.search);
    $('html, body').stop(true).animate({
      'scrollTop': 0
    }, 800);
  });

  /* ---------------------------------------------------------------------------
   * Smooth scrolling for mouse wheel.
   * --------------------------------------------------------------------------- */

  function smoothScroll(scrollTime, scrollDistance){

    if (navigator.userAgent.indexOf('Mac') != -1 || navigator.userAgent.indexOf('Firefox') > -1 || jQuery('body').hasClass('is-horizontal')){
      return;
    }

    jQuery(window).on("mousewheel DOMMouseScroll", function(event){

      event.preventDefault();

      var delta = event.originalEvent.wheelDelta/120 || -event.originalEvent.detail/3;
      var scrollTop = jQuery(window).scrollTop();
      var finalScroll = scrollTop - parseInt(delta*scrollDistance);

      TweenMax.to(jQuery(window), scrollTime, {
        scrollTo : { y: finalScroll, autoKill:true },
        ease: Expo.easeOut,
        autoKill: true,
        overwrite: 5
      });

    });

  }

  /* ---------------------------------------------------------------------------
   * Hide mobile collapsable menu on clicking a link.
   * --------------------------------------------------------------------------- */

  $(document).on('click','.navbar-collapse.in',function(e){
    if( $(e.target).is('a') && $(e.target).attr('class') != 'dropdown-toggle' ){
      $(this).collapse('hide');
    }
  });

  /* ---------------------------------------------------------------------------
   * On window load.
   * --------------------------------------------------------------------------- */

  $(window).load(function(){

    // Enable smooth scrolling with mouse wheel
    smoothScroll(1.3, 220);

    // Image/font loading can change section positions after the first native jump.
    anchorOffset();
    alignCurrentSection();

  });

})(jQuery);
