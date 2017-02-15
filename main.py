#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import webapp2
import jinja2
import os

from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), "templates")
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
                                                            autoescape = True)


class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

class Blog(db.Model):
    title = db.StringProperty(required = True)
    blog = db.TextProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)

class MainBlog(Handler):
    def get(self):
        blogs = db.GqlQuery("SELECT * FROM Blog ORDER BY created DESC LIMIT 5 OFFSET 0")

        self.render("main.html", blogs=blogs)

class NewPost(Handler):
    def get(self):
        self.render("new-post.html")

    def post(self):
        title = self.request.get("title")
        blog = self.request.get("blog")

        if title and blog:
            b = Blog(title = title, blog = blog)
            b.put()
            blog_id = b.key().id()
            self.redirect("/blog/" + str(blog_id))
            #self.render("single-post.html", blog=b)
        else:
            error = "we need both a title and some text!"
            self.render("new-post.html", title=title, blog=blog, error=error)

class ViewPostHandler(Handler):
    def get(self, id):
        blog = Blog.get_by_id(int(id), parent=None)

        if blog:
            self.render("single-post.html", blog=blog)
        else:
            error = "blog post does not exist!"
            self.render("single-post.html", blog=blog, error=error)

app = webapp2.WSGIApplication([
    ('/blog', MainBlog),
    ('/newpost', NewPost),
    webapp2.Route('/blog/<id:\d+>', ViewPostHandler)
], debug=True)
