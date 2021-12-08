import time
import wx
import subprocess
import pymysql
import smtplib
import pytest
from email.mime.text import MIMEText
from email.header import Header
from wx.lib.pubsub import pub
from switch_keycode import switch_keycode
from Verify_SN import Verify_SN
from Free_Mac_Fetch import FreeMacFetch
from Setting import Setting
# from Test_item import TestItem
# from ETH_test import ETH_test
# from VGA_test import VGA_test
# from USB_test import USB_test
# from SATA_test import SATA_test
# from CPU_test import CPU_test
# from Memory_test import Memory_test
# from CONSOLE_test import CONSOLE_test
# from PCIE_test import PCIE_test
# from SSD_test import SSD_test
# from SFP_test import SFP_test
# from Search_SN_Maxwell import fetch_MAC
# from Write_MAC import write_Mac
# from Write_FRU import write_FRU


class Frame(wx.Frame):
    def __init__(self, title):
        wx.Frame.__init__(self, None, title=title, pos=(720, 50), size=(1080, 720))
        self.Bind(wx.EVT_CLOSE, self.close_frame)

        # publish listener
        pub.subscribe(self.vga_result, 'vga')
        pub.subscribe(self.write_mac_result, 'mac')
        pub.subscribe(self.write_fru_result, 'fru')
        pub.subscribe(self.eth_result, 'eth')
        pub.subscribe(self.sfp_result, 'eth')
        pub.subscribe(self.cpu_result, 'eth')
        pub.subscribe(self.memory_result, 'memory')
        pub.subscribe(self.console_result, 'console')
        pub.subscribe(self.usb_result, 'usb')
        pub.subscribe(self.pcie_result, 'pcie')
        pub.subscribe(self.sata_result, 'sata')
        pub.subscribe(self.m2_result, 'm2')
        pub.subscribe(self.all_result, 'all')

        self.panel = wx.Panel(self)
        self.vbox = wx.BoxSizer(wx.VERTICAL)
        self.hbox = wx.BoxSizer(wx.HORIZONTAL)

        # Font configuration
        self.font_00 = wx.Font(20, wx.FONTFAMILY_MODERN, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
        self.font_01 = wx.Font(14, wx.FONTFAMILY_MODERN, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)

        # Text for window title
        self.m_text = wx.StaticText(self.panel, -1, "Maxwell Function Test!")
        self.m_text.SetFont(self.font_00)
        self.m_text.SetSize(self.m_text.GetBestSize())
        self.vbox.Add(self.m_text, 0, wx.ALIGN_CENTER | wx.TOP | wx.LEFT | wx.RIGHT | wx.BOTTOM, 20)

        # Test button
        self.test_bt = wx.Button(self.panel, wx.ID_CLOSE, "Start Test", size=(200, 30))
        self.test_bt.SetFont(self.font_01)
        self.test_bt.Bind(wx.EVT_BUTTON, self.start_test)
        self.vbox.Add(self.test_bt, 0, wx.ALIGN_LEFT | wx.ALL, 6)

        # Serial number
        self.m_text_SN = wx.StaticText(self.panel, 1, "Scan SN:")
        self.m_text_SN.SetFont(self.font_01)
        self.m_text_SN.SetSize(self.m_text_SN.GetBestSize())
        self.hbox.Add(self.m_text_SN, 1, flag=wx.ALL, border=6)

        # Serial number Text entry 02CB091800002
        self.m_serial = wx.TextCtrl(self.panel, 1,)
        self.hbox.Add(self.m_serial, 2, flag=wx.ALL, border=6)

        self.T_01_VGA = wx.CheckBox(self.panel, 1, '01-VGA Test')
        self.T_01_VGA.SetValue(True)
        self.T_02_Write_MAC = wx.CheckBox(self.panel, 2, '02-Write_MAC')
        self.T_02_Write_MAC.SetValue(True)
        self.T_03_Write_FRU = wx.CheckBox(self.panel, 3, '03-Write_FRU')
        self.T_03_Write_FRU.SetValue(True)

        self.T_04_ETH = wx.CheckBox(self.panel, 4, '04-ETH_Test')
        self.T_04_ETH.SetValue(True)
        self.T_05_SFP = wx.CheckBox(self.panel, 5, '05-SFP_Test')
        self.T_05_SFP.SetValue(True)
        self.T_06_CPU = wx.CheckBox(self.panel, 6, '06-CPU_Test')
        self.T_06_CPU.SetValue(True)

        self.T_07_Memory = wx.CheckBox(self.panel, 7, '07-Memory_Test')
        self.T_07_Memory.SetValue(True)
        self.T_08_Console = wx.CheckBox(self.panel, 8, '08-Console_Test')
        self.T_08_Console.SetValue(True)
        self.T_09_USB = wx.CheckBox(self.panel, 9, '09-USB_Test')
        self.T_09_USB.SetValue(True)

        self.T_10_PCI_E = wx.CheckBox(self.panel, 10, '10-PCI-E_Test')
        self.T_10_PCI_E.SetValue(True)
        self.T_11_SATA = wx.CheckBox(self.panel, 11, '11-SATA_Test')
        self.T_11_SATA.SetValue(True)
        self.T_12_M_2 = wx.CheckBox(self.panel, 12, '12-M.2_Test')
        self.T_12_M_2.SetValue(True)

        # self.Bind(wx.EVT_CHECKBOX, self.on_checkbox_click, id=1, id2=3)
        # self.Bind(wx.EVT_CHECKBOX, self.on_checkbox_click, id=1)
        # self.Bind(wx.EVT_CHECKBOX, self.on_checkbox_click, id=2)
        # self.Bind(wx.EVT_CHECKBOX, self.on_checkbox_click, id=3)
        self.vbox.Add(self.hbox, 0, flag=wx.ALL, border=6)

        self.vbox.Add(self.T_01_VGA, 0, flag=wx.ALL, border=6)
        self.vbox.Add(self.T_02_Write_MAC, 0, flag=wx.ALL, border=6)
        self.vbox.Add(self.T_03_Write_FRU, 0, flag=wx.ALL, border=6)

        self.vbox.Add(self.T_04_ETH, 0, flag=wx.ALL, border=6)
        self.vbox.Add(self.T_05_SFP, 0, flag=wx.ALL, border=6)
        self.vbox.Add(self.T_06_CPU, 0, flag=wx.ALL, border=6)

        self.vbox.Add(self.T_07_Memory, 0, flag=wx.ALL, border=6)
        self.vbox.Add(self.T_08_Console, 0, flag=wx.ALL, border=6)
        self.vbox.Add(self.T_09_USB, 0, flag=wx.ALL, border=6)

        self.vbox.Add(self.T_10_PCI_E, 0, flag=wx.ALL, border=6)
        self.vbox.Add(self.T_11_SATA, 0, flag=wx.ALL, border=6)
        self.vbox.Add(self.T_12_M_2, 0, flag=wx.ALL, border=6)

        self.panel.SetSizer(self.vbox)
        self.panel.Layout()

        # setting variable
        self.setting = Setting()

        # input setting
        self.value2 = ''

        # fetch free mac number
        test_execute00 = FreeMacFetch(self)
        test_execute00.start()

    def on_key_press(self, event):
        # print('key press')
        self.t_press = time.time()
        self.Key_Code = event.GetKeyCode()
        if 48 <= self.Key_Code <= 90:
            self.value = switch_keycode(self.Key_Code).switch_content()
            self.value2 = str(self.value2) + str(self.value)
            # print(value)
            # print(value2)
        # event.Skip()

    def on_key_release(self, event):
        # print('key release')
        self.t_realease = time.time()
        self.duration = self.t_realease - self.t_press
        # print(duration)
        if self.duration > 0.04:
            warning_message = wx.MessageDialog(self.panel, "please do not input manually", "warning",
                                               wx.OK | wx.ICON_INFORMATION)
            value2 = ''
            self.m_serial.Clear()
            if warning_message.ShowModal() == wx.ID_OK:
                warning_message.Destroy()
        elif self.Key_Code == 13:
            # print('press enter')
            self.m_serial.SetValue(self.value2)
        # event.Skip()

    def start_test(self, event):

        start_dialog = wx.MessageDialog(self.panel, "要进行测试吗？ Do You Want To Test?", "测试",
                                        wx.YES_NO | wx.ICON_QUESTION)
        start_result = start_dialog.ShowModal()
        start_dialog.Destroy()

        if start_result == wx.ID_YES:
            # subprocess.getoutput("rm -f %s" % self.setting.logname)
            # self.start_dialog.Destroy()
            self.Serial_number = self.m_serial.GetValue()
            SN_check = Verify_SN(self.Serial_number).test_content()
            connect = subprocess.getoutput("ping -c 2 %s" % self.setting.BBU_USB_IP)
            if SN_check == 'FAIL':
                warning_message = wx.MessageDialog(self.panel, "Wrong serial or serial number has lower case",
                                                   "warning", wx.OK | wx.ICON_INFORMATION)
                if warning_message.ShowModal() == wx.ID_OK:
                    warning_message.Destroy()

            elif '100% packet loss' in connect:
                warning_message = wx.MessageDialog(self.panel, "Connect to BBU failed, please check the network,"
                                                               " test stop", "warning",
                                                   wx.OK | wx.ICON_INFORMATION)
                if warning_message.ShowModal() == wx.ID_OK:
                    warning_message.Destroy()

            else:
                T_101_VGA = self.T_01_VGA.GetValue()
                T_102_Write_MAC = self.T_02_Write_MAC.GetValue()
                T_103_Write_FRU = self.T_03_Write_FRU.GetValue()

                T_104_ETH = self.T_04_ETH.GetValue()
                T_105_SFP = self.T_05_SFP.GetValue()
                T_106_CPU = self.T_06_CPU.GetValue()

                T_107_Memory = self.T_07_Memory.GetValue()
                T_108_Console = self.T_08_Console.GetValue()
                T_109_USB = self.T_09_USB.GetValue()

                T_110_PCI_E = self.T_10_PCI_E.GetValue()
                T_111_SATA = self.T_11_SATA.GetValue()
                T_112_M_2 = self.T_12_M_2.GetValue()

                self.m_serial.Enable(False)
                self.test_bt.Disable()
                self.test_bt.SetBackgroundColour((0, 220, 18))
                self.test_bt.SetFont(self.font_01)
                self.test_bt.SetLabelText("Testing")
                test_list = ['test_all']
                if T_101_VGA == 1:
                    test_list.append('test_vga')
                if T_102_Write_MAC == 1:
                    test_list.append('test_mac')
                if T_103_Write_FRU == 1:
                    test_list.append('test_fru')
                if T_104_ETH == 1:
                    test_list.append('test_eth')
                if T_105_SFP == 1:
                    test_list.append('test_sfp')
                if T_106_CPU == 1:
                    test_list.append('test_cpu')
                if T_107_Memory == 1:
                    test_list.append('test_memory')
                if T_108_Console == 1:
                    test_list.append('test_console')
                if T_109_USB == 1:
                    test_list.append('test_usb')
                if T_110_PCI_E == 1:
                    test_list.append('test_pcie')
                if T_111_SATA == 1:
                    test_list.append('test_sata')
                if T_112_M_2 == 1:
                    test_list.append('test_m2')
                item = ' or '.join(test_list)
                time_format = time.strftime("%Y-%m-%d_%H-%M-%S", time.localtime())
                logname = 'SN='+self.Serial_number+'_'+time_format

                # pytest传递参数Serial_number
                @pytest.fixture()
                def Serial_number():
                    SN = self.Serial_number
                    return SN

                arg = ["-s", "-k", item, "Test_item.py", "--html=ft_test_log/%s.html" % logname]  # "--capture=sys"
                pytest.main(arg)
                # print(a)
                # if 'FAILED' in str(pytest.main(arg)):
                #     result = 'test failed'
                # else:
                #     result = 'test pass'
                # summary_dialog = wx.MessageDialog(self, result, "测试结果如下：", wx.OK | wx.ICON_INFORMATION)
                # summary_dialog.ShowModal()
                # summary_dialog.Destroy()

        else:
            print("No")
            print("No")
            print("No")
            print("No")
            print("No")
            print("No")
            self.Destroy()

    def close_frame(self, event):
        dialog = wx.MessageDialog(self.panel, "Do You Want To Exit?", "Close", wx.YES_NO | wx.ICON_QUESTION)
        result = dialog.ShowModal()
        dialog.Destroy()
        if result == wx.ID_YES:
            self.Destroy()

    # pop total_result, record result to mysql and send e-mail
    def all_result(self, vga_result, write_mac_result, write_fru_result, eth_result, sfp_result, cpu_result,
                   memory_result, console_result, usb_result, pcie_result, sata_result, m2_result):
        mydb = pymysql.connect(host=self.setting.mysql_host, user=self.setting.mysql_user,
                               passwd=self.setting.mysql_password, database=self.setting.mysql_database)
        mycursor = mydb.cursor()
        i = 0
        if write_mac_result != 'PASS' or write_mac_result != 'Not Test':
            mql = "insert into test_result (test_run_result,test_run_summary) values ('FAIL','%s_write_mac_%s')"\
                  % (self.Serial_number, write_mac_result)
            mycursor.execute(mql)
            i += 1
        if write_fru_result != 'PASS' or write_fru_result != 'Not Test':
            mql = "insert into test_result (test_run_result,test_run_summary) values ('FAIL','%s_write_fru_%s')"\
                  % (self.Serial_number, write_fru_result)
            mycursor.execute(mql)
            i += 1
        if vga_result != 'PASS' or vga_result != 'Not Test':
            mql = "insert into test_result (test_run_result,test_run_summary) values ('FAIL','%s_vga_test_%s')"\
                  % (self.Serial_number, vga_result)
            mycursor.execute(mql)
            i += 1
        if eth_result != 'PASS' or eth_result != 'Not Test':
            mql = "insert into test_result (test_run_result,test_run_summary) values ('FAIL','%s_eth_test_%s')"\
                  % (self.Serial_number, eth_result)
            mycursor.execute(mql)
            i += 1
        if memory_result != 'PASS' or memory_result != 'Not Test':
            mql = "insert into test_result (test_run_result,test_run_summary) values ('FAIL','%s_memory_test_%s')"\
                  % (self.Serial_number, memory_result)
            mycursor.execute(mql)
            i += 1
        if sfp_result != 'PASS' or sfp_result != 'Not Test':
            mql = "insert into test_result (test_run_result,test_run_summary) values ('FAIL','%s_sfp_test_%s')"\
                  % (self.Serial_number, sfp_result)
            mycursor.execute(mql)
            i += 1
        if cpu_result != 'PASS' or cpu_result != 'Not Test':
            mql = "insert into test_result (test_run_result,test_run_summary) values ('FAIL','%s_cpu_test_%s')"\
                  % (self.Serial_number, cpu_result)
            mycursor.execute(mql)
            i += 1
        if console_result != 'PASS' or console_result != 'Not Test':
            mql = "insert into test_result (test_run_result,test_run_summary) values ('FAIL','%s_console_test_%s')"\
                  % (self.Serial_number, console_result)
            mycursor.execute(mql)
            i += 1
        if usb_result != 'PASS' or usb_result != 'Not Test':
            mql = "insert into test_result (test_run_result,test_run_summary) values ('FAIL','%s_usb_test_%s')"\
                  % (self.Serial_number, usb_result)
            mycursor.execute(mql)
            i += 1
        if pcie_result != 'PASS' or pcie_result != 'Not Test':
            mql = "insert into test_result (test_run_result,test_run_summary) values ('FAIL','%s_pcie_test_%s')"\
                  % (self.Serial_number, pcie_result)
            mycursor.execute(mql)
            i += 1
        if sata_result != 'PASS' or sata_result != 'Not Test':
            mql = "insert into test_result (test_run_result,test_run_summary) values ('FAIL','%s_sata_test_%s')"\
                  % (self.Serial_number, sata_result)
            mycursor.execute(mql)
            i += 1
        if m2_result != 'PASS' or m2_result != 'Not Test':
            mql = "insert into test_result (test_run_result,test_run_summary) values ('FAIL','%s_m2_test_%s')"\
                  % (self.Serial_number, m2_result)
            mycursor.execute(mql)
            i += 1
        if i == 0:
            mql = "insert into test_result (test_run_result,test_run_summary) values ('PASS','%s')"\
                  % self.Serial_number
            mycursor.execute(mql)

        # send mail to my e-mail
        mail_sender = '316756844@qq.com'
        mail_password = 'rptmuskmfpotbhca'
        mail_receiver = '316756844@qq.com'
        test_time = time.strftime("%Y-%m-%d_%H:%M:%S", time.localtime())

        message = MIMEText('test result on board %s is<br> vga: %s <br> mac: %s <br> fru: %s <br> eth: %s <br> '
                           'sfp: %s <br> cpu: %s <br> memory: %s <br> console: %s <br> usb: %s <br> pcie: %s <br> '
                           'sata: %s <br> m.2: %s <br> test time is %s'
                           % (self.Serial_number, vga_result, write_mac_result, write_fru_result, eth_result,
                              sfp_result, cpu_result, memory_result, console_result, usb_result, pcie_result,
                              sata_result, m2_result, test_time), 'plain', 'utf-8')
        message['From'] = Header('BBU_test', 'utf-8')
        message['To'] = Header('shanghai_lab', 'utf-8')
        subject = 'Maxwell BBU test'
        message['Subject'] = Header(subject, 'utf-8')

        try:
            server = smtplib.SMTP_SSL('smtp.qq.com', 465)
            server.login(mail_sender, mail_password)
            server.sendmail(mail_sender, mail_receiver, message.as_string())
            server.quit()
            print('send mail successfully')
        except Exception:
            print('error, send mail failed')
        result = 'VGA: %s \nMAC: %s \nFRU: %s \nETH: %s \nSFP: %s \nCPU: %s\nMemory: %s \nCONSOLE: %s\nUSB: %s\n' \
                 'PCIE: %s\n SATA: %s\nM.2: %s' % (vga_result, write_mac_result, write_fru_result, eth_result,
                                                   sfp_result, cpu_result, memory_result, console_result, usb_result,
                                                   pcie_result, sata_result, m2_result)
        summary_dialog = wx.MessageDialog(self.panel, result, "测试结果如下：", wx.OK | wx.ICON_INFORMATION)
        summary_dialog.ShowModal()
        summary_dialog.Destroy()

        self.Destroy()

    # display vga result
    def vga_result(self, result):
        vga_result = wx.StaticText(self.panel, -1, 'VGA test result is %s' % result, pos=(300, 160), size=(720, 40))
        vga_result.SetFont(self.font_00)
        if result == 'PASS':
            vga_result.SetForegroundColour((0, 128, 0))
        elif result == 'Not Test':
            vga_result.SetForegroundColour((96, 96, 96))
        else:
            vga_result.SetForegroundColour((255, 0, 0))

    # display mac result
    def write_mac_result(self, result):
        write_mac_result = wx.StaticText(self.panel, -1, 'Write mac result is %s' % result, pos=(300, 200), size=(720, 40))
        write_mac_result.SetFont(self.font_00)
        if result == 'PASS':
            write_mac_result.SetForegroundColour((0, 128, 0))
        elif result == 'Not Write' or 'Old board, no need to write':
            write_mac_result.SetForegroundColour((96, 96, 96))
        else:
            write_mac_result.SetForegroundColour((255, 0, 0))

    # display fru result
    def write_fru_result(self, result):
        write_fru_result = wx.StaticText(self.panel, -1, 'Write fru result is %s' % result, pos=(300, 240), size=(720, 40))
        write_fru_result.SetFont(self.font_00)
        if result == 'PASS':
            write_fru_result.SetForegroundColour((0, 128, 0))
        elif result == 'Not Write':
            write_fru_result.SetForegroundColour((96, 96, 96))
        else:
            write_fru_result.SetForegroundColour((255, 0, 0))

    # display eth result
    def eth_result(self, result):
        eth_result = wx.StaticText(self.panel, -1, 'ETH test result is %s' % result, pos=(300, 280), size=(720, 40))
        eth_result.SetFont(self.font_00)
        if result == 'PASS':
            eth_result.SetForegroundColour((0, 128, 0))
        elif result == 'Not Test':
            eth_result.SetForegroundColour((96, 96, 96))
        else:
            eth_result.SetForegroundColour((255, 0, 0))

    # display sfp result
    def sfp_result(self, result):
        sfp_result = wx.StaticText(self.panel, -1, 'SFP test result is %s' % result, pos=(300, 320), size=(720, 40))
        sfp_result.SetFont(self.font_00)
        if result == 'PASS':
            sfp_result.SetForegroundColour((0, 128, 0))
        elif result == 'Not Test':
            sfp_result.SetForegroundColour((96, 96, 96))
        else:
            sfp_result.SetForegroundColour((255, 0, 0))

    # display cpu result
    def cpu_result(self, result):
        cpu_result = wx.StaticText(self.panel, -1, 'CPU test result is %s' % result, pos=(300, 360), size=(720, 40))
        cpu_result.SetFont(self.font_00)
        if result == 'PASS':
            cpu_result.SetForegroundColour((0, 128, 0))
        elif result == 'Not Test':
            cpu_result.SetForegroundColour((96, 96, 96))
        else:
            cpu_result.SetForegroundColour((255, 0, 0))

    # display memory result
    def memory_result(self, result):
        memory_result = wx.StaticText(self.panel, -1, 'Memory test result is %s' % result, pos=(300, 400), size=(720, 40))
        memory_result.SetFont(self.font_00)
        if result == 'PASS':
            memory_result.SetForegroundColour((0, 128, 0))
        elif result == 'Not Test':
            memory_result.SetForegroundColour((96, 96, 96))
        else:
            memory_result.SetForegroundColour((255, 0, 0))

    # display console result
    def console_result(self, result):
        console_result = wx.StaticText(self.panel, -1, 'Console test result is %s' % result, pos=(300, 440), size=(720, 40))
        console_result.SetFont(self.font_00)
        if result == 'PASS':
            console_result.SetForegroundColour((0, 128, 0))
        elif result == 'Not Test':
            console_result.SetForegroundColour((96, 96, 96))
        else:
            console_result.SetForegroundColour((255, 0, 0))

    # display usb result
    def usb_result(self, result):
        usb_result = wx.StaticText(self.panel, -1, 'USB test result is %s' % result, pos=(300, 480), size=(720, 40))
        usb_result.SetFont(self.font_00)
        if result == 'PASS':
            usb_result.SetForegroundColour((0, 128, 0))
        elif result == 'Not Test':
            usb_result.SetForegroundColour((96, 96, 96))
        else:
            usb_result.SetForegroundColour((255, 0, 0))

    # display pcie result
    def pcie_result(self, result):
        pcie_result = wx.StaticText(self.panel, -1, 'PCI-E test result is %s' % result, pos=(300, 520), size=(720, 40))
        pcie_result.SetFont(self.font_00)
        if result == 'PASS':
            pcie_result.SetForegroundColour((0, 128, 0))
        elif result == 'Not Test':
            pcie_result.SetForegroundColour((96, 96, 96))
        else:
            pcie_result.SetForegroundColour((255, 0, 0))

    # display sata result
    def sata_result(self, result):
        sata_result = wx.StaticText(self.panel, -1, 'SATA test result is %s' % result, pos=(300, 560), size=(720, 40))
        sata_result.SetFont(self.font_00)
        if result == 'PASS':
            sata_result.SetForegroundColour((0, 128, 0))
        elif result == 'Not Test':
            sata_result.SetForegroundColour((96, 96, 96))
        else:
            sata_result.SetForegroundColour((255, 0, 0))

    # display m2 result
    def m2_result(self, result):
        m2_result = wx.StaticText(self.panel, -1, 'M.2 test result is %s' % result, pos=(300, 600), size=(720, 40))
        m2_result.SetFont(self.font_00)
        if result == 'PASS':
            m2_result.SetForegroundColour((0, 128, 0))
        elif result == 'Not Test':
            m2_result.SetForegroundColour((96, 96, 96))
        else:
            m2_result.SetForegroundColour((255, 0, 0))

    def close_window(self, event):
        self.Destroy()


class MyApp(wx.App):
    def OnInit(self):
        frame = Frame("Function Test Platform V1.0")
        self.Bind(wx.EVT_KEY_DOWN, frame.on_key_press)
        self.Bind(wx.EVT_KEY_UP, frame.on_key_release)
        frame.Show()
        return True


if __name__ == '__main__':
    app = MyApp()
    app.MainLoop()

