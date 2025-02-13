# Техническая документация


## Оглавление
- [1. Входные данных для обучения](https://github.com/azudilins/sf_data_science/tree/main/final_project/docker_service/README.md#Входные-данных-для-обучения)
- [2. Трансформации исходного датасета](https://github.com/azudilins/sf_data_science/tree/main/final_project/docker_service/README.md#Трансформации-исходного-датасета)
- [3. Построение валидации](https://github.com/azudilins/sf_data_science/tree/main/final_project/docker_service/README.md#Построение-валидации)
- [4. Проведённые эксперименты](https://github.com/azudilins/sf_data_science/tree/main/final_project/docker_service/README.md#Проведённые-эксперименты)
- [5. Docker образ](https://github.com/azudilins/sf_data_science/tree/main/final_project/docker_service/README.md#Docker-образ)
- [6. API сервиса](https://github.com/azudilins/sf_data_science/tree/main/final_project/docker_service/README.md#API-сервиса)


### Входные данных для обучения
- Формат: XGBoost DMatrix
- Факторы: [
    'weekday', 'month', 'day', 'hour', 'minute', 'afternoon', '698', '689',
    '28', '928', '348', 'time_feature', 'property_feature', 'user_feature',
    'item_feature'
  ]


### Трансформации исходного датасета
- кодирование событий ['view' 'addtocart' 'transaction']
- создание признаков из даты
- удаление дубликатов и неинформативного признак 'transactionid'
- кодирование свойств продуктов (топ-20)
- агрегация статистических данных user-item
- преобразование коррелирующих признаков


### Построение валидации
- сортировка по временной метке
- разделение на train, test и valid без перемешивания
- обучение на train
- подбор параметров модели на test
- рассчёт метрики на valid


### Проведённые эксперименты
- Тип модели: Коллаборативная фильтрация
    - Precision@3: 0.1073
- Тип модели: Факторизационные машины
    - Precision@3: 0.0857
- Тип модели: XGBoost
    - Precision@3: 0.2642
    - Гиперпараметры: {
        'min_child_weight': 20, 'eta': 0.1, 'colsample_bytree': 0.9,
        'max_depth': 6, 'subsample': 0.9, 'lambda': 1, 'nthread': -1,
        'booster' : 'gbtree', 'eval_metric': 'rmse', 'objective': 'reg:squarederror'
      }


### Docker образ
- Команды для запуска:
    - docker pull azudilins/final_project_image
    - docker run -it --rm --name=server_container -p=5000:5000 final_project_image
- Устройство: flask-приложение


### API сервиса
- вводим идентификатор пользователя и получаем рекоммендацию 3 продуктов 
- при нажатии на кнопку Метрика получаем Precision@3 на валидации

:arrow_up: [к оглавлению](https://github.com/azudilins/sf_data_science/tree/main/final_project/docker_service/README.md#Оглавление)