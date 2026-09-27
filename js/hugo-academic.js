/*************************************************
 *  Hugo Academic: an academic theme for Hugo.
 *  https://github.com/gcushen/hugo-academic
 **************************************************/

(function($){
  var scroller = $(document.scrollingElement || document.documentElement);
  var navigationId = 0;
  var anchoredHash = section(window.location.hash) ? window.location.hash : null;

  function section(hash) {
    if (!/^#[a-z][a-z0-9-]*$/i.test(hash || '')) return null;
    var target = document.getElementById(hash.slice(1));
    return target && $('#homepage').length &&
      (hash === '#top' || $(target).hasClass('home-section')) ? target : null;
  }

  function anchorOffset() {
    var navbar = $('#navbar-main');
    var height = navbar.outerHeight() || 0;
    // An expanded mobile menu must not become part of the permanent offset.
    if (navbar.find('.navbar-toggle').is(':visible')) {
      height = navbar.find('.navbar-header').outerHeight() || height;
      height += parseFloat(navbar.css('border-top-width')) || 0;
      height += parseFloat(navbar.css('border-bottom-width')) || 0;
    }
    var offset = Math.ceil(height) + 24;
    document.documentElement.style.setProperty('--homepage-anchor-offset', offset + 'px');
    return offset;
  }

  function sectionPosition(hash) {
    var target = section(hash);
    if (!target || hash === '#top') return 0;
    return Math.max(0, target.getBoundingClientRect().top + window.pageYOffset - anchorOffset());
  }

  function navigate(hash, animate) {
    if (!section(hash)) return;
    anchoredHash = hash;
    var request = ++navigationId;
    scroller.stop(true);

    function finish() {
      if (request !== navigationId) return;
      // Re-measure after animation: fonts, wrapping, or navbar height may have changed.
      window.scrollTo(0, sectionPosition(hash));
    }

    function start() {
      if (request !== navigationId) return;
      var reduceMotion = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
      if (animate && !reduceMotion) {
        // Animate the browser's actual scrolling element, never both html and body.
        scroller.animate({scrollTop: sectionPosition(hash)}, 350, finish);
      } else {
        finish();
      }
    }

    var menu = $('#navbar-main .navbar-collapse.in, #navbar-main .navbar-collapse.collapsing');
    if (menu.length && $('#navbar-main .navbar-toggle').is(':visible')) {
      menu.one('hidden.bs.collapse', start).collapse('hide');
    } else {
      start();
    }
  }

  function realign() {
    anchorOffset();
    if (anchoredHash) navigate(anchoredHash, false);
  }

  $('#navbar-main li.nav-item a').on('click', function(event){
    if (!section(this.hash)) return;
    event.preventDefault();
    var nextHash = this.hash === '#top' ? '' : this.hash;
    if (window.location.hash !== nextHash) {
      window.history.pushState(null, '', window.location.pathname + window.location.search + nextHash);
    }
    navigate(this.hash, true);
  });

  $('#back_to_top').on('click', function(event){
    event.preventDefault();
    window.history.pushState(null, '', window.location.pathname + window.location.search);
    if (section('#top')) navigate('#top', true);
    else scroller.stop(true).animate({scrollTop: 0}, 350);
  });

  // Leave wheel/touch scrolling to the browser and cancel pending automatic alignment
  // as soon as the reader scrolls manually, including during an animation.
  $(window).on('wheel touchstart pointerdown keydown', function(event){
    if (event.type === 'keydown' && !/^(ArrowUp|ArrowDown|PageUp|PageDown|Home|End| )$/.test(event.key)) return;
    anchoredHash = null;
    navigationId++;
    scroller.stop(true);
  });

  $(window).on('resize load', realign);
  $(window).on('popstate hashchange', function(){
    anchoredHash = section(window.location.hash) ? window.location.hash : null;
    realign();
  });
  if (document.fonts && document.fonts.ready) document.fonts.ready.then(realign);
  anchorOffset();
})(jQuery);
