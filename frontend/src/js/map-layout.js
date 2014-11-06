
/* Map Tabs */

(function( $ ) {
  $.fn.mapusaurusTabs = function() {

    var tabList = this.find('> ul');
    var tabPanel = $('#map-aside-header__tabpanels > div');

    // Hide all the inactive tab panels. They are not hidden by CSS for 508 compliance
    tabPanel.hide();
    tabPanel.first().show().addClass('active');

    tabList.find('a').first().addClass('active');
    
    //set the default aria attributes to the tab list
    tabList.attr('role', 'tablist');
    tabList.find('li').attr('role', 'presentation');
    tabList.find('a').attr('role', 'tab').attr('aria-selected', 'false').attr('aria-expanded', 'false').attr('tabindex', '-1');
    tabList.find('a').first().attr('aria-selected', 'true').attr('aria-expanded', 'true').attr('tabindex', '0');

    // add the default aria attributes to the tab panel
    tabPanel.attr('role', 'tabpanel').attr('aria-hidden', 'true').attr('tabindex', '-1');
    tabPanel.first().attr('aria-hidden', 'false').attr('tabindex', '0');

    // create IDs for each anchor for the area-labelledby
    tabList.find('a').each(function() {
      var tabID = $( this ).attr('href').substring(1);
      $(this).attr('id','tablist-' + tabID).attr('aria-controls', tabID);
    });

    tabPanel.each(function() {
      var tabID = 'tablist-' + $( this ).attr('id');
      $(this).attr('aria-labelledby',tabID).addClass('tabpanel');
    });


    // Attach a click handler to all tab anchor elements
    this.find('> ul a').click(function(event) {
      // prevent the anchor link from modifing the url. We don't want the brower scrolling down to the anchor.
      event.preventDefault();
      // The entire tabset, the parent of the clicked tab
      var $thisTabList = $(this).closest('.tabs');
      var $thisTabPanels = $('#map-aside-header__tabpanels');

      var thisTabID = $(this).attr('href');

      // remove all the active classes on the tabs and panels
      $thisTabList.find('.active').removeClass('active');
      $thisTabPanels.find('.active').removeClass('active');
      // hide all the tab panels
      $thisTabPanels.find('.tabpanel').hide().attr('aria-hidden', 'true').attr('tabindex', '-1');
      
      // show the panel
      $(thisTabID).addClass('active').show().attr('aria-hidden', 'false').attr('tabindex', '0');
      //highlight the clicked tab
      $(this).addClass('active').attr('aria-selected', 'true').attr('aria-expanded', 'true').attr('tabindex', '0');
      $(this).focus();
    });

    //set keydown events on tabList item for navigating tabs
    $(tabList).delegate('a', 'keydown',
      function (e) {
        switch (e.which) {
          case 37: case 38:
            if ($(this).parent().prev().length!==0) {
              $(this).parent().prev().find('>a').click();
            } else {
              $(tabList).find('li:last>a').click();
            }
            break;
          case 39: case 40:
            if ($(this).parent().next().length!==0) {
              $(this).parent().next().find('>a').click();
            } else {
              $(tabList).find('li:first>a').click();
            }
            break;
        }
      }
    );


  };

  // auto-init
  $(function(){
    $('.tabs').mapusaurusTabs();
  });

})( jQuery );
