# Техническая документация


## Оглавление
- [1. Входных данных для обучения](https://github.com/azudilins/sf_data_science/tree/main/final_project/docker_service/README.md#Входных-данных-для-обучения)
- [2. Трансформации исходного датасета](https://github.com/azudilins/sf_data_science/tree/main/final_project/docker_service/README.md#Трансформации-исходного-датасета)
- [3. Краткая информация о данных](https://github.com/azudilins/sf_data_science/tree/main/final_project/docker_service/README.md#Краткая-информация-о-данных)
- [4. Этапы работы над проектом](https://github.com/azudilins/sf_data_science/tree/main/final_project/docker_service/README.md#Этапы-работы-над-проектом)
- [5. Результат](https://github.com/azudilins/sf_data_science/tree/main/final_project/docker_service/README.md#Результат)
- [6. Выводы](https://github.com/azudilins/sf_data_science/tree/main/final_project/docker_service/README.md#Выводы)


### Входных данных для обучения
- Формат: xgb.DMatrix
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


**Проблематика**
- Есть только три места для показа товаров на главной странице.


**Метрика качества**
- Precision@3 (техническая метрика)
- Прибыль (бизнес-метрика)


**Что практикуем**
- Обработка и очистка данных
- Использование инструментов визуализации
- Применение машинного обучения для задачи рекомендации
- Валидация моделей и оценка качества
- Создание flask-приложения
- Контейнеризация сервиса в docker-образ


### Краткая информация о данных
- events: датасет с событиями
- category_tree: файл с деревом категорий
- item_properties: файл со свойствами товаров
- презентация: https://docs.google.com/presentation/d/1uXfSEuQ0tiLStNCexBeXZ51sEG-1KjhTn-pUL5AKSvM/edit?usp=sharing


### Этапы работы над проектом
- Исследование данных
- Очистка данных
- Создание факторов для модели
- Генерация факторов item-user
- Обнаружение и ликвидация неинформативных признаков
- Корреляция и снижение размерности
- Визуализация данных
- Проведение экспериментов
- Создание MVP
- Контейнеризация


### Результат
- Разработаны модели: коллаборативная фильтрация, факторизационные машины, XGBoost.
- Лучшая модель подготовлена для запуска в продакшен.
- Лучший результат Precision@3: 0.2642 - XGBoost


### Выводы
Это лишь один из возможных вариантов работы над проектом, дополнительно можно:
- перебрать больше свойств товаров (использовано только 20 из более чем 1000),
- искать выбросы, подобрать гиперпараметры модели и т.д.

:arrow_up: [к оглавлению](https://github.com/azudilins/sf_data_science/tree/main/final_project/README.md#Оглавление)