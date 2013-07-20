from five import grok
from zope.interface import Interface
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

import plone.api

class QuickLinksView(grok.View):
    grok.context(Interface)
    grok.name('quicklinks')
    grok.require('zope2.View')

    view_template = ViewPageTemplateFile('quicklinks_templates/view.pt')

    def render(self):
        self.request.response.setHeader('Cache-Control', 'no-cache')
        return self.view_template()

    def get_links(self):
        members_folder = getattr(plone.api.portal.get(), 'Members')
        results = list(members_folder.getFolderContents(
                   contentFilter={'portal_type': 'pfwbgedcollection'}))
        current = plone.api.user.get_current()
        if hasattr(members_folder, current.id):
            current_member_folder = getattr(members_folder, current.id)
            results.extend(list(current_member_folder.getFolderContents(
                contentFilter={'portal_type': 'pfwbgedcollection'})))
        return results
