"""Игра угадай число.
   Компьютер сам загадывает и сам угадывает число
   за найменьшее число попыток.
"""

import numpy as np

def random_predict(number:int=1) -> int:
    """ Угадываем число за найменьшее число попыток.

    Args:
        number (int, optional): Загаданное число. Defaults to 1.

    Returns:
        int: Число попыток.
    """
    count = 0
    num_min = 1
    num_max = 101
    
    while True:
        count+=1
        predict_number = int((num_min + num_max) / 2) # предполагаемое число
        if number == predict_number:
            break # выход из цикла если угадали
        elif predict_number > number:
            num_max = predict_number # меняем максимально возможное число
        elif predict_number < number:
            num_min = predict_number # меняем минимально возможное число
            
    return(count)


def score_game(random_predict) -> int:
    """За какое количество попыток в среднем за 1000 подходов угадывает наш алгоритм

    Args:
        random_predic ([type]): функция угадывания

    Returns:
        int: среднее количество попыток
    """
    count_ls = []
    random_array = np.random.randint(1, 101, size=(1000)) # загадали список чисел
    
    for number in random_array:
        count_ls.append(random_predict(number))
    
    score = int(np.mean(count_ls))
    print(f'Ваш алгоритм угадывает число в среднем за: {score} попыток')
    return(score)

#RUN
score_game(random_predict)