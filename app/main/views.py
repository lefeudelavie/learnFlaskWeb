"""
view module for app
"""

from datetime import datetime
from flask import render_template, session, redirect, url_for, current_app
from .. import db
from ..models import User
from ..mail import send_mail
from . import main
from .forms import NameForm


@main.route("/", methods=['GET', 'POST'])
def index():
    """main page route for app"""
    form = NameForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.name.data).first()
        if user is None:
            db.session.add(user)
            db.session.commit()
            session['known'] = False
            if current_app.config['FLASKY_ADMIN']:
                send_mail(current_app['FLASKY_ADMIN'], 'New User',
                          'mail/new_user', user=user)
        else:
            session['known'] = True
        session['name'] = form.name.data
        return redirect(url_for('.index'))
    return render_template('index.html',
                           form=form, name=session.get('name'),
                           known=session.get('known', False),
                           current_time=datetime.utcnow())
