# encoding: utf-8

import re
import datetime
import calendar
import requests
import prettytable as pt


class WorkTime(object):
    def __init__(self):
        self.now = datetime.datetime.now()
        self.year = self.now.year
        self.month = self.now.month
        self.day = self.now.day
        self.today = self.now.date()
        self.headers = {'cookie': 'ASP.NET_SessionId=xrmsb5afak3wlraq0fsmrnqj'}
        # self.login()

    def login(self):
        url = 'http://192.168.1.160:90/Admin/Home/Login_on'
        data = {
            'loginIP': '61.134.235.210',
            'username': '李文浩',
            'passwordhash': 'jakcom0506',
        }
        response = requests.post(url, data=data)
        coookie = re.findall(re.compile(r'ASP\.NET_SessionId=(.*?);', re.S), str(response.headers))[0]
        print(coookie)
        self.headers = {'cookie': 'ASP.NET_SessionId=' + coookie}
        print(self.headers)

    def getTodayMinute(self):
        url = 'http://192.168.1.160:90/Admin/Home/Container'
        response = requests.get(url, headers=self.headers)
        reStr = r'<td>{}-\d*?</td>\s*<td>(\d*?)</td>'.format('-'.join(str(self.today).split('-')[:-1]))
        minutes = re.findall(re.compile(reStr, re.S), response.text)
        sumMinute = sum([int(i) for i in minutes])
        try:
            todayMinute = int(minutes[0])
        except Exception as e:
            todayMinute = 0
        return sumMinute, todayMinute

    def get(self):
        # totalMinute = 17550
        totalMinute = 20000
        regulationMinute = 13500
        salary = 6000
        totalDays = calendar.monthrange(self.year, self.month)[1] - 5
        sumMinute, todayMinute = self.getTodayMinute()
        remainingMinute = totalMinute - sumMinute
        remainingDay = totalDays - self.day
        todayAimsMinute = (totalMinute - sumMinute + todayMinute) / (remainingDay + 1)
        todayRemainingMinute = todayAimsMinute - todayMinute
        everydayMinute = (remainingMinute - todayRemainingMinute) / remainingDay if remainingDay is not 0 else round(todayRemainingMinute)
        expectedSalary = salary / regulationMinute * totalMinute
        nowSalary = salary / regulationMinute * sumMinute
        # print('本月目标分钟数', totalMinute)
        # print('今日目标分钟数', round(todayAimsMinute))
        # print('本月分钟数', sumMinute)
        # print('今日分钟数', todayMinute)
        # print('剩余天数', remainingDay)
        # print('剩余分钟数', remainingMinute)
        # print(todayRemainingMinute)
        # print('今日剩余分钟数', round(todayRemainingMinute))
        # print('本月剩余天数每日分钟数', round(everydayMinute))
        remainingTodayHours = todayRemainingMinute // 60
        remainingTodayMinute = todayRemainingMinute % 60
        remainingDate = datetime.datetime.now() + datetime.timedelta(hours=remainingTodayHours, minutes=remainingTodayMinute)
        print(remainingDate.strftime('%Y-%m-%d %H:%M:%S'))
        print(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        startHours = todayMinute // 60
        startMinute = todayMinute % 60
        startDate = datetime.datetime.now() - datetime.timedelta(hours=startHours, minutes=startMinute)
        tb = pt.PrettyTable()
        tb.set_style(pt.DEFAULT)
        tb.field_names = ['今日上班时间', '本月目标分钟数', '剩余天数', '本月分钟数', '本月剩余分钟数', '今日目标分钟数',
                          '今日分钟数', '今日剩余分钟数', '预计今日下班时间', '剩余每日分钟数', '目前薪资', '预计薪资']
        tb.add_row([startDate.strftime('%Y-%m-%d %H:%M:%S') ,totalMinute, remainingDay, sumMinute, remainingMinute,
                    round(todayAimsMinute), todayMinute, round(todayRemainingMinute), remainingDate.strftime('%Y-%m-%d %H:%M:%S'),
                    round(everydayMinute), round(nowSalary), round(expectedSalary)])
        print(tb)

    def main(self):
        # self.login()
        self.get()




def main():
    workTime = WorkTime()
    workTime.main()


if __name__ == '__main__':
    main()