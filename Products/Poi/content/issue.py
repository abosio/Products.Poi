# -*- coding: utf-8 -*-
from zope.interface import implementer
from zope import schema

from plone import api
from plone.app.textfield import RichText
from plone.app.vocabularies.catalog import CatalogSource
from plone.app.z3cform.widget import AjaxSelectFieldWidget
from plone.app.z3cform.widget import RelatedItemsFieldWidget
from plone.autoform.directives import write_permission, read_permission
from plone.autoform.directives import widget
from plone.dexterity.content import Container
from plone.namedfile.field import NamedBlobFile
from plone.schema import email
from plone.supermodel import model
from plone.z3cform.textlines import TextLinesFieldWidget
from z3c.relationfield import RelationList, RelationChoice

from Products.Poi import PoiMessageFactory as _
from .tracker import default_severity
from .tracker import possibleAreas
from .tracker import possibleIssueTypes
from .tracker import possibleSeverities
from .tracker import possibleTargetReleases
from .tracker import possibleAssignees


class IIssue(model.Schema):
    """Marker interface for Poi issue"""

    title = schema.TextLine(
        title=_(u'Poi_label_issue_title', default=u"Title"),
        description=_(u'Poi_help_issue_title',
                      default=u"Enter a short, descriptive title for "
                      u"the issue. A good title will make it easier "
                      u"for project managers to identify and respond "
                      u"to the issue.")
    )

    release = schema.Choice(
        title=_(u'Poi_label_issue_release', default=u'Release'),
        description=_(u'Poi_help_issue_release',
                      default=u"Select the version the issue was found in."),
        required=False,
        source=possibleTargetReleases
    )

    details = RichText(
        title=_(u'Poi_label_issue_details', default=u'Details'),
        description=_(u'Poi_help_issue_details',
                      default=u"Please provide further details")
    )

    steps = RichText(
        title=_(u'Poi_label_issue_steps', default=u'Steps To Reproduce'),
        description=_(u'Poi_help_issue_steps',
                      default=u"If applicable, please provide the steps to "
                      u"reproduce the error or identify the issue, one per "
                      u"line."),
        required=False,
    )

    read_permission(attachment='Poi.UploadAttachment')
    write_permission(attachment='Poi.UploadAttachment')
    attachment = NamedBlobFile(
        title=_(u'Poi_label_issue_attachment', default=u'Attachment'),
        required=False,
        description=_(u'Poi_help_issue_attachment',
                      default=u"You may optionally upload a file attachment. Please "
                      u"do not upload unnecessarily large files.")
    )

    area = schema.Choice(
        title=_(u'Poi_label_issue_area', default=u'Area'),
        description=_(u'Poi_help_issue_area',
                      default=u"Select the area this issue is relevant to."),
        source=possibleAreas
    )

    issue_type = schema.Choice(
        title=_(u'Poi_label_issue_type', default=u'Issue Type'),
        description=_(u'Poi_help_issue_type',
                      default=u"Select the type of issue."),
        source=possibleIssueTypes
    )

    read_permission(severity='Poi.ModifyIssueSeverity')
    write_permission(severity='Poi.ModifyIssueSeverity')
    severity = schema.Choice(
        title=_(u'Poi_label_issue_severity', default=u'Severity'),
        description=_(u'Poi_help_issue_severity',
                      default=u"Select the severity of this issue."),
        defaultFactory=default_severity,
        source=possibleSeverities
    )

    read_permission(target_release='Poi.ModifyIssueTargetRelease')
    write_permission(target_release='Poi.ModifyIssueTargetRelease')
    target_release = schema.Choice(
        title=_(u'Poi_label_issue_target_release', default=u'Target Release'),
        description=_(u'Poi_help_issue_target_release',
                      default=u"Release this issue is targetted to be fixed in"),
        source=possibleTargetReleases,
        required=False,
    )

    read_permission(assignee='Poi.ModifyIssueAssignment')
    write_permission(assignee='Poi.ModifyIssueAssignment')
    assignee = schema.Choice(
        title=_(u'Poi_label_issue_assignee', default=u'Assignee'),
        description=_(u'Poi_help_issue_assignee',
                      default=u"Select which person, if any, is assigned to "
                      u"this issue."),
        source=possibleAssignees,
        required=False,
    )

    contact_email = email.Email(
        title=_(u'Poi_label_issue_contact_email', default=u'Contact Email'),
        description=_(u'Poi_help_issue_contact_email',
                      default=u"Please provide an email address where you can be "
                      u"contacted for further information or when a "
                      u"resolution is available. Note that your email "
                      u"address will not be displayed to others."),
        required=False,
    )

    read_permission(watchers='Poi.ModifyIssueWatchers')
    write_permission(watchers='Poi.ModifyIssueWatchers')
    widget('watchers',
           AjaxSelectFieldWidget,
           vocabulary='plone.app.vocabularies.Users')
    watchers = schema.List(
        title=_(u'Poi_label_issue_watchers', default=u'Watchers'),
        description=_(u'Poi_help_issue_watchers',
                      default=u"Enter the user ids of members who are watching "
                      u"this issue, one per line. E-mail addresses are "
                      u"allowed too. These persons will "
                      u"receive an email when a response is added to the "
                      u"issue. Members can also add themselves as "
                      u"watchers."),
        value_type=schema.TextLine(),
        required=False,
    )

    write_permission(subject='Poi.ModifyIssueTags')
    read_permission(subject='Poi.ModifyIssueTags')
    widget('subject',
           AjaxSelectFieldWidget,
           vocabulary='plone.app.vocabularies.Keywords',
           pattern_options={
              'allowNewItems': 'true'
           })
    subject = schema.Tuple(
        title=_(u'Poi_label_issue_subject', default=u'Subject'),
        description=_(u'Poi_help_issue_subject',
                      default=u"Tags can be used to add arbitrary categorisation to "
                      u"issues. The list below shows existing tags which "
                      u"you can select, or you can add new ones."),
        value_type=schema.TextLine(),
        required=False,
        missing_value=[],
    )

    widget('related_issue',
           RelatedItemsFieldWidget,
           pattern_options={
               'basePath': '.',
               'selectableTypes': ['Issue'],
               'folderTypes': ['Folder']
           })
    related_issue = RelationList(
        title=_(u'Poi_label_issue_related', default=u'Related Issue(s)'),
        description=_(u'Poi_help_issue_related',
                      default=u'Link related issues.'),
        value_type=RelationChoice(
            title=u"Related",
            source=CatalogSource(portal_type=('Issue',),
                                 path='/')
        ),
        required=False
    )


