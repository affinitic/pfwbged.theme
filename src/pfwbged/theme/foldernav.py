# initially copied from plone/app/portlets/portlets/navigation*

import plone.api

from plone.i18n.normalizer.interfaces import IIDNormalizer
from plone.memoize.instance import memoize
from plone.portlets.interfaces import IPortletDataProvider
from plone.app.layout.navigation.defaultpage import isDefaultPage
from plone.app.layout.navigation.interfaces import INavtreeStrategy
from plone.app.layout.navigation.interfaces import INavigationQueryBuilder
from plone.app.layout.navigation.navtree import buildFolderTree
from plone.app.layout.navigation.root import getNavigationRoot
from zope.component import adapts, getMultiAdapter, queryUtility
from zope.formlib import form
from zope.interface import implements, Interface
from zope import schema

from Acquisition import aq_inner, aq_base, aq_parent
from Products.CMFCore.utils import getToolByName
from Products.CMFDynamicViewFTI.interface import IBrowserDefault
from Products.CMFPlone import utils
from Products.CMFPlone.browser.navtree import SitemapNavtreeStrategy
from Products.CMFPlone.interfaces import INonStructuralFolder
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from plone.app.portlets.portlets import base

_ = lambda x:x


class INavigationPortlet(IPortletDataProvider):
    """A portlet which can render the navigation tree
    """

    name = schema.TextLine(
            title=_(u"Title"),
            description=_(u"The title of the navigation tree."),
            default=u"",
            required=False)


class Assignment(base.Assignment):
    implements(INavigationPortlet)

    title = _(u'Navigation')

    name = u""
    root = None
    currentFolderOnly = True
    includeTop = False
    topLevel = 1
    bottomLevel = 0

    def __init__(self, name=u""):
        self.name = name

class Renderer(base.Renderer):

    def __init__(self, context, request, view, manager, data):
        base.Renderer.__init__(self, context, request, view, manager, data)

        self.properties = getToolByName(context, 'portal_properties').navtree_properties
        self.urltool = getToolByName(context, 'portal_url')

    def title(self):
        return self.data.name or self.data.title

    def hasName(self):
        return self.data.name

    @property
    def available(self):
        rootpath = self.getNavRootPath()
        if rootpath is None:
            return False

        tree = self.getNavTree()
        return len(tree['children']) > 0

    def include_top(self):
        return getattr(self.data, 'includeTop', self.properties.includeTop)

    def navigation_root(self):
        return self.getNavRoot()

    def root_type_name(self):
        root = self.getNavRoot()
        return queryUtility(IIDNormalizer).normalize(root.portal_type)

    def root_item_class(self):
        context = aq_inner(self.context)
        root = self.getNavRoot()
        container = aq_parent(context)
        if (aq_base(root) is aq_base(context) or
                (aq_base(root) is aq_base(container) and
                isDefaultPage(container, context))):
            return 'navTreeCurrentItem'
        return ''

    def root_icon(self):
        ploneview = getMultiAdapter((self.context, self.request), name=u'plone')
        icon = ploneview.getIcon(self.getNavRoot())
        return icon.url

    def root_is_portal(self):
        root = self.getNavRoot()
        return aq_base(root) is aq_base(self.urltool.getPortalObject())

    def createNavTree(self):
        data = self.getNavTree()

        bottomLevel = self.data.bottomLevel or self.properties.getProperty('bottomLevel', 0)

        return self.recurse(children=data.get('children', []), level=1, bottomLevel=bottomLevel)

    # Cached lookups

    @memoize
    def getNavRootPath(self):
        currentFolderOnly = self.data.currentFolderOnly or \
                            self.properties.getProperty('currentFolderOnlyInNavtree', False)
        topLevel = self.data.topLevel or self.properties.getProperty('topLevel', 0)
        return getRootPath(self.context, currentFolderOnly, topLevel, self.data.root)

    @memoize
    def getNavRoot(self, _marker=[]):
        portal = self.urltool.getPortalObject()
        rootPath = self.getNavRootPath()
        if rootPath is None:
            return rootPath

        if rootPath == self.urltool.getPortalPath():
            return portal
        else:
            try:
                return portal.unrestrictedTraverse(rootPath)
            except (AttributeError, KeyError):
                return portal

    @memoize
    def getNavTree(self, _marker=[]):
        context = aq_inner(self.context)
        user = plone.api.user.get_current()
        portal = plone.api.portal.get()
        root = '/'.join(portal.getPhysicalPath())

        roots = ['%s/Members/%s' % (root, user.id)]
        for service in ['services/informatique',]:
            # XXX: get real data from user
            roots.append('%s/%s' % (root, service))

        tree = {}
        tree['children'] = []
        for root in roots:
            ctx = portal
            for p in root.split('/')[1:]:
                try:
                    ctx = getattr(ctx, p)
                except KeyError:
                    break
            strategy = getMultiAdapter((ctx, self.data), INavtreeStrategy)
            strategy.rootPath = root
            queryBuilder = getMultiAdapter((ctx, self.data), INavigationQueryBuilder)
            query = queryBuilder()
            query['path']['query'] = root
            result = buildFolderTree(context, obj=ctx, query=query, strategy=strategy)
            tree['children'].append(result)

        return tree

    def update(self):
        pass

    def render(self):
        return self._template()

    _template = ViewPageTemplateFile('foldernav.pt')
    recurse = ViewPageTemplateFile('foldernav_recurse.pt')


