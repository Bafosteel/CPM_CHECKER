import time
import json
from tkinter import *
from tkinter.filedialog import askopenfilename
import requests
import openpyxl
import ctypes
from datetime import timedelta
import datetime
import calendar
import logging

logging.basicConfig(filename="cpm_logs/sample.log", level=logging.INFO)


class Gui:
    def __init__(self):
        self.list = []

    def search_folder_for_new_excel_file(self):
        path_to = askopenfilename()

        self.text_1.delete(0, END)
        self.text_1.insert(END, path_to)

    def get_columns_data(self):
        # Get cells from excel file
        token = "AIzaSyDYz0lFD9GCPhm53nPHNGndIvXuqBeZCvg"
        response = requests.get("https://sheets.googleapis.com/v4/spreadsheets/1mg-9BKqsfwCh32zhWLLnDI16AcT4FfwuHPQSHW"
                                "Yn-Gw/values/A1:L20?majorDimension=columns&key=" + str(token))

        # data
        data = [[], [], [], [], [], [], [], [], [], [], [], []]

        for i in range(len(response.json()['values'])):
            for j in range(2, len(response.json()['values'][i])):
                data[i].append(response.json()['values'][i][j])

        return data[0], data[1], data[2], data[3], data[4], data[5], data[6], data[7], data[8], data[9], \
               data[10], data[11]

    def __get_date_time(self, data):
        right_datetime = []
        for elem in data:
            date = datetime.datetime.strptime(str(elem), "%d.%m.%Y %H:%M")
            right_datetime.append(str(datetime.datetime.strftime(date, '%Y-%m-%d')))
        return right_datetime

    def __get_date_list(self, start_time, stop_time):
        date_list = []
        for i in range(len(start_time)):
            d1 = datetime.datetime.strptime(start_time[i], "%d.%m.%Y %H:%M")
            d2 = datetime.datetime.strptime(stop_time[i], "%d.%m.%Y %H:%M")
            date = (d2 - d1).days
            date_list.append(date)
        return date_list

    def __script_one(self, account_id, client_id, ids, ads_ids, min_cpm, plan_cpm, start_campaigns_right_datetime,
                     stop_campaigns_right_datetime, date_list, money_limit, impressions_count,
                     token):

        current_cpm = []

        for i in range(len(account_id)):
            __method = 'https://api.vk.com/method/ads.getAds'
            __params = {
                "account_id": account_id[i],
                "client_id": client_id[i],
                "access_token": token[i],
                "v": '5.92'
            }

            response = requests.post(__method, params=__params)


            for j in range(len(response.json()['response'])):
                if str(response.json()['response'][j]['campaign_id']) == str(ids[i]):
                    print('da')
                    after_dot = str(response.json()['response'][j]['cpm'])
                    index = str(response.json()['response'][j]['cpm']).find(after_dot[-2:])
                    output_line = str(response.json()['response'][j]['cpm'])[:index] + '.' \
                                  + str(response.json()['response'][j]['cpm'])[index:]
                    current_cpm.append(float(output_line))

        for k in range(len(account_id)):

            impressions_count_day = int(impressions_count[k]) / date_list[k]

            __method = "https://api.vk.com/method/ads.getStatistics"

            __params = {
                "account_id": account_id[k],
                "ids_type": "ad",
                "ids": ads_ids[k],
                "period": "day",
                "date_from": start_campaigns_right_datetime[k],
                "date_to": stop_campaigns_right_datetime[k],
                "access_token": token,
                "v": "5.92"
            }

            response = requests.post(__method, params=__params)

            previous_day_today = str(datetime.date.today() - timedelta(days=1))
            # цикл по объявлениям, в нем цикл по статам, и еще где-то цикл по плановым и минимальным сpm-кам
            #  если минимальная ставка равна плановой, то не идет в этот шаг
            if plan_cpm[k] != current_cpm[k]:
                for m in range(len(response.json()['response'])):
                    for n in range(len(response.json()['response'][m]['stats'])):

                        if str(response.json()['response'][m]['stats'][n]['day']) == str(previous_day_today):
                            print('dada')
                            if str(response.json()['response'][m]['stats'][n]['impressions']) < str(impressions_count_day):
                                # нужно так же добавить просмотр по текущий_день-1 + имеет больший смысл, наверное,
                                # смотреть по объявлениям
                                # impressions_count[l] -= response["response"][l]["stats"][0]["impressions"]
                                # -- имеет ли смысл?
                                step = ((plan_cpm[k] - current_cpm[k]) / date_list[k])
                                cpm = current_cpm[k] + step
                                __method = 'https://api.vk.com/method/ads.updateAds'
                                logging.info("for account " + str(account_id[k]) + " and ads " + str(ads_ids[k]) +
                                             " current_cpm was " + str(current_cpm[k]) + "; now cpm is " + str(cpm))
                                __data = [{
                                    "ad_id": ads_ids[k], "cpm": float(cpm)
                                }]

                                __params = {
                                    "account_id": account_id[k],
                                    "data": json.dumps(__data),
                                    "access_token": token,
                                    "v": '5.73'
                                }

                                requests.post(__method, params=__params)
                                print('Done!')

        return ids

    def __script_two(self, account_id, client_id, ids, start_campaigns_unix_time, stop_campaigns_unix_time,
                     money_limit, impressions_count, token):
        '''

        :param account_id:
        :param client_id:
        :param ids:
        :param start_campaigns_unix_time:
        :param stop_campaigns_unix_time:
        :param money_limit:
        :param impressions_count:
        :param token:
        :return:
        '''

        '''

        '''
        pass

    def start(self):

        account_id, client_id, ids, ads_ids, min_cpm, plan_cpm, start_time, stop_time, money_limit, impressions_count, script, \
        token = self.get_columns_data()

        start_campaigns_right_datetime = self.__get_date_time(start_time)
        stop_campaigns_right_datetime = self.__get_date_time(stop_time)

        date_list = self.__get_date_list(start_time, stop_time)
        print(date_list)

        if script[0] == str(1):
            __first_script = self.__script_one(account_id, client_id, ids, ads_ids, min_cpm,plan_cpm, start_campaigns_right_datetime,
                                               stop_campaigns_right_datetime, date_list, money_limit, impressions_count,
                                               token)
            print(__first_script)

        elif script[0] == str(2):
            __second_script = self.__script_two(account_id, client_id, ids, start_campaigns_right_datetime,
                                                stop_campaigns_right_datetime,
                                                money_limit, impressions_count, token)
            print(__second_script)
        else:
            print('Требуемый сценарий отсутствует')

        print('ok')

        return {}


class_gui = Gui()
class_gui.start()