@implementer(IIssue)
class Issue(Container):
    """
    An issue in the Poi Tracker
    """
    _tracker_uid = ''

    def getTracker(self):
        """Return the tracker."""
        return api.content.get(UID=self._tracker_uid)

    def getContactEmail(self):
        return api.user.get(self.Creator()).getProperty('email')

    def getReviewState(self):
        """get the current workflow state of the issue"""
        wftool = api.portal.get_tool('portal_workflow')
        state = wftool.getInfoFor(self, 'review_state')
        title = wftool.getTitleForStateOnType(state, self.portal_type)
        return {
            'state': state,
            'title': title,
        }

    def display_area(self):
        tracker = self.getTracker()
        areas = possibleAreas(tracker)
        return areas.by_value[self.area].title

    def display_issue_type(self):
        tracker = self.getTracker()
        issue_types = possibleIssueTypes(tracker)
        return issue_types.by_value[self.issue_type].title

    def isWatching(self):
        """
        Determine if the current user is watching this issue or not.
        """
        portal_membership = api.portal.get_tool('portal_membership')
        member = portal_membership.getAuthenticatedMember()
        return member.getId() in self.watchers

    def isValid(self):

        """Check if the response is valid.

        Meaning: a response has been filled in.
        """
        errors = schema.getValidationErrors(IIssue, self)
        if errors:
            return False
        else:
            return True


# this is implemented here to reduce the chance of a circular
# import with IIssue
def next_issue_id(tracker):
    """find the next available issue ID (integer) for a Poi tracker"""
    issue_id = 1
    issues = api.content.find(context=tracker, object_provides=IIssue)
    existing_ids = [int(issue.id) for issue in issues if issue.id.isdigit()]
    if len(existing_ids):
        issue_id = max(existing_ids) + 1
    return str(issue_id)
