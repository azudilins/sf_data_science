FROM python

WORKDIR /app

COPY ./requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

COPY ./app.py ./
COPY ./events_featured.csv ./
COPY ./index.html ./
COPY ./time_pca ./
COPY ./xgb_model ./

CMD [ "python", "./app.py" ]