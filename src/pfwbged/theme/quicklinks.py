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

    def get_home_url(self):
        current = plone.api.user.get_current()
        members_folder = getattr(plone.api.portal.get(), 'Members')
        if hasattr(members_folder, current.id):
            return getattr(members_folder, current.id).absolute_url()
        return None

    def get_global_collections(self):
        members_folder = getattr(plone.api.portal.get(), 'Members')
        results = list(members_folder.getFolderContents(
            contentFilter={'portal_type': 'pfwbgedcollection',
                'sort_on': 'sortable_title'}))
        return results

    def get_user_collections(self):
        members_folder = getattr(plone.api.portal.get(), 'Members')
        current = plone.api.user.get_current()
        if not hasattr(members_folder, current.id):
            return None
        current_member_folder = getattr(members_folder, current.id)
        results = list(current_member_folder.getFolderContents(
            contentFilter={'portal_type': 'pfwbgedcollection',
                'sort_on': 'sortable_title'}))
        return results
