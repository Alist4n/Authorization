import datetime
from flask import Flask, flash, redirect, render_template, request, session
#from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import pandas as pd
import numpy

def calculate_days(appointment_date):
    days_difference = (appointment_date - datetime.datetime.now()).days
    return days_difference

data_frame = pd.read_excel("task_resources/receptions.xlsx")
  
data_frame['id'] = data_frame['id'].astype(int)
data_frame['doctor_fio'] = data_frame['doctor_fio'].astype(str)
data_frame['start_time'] = pd.to_datetime(data_frame['start_time'])
data_frame['phone'] = data_frame['phone'].fillna(1)
data_frame['phone'] = data_frame['phone'].astype(int)
data_frame['phone'] = data_frame['phone'].replace(1, '')
data_frame['cancel_time']= data_frame['cancel_time'].astype(str).replace('NaT', '')
data_frame= data_frame.fillna("")
data_frame = data_frame.drop(['card_comment', 'reception_comment'], axis=1)
  
# Создаем новый столбец с расчетами
data_frame['days_until_or_since'] = data_frame['start_time'].apply(calculate_days)

username = 7999
print(username)
# Фильтрация по номеру телефона
filtered_df = data_frame[data_frame['phone'] == username]
print(filtered_df)
clinics = []
results = []

# Проверка, если есть результаты
if not filtered_df.empty:

    # Получаем уникальные клиники
    clinics = filtered_df['clinic'].unique()

    for index, row in filtered_df.iterrows():
        # Форматирование start_time и end_time
        start_time = pd.to_datetime(row['start_time'])
        end_time = pd.to_datetime(row['end_time'])
        formatted_start = start_time.strftime('%d %b (%a) %H:%M')
        formatted_end = end_time.strftime('%H:%M')

        # Форматирование days_until_or_since
        days_info = row['days_until_or_since']
        if days_info > 0:
            days_string = f'через {days_info} дней'
        elif days_info < 0:
            days_string = f'{abs(days_info)} дней назад'
        else:
            days_string = 'Сегодня'

        time = f"{formatted_start} - {formatted_end}"
        doctor_fio = row['doctor_fio']
        days_info = days_string

        results.append({'time': time, 'doctor_fio': doctor_fio, 'days_info': days_string})
    for result in results:
        print(result['time'])
        print(result['doctor_fio'])
print(results)


