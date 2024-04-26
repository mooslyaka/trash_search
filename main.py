from flask import Flask, redirect, render_template
from data import db_session
from data.users import User
from forms.user import RegisterForm, LoginForm
from flask_login import LoginManager, login_user, current_user
import requests
import os

numerationpages = -1  # счетчик для прокрутки заявок
with open('coordinates.txt') as file:
    lines = [line.rstrip() for line in file]

app = Flask(__name__,
            static_url_path='',
            static_folder='photos',
            template_folder='templates')
login_manager = LoginManager()
login_manager.init_app(app)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'

path = r'C:\Users\Home\PycharmProjects\trash_search9\photos'
listofphotos = []
for filename in os.listdir(path):
    if os.path.isfile(os.path.join(path, filename)):
        listofphotos.append(filename)


def get_address(lonlat):
    geocoder_request = f"http://geocode-maps.yandex.ru/1.x/?apikey=40d1649f-0493-4b70-98ba-98533de7710b&geocode={lonlat}&format=json"
    response = requests.get(geocoder_request)
    if response:
        json_response = response.json()
        toponym = json_response["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]
        toponym_address = toponym["metaDataProperty"]["GeocoderMetaData"]["text"]
        return (toponym_address)
    else:
        print("Ошибка выполнения запроса:")
        print(geocoder_request)
        print("Http статус:", response.status_code, "(", response.reason, ")")
        return 'не найден'


def main():
    db_session.global_init("db/blogs.db")
    app.run()


@app.route('/')
def base():
    if not current_user.is_authenticated:
        return redirect('/register')
    global numerationpages
    numerationpages += 1
    numerationpages = numerationpages % len(lines)
    return render_template('main.html', lonlat=lines[numerationpages], address=get_address(lines[numerationpages]),
                           photoname=str(listofphotos[numerationpages]))


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/register', methods=['GET', 'POST'])
def reqister():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть")
        user = User(
            name=form.name.data,
            email=form.email.data,
            about=form.about.data
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=form)


if __name__ == '__main__':
    main()
