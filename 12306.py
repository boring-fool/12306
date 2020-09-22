import time
import json
import re
import requests
from utils.stations_dict import stations_dict
from utils.parse_seat_type import seat_type_dict
from utils.parse_passenger import parsePassenger
from utils.parse_date import parseDate
from utils.parse_trains_infos import parseTrainsInfos
from selenium import webdriver
from PIL import Image
from io import BytesIO
from selenium.webdriver import ActionChains
from utils.chaojiying import get_result
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

class Funk12306():

# 创建对象
    def __init__(self,username,password):
        self.username = username
        self.password = password
        self.session = requests.session()
        self.session.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36',
            'Accept-Encoding': ', '.join(('gzip', 'deflate')),
            'Accept': '*/*',
            'Connection': 'keep-alive',
            }
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('--headless')  # 无头模式
        chrome_options.add_argument('--disable-gpu')  # 禁用GPU加速
        chrome_options.add_argument('--window-size=1536,864')
        chrome_options.add_experimental_option("excludeSwitches", ['enable-automation'])
        chrome_options.add_experimental_option("useAutomationExtension", False)
        self.browser = webdriver.Chrome(options=chrome_options)
        self.browser.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
            "source": """Object.defineProperty(navigator, 'webdriver', {get: () => undefined})""",
        })
        self.wait = WebDriverWait(self.browser, 20, 0.5)
    def get_cookies(self):

        # 12306的登录网址
        self.browser.get('https://kyfw.12306.cn/otn/resources/login.html')
        # 窗口最大化
        self.browser.maximize_window()
        # 点击账号登录
        self.browser.find_element_by_xpath('/html/body/div[2]/div[2]/ul/li[2]/a').click()
        time.sleep(1)
        #截取验证码图片
        while True:
            try:
                full_img_data = self.browser.get_screenshot_as_png()
                login_image_data = self.wait.until(EC.visibility_of_element_located((By.ID,'J-loginImg')))
                x1 = login_image_data.location['x']
                y1 = login_image_data.location['y']
                x2 = login_image_data.size['width']+x1
                y2 = login_image_data.size['height']+y1
                cut_info = (x1,y1,x2,y2)
                full_img = Image.open(BytesIO(full_img_data))
                cut_img = full_img.crop(cut_info)
                temp = str(time.time()*1000)[:-5]
                cut_img.save('./imgs/{}.png'.format(temp))
                with open('./imgs/{}.png'.format(temp),'rb') as im:
                    answer = get_result(im)
                #验证码登录
                for ans in answer:
                    x = float(ans.split(',')[0])
                    y = float(ans.split(',')[1])
                    ActionChains(self.browser).move_to_element_with_offset(login_image_data,x,y).click().perform()
                put1 = self.browser.find_element_by_id("J-userName")
                put1.clear()
                put1.send_keys('{}'.format(self.username))
                put2 = self.browser.find_element_by_id("J-password")
                put2.clear()
                put2.send_keys(self.password)
                time.sleep(1)
                self.browser.find_element_by_id("J-login").click()
                time.sleep(5)
                self.browser.find_element_by_xpath('//span[@id="nc_1_n1z"]')
                break
            except:
                pass
        time.sleep(2)

            # pyautogui.press('f5')
            # keyboard.press(Key.f5)

        # mouse = Controller()
        #
        # mouse.position = (590,436)
        # mouse.press(Button.left)
        # mouse.move(590+310,436+10)
        # mouse.release(Button.left)
        # time.sleep(3)


        # action = ActionChains(browser)
        # # 点击长按指定的标签
        # action.click_and_hold(span).perform()
        # action.drag_and_drop_by_offset(span, 310, 0).perform()
        while True:
            try:
                span = self.browser.find_element_by_xpath('//span[@id="nc_1_n1z"]')
                action = ActionChains(self.browser)
                # 点击长按指定的标签
                action.click_and_hold(span).perform()
                action.drag_and_drop_by_offset(span, 310, 0).perform()
                info=self.browser.find_element_by_xpath('//div[@class="errloading"]//span').text
                print(info)
                if info=='哎呀，出错了，点击刷新再来一次':#点击刷新
                    self.browser.find_element_by_xpath('//div[@class="errloading"]//a').click()
                    time.sleep(0.2)
                #重新移动滑块
                time.sleep(3)
            except:
                 print('ok!')
                 action.release()
                 break
        time.sleep(10)
        c = self.browser.get_cookies()
        for cookie in c:
            self.session.cookies.set(cookie['name'], cookie['value'])
    def buy_ticket(self):
        from_station = input('输入出发城市或车站:')
        to_station = input('输入到达城市或车站:')
        train_date = input('输入出行日期,格式为2018-12-03:')
        from_station_code = stations_dict.get(from_station, '')
        to_station_code = stations_dict.get(to_station, '')
        # 查询车量具体信息query
        url = 'https://kyfw.12306.cn/otn/leftTicket/query?leftTicketDTO.train_date=2020-10-01&leftTicketDTO.from_station=CDW&leftTicketDTO.to_station=WUJ&purpose_codes=ADULT'
        response = self.session.get(url)
        # 解析获取trains_list
        trains_list = parseTrainsInfos(json.loads(response.content)['data']['result'])
        print('查询的列车信息如下：')
        print(trains_list)
        # 获取选择的列车
        train_info_dict = trains_list[int(input('请输入选中车次的下标：'))]
        print('选中了列车信息为：')
        print(train_info_dict)
        # 列车信息
        secretStr = train_info_dict['secretStr']
        leftTicket = train_info_dict['leftTicket']
        train_location = train_info_dict['train_location']

        # 点击预定
        url = 'https://kyfw.12306.cn/otn/leftTicket/submitOrderRequest'
        data = {
            'secretStr': secretStr,
            'train_date': train_date,
            'back_train_date': train_date,
            'tour_flag': 'dc',  # dc 单程 wf 往返
            'purpose_codes': 'ADULT',  # 成人
            'query_from_station_name': from_station,
            'query_to_station_name': to_station,
            'undefined': ''
        }
        resp = self.session.post(url, data=data)
        # 订单初始化 获取REPEAT_SUBMIT_TOKEN key_check_isChange
        url = 'https://kyfw.12306.cn/otn/confirmPassenger/initDc'
        data = {'_json_att': ''}
        response = self.session.post(url, data=data)
        repeat_submit_token = re.search(r"var globalRepeatSubmitToken = '([a-z0-9]+)';",
                                        response.content.decode()).group(1)
        key_check_isChange = re.search("'key_check_isChange':'([A-Z0-9]+)'", response.content.decode()).group(1)

        # 获取用户信息
        url = 'https://kyfw.12306.cn/otn/confirmPassenger/getPassengerDTOs'
        data = {'_json_att': '',
                'REPEAT_SUBMIT_TOKEN': repeat_submit_token}
        response = self.session.post(url, data=data)

        # 解析并构造乘客信息列表
        passenger_list = parsePassenger(json.loads(response.content))
        print('获取乘客信息有：')
        print(passenger_list)
        passenger_info_dict = passenger_list[int(input('输入要购票的乘车人的下标'))]

        # 坐席类型
        try:
            seat_type = seat_type_dict[input('请输入要购买的坐席类型的拼音，如果输入错误，将强行购买无座，能回家就行了，还要tm什么自行车！：')]
        except:
            seat_type = seat_type_dict['wuzuo']

        # 构造乘客信息
        passengerTicketStr = '%s,0,1,%s,%s,%s,%s,N' % (
            seat_type, passenger_info_dict['passenger_name'],
            passenger_info_dict['passenger_id_type_code'],
            passenger_info_dict['passenger_id_no'],
            passenger_info_dict['passenger_mobile_no'])
        oldPassengerStr = '%s,%s,%s,1_' % (
            passenger_info_dict['passenger_name'],
            passenger_info_dict['passenger_id_type_code'],
            passenger_info_dict['passenger_id_no'])

        # 检查选票人信息
        url = 'https://kyfw.12306.cn/otn/confirmPassenger/checkOrderInfo'
        data = {
            'cancel_flag': '2',  # 未知
            'bed_level_order_num': '000000000000000000000000000000',  # 未知
            'passengerTicketStr': passengerTicketStr.encode('utf-8'),
            'oldPassengerStr': oldPassengerStr.encode('utf-8'),
            'tour_flag': 'dc',  # 单程
            'randCode': '',
            'whatsSelect': '1',
            '_json_att': '',
            'REPEAT_SUBMIT_TOKEN': repeat_submit_token
        }
        resp = self.session.post(url, data=data)
        print(resp.text)

        # 提交订单,并获取排队人数,和车票的真实余数
        url = 'https://kyfw.12306.cn/otn/confirmPassenger/getQueueCount'
        data = {
            'train_date': parseDate(train_date),  # Fri Nov 24 2017 00:00:00 GMT+0800 (中国标准时间)
            'train_no': train_info_dict['train_no'],  # 6c0000G31205
            'stationTrainCode': train_info_dict['stationTrainCode'],  # G312
            'seatType': seat_type,  # 席别
            'fromStationTelecode': train_info_dict['from_station'],  # one_train[6]
            'toStationTelecode': train_info_dict['to_station'],  # ? one_train[7]
            'leftTicket': train_info_dict['leftTicket'],  # one_train[12]
            'purpose_codes': '00',
            'train_location': train_info_dict['train_location'],  # one_train[15]
            '_json_att': '',
            'REPEAT_SUBMIT_TOKEN': repeat_submit_token
        }
        resp = self.session.post(url, data=data)
        print(resp.text)
        print('此时排队买票的人数为：{}'.format(json.loads(resp.text)['data']['count']))
        ticket = json.loads(resp.text)['data']['ticket']
        print('此时该车次的余票数量为：{}'.format(ticket))
        if ticket == '0':
            print('没有余票，购票失败')
            return '没有余票，购票失败'

        # 确认订单,进行扣票 需要 key_check_isChange
        url = 'https://kyfw.12306.cn/otn/confirmPassenger/confirmSingleForQueue'
        data = {
            'passengerTicketStr': passengerTicketStr.encode('utf-8'),
            'oldPassengerStr': oldPassengerStr.encode('utf-8'),
            'randCode': '',
            'purpose_codes': '00',
            'key_check_isChange': key_check_isChange,
            'leftTicketStr': leftTicket,
            'train_location': train_location,  # one_train[15]
            'choose_seats': '',  # 选择坐席 ABCDEF 上中下铺 默认为空不选
            'seatDetailType': '000',
            'whatsSelect': '1',
            'roomType': '00',
            'dwAll': 'N',  # ?
            '_json_att': '',
            'REPEAT_SUBMIT_TOKEN': repeat_submit_token
        }
        resp = self.session.post(url, data=data)
        print(json.loads(resp.text))
        if json.loads(resp.text)['status'] == False or json.loads(resp.text)['data']['submitStatus'] == False:
            print('扣票失败')
            return '扣票失败'

        # 排队等待 返回waittime  获取 requestID 和 orderID
        timestamp = str(int(time.time() * 1000))  # str(time.time() * 1000)[:-4]
        url = 'https://kyfw.12306.cn/otn/confirmPassenger/queryOrderWaitTime?random=%s&tourFlag=dc&_json_att=&REPEAT_SUBMIT_TOKEN=%s' % (
            timestamp, repeat_submit_token)
        resp = self.session.get(url)
        print(resp.text)
        try:
            orderID = json.loads(resp.text)['data']['orderId']
        except:
            # 排队等待 返回waittime  获取 requestID 和 orderID
            timestamp = str(int(time.time() * 1000))  # str(time.time() * 1000)[:-4]
            url = 'https://kyfw.12306.cn/otn/confirmPassenger/queryOrderWaitTime?random=%s&tourFlag=dc&_json_att=&REPEAT_SUBMIT_TOKEN=%s' % (
                timestamp, repeat_submit_token)
            resp = self.browser.get(url)
            print(resp.text)
            try:
                orderID = json.loads(resp.text)['data']['orderId']
            except:
                return '购票失败'

        # 订单结果
        url = 'https://kyfw.12306.cn/otn/confirmPassenger/resultOrderForDcQueue'
        data = {
            'orderSequence_no': orderID,
            '_json_att': '',
            'REPEAT_SUBMIT_TOKEN': repeat_submit_token
        }
        resp = self.session.post(url, data=data)
        print(resp.text)

    def run(self):
        # 登录 获取cookies
        self.get_cookies()
        # 买票
        self.buy_ticket()
if __name__ == '__main__':

    username = input('请输入12306账号：')
    password = input('请输入12306密码：')

    funk = Funk12306(username, password)
    funk.run()
