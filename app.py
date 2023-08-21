from flask import Flask, render_template, request, flash
from flask import request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, date, timedelta
import hashlib

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///rsv.db'
db = SQLAlchemy(app)

class mrrsv(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(10), nullable = False)
    rsv_date = db.Column(db.DateTime, nullable = False)
    date_start = db.Column(db.DateTime, nullable = False)
    date_end = db.Column(db.DateTime, nullable = False)
    detail = db.Column(db.String(50), nullable = True)
    pw = db.Column(db.String(), nullable = False)
    apply_date = db.Column(db.DateTime, nullable = False)


@app.route('/', methods = ['GET', 'POST'])
def index():
    error_message = ''
    today = datetime.now()
    if request.method == 'GET':
        posts = mrrsv.query.order_by(mrrsv.rsv_date).all()
        # posts = mrrsv.query.all()
        
        for post in posts:
            if post.rsv_date < today - timedelta(1):
                # print(today, post.rsv_date)
                db.session.delete(post)
                db.session.commit()

        return render_template('index.html', posts = posts, error_message = error_message)
    else: #request.method == 'POST'
        name = request.form.get('name')
        rsv_date = request.form.get('rsv_date')
        rsv_date = datetime.strptime(rsv_date, '%Y-%m-%d')
        date_start = request.form.get('date_start')
        date_end = request.form.get('date_end')
        detail = request.form.get('detail')
        pw = request.form.get('pw')
        pw_sha = hashlib.sha256(pw.encode()).hexdigest()
        apply_date = datetime.now()
        
        if today  - timedelta(1) >= rsv_date:
            error_message = 'Error'
            posts = mrrsv.query.order_by(mrrsv.rsv_date).all()
            return render_template('index.html', error_message = error_message, posts = posts)
        date_start = datetime.strptime(date_start, '%H:%M')
        date_end = datetime.strptime(date_end, '%H:%M')

        new_post = mrrsv(name = name, rsv_date = rsv_date, date_start = date_start, date_end = date_end, detail = detail, pw = pw_sha, apply_date = apply_date)
        
        db.session.add(new_post)
        db.session.commit()
        return redirect('/')

@app.route('/detail/<int:id>', methods = ['GET'])
def read(id):
    post = mrrsv.query.get(id)
    return render_template('detail.html' , post = post)

@app.route('/cancel/<int:id>', methods = ['POST', 'GET'])
def delete(id):
    if request.method == 'GET':
        post = mrrsv.query.get(id)
        return render_template('cancel.html', post = post)
        # pass
    else: # request.method == 'POST'
        # TODO: failed message 
        post = mrrsv.query.get(id)
        pw = request.form.get('pw')
        pw_sha = hashlib.sha256(pw.encode()).hexdigest()
        pw_db = post.pw
        if pw_sha == pw_db:
            db.session.delete(post)
            db.session.commit()
            return redirect('/')
        else:
            # flash('Wrong password')
            post = mrrsv.query.get(id)
            return render_template('cancel.html', post = post)

if __name__ == '__main__':
    app.run(debug=True)