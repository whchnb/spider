import re
import datetime
import calendar
import requests
import tkinter as tk  # 使用Tkinter前需要先导入
import prettytable as pt


class WorkTime(object):
    def __init__(self):
        self.now = datetime.datetime.now()
        self.year = self.now.year
        self.month = self.now.month
        self.day = self.now.day
        self.today = self.now.date()
        self.headers = {'cookie': 'ASP.NET_SessionId=uxrpomdsz1hcszz22zqgvuat'}
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
        todayMinute = int(minutes[0])
        return sumMinute, todayMinute

    def get(self):
        # totalMinute = 17550
        totalMinute = 18000
        regulationMinute = 13500
        salary = 6000
        totalDays = calendar.monthrange(self.year, self.month)[1]
        sumMinute, todayMinute = self.getTodayMinute()
        remainingMinute = totalMinute - sumMinute
        remainingDay = totalDays - self.day
        todayAimsMinute = (totalMinute - sumMinute + todayMinute) / (remainingDay + 1)
        todayRemainingMinute = todayAimsMinute - todayMinute
        everydayMinute = (remainingMinute - todayRemainingMinute) / remainingDay
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
        print(tb.get_string())
        # 第1步，实例化object，建立窗口window
        window = tk.Tk()
        # 第2步，给窗口的可视化起名字
        window.title('My Window')
        # 第3步，设定窗口的大小(长 * 宽)
        window.geometry('1040x800')  # 这里的乘是小x
        # 第4步，在图形界面上设定标签
        l = tk.Label(window, text=tb.get_string(), bg='green')
        # 说明： bg为背景，font为字体，width为长，height为高，这里的长和高是字符的长和高，比如height=2,就是标签有2个字符这么高
        # 第5步，放置标签
        l.pack()  # Label内容content区域放置位置，自动调节尺寸
        # 放置lable的方法有：1）l.pack(); 2)l.place();

        # 第6步，主窗口循环显示
        window.mainloop()

    def main(self):
        # self.login()
        self.get()




def main():
    workTime = WorkTime()
    workTime.main()


if __name__ == '__main__':
    main()