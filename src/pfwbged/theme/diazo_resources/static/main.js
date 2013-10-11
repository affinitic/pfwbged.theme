/* JavaScript for the 'ICustomTheme' Plone browser layer */

/*jslint white:false, onevar:true, undef:true, nomen:true, eqeqeq:true, plusplus:true, bitwise:true, regexp:true, newcap:true, immed:true, strict:false, browser:true */
/*global jQuery:false, document:false, window:false, location:false */

/* watch version being selected, so menu entries can be shown/hidden */
$('#contentActionMenus .version-action').closest('li').hide();
$('.version-link').closest('tr').on('select-version', function() {
  var version_href = $(this).find('.version-link').attr('href');
  var version_id = version_href.substr(version_href.lastIndexOf('/')+1);
  $('#contentActionMenus .version-action').closest('li').hide();
  $('#contentActionMenus .version-id-' + version_id).closest('li').show();
});

$(function() {
  /* initialize quicklinks/favorites menu */
  $('#portal-down a.open').click(function() {
    if ($('#favorites ul').length == 0) {
      $('#favorites').load('quicklinks');
      $('#favorites').toggle();
      return false;
    } else {
      $('#favorites').toggle();
      return false;
    };
  });
});
