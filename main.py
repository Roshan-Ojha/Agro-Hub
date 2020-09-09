import logging
from flask import Flask, render_template, jsonify, request, url_for, redirect, session, flash
from flask_mail import Mail, Message
import random
from functools import wraps
import datetime

import sqlite3

app = Flask(__name__)


app.config['SECRET_KEY'] = 'thisissecret'

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = "your_email"
app.config['MAIL_PASSWORD'] = 'Your_password'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True


mail = Mail(app)

app.jinja_options['extensions'].append('jinja2.ext.loopcontrols')


def login_required(test):
    @wraps(test)
    def wrap(*args, **kwargs):
        if 'login' in session:
            return test(*args, **kwargs)
        else:
            flash('You need to login first')
            return redirect(url_for('main'))
    return wrap


@app.route('/')
def main():
    return render_template('main.html')


@app.route('/signup')
def signup():
    return render_template('signup.html')


@app.route('/verify', methods=['POST', 'GET'])
def verify():
    if request.method == 'POST':
        global user_name, email, password, otp
        a = 1
        otp = ""
        for i in range(6):
            otp = otp + str(random.randint(1, 9))
        user_name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        # msg=Message('Verification',sender='agroflowproject@gmail.com',recipients=[email])
        # msg.body="{} is your AgroHub verification code.".format(otp)
        # mail.send(msg)
        # print(name)

        print("{} is your AgroHub verification code.".format(otp))
        return jsonify({'otp': otp})
    else:
        return redirect(url_for('signup'))


@app.route('/check', methods=['POST', 'GET'])
def check():
    if request.method == 'POST':
        client_otp = request.form.get('otp')
        print("otp={}".format(otp))
        print("client_otp={}".format(client_otp))

        if client_otp == otp:

            conn = sqlite3.connect('signup.db')
            c = conn.cursor()
            c.execute("INSERT INTO signup VALUES (:user_name,:email,:password,:photo)", {
                'user_name': user_name,
                'email': email,
                'password': password,
                'photo': None
            })
            conn.commit()
            conn.close()
            session['login'] = True
            session['name'] = user_name
            session['mail'] = email
            return jsonify({'d': True})
        else:
            return jsonify({'d': False})
    else:
        return redirect(url_for('signup'))


@app.route('/account')
@login_required
def account():

    connect = sqlite3.connect('question_product.db')
    cursor = connect.cursor()
    cursor.execute("SELECT * FROM product WHERE email=:mail UNION ALL SELECT * FROM question WHERE email=:mail ORDER BY date_time DESC ", {
        'mail': session['mail']
    })
    data = cursor.fetchall()
    connect.commit()
    connect.close()

    conn = sqlite3.connect('signup.db')
    c = conn.cursor()
    c.execute("SELECT * FROM signup WHERE email=:mail", {
        'mail': session['mail']
    })
    photo = c.fetchall()
    conn.commit()
    conn.close()

    pro = sqlite3.connect('product.db')
    por = pro.cursor()
    por.execute("SELECT * FROM buy_product")
    buyed_product = por.fetchall()
    pro.commit()
    pro.close()

    connection=sqlite3.connect('answer.db')
    cur=connection.cursor()
    cur.execute("SELECT * FROM answer")
    answers=cur.fetchall()
    connection.commit()
    connection.close()
    return render_template('account.html', user_photo=photo, data=data, product=buyed_product, answers=answers)


@app.route('/logout')
def logout():
    session.pop('mail', None)
    session.pop('login', None)
    session.pop('name', None)
    return redirect(url_for('main'))


@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        user_email = request.form.get('email')
        user_password = request.form.get('password')
        conn = sqlite3.connect('signup.db')
        c = conn.cursor()
        c.execute("SELECT * FROM signup WHERE email=:mail",
                  {
                      'mail': user_email
                  })
        data = c.fetchall()
        conn.commit()
        conn.close()
        if data == []:
            return jsonify({'no_mail': True})
        else:
            if data[0][2] == user_password:
                print('True')
                session['name'] = data[0][0]
                session['mail'] = user_email
                session['login'] = True
                return jsonify({'st': True})
            else:
                return jsonify({'st': False})
    else:
        return redirect(url_for('main'))


@app.route('/savephoto', methods=['POST', 'GET'])
def savephoto():
    if request.method == 'POST':
        print(session['mail'])
        image = request.form.get('photooo')
        conn = sqlite3.connect('signup.db')
        c = conn.cursor()
        c.execute("UPDATE signup SET photo=:image WHERE email=:mail", {
            'image': image,
            'mail': session['mail']
        })
        conn.commit()
        conn.close()
        return jsonify({'a': 'hello'})
    else:
        return redirect(url_for('account'))


@app.route('/question', methods=['GET', 'POST'])
def question():
    if request.method == 'POST':
        title = request.form.get('title')
        ques = request.form.get('question')
        photo = request.form.get('question_photo')

        conn = sqlite3.connect('question_product.db')
        c = conn.cursor()
        c.execute("""INSERT INTO question VALUES (:date_time,:email,:title,:question,:photo,:type,:asked_by)""",
                  {
                      'date_time': datetime.datetime.now(),
                      'email': session['mail'],
                      'title': title,
                      'question': ques,
                      'photo': photo,
                      'type': "question",
                      'asked_by': session['name']
                  })
        conn.commit()
        conn.close()

        return jsonify({'data': "hello"})
    else:
        return jsonify({'data': "hello"})


