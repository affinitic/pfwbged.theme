from zope import schema
from zope.formlib import form
from zope.interface import implements
from plone.app.portlets.portlets import base
from plone.memoize.instance import memoize
from plone.portlets.interfaces import IPortletDataProvider
from DateTime import DateTime
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import base_hasattr

from plone import api

from . import _


class IFolderLinksPortlet(IPortletDataProvider):
    name = schema.TextLine(
            title=_(u"Title"),
            description=_(u"The title of the navigation tree."),
            default=_(u"Shortcuts"),
            required=False)


class Assignment(base.Assignment):
    implements(IFolderLinksPortlet)
    title = _(u'Folder Links')
    name = _(u'Folders')


class Renderer(base.Renderer):
    render = ViewPageTemplateFile('folderlinks.pt')

    def title(self):
        return self.data.name or _(u'Shortcuts')

    @property
    def available(self):
        return True

    def folders(self):
        current_user = api.user.get_current()
        current_user_id = current_user.getId()
        members_folder = getattr(api.portal.get(), 'Members')
        folders = []
        if base_hasattr(members_folder, current_user_id):
            folder = members_folder[current_user_id]
            folders.append({'title': _('Home Folder'), 'url': folder.absolute_url()})

        folder = getattr(api.portal.get(), 'dossiers')
        folders.append({'title': _('All Folders'), 'url': folder.absolute_url()})

        dossiers_folder = getattr(api.portal.get(), 'dossiers')
        for group in api.group.get_groups(user=current_user):
            if base_hasattr(dossiers_folder, group.id):
                folder = dossiers_folder[group.id]
                folders.append({'title': folder.title, 'url': folder.absolute_url()})

        return folders


class AddForm(base.AddForm):
    form_fields = form.Fields(IFolderLinksPortlet)
    label = _(u'Add Folder Links Portlet')
    description = _(u'This portlet display links to main folders')

    def create(self, data):
        return Assignment()


class EditForm(base.EditForm):
    form_fields = form.Fields(IFolderLinksPortlet)
    label = _(u'Edit Folder Links Portlet')
    description = _(u'This portlet display links to main folders')
