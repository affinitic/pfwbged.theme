from five import grok
from zope.interface import Interface

from Products.CMFPlone.utils import base_hasattr
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

import plone.api


class QuickLinksView(grok.View):
    grok.context(Interface)
    grok.name('quicklinks')
    grok.require('zope2.View')

    view_template = ViewPageTemplateFile('quicklinks_templates/view.pt')

    def update(self):
        self.member_folder = self._get_member_folder()

    def render(self):
        self.request.response.setHeader('Cache-Control', 'no-cache')
        return self.view_template()

    def _get_member_folder(self):
        current = plone.api.user.get_current()
        # When Anonymous current.id == 'acl_users' and current.getId() is None
        current_id = current.getId()
        if current_id is None:
            return None

        members_folder = getattr(plone.api.portal.get(), 'Members')
        if base_hasattr(members_folder, current_id):
            member_folder = getattr(members_folder, current_id)
            return member_folder

        return None

    def get_home_url(self):
        member_folder = self.member_folder
        if member_folder is not None:
            return member_folder.absolute_url()

        return None

    def get_global_collections(self):
        members_folder = getattr(plone.api.portal.get(), 'Members')
        results = list(members_folder.getFolderContents(
            contentFilter={'portal_type': 'pfwbgedcollection',
                'sort_on': 'sortable_title'}))
        return results

    def get_user_collections(self):
        member_folder = self.member_folder
        if member_folder is None:
            return None

        results = list(member_folder.getFolderContents(
            contentFilter={'portal_type': 'pfwbgedcollection',
                'sort_on': 'sortable_title'}))
        return results
