import os
import urllib

from google.appengine.api import users
from google.appengine.ext import ndb

import jinja2
import webapp2
import time
import logging

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

DEFAULT_PROJECT_NAME = 'default_project'


# We set a parent key on the 'Greetings' to ensure that they are all
# in the same entity group. Queries across the single entity group
# will be consistent. However, the write rate should be limited to
# ~1/second.

def project_key(project_name=DEFAULT_PROJECT_NAME):
    """Constructs a Datastore key for a Project entity.

    We use project_name as the key.
    """
    return ndb.Key('Project', project_name)


class Author(ndb.Model):
    """Sub model for representing an author."""
    identity = ndb.StringProperty(indexed=False)
    email = ndb.StringProperty(indexed=False)


class Greeting(ndb.Model):
    """A main model for representing an individual Guestbook entry."""
    author = ndb.StructuredProperty(Author)
    content = ndb.StringProperty(indexed=False)
    date = ndb.DateTimeProperty(auto_now_add=True)

class Project(ndb.Model):
    """ notes """
    name = ndb.StringProperty(indexed=True)
    description = ndb.StringProperty(indexed=False)

class SubProject(ndb.Model):
    """ notes """
    name = ndb.StringProperty(indexed=False)
    description = ndb.StringProperty(indexed=False)

class TimeEntry(ndb.Model):
    """ notes """
    start_date = ndb.DateTimeProperty(auto_now_add=False)
    end_date = ndb.DateTimeProperty(auto_now_add=False)
    comment = ndb.StringProperty(indexed=False)
    belongs_to = ndb.KeyProperty(kind=SubProject, repeated=True)
    

# class MainPage(webapp2.RequestHandler):

#     def get(self):
#         guestbook_name = self.request.get('guestbook_name',
#                                           DEFAULT_GUESTBOOK_NAME)
#         greetings_query = Greeting.query(
#             ancestor=guestbook_key(guestbook_name)).order(-Greeting.date)
#         greetings = greetings_query.fetch(10)

#         user = users.get_current_user()
#         if user:
#             url = users.create_logout_url(self.request.uri)
#             url_linktext = 'Logout'
#         else:
#             url = users.create_login_url(self.request.uri)
#             url_linktext = 'Login'

#         template_values = {
#             'user': user,
#             'greetings': greetings,
#             'guestbook_name': urllib.quote_plus(guestbook_name),
#             'url': url,
#             'url_linktext': url_linktext,
#         }

#         template = JINJA_ENVIRONMENT.get_template('index.html')
#         self.response.write(template.render(template_values))


class ClockManager(webapp2.RequestHandler):
    def get(self):
        time.sleep(0.1)
        project_query = Project.query()
        projects = project_query.fetch()

        items = list()
        if projects:
            for proj in projects:

                # proj_desc = {
                #     'name': proj.name,
                #     subprojs: [ ]
                # }

                items.append(proj)
                subproject_query = SubProject.query(ancestor=proj.key)
                subprojects = subproject_query.fetch()
                print subprojects
                if subprojects:
                    for subproj in subprojects:
                        items.append(subproj)

        url = users.create_login_url(self.request.uri)
        url_linktext = 'Login'

        template_values = {
            'items': items,
            'url': url,
            'url_linktext': url_linktext,
        }

        template = JINJA_ENVIRONMENT.get_template('clock.html')
        self.response.write(template.render(template_values))

class ProjectManager(webapp2.RequestHandler):

    def get(self):
        time.sleep(0.1)
        project_query = Project.query()
        projects = project_query.fetch()

        ret_list = []
        if projects:
            for proj in projects:

                sub_list = []

                subprojects = SubProject.query(ancestor=proj.key).fetch()
                if subprojects:
                    for subproj in subprojects:
                        sub_list.append(subproj.name)
                ret_list.append({
                    'project': proj.name,
                    'subprojects': sub_list
                })

        url = users.create_login_url(self.request.uri)
        url_linktext = 'Login'
        template_values = {
            'ret_list': ret_list,
            'url': url,
            'url_linktext': url_linktext,
        }

        template = JINJA_ENVIRONMENT.get_template('projectmanager.html')
        self.response.write(template.render(template_values))

    def post(self):
        # We set the same parent key on the 'Greeting' to ensure each
        # Greeting is in the same entity group. Queries across the
        # single entity group will be consistent. However, the write
        # rate to a single entity group should be limited to
        # ~1/second.
        #project_name = self.request.get('project_name',
        #                                  DEFAULT_PROJECT_NAME)

        # guestbook_name = self.request.get('guestbook_name',
        #                                   DEFAULT_GUESTBOOK_NAME)
        # greeting = Greeting(parent=guestbook_key(guestbook_name))

        #if users.get_current_user():
        #    greeting.author = Author(
        #            identity=users.get_current_user().user_id(),
        #            email=users.get_current_user().email())
        if not self.request.get('project'):
            exit("ERROR: No project provided.")
        else:
            if self.request.get('subproject'):
                proj = Project.query(Project.name==self.request.get('project')).fetch(1)
                if proj:
                    subproject = SubProject(parent=proj.pop().key)
                    #logging.debug("proj_key = %s", str(proj_key))
                    subproject.name = self.request.get('subproject')
                    subproject.description = self.request.get('description')
                    subproject.put()
                else:
                    exit("ERROR: No project with that name exists.")
            else: #create new project
                project = Project()
                project.name = self.request.get('project')
                project.description = self.request.get('description')
                project.put()

        # query_params = {'guestbook_name': guestbook_name}
        # self.redirect('/?' + urllib.urlencode(query_params))
        #query_params = {'guestbook_name': guestbook_name}
        self.redirect('/?')

    def get_time_entries(self):
        return TimeEntry.query(TimeEntry.belongs_to==self.key)

class TimeManager(webapp2.RequestHandler):

    def post(self):
        # create a time entry object with dates and comment
        time_entry = TimeEntry(start_date=self.request.get('start_date'), 
            end_date=self.request.get('end_date'))
        if self.request.get('comment'):
            time_entry.comment=self.request.get('comment')
        # get the keys for the subprojects it belongs to and append into belongs_to
        for item in allocations:
            proj = Project.query(Project.name==item.project).fetch(1)
            if proj:
                subproj = SubProject.query(SubProject.name==item.subproject, ancestor=proj.pop().key).fetch(1)
            else:
                exit("ERROR: No project with that name.")
            if subproj:
                time_entry.belongs_to.append(subproj.key)
        # put the new time entry
        time_entry.put()


app = webapp2.WSGIApplication([
    ('/', ProjectManager),
    ('/timer', ClockManager),
    ('/sign', ProjectManager),
    ('/newproject', ProjectManager),
    ('/timeentry', TimeManager),
], debug=True)
