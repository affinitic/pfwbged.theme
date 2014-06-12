/* JavaScript for the 'ICustomTheme' Plone browser layer */

/*jslint white:false, onevar:true, undef:true, nomen:true, eqeqeq:true, plusplus:true, bitwise:true, regexp:true, newcap:true, immed:true, strict:false, browser:true */
/*global jQuery:false, document:false, window:false, location:false */

(function ($) {

  /* define pfwbged namespace if it doesn't exist */
  if (typeof($.pfwbged) === "undefined") {
      $.pfwbged = { };
  }

  $.pfwbged.prepareLinearNavigation = function () {
    /* prepare for linear navigation from document page to document page */
    var doc_links = $('.ResultsTasksTable tr a, .ResultsTable tr a').map(
                  function(a, b) { return $(b).attr('href'); });
    if (doc_links.length > 0) {
      /* remove duplicated items */
      var doc_links_uniq = Array();
      for (i=0, len=doc_links.length; i < len; ++i) {
        var val = doc_links[i];
        if (doc_links_uniq.indexOf(val) == -1) {
           doc_links_uniq.push(val);
        }
      }
      doc_links = doc_links_uniq;
      /* write the variables to local storage */
      window.localStorage.setItem('table-documents', JSON.stringify($.makeArray(doc_links)));
      window.localStorage.setItem('table-documents-url', window.location.href);
    }
  };

  $.pfwbged.doLinearNavigation = function () {
    var doc_links = JSON.parse(localStorage.getItem('table-documents'));
    var table_url = window.localStorage.getItem('table-documents-url');
    if (typeof(doc_links) != 'object') return;
    var idx = doc_links.indexOf(window.location.href);
    if (idx == -1) return;
    if (idx > 0) {
      /* append a "previous" link */
      var url = doc_links[idx-1];
      $('#content-views').append('<li id="contentview-prev" class="plain">' +
                      '<a href="' + url + '">Précédent</a></li>');
    }
    if (table_url) {
      $('#content-views').append('<li id="contentview-table" class="plain">' +
                      '<a href="' + table_url + '">Tableau</a></li>');
    }
    if (idx < doc_links.length-1) {
      /* append a "next" link */
      var url = doc_links[idx+1];
      $('#content-views').append('<li id="contentview-next" class="plain">' +
                      '<a href="' + url + '">Suivant</a></li>');
    }
  };

}(jQuery));

/* watch version being selected, so menu entries can be shown/hidden */
$('#contentActionMenus .version-action').closest('li').hide();
$('.version-link').closest('tr').on('select-version', function() {
  var version_href = $(this).find('.version-link').attr('href');
  var version_id = version_href.substr(version_href.lastIndexOf('/')+1);
  $('#contentActionMenus .version-action').closest('li').hide();
  $('#contentActionMenus .version-id-' + version_id).closest('li').show();
});

/* highlight home folder icon when the dossiers icon is selected, as that one
 * is hidden (this should probably be done earlier, when producing the HTML). */
if ($('#portaltab-dossiers.selected').length == 1) {
   $('#portaltab-mystuff').addClass('selected');
}

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
  $('.actionicon-object_buttons-create_signed_version span').click(function() {
    if (confirm("Vraiment créer la version signée ?\n(cette action est définitive)") == true) {
      return true; /* this will let the event flow the <a> below */
    }
    return false;
  });
  $('.version-action-finish_without_validation span').click(function() {
    if (confirm("Vraiment valider et finaliser la version ?\n(cette action est définitive)") == true) {
      return true; /* this will let the event flow the <a> below */
    }
    return false;
  });
  var xhr_preview = null;
  $('.ResultsTasksTable tr a, .ResultsTable tr a').hover(function() {
     $('#preview-doc').remove();
     xhr_preview = $.getJSON($(this).attr('href') + '/@@preview',
        function (data) {
           xhr_preview = null;
           $('#preview-doc').remove();
           if (xhr_preview !== null) xhr_preview.abort();
           if (data.thumbnail_url) {
             $('body').append('<div id="preview-doc">');
             $('#preview-doc').append('<img src="' + data.thumbnail_url + '"/>');
           }
     });
  }, function() {
     if (xhr_preview !== null) xhr_preview.abort();
     $('#preview-doc').remove();
  });

  $.pfwbged.prepareLinearNavigation();
  $.pfwbged.doLinearNavigation();

});
