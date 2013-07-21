/* JavaScript for the 'ICustomTheme' Plone browser layer */

/*jslint white:false, onevar:true, undef:true, nomen:true, eqeqeq:true, plusplus:true, bitwise:true, regexp:true, newcap:true, immed:true, strict:false, browser:true */
/*global jQuery:false, document:false, window:false, location:false */

$(function() {
  /* highlight index icon when the member icon is selected, as that one is
   * hidden; this should probably be done earlier, when producing the HTML. */
  if ($('#portaltab-mystuff.selected').length == 1) {
     $('#portaltab-index_html').addClass('selected');
  }
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