class AddForm(base.AddForm):
    form_fields = form.Fields(INavigationPortlet)
    label = _(u"Add Folder Navigation Portlet")
    description = _(u"This portlet display a navigation tree.")

    def create(self, data):
        return Assignment(name=data.get('name', u""))


class EditForm(base.EditForm):
    form_fields = form.Fields(INavigationPortlet)
    label = _(u"Edit Folder Navigation Portlet")
    description = _(u"This portlet display a navigation tree.")


class QueryBuilder(object):
    """Build a navtree query based on the settings in navtree_properties
    and those set on the portlet.
    """
    implements(INavigationQueryBuilder)
    adapts(Interface, INavigationPortlet)

    def __init__(self, context, portlet):
        self.context = context
        self.portlet = portlet

        portal_properties = getToolByName(context, 'portal_properties')
        navtree_properties = getattr(portal_properties, 'navtree_properties')

        portal_url = getToolByName(context, 'portal_url')

        # Acquire a custom nav query if available
        customQuery = getattr(context, 'getCustomNavQuery', None)
        if customQuery is not None and utils.safe_callable(customQuery):
            query = customQuery()
        else:
            query = {}

        # Construct the path query

        rootPath = getNavigationRoot(context, relativeRoot=portlet.root)
        currentPath = '/'.join(context.getPhysicalPath())

        # If we are above the navigation root, a navtree query would return
        # nothing (since we explicitly start from the root always). Hence,
        # use a regular depth-1 query in this case.

        if currentPath!=rootPath and not currentPath.startswith(rootPath + '/'):
            query['path'] = {'query': rootPath, 'depth': 1}
        else:
            query['path'] = {'query': currentPath, 'navtree': 1}

        topLevel = portlet.topLevel or navtree_properties.getProperty('topLevel', 0)
        if topLevel and topLevel > 0:
            query['path']['navtree_start'] = topLevel + 1

        # XXX: It'd make sense to use 'depth' for bottomLevel, but it doesn't
        # seem to work with EPI.

        # Only list the applicable types
        query['portal_type'] = utils.typesToList(context)

        # Apply the desired sort
        sortAttribute = navtree_properties.getProperty('sortAttribute', None)
        if sortAttribute is not None:
            query['sort_on'] = sortAttribute
            sortOrder = navtree_properties.getProperty('sortOrder', None)
            if sortOrder is not None:
                query['sort_order'] = sortOrder

        # Filter on workflow states, if enabled
        if navtree_properties.getProperty('enable_wf_state_filtering', False):
            query['review_state'] = navtree_properties.getProperty('wf_states_to_show', ())

        self.query = query

    def __call__(self):
        return self.query


class NavtreeStrategy(SitemapNavtreeStrategy):
    """The navtree strategy used for the default navigation portlet
    """
    implements(INavtreeStrategy)
    adapts(Interface, INavigationPortlet)

    def __init__(self, context, portlet):
        SitemapNavtreeStrategy.__init__(self, context, portlet)
        portal_properties = getToolByName(context, 'portal_properties')
        navtree_properties = getattr(portal_properties, 'navtree_properties')

        # XXX: We can't do this with a 'depth' query to EPI...
        self.bottomLevel = portlet.bottomLevel or \
                           navtree_properties.getProperty('bottomLevel', 0)

        currentFolderOnly = portlet.currentFolderOnly or \
            navtree_properties.getProperty('currentFolderOnlyInNavtree', False)

        topLevel = portlet.topLevel or navtree_properties.getProperty('topLevel', 0)
        self.rootPath = getRootPath(context, currentFolderOnly, topLevel, portlet.root)

    def subtreeFilter(self, node):
        sitemapDecision = SitemapNavtreeStrategy.subtreeFilter(self, node)
        if sitemapDecision == False:
            return False
        depth = node.get('depth', 0)
        if depth > 0 and self.bottomLevel > 0 and depth >= self.bottomLevel:
            return False
        else:
            return True


def getRootPath(context, currentFolderOnly, topLevel, root):
    """Helper function to calculate the real root path
    """
    context = aq_inner(context)
    if currentFolderOnly:
        folderish = getattr(aq_base(context), 'isPrincipiaFolderish', False) and \
                    not INonStructuralFolder.providedBy(context)
        parent = aq_parent(context)

        is_default_page = False
        browser_default = IBrowserDefault(parent, None)
        if browser_default is not None:
            is_default_page = (browser_default.getDefaultPage() == context.getId())

        if not folderish or is_default_page:
            return '/'.join(parent.getPhysicalPath())
        else:
            return '/'.join(context.getPhysicalPath())

    rootPath = getNavigationRoot(context, relativeRoot=root)

    # Adjust for topLevel
    if topLevel > 0:
        contextPath = '/'.join(context.getPhysicalPath())
        if not contextPath.startswith(rootPath):
            return None
        contextSubPathElements = contextPath[len(rootPath)+1:]
        if contextSubPathElements:
            contextSubPathElements = contextSubPathElements.split('/')
            if len(contextSubPathElements) < topLevel:
                return None
            rootPath = rootPath + '/' + '/'.join(contextSubPathElements[:topLevel])
        else:
            return None

    return rootPath
