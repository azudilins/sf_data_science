# импортируем библиотеки
import pandas as pd
import joblib
import xgboost as xgb
import warnings
import datetime
warnings.filterwarnings('ignore')

from flask import Flask, request, render_template

# создаём flask приложение
app = Flask(__name__, template_folder='./')

# загружаем данные и модель
events = pd.read_csv('events_featured.csv')
model = joblib.load('xgb_model')
time_pca = joblib.load('time_pca')

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/metric")
def metric():
    return render_template(
        "index.html",
        prediction_text = 'Precision@3 на валидации: 0.2642'
    )

@app.route("/predict", methods = ["POST"])
def predict():
    # запрашиваем идентификатор
    # user = request.args.get('user')
    # user = input('Введите идентификатор пользователя: ')
    user = [x for x in request.form.values()]

    try:
        user = int(user[0])
    except:
        return render_template(
            "index.html",
            prediction_text=f'visitorid должен быть целым числом!'
        )

    if user < 0:
        return render_template(
            "index.html",
            prediction_text=f'visitorid не может быть отрицательным числом!'
        )

    if user > 1407579:
        tmp_df = events.copy()
        # заполняем колонку 'user_feature' значением которое выдаёт user_pca для новых посетителей
        tmp_df['user_feature'] = -1189.36843
    else:
        # убираем из данных продукты с которыми пользователь уже взаимодействовал
        known_items = events[events['visitorid'] == user]['itemid'].unique()
        tmp_df = events[~events['itemid'].isin(known_items)]
        # заполняем колонку 'user_feature' значением нашего посетителя
        tmp_df['user_feature'] = events[events['visitorid'] == user]['user_feature'].unique()[0]

    # заполняем признаки связанные с временем и датой текущими значениями
    now = datetime.datetime.now()
    tmp_df['timestamp'] = pd.to_datetime(now)
    tmp_df['weekday'] = tmp_df['timestamp'].dt.weekday
    tmp_df['month'] = tmp_df['timestamp'].dt.month
    tmp_df['day'] = tmp_df['timestamp'].dt.day
    tmp_df['hour'] = tmp_df['timestamp'].dt.hour
    tmp_df['minute'] = tmp_df['timestamp'].dt.minute

    if (now.hour >= 12) and (now.hour < 16):
        tmp_df['afternoon'] = 1
    else:
        tmp_df['afternoon'] = 0

    if (now.hour >= 16) and (now.hour < 22):
        tmp_df['evening'] = 1
    else:
        tmp_df['evening'] = 0

    if (now.hour >= 22) and (now.hour < 3):
        tmp_df['night'] = 1
    else:
        tmp_df['night'] = 0

    tmp_df['time_feature'] = time_pca.transform(tmp_df[['evening', 'night']])
    tmp_df.drop(['timestamp', 'evening', 'night'], axis = 1, inplace = True)
    tmp_df.drop_duplicates('itemid', inplace = True)

    # делаем предсказание
    d_matrix = xgb.DMatrix(tmp_df[[
        'weekday', 'month', 'day', 'hour', 'minute', 'afternoon', '698', '689',
        '28', '928', '348', 'time_feature', 'property_feature', 'user_feature',
        'item_feature'
    ]])
    tmp_df['pred'] = model.predict(d_matrix)
    top_3 = (
        tmp_df
        .sort_values('pred', ascending = False)
        .head(3)['itemid'].
        values
    )
    return render_template(
        "index.html",
        prediction_text = f'Рекомендации для visitorid {user}: {top_3[0]}, {top_3[1]}, {top_3[2]}'
    )


if __name__ == "__main__":
    app.run('0.0.0.0', 5000)