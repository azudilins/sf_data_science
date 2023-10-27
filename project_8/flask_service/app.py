import numpy as np
import pandas as pd
import re
from ast import literal_eval
from flask import Flask, request, render_template
import pickle
from sklearn.base import TransformerMixin, BaseEstimator

class MyTransformer(TransformerMixin, BaseEstimator):
    '''Шаблон кастомного трансформера'''


    def __init__(self):
        '''
        Здесь прописывается инициализация параметров, не зависящих от данных.
        '''
        pass


    def fit(self, data, y=None):
        '''
        Здесь прописывается «обучение» трансформера.
        Вычисляются необходимые для работы трансформера параметры
        (если они нужны).
        '''
        return self


    def transform(self, data):
        '''Здесь прописываются действия с данными.'''

        # распаковываем признак 'homeFacts'
        structure = literal_eval(data['homeFacts'].iloc[0])['atAGlanceFacts']
        for i, fact in enumerate(structure):
            data[fact['factLabel']] = (
                data['homeFacts']
                .apply(
                    lambda x: literal_eval(x)['atAGlanceFacts'][i]['factValue']
                )
                .replace('', np.NaN) # заменяем скрытые пропуски на np.NaN
                .replace('—', np.NaN)
                .replace('No Data', np.NaN)
                .replace('None', np.NaN)
                .replace('No Info', np.NaN)
                .replace('-- sqft lot', np.NaN)
            )
        data = data.drop('homeFacts', axis=1)

        # распаковываем признак 'schools'
        structure = literal_eval(data['schools'].iloc[0])
        data['schools_rating'] = (
            data['schools']
            .apply(lambda x: literal_eval(x)[0]['rating'])
        )
        data['schools_distance'] = (
            data['schools']
            .apply(lambda x: literal_eval(x)[0]['data']['Distance'])
        )
        data['schools_grades'] = (
            data['schools']
            .apply(lambda x: literal_eval(x)[0]['data']['Grades'])
        )
        data['schools_name'] = (
            data['schools'].apply(lambda x: literal_eval(x)[0]['name'])
        )
        data = data.drop('schools', axis=1)

        # создаём колонки-индикаторы из признака 'status'
        data['for_sale'] = (
            data['status']
            .apply(lambda x: 1 if 'forsale' in re.sub(
                '[^a-z]','',str(x).lower()
            ) else 0)
            .astype('int8')
        )

        # создаём колонки-индикаторы из признака 'propertyType'
        property_types = ['single_family', 'condo', 'land', 'townhouse']
        for prop in property_types:
            prop_regex = re.sub('[^a-z]', '', str(prop).lower())
            data[prop] = (
                data['propertyType']
                .apply(lambda x: 1 if prop_regex in re.sub(
                    '[^a-z]', '', str(x).lower()
                ) else 0)
                .astype('int8')
            )

        # создаём колонки-индикаторы из признака 'street'
        str_types = ['St', 'Dr', 'Ln', 'W', 'Ct', 'SW', 'E', 'NW', 'Blvd']
        for str_type in str_types:
            data[str_type.lower()] = data['street'].apply(
                lambda x: 1 if str_type in str(x).split(' ') else 0
            ).astype('int8')

        # преобразуем признак 'baths' к числовому типу
        def get_baths(x):
            x_list = str(x).split(' ')
            if x_list[0] == 'Bathrooms:':
                x = x_list[-1]
            else:
                x = x_list[0]
            try:
                return float(
                    str(x)
                    .split('-')[0]
                    .replace(',', '.')
                    .replace('+', '')
                )
            except:
                return np.NaN
        data['baths'] = (
            data['baths']
            .apply(get_baths)
            .astype('float')
            .fillna(2.5)
            .apply(lambda x: 2.5 if x > 241 else x)
        )

        # обрабатываем признаки годов постройки и реновации
        data['year_built'] = (
            data['Year built']
            .fillna(data['Remodeled year'])
            .fillna(1985)
            .astype('int')
            .apply(lambda x: 1985 if x > 2025 else x)
        )

        # создаём колонку-индикатор было ли здание реконструировано
        data['remodeled'] = (
            data['Remodeled year']
            .apply(lambda x: 0 if (x is np.NaN or x is None) else 1)
            .astype('int8')
        )

        # создаём колонки-индикаторы из признака 'Heating'
        data['forced_air'] = (
            data['Heating']
            .apply(lambda x: 1 if 'forcedair' in re.sub(
                '[^a-z]','',str(x).lower()
            ) else 0)
            .astype('int8')
        )
        data['other_heating'] = (
            data['Heating']
            .apply(lambda x: 0 if (x is np.NaN or x is None) else 1)
            .astype('int8')
        ) - data['forced_air']

        # создаём колонки-индикаторы из признака 'Cooling'
        data['central_cooling'] = (
            data['Cooling']
            .apply(lambda x: 1 if 'central' in re.sub(
                '[^a-z]','',str(x).lower()
            ) else 0)
            .astype('int8')
        )

        # преобразуем признак 'Parking' к числовому типу
        def get_parking(x):
            numbers = re.findall('[0-9]+', str(x))
            if len(numbers) == 0:
                return 1
            if len(numbers) == 1:
                return numbers[0]
            else:
                counter = 0
                for num in numbers:
                    counter += int(num)
                return counter
        data['parking'] = (
            data['Parking']
            .fillna(0)
            .apply(get_parking)
            .astype('int')
        )

        # создаём дополнительные колонки-индикаторы из признака 'Parking'
        data['attached_garage'] = (
            data['Parking']
            .apply(lambda x: 1 if 'attachedgarage' in re.sub(
                '[^a-z]','',str(x).lower()
            ) else 0)
            .astype('int8')
        )
        data['detached_garage'] = (
            data['Parking']
            .apply(lambda x: 1 if 'detachedgarage' in re.sub(
                '[^a-z]','',str(x).lower()
            ) else 0)
            .astype('int8')
        )

        # преобразуем признак 'lotsize' к числовому типу
        def get_lotsize(x):
            x_list = str(x).split(' ')
            if len(x_list) == 1:
                return float(x_list[0].replace(',', '')) / 43560
            if x_list[1].lower()[:4] == 'acre':
                return float(x_list[0].replace(',', ''))
            if x_list[1].lower()[:2] == 'sq':
                return float(x_list[0].replace(',', '')) / 43560
        data['lotsize'] = (
            data['lotsize']
            .fillna(0.19)
            .apply(get_lotsize)
            .abs()
            .apply(lambda x: 0.19 if x > 42689 else x)
        )

        # преобразуем признак 'fireplace' к числовому типу
        def get_fireplace(x):
            x_list = str(x).split()
            try:
                return int(x_list[0])
            except:
                return 1
        data['fireplace'] = (
            data['fireplace']
            .fillna(0)
            .apply(get_fireplace)
            .astype('int')
        )


        # создаём колонки-индикаторы из признака 'city'
        data['houston'] = (
            data['city']
            .apply(lambda x: 1 if 'houston' in re.sub(
                '[^a-z]','',str(x).lower()
            ) else 0)
            .astype('int8')
        )
        data['san_antonio'] = (
            data['city']
            .apply(lambda x: 1 if 'sanantonio' in re.sub(
                '[^a-z]','',str(x).lower()
            ) else 0)
            .astype('int8')
        )

        # создаём колонку среднего рейтинга школ
        def get_avg_schools_rating(x):
            if len(x) == 0:
                return np.NaN
            score_sum = 0
            score_count = 0
            for score in x:
                score = score.split('/')[0]
                if score.isdigit():
                    score_sum += int(score)
                    score_count += 1
            if score_count == 0:
                return np.NaN
            else: return score_sum / score_count
        data['schools_rating'] = (
            data['schools_rating']
            .apply(get_avg_schools_rating)
            .fillna(5)
        )

        # создаём колонку среднего расстояния до школы
        def get_avg_schools_distance(x):
            if len(x) == 0:
                return np.NaN
            distance_sum = 0
            distance_count = 0
            for distance in x:
                distance = distance[:-2] # убераем окончание mi
                distance_sum += float(distance)
                distance_count += 1
            if distance_count == 0:
                return np.NaN
            else: return distance_sum / distance_count
        data['schools_distance'] = (
            data['schools_distance']
            .apply(get_avg_schools_distance)
            .fillna(1.78)
            .apply(lambda x: 1.78 if x > 725.44 else x)
        )

        # создаём колонки-индикаторы из признака 'schools_grades'
        def get_pk_5(x):
            for grade in x:
                if ('P' in str(grade) or 'K' in str(grade)) and '5' in str(grade):
                    return 1
            return 0
        def get_pk_6(x):
            for grade in x:
                if ('P' in str(grade) or 'K' in str(grade)) and '6' in str(grade):
                    return 1
            return 0
        def get_pk_8(x):
            for grade in x:
                if ('P' in str(grade) or 'K' in str(grade)) and '8' in str(grade):
                    return 1
            return 0
        def get_pk_12(x):
            for grade in x:
                if ('P' in str(grade) or 'K' in str(grade)) and '12' in str(grade):
                    return 1
            return 0
        def get_6_8(x):
            for grade in x:
                if '6' in str(grade) and '8' in str(grade):
                    return 1
            return 0
        def get_7_8(x):
            for grade in x:
                if '7' in str(grade) and '8' in str(grade):
                    return 1
            return 0
        def get_9_12(x):
            for grade in x:
                if '9' in str(grade) and '12' in str(grade):
                    return 1
            return 0
        data['pk_5'] = data['schools_grades'].apply(get_pk_5).astype('int8')
        data['pk_6'] = data['schools_grades'].apply(get_pk_6).astype('int8')
        data['pk_8'] = data['schools_grades'].apply(get_pk_8).astype('int8')
        data['pk_12'] = data['schools_grades'].apply(get_pk_12).astype('int8')
        data['6_8'] = data['schools_grades'].apply(get_6_8).astype('int8')
        data['7_8'] = data['schools_grades'].apply(get_7_8).astype('int8')
        data['9_12'] = data['schools_grades'].apply(get_9_12).astype('int8')

        # создаём колонки-индикатры из признака 'schools_name'
        data['abes'] = (
            data['schools_name']
            .apply(lambda x: 1 if 'Air Base Elementary School' in x else 0)
            .astype('int8')
        )
        data['rmvti'] = (
            data['schools_name']
            .apply(lambda x: 1 if 'Robert Morgan Voc-Tech Institute' in x else 0)
            .astype('int8')
        )

        # преобразуем признак 'sqft' к числовому типу
        def get_sqft(x):
            if (x is np.NaN) or (x is None):
                return np.NaN
            x_list = str(x).split(' ')
            if x_list[-1] == 'sqft':
                try:
                    # если встречается диапазон, берём только первую часть
                    return float(x_list[-2].split('-')[0].replace(',', ''))
                except:
                    return np.NaN
            else:
                try:
                    return float(x_list[-1].split('-')[0].replace(',', ''))
                except:
                    return np.NaN
        data['sqft'] = (
            data['sqft']
            .apply(get_sqft)
            .fillna(1800)
            .astype('int')
            .apply(lambda x: 1800 if x < 1 else x)
            .apply(lambda x: 1800 if x > 7078574 else x)
        )


        # создаём колонки-индикаторы из признака 'zipcode'
        data['zipcode'] = data['zipcode'].apply(lambda x: x[0])
        zip_codes = ['3', '7', '9', '4', '8']
        for zip in zip_codes:
            data['zip_'+zip] = (
                data['zipcode']
                .apply(lambda x: 1 if x == zip else 0)
                .astype('int8')
            )

        # преобразуем признак 'beds' к числовому типу
        def get_beds(x):
            x_list = str(x).split(' ')
            false_info = ['acre', 'bath', 'sqft']
            if x_list[-1].lower()[:4] in false_info:
                return np.NaN
            try:
                return float(x_list[0].split('-')[0])
            except:
                return np.NaN
        data['en_suite_bath'] = (
            data['beds']
            .apply(lambda x: 1 if 'bath' in re.sub(
                '[^a-z]','',str(x).lower()
            ) else 0)
            .astype('int8')
        )
        data['beds'] = (
            data['beds']
            .apply(get_beds)
            .fillna(3)
            .astype('int')
            .apply(lambda x: 3 if x < 1 else x)
            .apply(lambda x: 3 if x > 35 else x)
        )

        # создаём колонки-индикаторы из признака 'state'
        states = ['NY', 'CA', 'NC', 'TN', 'WA']
        for state in states:
            data[state.lower()] = (
                data['state']
                .apply(lambda x: 1 if x == state else 0)
                .astype('int8')
            )

        # преобразуем признак 'stories' к числовому типу
        def get_stories(x):
            x = str(x).split(' ')[0].split('/')[-1]
            if 'one' in x.lower():
                return 1
            if 'two' in x.lower():
                return 2
            if 'three' in x.lower():
                return 3
            try:
                return float(x.replace('+', '').replace(',', '').split('-')[0])
            except:
                return 1
        data['stories'] = (
            data['stories']
            .fillna(0)
            .apply(get_stories)
            .apply(lambda x: 1 if x > 96 else x)
        )

        # создаём колонку-индикатор есть ли идентификатор MLS
        data['mls_id'] = (
            data['MlsId']
            .fillna(data['mls-id'])
            .apply(lambda x: 0 if (
                (x is np.NaN) or (x is None) or ('no' in str(x).lower())
            ) else 1)
            .astype('int8')
        )

        # создаём колонку-индикаторы есть ли бассейн'
        data['private_pool'] = (
            data['PrivatePool']
            .fillna(data['private pool'])
            .apply(lambda x: 0 if (x is np.NaN or x is None) else 1)
            .astype('int8')
        )

        # убираем признаки с dtypes "object"
        data.drop([
            'Year built',
            'Remodeled year',
            'Heating',
            'Cooling',
            'Parking',
            'Price/sqft'
        ], axis = 1, inplace = True )
        object_columns = [s for s in data.columns if data[s].dtypes == 'object']
        data.drop(object_columns, axis = 1, inplace = True)

        return data

# Create flask app
app = Flask(__name__)
model = pickle.load(open("my_pipeline.pkl", "rb"))

@app.route("/")
def Home():
    return render_template("index.html")

@app.route("/predict", methods = ["POST"])
def predict():
    data_cols = ['status', 'private pool', 'propertyType', 'street', 'baths',
       'homeFacts', 'fireplace', 'city', 'schools', 'sqft', 'zipcode', 'beds',
       'state', 'stories', 'mls-id', 'PrivatePool', 'MlsId']
    str_features = [x for x in request.form.values()]
    object_data = pd.DataFrame()
    for i, feature in enumerate(str_features):
        if feature is None:
            object_data[data_cols[i]] = ['']
        else:
            object_data[data_cols[i]] = [feature]
    real_estate_value = int(round(np.exp(model.predict(object_data))[0]))
    return render_template(
        "index.html",
        prediction_text = f"The Object Value is: ${real_estate_value :,}"
    )

if __name__ == "__main__":
    app.run('localhost', 5000)