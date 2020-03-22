import bottle
from beaker.middleware import SessionMiddleware
from bottle.ext import sqlalchemy

import models
models.Base.metadata.create_all(models.engine)

#create the app instance
app = bottle.app()

#set up the sqlalchemy plugin to handle db sessions
plugin = sqlalchemy.Plugin(
    models.engine, # SQLAlchemy engine created with create_engine function.
    models.Base.metadata, # SQLAlchemy metadata, required only if create=True.
    keyword='db', # Keyword used to inject session database in a route (default 'db').
    create=True, # If it is true, execute `metadata.create_all(engine)` when plugin is applied (default False).
    commit=True, # If it is true, plugin commit changes after route is executed (default True).
    use_kwargs=False, # If it is true and keyword is not defined, plugin uses **kwargs argument to inject session database (default False).
    create_session=models.Session,
)
app.install(plugin)

#set up beaker for session handling
session_opts = {
    'session.cookie_expires': False,
    'session.auto': True,
}
app = SessionMiddleware(app, session_opts)

@bottle.route('/')
def home(db):
    return("Hello covidPlots")




if __name__ == "__main__":
    bottle.run(host='localhost', port=8080, app=app, reloader=True)
