import os
import webapp2
import jinja2
import time
from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
                               autoescape=True)


class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render_form(self, template, **kw):
        self.write(self.render_str(template, **kw))

    def getParam(self, name):
        return self.request.get(name)

class Blog(db.Model):
    subject = db.StringProperty(required = True)
    content = db.TextProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)

################################ HANDLERS ######################################

class BlogHomeHandler(Handler):
    def render_front(self):
        blogposts = db.GqlQuery("SELECT * FROM Blog ORDER BY created DESC")
        posts = dict()
        for post in blogposts:
            posts[post.key().id()] = post
        blogposts = posts
        self.render_form("blog.html", blogposts=blogposts)

    def get(self):
        time.sleep(0.1)
        self.render_front()

    def post(self):
        time.sleep(0.3)
        self.redirect("/blog")


class SinglePostHandler(Handler):
    def render_single(self, postid=""):
        postid = int(postid)
        blogpost = Blog.get_by_id(postid)
        postid = str(postid)
        self.render_form("singlepost.html", postid=postid, blogpost=blogpost)

    def get(self, postid):
        self.render_single(postid=postid)


class NewPostHandler(Handler):
    def render_newpost(self, subject="", content="", error=""):
        self.render_form("newpost.html", subject=subject, content=content,
                         error=error)

    def get(self):
        self.render_newpost()

    def post(self):
        subject = self.request.get("subject")
        content = self.request.get("content")

        if subject and content:
            post = Blog(subject = subject, content = content)
            post.put()
            time.sleep(0.2)
            self.redirect( "/blog/" + str(post.key().id()) )
        else:
            error = "We need both a subject and some content!"
            self.render_newpost(subject, content, error)


# HERE BE DAEMONS
app = webapp2.WSGIApplication([webapp2.Route(r'/blog',
                                             handler=BlogHomeHandler,
                                             name='home'),
                               webapp2.Route(r'/blog/<postid:\d+>',
                                             handler=SinglePostHandler,
                                             name='singlepost'),
                               webapp2.Route(r'/blog/newpost',
                                             handler=NewPostHandler,
                                             name='newpost')],
                               debug=True)
