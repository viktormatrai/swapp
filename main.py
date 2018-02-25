import os
import requests
import json

from flask import Flask, render_template, request, session, url_for, redirect, flash, abort
from werkzeug.security import generate_password_hash, check_password_hash

import connect_to_db

app = Flask(__name__)
app.secret_key = b'i\x15\xdc[\x18A\x173!\xce\xad\x804^\xdf\x86\xff\x85\x14\x9f}\xa3\xe6\xc4'


def format_planet_data(planet_data):
    for planet in planet_data.get('results'):
        if planet.get('diameter') != 'unknown':
            planet['diameter'] = '{:,} km'.format(int(planet['diameter']))
        if planet.get('population') != 'unknown':
            planet['population'] = '{:,}'.format(int(planet['population']))
        planet['id'] = planet.get('url').split('/')[-2]


def construct_modal_data(planet, residents):
    data = dict()
    data['modal_title'] = '{}\'{} residents'.format(planet['name'], '' if planet['name'].endswith('s') else 's')
    data['residents'] = residents
    for resident in residents:
        if resident.get('height') != 'unknown':
            resident['height'] = '{} m'.format(int(resident['height']) / 100)
        if resident.get('mass') != 'unknown':
            resident['mass'] = '{} kg'.format(resident['mass'])
    return data


@app.route('/')
def index():
    planet_data = requests.get('http://swapi.co/api/planets').json()
    format_planet_data(planet_data)
    parent_template = app.jinja_env.get_template('index.html')
    return render_template('planets_table.html', parent_template=parent_template, data=planet_data)


@app.route('/get-table')
def get_table():
    planet_data = requests.get(request.args.get('url')).json()
    format_planet_data(planet_data)
    return render_template('planets_table.html', data=planet_data)


@app.route('/get-modal-content')
def get_modal_content():
    planet = requests.get(request.args.get('url')).json()
    residents = list()
    for resident in planet['residents']:
        residents.append(requests.get(resident).json())
    data = construct_modal_data(planet, residents)
    return render_template('residents_modal.html', data=data)


@app.route('/register', methods=['GET', 'POST'])
def register():
    success = False
    if session.get('user') is None:
        if request.method == 'GET':
            return render_template('register.html')
        else:
            try:
                username = request.form.get('username')
                password = generate_password_hash(request.form.get('password'))
                user = connect_to_db.get_user(username)
                if user is None:
                    if not check_password_hash(password, request.form.get('password_verify')):
                        flash('Passwords do not match!')
                    else:
                        connect_to_db.add_user(username, password)
                        session['user'] = username
                        success = True
                else:
                    flash('Username taken!')
            except (connect_to_db.CredentialsMissingError, connect_to_db.DatabaseError):
                abort(500, 'A database error occured!')
    else:
        flash('Already logged in!')
        success = True
    if success:
        return redirect(url_for('index'))
    else:
        return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    success = False
    if session.get('user') is None:
        if request.method == 'GET':
            return render_template('login.html')
        else:
            try:
                user = connect_to_db.get_user(request.form.get('username'))
                if user is None:
                        flash('Wrong username!')
                else:
                    if check_password_hash(user.get('password'), request.form.get('password')):
                        session['user'] = request.form.get('username')
                        success = True
                    else:
                        flash('Wrong password!')
            except (connect_to_db.CredentialsMissingError, connect_to_db.DatabaseError):
                abort(500, 'A database error occured!')
    else:
        flash('Already logged in!')
        success = True
    if success:
        return redirect(url_for('index'))
    else:
        pass


@app.route('/vote-for-planet')
def vote_for_planet():
    try:
        user = connect_to_db.get_user(session.get('user'))
        connect_to_db.add_vote(user.get('id'), request.args.get('pname'))
        result = '''
                    <div class="flashed-message bg-success">
                        <p class="text-success">Successfully voted.</p>
                    </div>
                 '''
    except (connect_to_db.CredentialsMissingError, connect_to_db.DatabaseError):
        result = '''
                    <div class="flashed-message bg-warning">
                        <p class="text-danger">Vote unsuccessful.</p>
                    </div>
                 '''
    return render_template('login.html')
    return result


@app.route('/check-user')
def check_user():
    try:
        user = connect_to_db.get_user(request.args.get('username'))
        return str(user is not None)
    except (connect_to_db.CredentialsMissingError, connect_to_db.DatabaseError):
        return str(False)


@app.route('/get-statistics')
def get_statistics():
    try:
        data = connect_to_db.get_statistics()
        return json.dumps(data)
    except (connect_to_db.CredentialsMissingError, connect_to_db.DatabaseError):
        return '', 500


@app.route('/logout')
def logout():
    if session.get('user') is not None:
        session.pop('user', None)
    return redirect(url_for('index'))