@app.route('/product', methods=['GET', 'POST'])
def product():
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        photo = request.form.get('product_photo')

        conn = sqlite3.connect('question_product.db')
        c = conn.cursor()

        c.execute("""INSERT INTO product VALUES (:date_time,:email,:title,:description,:photo,:type,:added_by)""",
                  {
                      'date_time': datetime.datetime.now(),
                      'email': session['mail'],
                      'title': title,
                      'description': description,
                      'photo': photo,
                      'type': "product",
                      'added_by': session['name']

                  })

        conn.commit()
        conn.close()

        return jsonify({'data': 'hello'})
    else:
        return redirect(url_for('account'))


@app.route('/delete', methods=['GET', 'POST'])
def delete():
    if request.method == 'POST':
        time = request.form.get('data_time')
        data_type = request.form.get('data_type')
        print(time)
        print(data_type)
        if data_type == "question":
            conn = sqlite3.connect("question_product.db")
            c = conn.cursor()
            c.execute("DELETE FROM question WHERE date_time=:time AND email=:mail", {
                'time': time,
                'mail': session['mail']
            })
            conn.commit()
            conn.close()

            connection=sqlite3.connect('answer.db')
            cur=connection.cursor()
            cur.execute("DELETE FROM answer WHERE asked_on=:asked_on AND answer_by_email=:answer_email",{
                    'asked_on':time,
                    'answer_email':session['mail']
            })
            connection.commit()
            connection.close()
        elif data_type == "product":
            conn = sqlite3.connect("question_product.db")
            c = conn.cursor()
            c.execute("DELETE FROM product WHERE date_time=:time AND email=:mail", {
                'time': time,
                'mail': session['mail']
            })
            conn.commit()
            conn.close()

            connection=sqlite3.connect("product.db")
            cur=connection.cursor()
            cur.execute("DELETE FROM buy_product WHERE added_time=:added_time AND buyer_email=:buyer_email",
                        {
                            'added_time':time,
                            'buyer_email':session['mail']
                        })
            connection.commit()
            connection.close()
        return jsonify({'data': "data"})
    else:
        return redirect(url_for('account'))


@app.route('/queries', methods=['GET', 'POST'])
def queries():
    conn = sqlite3.connect('question_product.db')
    c = conn.cursor()
    c.execute("SELECT * FROM question ORDER BY date_time DESC ")
    data = c.fetchall()
    conn.commit()
    conn.close()

    connection = sqlite3.connect('answer.db')
    cur = connection.cursor()
    cur.execute("SELECT * FROM answer ORDER BY answered_on DESC")
    da = cur.fetchall()
    print(da)
    connection.commit()
    connection.close()
    return render_template('queries.html', questions=data, answers=da)


@app.route('/answer', methods=['GET', 'POST'])
def answer():
    if request.method == 'POST':
        asked_on = request.form.get('asked_on')
        ans = request.form.get('answer')
        photo = request.form.get('photo')
        print(asked_on)
        print(ans)
        print(photo)

        conn = sqlite3.connect('answer.db')
        c = conn.cursor()
        c.execute("""INSERT INTO answer VALUES (:asked_on,:answered_on,:answer,:photo,:answered_by,:answer_by_email)""",
                  {
                      'asked_on': asked_on,
                      'answered_on': datetime.datetime.now(),
                      'answer': ans,
                      'photo': photo,
                      'answered_by': session['name'],
                      'answer_by_email':session['mail']
                  })
        conn.commit()
        conn.close()

        return jsonify({'hello': "hello"})
    else:
        return redirect(url_for('queries'))


@app.route('/products')
def products():
    print("Hello")
    conn = sqlite3.connect('question_product.db')
    c = conn.cursor()
    c.execute("SELECT * FROM product ORDER BY date_time DESC")
    data = c.fetchall()
    conn.commit()
    conn.close()

    connection = sqlite3.connect('product.db')
    cur = connection.cursor()
    cur.execute("SELECT * FROM buy_product")
    status = cur.fetchall()
    connection.commit()
    connection.commit()
    print("hello")

    return render_template('product.html', products=data, status=status)


@app.route('/saveproduct', methods=['GET', 'POST'])
def saveproduct():
    if request.method == 'POST':
        added_time = request.form.get('added_time')
        print(added_time)
        conn = sqlite3.connect('product.db')
        c = conn.cursor()
        c.execute("""INSERT INTO buy_product VALUES (:added_time,:buyed_time,:buyer_email,:buyer_name)""",
                  {
                      'added_time': added_time,
                      'buyed_time': datetime.datetime.now(),
                      'buyer_email': session['mail'],
                      'buyer_name': session['name']
                  })
        conn.commit()
        conn.close()
        return jsonify({'hello': 'hello'})
    else:
        return redirect(url_for('products'))

@app.route('/about_us')
def about_us():
    return render_template('about_us.html')

if __name__ == '__main__':
    app.run(debug=True)
