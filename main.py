from flask import Flask, redirect, render_template
from data import db_session
from data.users import User
from forms.user import RegisterForm, LoginForm
from flask_login import LoginManager, login_user, current_user
import requests
import sys
import os

lonlat = []
time = []
numerationpages = -2  # счетчик для прокрутки заявок
with open('all_coordinates.txt') as file:
    lines = [line.rstrip() for line in file]
    for i in lines:
        ali = i.split()
        ll = ali[1] + ' ' + ali[2]
        lonlat.append(ll)
        time.append(ali[3] + ' ' + ali[4].split('.')[0])
ld = len(lines)
app = Flask(__name__,
            static_url_path='',
            static_folder='photos',
            template_folder='templates')
login_manager = LoginManager()
login_manager.init_app(app)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'

path = r'C:\Users\Home\PycharmProjects\trash_search16\photos'
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


def getImage(lonlat):
    lonlat = lonlat.split()
    map_request = f"http://static-maps.yandex.ru/1.x/?ll={lonlat[0]},{lonlat[1]}&spn=0.002,0.002&l=map"
    response = requests.get(map_request)

    if not response:
        print("Ошибка выполнения запроса:")
        print(map_request)
        print("Http статус:", response.status_code, "(", response.reason, ")")
        sys.exit(1)
    map_file = "photos/map.png"
    with open(map_file, "wb") as file:
        file.write(response.content)



def main():
    db_session.global_init("db/blogs.db")
    app.run()


@app.route('/')
def base():
    if not current_user.is_authenticated:
        return redirect('/register')
    global numerationpages
    global ld
    if ld <= 0:
        return render_template('no.html')
    numerationpages += 1
    numerationpages = numerationpages % ld
    getImage(lonlat[numerationpages])
    return render_template('main.html', lonlat=lonlat[numerationpages], address=get_address(lonlat[numerationpages]),
                           photoname=str(listofphotos[numerationpages]), photoname1='map.png', time=time[numerationpages])


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

@app.route('/del')
def delete():
    global numerationpages
    global ld
    path = r'C:\Users\Home\PycharmProjects\trash_search16\photos'
    fn = str(listofphotos[numerationpages])
    ph = path + r'\'' + fn
    ph = ph.replace("'", '')
    os.remove(ph)
    with open('all_coordinates.txt', 'r') as f:
        data = f.readlines()
        print(numerationpages)
        print(data)
        print(ld)
        print(lonlat)
        del data[numerationpages]
        f.close()
    with open('all_coordinates.txt', 'w') as f:
        f.writelines(data)
    ld -= 1
    return redirect('/')



if __name__ == '__main__':
    main()
