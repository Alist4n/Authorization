import datetime
from flask import Flask, flash, redirect, render_template, request, session
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import pandas as pd

def calculate_days(appointment_date):
    days_difference = (appointment_date - datetime.datetime.now()).days
    return days_difference
  
app = Flask(__name__)
app.secret_key = 'your_secret_key'
app.config['SESSION_TYPE'] = 'filesystem'

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

data_frame = pd.read_excel("task_resources/receptions.xlsx")
  
data_frame['id'] = data_frame['id'].astype(int)
data_frame['doctor_fio'] = data_frame['doctor_fio'].astype(str)
data_frame['start_time'] = pd.to_datetime(data_frame['start_time'])
data_frame['phone'] = data_frame['phone'].fillna(1)
data_frame['phone'] = data_frame['phone'].astype(int)
data_frame['phone'] = data_frame['phone'].replace(1, "")
data_frame['cancel_time']= data_frame['cancel_time'].astype(str).replace('NaT', '')
data_frame = data_frame.fillna("")
data_frame = data_frame.drop(['card_comment', 'reception_comment'], axis=1)
data_frame['days_until_or_since'] = data_frame['start_time'].apply(calculate_days)

  
class User(UserMixin):
    def __init__(self, id):
        self.id = id
        
@login_manager.user_loader
def load_user(user_id):
    return User(user_id)

@app.route('/')
def login():
    return render_template('auth.html')

@app.route('/login', methods=['POST'])
def submit():
    username = request.form['username']
    password = request.form['password']
    error = ""

    df = pd.read_excel('task_resources/auth.xlsx')
    df["login"] = df['login'].astype(str)
    accounts = df.set_index('login')['password'].to_dict()

    if username in accounts and str(accounts[username]) == password:
        user = User(username)
        login_user(user)
        session['username'] = username  # Сохраняем имя пользователя в сессии
        with open('task_resources/logs.txt', 'a') as file:
            file.write("login: "+username+" password: " + password + " result: access\n")
        return redirect('/welcome')  # Перенаправление на другую страницу
    else:
        error = "Неверное имя пользователя или пароль."
        with open('task_resources/logs.txt', 'a') as file:
            file.write("login: " + username + " password: " + password + " result: invalid\n")

    return render_template('auth.html', error=error)

@app.route('/welcome')
@login_required
def welcome():
    username = int(session['username'])
    print(username)
    filtered_df = data_frame[data_frame['phone'] == username]
    print(filtered_df)
    clinics = []
    results = []
    flag_next=False
    flag_previous=False
    if not filtered_df.empty:
        clinics = filtered_df['clinic'].unique()

    for index, row in filtered_df.iterrows():
        start_time = pd.to_datetime(row['start_time'])
        end_time = pd.to_datetime(row['end_time'])
        formatted_start = start_time.strftime('%d %b (%a) %H:%M')
        formatted_end = end_time.strftime('%H:%M')
        days_info = row['days_until_or_since']
        if days_info > 0:
            days_string = f'через {days_info} дней'
            flag_next = True
        elif days_info < 0:
            days_string = f'{abs(days_info)} дней назад'
            flag_previous = True
        else:
            days_string = 'Сегодня'
            flag_next = True
        time = f"{formatted_start} - {formatted_end}"
        doctor_fio = row['doctor_fio']
        days_info = days_string
        results.append({'time': time, 'doctor_fio': doctor_fio, 'days_info': days_string})
    return render_template('template.html',
                         username=username,
                         clinics=clinics,
                         results=results,
                         flag_previous=flag_previous,
                         flag_next=flag_next)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/')

if __name__ == "__main__":
  app.run(debug=True)
  
