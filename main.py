import sys
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5 import QtCore, QtGui, QtWidgets, QtWebEngineWidgets

from data_clean import clean_data
from mainwindow import Ui_MainWindow
from plot import MyFigure
from matplotlib import animation
from matplotlib.patches import Rectangle, Wedge
import matplotlib.colors as mc
import sip
from mpl_toolkits.basemap import Basemap
import folium
import numpy as np
import io

class main_plot(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self):
        super(main_plot, self).__init__()
        self.setupUi(self)
        self.data = clean_data()                      # 读取数据
        self.data_iter = self.get_data(1970)
        self.data_iter1 = self.get_data(1970)
        self.data_iter2 = self.get_data(1970)
        self.data_interval = None
        self.data_interval1 = None
        self.data_interval2 = None
        self.F = None                                 # canvas容器
        self.step = 0                                 # 记录操作次数
        self.y = None                                 # 当前年
        self.m = None                                 # 当前月
        self.iter_cnt = 0
        self.iter_cnt1 = 0
        self.iter_cnt2 = 0
        self.lat = None
        self.lon = None
        self.sub = None
        self.frame = 0
        self.pre = None

        self.colors_a_1 = ['r','g','b','y','c','m','k','olive','purple']
        color_list = [mc.to_rgb(c) for c in self.colors_a_1]
        self.colors = [make_rgb_transparent(c, [1,1,1], 0.5) for c in color_list] # 颜色

###--------------------柱状图变量---------------------------###
        self.annotation = []  # 标记
        self.annotation1 = []  # 标记
        self.annotation2 = []  # 标记
        self.bars = None  # 柱状图句柄
        self.bars1 = None
        self.bars2 = None
        self.anim = None  # 动画句柄
        self.anim1 = None
        self.anim2 = None
        self.curheight = [0, 0]  # 记录bar的当前高度
        self.curheight1 = [0, 0, 0, 0]
        self.curheight2 = [0, 0, 0, 0]
        self.curheight3 = [0, 0, 0]

###--------------------饼图变量---------------------------###
        self.pie = None                                    # 饼图句柄
        self.curangle1 = [0, 0, 0, 0, 0, 0, 0, 0, 0]       # 起始角度
        self.curangle2 = [0, 0, 0, 0, 0, 0, 0, 0, 360]     # 终止角度

###--------------------地图变量---------------------------###
        self.map = None
        self.scatter = None
        self.scatter1 = None
        self.scatter2 = None
        self.increase = True

    ###--------------------槽函数---------------------------###
    @pyqtSlot()
    def on_plot1_clicked(self):
        self.step += 1
        print(">>>>>step: ", self.step)
        y, m = self.get_ym()
        if self.step > 1:                           # 如果不是第一次操作，则将高度置0后重新绘图
            try:
                sip.delete(self.F)
            except:
                print("except")
            self.year.display(y)
            self.month.display(0)
            self.day.display(0)
            if self.sub:
                self.sub.close()
            self.plot_success()
        else:
            self.year.display(y)
            self.month.display(0)
            self.day.display(0)
            self.plot_success()

    @pyqtSlot()
    def on_plot2_clicked(self):
        self.step += 1
        print(">>>>>step: ", self.step)
        y, m = self.get_ym()
        if self.step > 1:
            try:
                sip.delete(self.F)
            except:
                print("except")
            self.year.display(y)
            self.month.display(0)
            self.day.display(0)
            if self.sub:
                self.sub.close()
            self.plot_attacktype()
        else:
            self.year.display(y)
            self.month.display(0)
            self.day.display(0)
            self.plot_attacktype()

    @pyqtSlot()
    def on_plot3_clicked(self):
        self.step += 1
        print(">>>>>step: ", self.step)
        y, m = self.get_ym()
        if self.step > 1:
            if self.sub:
                self.sub.close()
            try:
                sip.delete(self.F)
            except:
                print("except")
            self.year.display(y)
            self.month.display(0)
            self.day.display(0)
            self.plot_loss()
        else:
            self.year.display(y)
            self.month.display(0)
            self.day.display(0)
            self.plot_loss()

    @pyqtSlot()
    def on_plot4_clicked(self):
        self.step += 1
        print(">>>>>step: ", self.step)
        if self.step > 1:
            if self.sub:
                self.sub.close()
            try:
                sip.delete(self.F)
            except:
                print("except")
            self.plot_map()
        else:
            self.plot_map()

    @pyqtSlot()
    def on_plot5_clicked(self):
        self.step += 1
        print(">>>>>step: ", self.step)
        y, m = self.get_ym()
        if self.step > 1:
            try:
                sip.delete(self.F)
            except:
                print("except")
            if self.sub:
                self.sub.close()
            self.year.display(y)
            self.month.display(m)
            self.day.display(0)
            self.plot_dynamicmap()
        else:
            self.year.display(y)
            self.month.display(m)
            self.day.display(0)
            self.plot_dynamicmap()

    @pyqtSlot()
    def on_choose_color_clicked(self):
        color = QColorDialog.getColor()
        if color.isValid():
            hsv = color.getHsv()
            rgb = list(color.getRgb())[:3]
            for i in range(3):
                rgb[i] /= 255
            colors = [rgb]
            k = (255 - hsv[1]) / (359 - hsv[0])
            b = hsv[1] - k * hsv[0]
            delta = -15 if 359 - hsv[0] < 135 else 15
            for i in range(8):
                h = (i+1)*delta + hsv[0]
                s = k*h+b
                color.setHsv(h, s, 255, 255)
                c = list(color.getRgb())[:3]
                for i in range(3):
                    c[i] /= 255
                colors.append(c)
            self.colors_a_1 = colors
            self.colors = [make_rgb_transparent(c, [1,1,1], 0.5) for c in colors]

    @pyqtSlot()
    def on_play_clicked(self):
        self.step += 1
        if self.pre == 'success' or self.pre == None:
            if self.step > 1:                           # 如果不是第一次操作，则将高度置0后重新绘图
                try:
                    sip.delete(self.F)
                except:
                    print("except")
                self.curheight = [0, 0]
                self.plot_success(type=1)
            else:
                self.plot_success(type=1)
        elif self.pre == 'loss':
            if self.step > 1:                           # 如果不是第一次操作，则将高度置0后重新绘图
                try:
                    sip.delete(self.F)
                except:
                    print("except")
                self.annotation = []
                self.iter_cnt = 0
                self.iter_cnt1 = 0
                self.iter_cnt2 = 0
                self.curheight1 = [0, 0, 0, 0]
                self.curheight2 = [0, 0, 0, 0]
                self.curheight3 = [0, 0, 0]
                self.plot_loss(type=1)
            else:
                self.plot_loss(type=1)

        else:
            if self.step > 1:
                if self.sub:
                    self.sub.close()
                self.map_play()
            else:
                self.map_play()

    ###--------------------画图---------------------------###
    def success_move_event(self, event):
        anno_changed = False
        for rect, annote in self.annotation:           # 当鼠标移动到bar上时改变其颜色，显示其数量
            should_be_visible = (rect.contains(event)[0] == True)
            # c = 'r' if should_be_visible else 'b'
            alpha = 1 if should_be_visible else 0.5
            if should_be_visible != annote.get_visible():
                anno_changed = True
                annote.set_visible(should_be_visible)
                # rect.set_color(c)
                rect.set_alpha(alpha)
        if anno_changed:
            self.F.fig.canvas.draw()

    def attack_move_event(self, event):
        # print(1111)
        anno_changed = False
        for w, annote in self.annotation:  # 当鼠标移动到bar上时改变其颜色，显示其数量
            should_be_visible = (w.contains(event)[0] == True)
            alpha = 1 if should_be_visible else 0.5
            if should_be_visible != annote.get_visible():
                anno_changed = True
                annote.set_visible(should_be_visible)
                w.set_alpha(alpha)
        if anno_changed:
            # print("changed")
            self.F.fig.canvas.draw()

    def loss_move_event1(self, event):
        anno_changed = False
        for rect, annote in self.annotation:  # 当鼠标移动到bar上时改变其颜色，显示其数量
            should_be_visible = (rect.contains(event)[0] == True)
            # c = 'r' if should_be_visible else 'b'
            alpha = 1 if should_be_visible else 0.5
            if should_be_visible != annote.get_visible():
                anno_changed = True
                annote.set_visible(should_be_visible)
                # rect.set_color(c)
                rect.set_alpha(alpha)
        if anno_changed:
            self.F.fig.canvas.draw()

    def loss_move_event2(self, event):
        anno_changed = False
        for rect, annote in self.annotation1:  # 当鼠标移动到bar上时改变其颜色，显示其数量
            should_be_visible = (rect.contains(event)[0] == True)
            # c = 'r' if should_be_visible else 'b'
            alpha = 1 if should_be_visible else 0.5
            if should_be_visible != annote.get_visible():
                anno_changed = True
                annote.set_visible(should_be_visible)
                # rect.set_color(c)
                rect.set_alpha(alpha)
        if anno_changed:
            self.F.fig.canvas.draw()

    def loss_move_event3(self, event):
        anno_changed = False
        for rect, annote in self.annotation2:  # 当鼠标移动到bar上时改变其颜色，显示其数量
            should_be_visible = (rect.contains(event)[0] == True)
            # c = 'r' if should_be_visible else 'b'
            alpha = 1 if should_be_visible else 0.5
            if should_be_visible != annote.get_visible():
                anno_changed = True
                annote.set_visible(should_be_visible)
                # rect.set_color(c)
                rect.set_alpha(alpha)
        if anno_changed:
            self.F.fig.canvas.draw()

    def success_upd(self, t):
        y, _ = self.get_ym()
        data = self.data[self.data['iyear']==y]
        data = [data['success'].value_counts()[1], data['success'].value_counts()[0]]
        for i, rect in enumerate(self.bars):                      # 每次update，数量增长1000
            if abs(self.curheight[i] - data[i]) < 100:
                continue
            if self.curheight[i] < data[i]:
                self.curheight[i] = self.curheight[i] + 100
                rect.set_height(self.curheight[i])
                # self.F.fig.canvas.draw()
            elif self.curheight[i] > data[i]:
                self.curheight[i] = self.curheight[i] - 100
                rect.set_height(self.curheight[i])

        if t == 159:
            x = ['succeed', 'failed']
            y = data[:]
            self.curheight = y[:]
            self.F.axes.cla()
            self.bars = self.F.axes.bar(x, y, picker=True,color=[self.colors[0], self.colors[1]])
            self.F.axes.set_ylim([0, 15000])
            self.F.axes.grid(True, linestyle='-.')
            self.F.axes.set_ylabel('number of cases')
            self.F.fig.canvas.draw()                            # 最后一帧时精确绘图
            self.F.fig.canvas.mpl_connect('motion_notify_event', self.success_move_event)
            for i, x in enumerate(self.bars):                    # 将两个相同大小的矩阵加入到画布中，为了之后便于显示标签
                print(x)
                annotation = self.F.axes.annotate(str(data[i]), (x.get_x() + x.get_width() / 2., x.get_height()))
                annotation.set_visible(False)
                r = Rectangle(x.get_xy(), x.get_width(), x.get_height(), color=self.colors_a_1[i])
                r.set_alpha(0.5)
                r.set_edgecolor('none')
                self.F.axes.add_artist(r)
                self.annotation.append([r, annotation])
        return self.bars

    def play_success(self, t):
        if t == 0:
            y, _ = self.get_ym()
            self.data_iter = self.get_data(y)
            self.data_interval, y = self.data_iter.__next__()
            self.year.display(y)
            self.iter_cnt=-1
        try:
            data = [self.data_interval['success'].value_counts()[1], self.data_interval['success'].value_counts()[0]]
        except:
            data = [0, 0]

        if abs(data[0] - self.curheight[0]) > 500:
            delta = 100
        else:
            delta = 10

        for i, rect in enumerate(self.bars):
            if abs(self.curheight[i] - data[i]) < delta:
                continue
            if self.curheight[i] < data[i]:
                self.curheight[i] = self.curheight[i] + delta
                rect.set_height(self.curheight[i])
            elif self.curheight[i] > data[i]:
                self.curheight[i] = self.curheight[i] - delta
                rect.set_height(self.curheight[i])

        self.iter_cnt = self.iter_cnt + 1
        if self.iter_cnt == 50:
            self.data_interval, y = self.data_iter.__next__()
            self.year.display(y)
            self.iter_cnt = 0
        if t == self.frame-3:
            x = ['succeed', 'failed']
            y = data[:]
            self.curheight = data[:]
            print(self.curheight)
            # self.F.axes.cla()
            self.bars = self.F.axes.bar(x, y, picker=True, color=[self.colors[0], self.colors[1]])
            self.F.axes.set_ylim([0, 15000])
            self.F.axes.grid(True, linestyle='-.')
            self.F.axes.set_ylabel('number of cases')
            self.F.fig.canvas.draw()                # 最后一帧时精确绘图
            self.F.fig.canvas.mpl_connect('motion_notify_event', self.success_move_event)
            for i, x in enumerate(self.bars):       # 将两个相同大小的矩阵加入到画布中，为了之后便于显示标签
                annotation = self.F.axes.annotate(str(data[i]), (x.get_x() + x.get_width() / 2., x.get_height()))
                annotation.set_visible(False)
                r = Rectangle(x.get_xy(), x.get_width(), x.get_height(), color=self.colors_a_1[i])
                r.set_alpha(0.5)
                r.set_edgecolor('none')
                self.F.axes.add_artist(r)
                self.annotation.append([r, annotation])
        return self.bars

    def scatter_upd(self, t):
        if t == 0:
            y, _ = self.get_ym()
            self.data_iter1 = self.get_data(y)
        if t % 50 == 0 or t == self.frame-1:
            data, y = self.data_iter1.__next__()
            try:
                data = [data['success'].value_counts()[1], data['success'].value_counts()[0]]
            except:
                data = [0, 0]
            self.scatter1 = self.F.axes1.scatter(y, data[0], animated=True, c=self.colors_a_1[0],
                                                marker='*', s=200)
            self.scatter2 = self.F.axes1.scatter(y, data[1], animated=True, c=self.colors_a_1[1],
                                                 marker='*', s=200)

        return self.scatter1, self.scatter2

    def attack_upd(self, t):
        # print("t:", t)
        y, _ = self.get_ym()
        d = self.data[self.data['iyear']==y]
        data = []
        tag = ['Bombing/Explosion', 'Armed Assault', 'Assassination', 'Facility/Infrastructure Attack',
               'Hostage Taking (Kidnapping)', 'Unknown', 'Unarmed Assault', 'Hostage Taking (Barricade Incident)',
               'Hijacking']
        for i in range(9):
            try:
                data.append(d['attacktype1_txt'].value_counts(normalize=True)[tag[i]] * 360)
            except:
                data.append(0)
        sum = 0
        for i, wedge in enumerate(self.pie[0]):
            curangle = self.curangle2[i]-self.curangle1[i]
            if curangle < data[i]:
                delta = 1
            else:
                delta= -4
            if abs(curangle-data[i]) > 1 and i == 0:
                self.curangle2[i] += delta
                if self.curangle2[i] < self.curangle1[i]:
                    self.curangle2[i] = self.curangle1[i]
                wedge.set_theta1(self.curangle1[i])
                wedge.set_theta2(self.curangle2[i])
            elif i != 8 and i != 0:
                sub = self.curangle2[i-1] - self.curangle1[i]
                self.curangle1[i] = self.curangle2[i-1]
                self.curangle2[i] = self.curangle2[i] + sub
                if abs(curangle - data[i]) > 1:
                    self.curangle2[i] = self.curangle2[i] + delta
                    if self.curangle2[i] < self.curangle1[i]:
                        self.curangle2[i] = self.curangle1[i]
                wedge.set_theta1(self.curangle1[i])
                wedge.set_theta2(self.curangle2[i])
            elif i == 8:
                self.curangle1[i] = sum
                wedge.set_theta1(self.curangle1[i])
            # print("start_angle" + str(i), self.curangle1[i], "end_angle" + str(i), self.curangle2[i])
            sum = sum + self.curangle2[i] - self.curangle1[i]
        if t == 199:
            tag = ['Bombing/Explosion', 'Armed Assault', 'Assassination', 'Facility/Infrastructure Attack',
                   'Hostage Taking \n(Kidnapping)', 'Unknown', 'Unarmed Assault', 'Hostage Taking \n(Barricade Incident)',
                   'Hijacking']
            self.F.axes.cla()
            self.pie = self.F.axes.pie(x=data, colors=self.colors)
            self.F.axes.legend(self.pie[0], tag, loc=2, bbox_to_anchor=(-0.75, 1.0),borderaxespad = 0.,frameon=False)
            self.curangle1 = []
            self.curangle2 = []
            for i, x in enumerate(self.pie[0]):
                num = round(100 * data[i] / 360., 2)
                annotation = self.F.axes.annotate(str(num)+'%\n'+str(tag[i]), (0.75, 0.75))
                annotation.set_visible(False)
                w = Wedge(center=(0,0), r=1, theta1=x.theta1, theta2=x.theta2, width=None)
                self.curangle1.append(x.theta1)
                self.curangle2.append(x.theta2)
                w.set_color(self.colors_a_1[i])
                w.set_alpha(0.5)
                w.set_edgecolor('none')
                self.F.axes.add_artist(w)
                self.annotation.append([w, annotation])
            self.F.fig.canvas.draw()                            # 最后一帧时精确绘图
            self.F.fig.canvas.mpl_connect('motion_notify_event', self.attack_move_event)
        return self.pie[0]

    def loss_upd(self, t):
        y, _ = self.get_ym()
        data = self.data[self.data['iyear']==y]
        num = ['10~30','30~50','50~100','>100']
        y1 = [data[data['nkill']>=10].count()['iyear']-data[data['nkill']>=30].count()['iyear'],
              data[data['nkill'] >= 30].count()['iyear'] - data[data['nkill'] >= 50].count()['iyear'],
              data[data['nkill'] >= 50].count()['iyear'] - data[data['nkill'] >= 100].count()['iyear'],
              data[data['nkill'] >= 100].count()['iyear']]
        for i , bar1 in enumerate(self.bars):
            if abs(self.curheight1[i] - y1[i]) < 10:
                continue
            if self.curheight1[i] < y1[i]:
                self.curheight1[i] = self.curheight1[i] + 10
                bar1.set_width(self.curheight1[i])
            elif self.curheight1[i] > y1[i]:
                self.curheight1[i] = self.curheight1[i] - 10
                bar1.set_width(self.curheight1[i])

        if t == 79:
            self.F.axes1.cla()
            self.curheight1 = y1[:]
            self.bars = self.F.axes1.barh(num, y1, picker=True, color=[self.colors[i] for i in range(4)])
            self.F.axes1.set_xlim([0, 1000])
            self.F.axes1.grid(True, linestyle='-.')
            self.F.axes1.set_ylabel('number of death')
            self.F.axes1.set_xlabel('number of cases')
            self.F.fig.canvas.draw()  # 最后一帧时精确绘图
            self.F.fig.canvas.mpl_connect('motion_notify_event', self.loss_move_event1)
            for i, x in enumerate(self.bars):  # 将两个相同大小的矩阵加入到画布中，为了之后便于显示标签
                # print(x)
                annotation = self.F.axes1.annotate(str(y1[i]), (x.get_width(), x.get_xy()[1]))
                annotation.set_visible(False)
                r = Rectangle(x.get_xy(), x.get_width(), x.get_height(), color=self.colors_a_1[i])
                r.set_alpha(0.5)
                r.set_edgecolor('none')
                self.F.axes1.add_artist(r)
                self.annotation.append([r, annotation])
        return self.bars

    def loss_upd1(self, t):
        y, _ = self.get_ym()
        data = self.data[self.data['iyear']==y]
        num = ['10~30','30~50','50~100','>100']
        y2 = [data[data['nwound'] >= 10].count()['iyear'] - data[data['nwound'] >= 30].count()['iyear'],
              data[data['nwound'] >= 30].count()['iyear'] - data[data['nwound'] >= 50].count()['iyear'],
              data[data['nwound'] >= 50].count()['iyear'] - data[data['nwound'] >= 100].count()['iyear'],
              data[data['nwound'] >= 100].count()['iyear']]
        for i , bar2 in enumerate(self.bars1):
            if abs(self.curheight2[i] - y2[i]) < 10:
                continue
            if self.curheight2[i] < y2[i]:
                self.curheight2[i] = self.curheight2[i] + 10
                bar2.set_width(self.curheight2[i])
            elif self.curheight2[i] > y2[i]:
                self.curheight2[i] = self.curheight2[i] - 10
                bar2.set_width(self.curheight2[i])
        if t == 79:
            self.F.axes2.cla()
            self.bars1 = self.F.axes2.barh(num, y2, picker=True,color=[self.colors[i] for i in range(4)])
            self.curheight2 = y2[:]
            self.F.axes2.set_xlim([0, 1000])
            self.F.axes2.grid(True, linestyle='-.')
            self.F.axes2.set_ylabel('number of injured')
            self.F.axes2.set_xlabel('number of cases')
            self.F.fig.canvas.draw()  # 最后一帧时精确绘图
            self.F.fig.canvas.mpl_connect('motion_notify_event', self.loss_move_event2)
            for i, x in enumerate(self.bars1):  # 将两个相同大小的矩阵加入到画布中，为了之后便于显示标签
                # print(x)
                annotation = self.F.axes2.annotate(str(y2[i]), (x.get_width(), x.get_xy()[1]))
                annotation.set_visible(False)
                r = Rectangle(x.get_xy(), x.get_width(), x.get_height(), color=self.colors_a_1[i])
                r.set_alpha(0.5)
                r.set_edgecolor('none')
                self.F.axes2.add_artist(r)
                self.annotation1.append([r, annotation])
        return self.bars1

    def loss_upd2(self, t):
        prop = [1, 2, 3]
        y, _ = self.get_ym()
        data = self.data[self.data['iyear']==y]
        y3 = [data[data['propextent'] == n].count()['iyear'] for n in prop]
        for i , bar3 in enumerate(self.bars2):
            if abs(self.curheight3[i] - y3[i]) < 100:
                continue
            if self.curheight3[i] < y3[i]:
                self.curheight3[i] = self.curheight3[i] + 100
                bar3.set_width(self.curheight3[i])
            if self.curheight3[i] > y3[i]:
                self.curheight3[i] = self.curheight3[i] - 100
                bar3.set_width(self.curheight3[i])
        if t == 79:
            self.F.axes3.cla()
            prop = ['<1', '1~1000', '>=1000']
            self.bars2 = self.F.axes3.barh(prop, y3, picker=True, color=[self.colors[i] for i in range(3)])
            self.curheight3 = y3[:]
            self.F.axes3.set_xlim([0, 6000])
            self.F.axes3.grid(True, linestyle='-.')
            self.F.axes3.set_ylabel('property loss extent(million dollars)')
            self.F.axes3.set_xlabel('number of cases')
            self.F.fig.canvas.draw()  # 最后一帧时精确绘图
            self.F.fig.canvas.mpl_connect('motion_notify_event', self.loss_move_event3)
            for i, x in enumerate(self.bars2):  # 将两个相同大小的矩阵加入到画布中，为了之后便于显示标签
                # print(x)
                annotation = self.F.axes3.annotate(str(y3[i]), (x.get_width(), x.get_xy()[1]))
                annotation.set_visible(False)
                r = Rectangle(x.get_xy(), x.get_width(), x.get_height(), color=self.colors_a_1[i])
                r.set_alpha(0.5)
                r.set_edgecolor('none')
                self.F.axes3.add_artist(r)
                self.annotation2.append([r, annotation])
        return self.bars2

    def loss_play(self, t):
        if t == 0:
            y, _ = self.get_ym()
            self.data_iter = self.get_data(y)
            self.data_interval, y = self.data_iter.__next__()
            self.year.display(y)
            self.iter_cnt = -1
        try:
            data = [self.data_interval[self.data_interval['nkill'] >= 10].count()['iyear'] - self.data_interval[self.data_interval['nkill'] >= 30].count()['iyear'],
                  self.data_interval[self.data_interval['nkill'] >= 30].count()['iyear'] - self.data_interval[self.data_interval['nkill'] >= 50].count()['iyear'],
                  self.data_interval[self.data_interval['nkill'] >= 50].count()['iyear'] - self.data_interval[self.data_interval['nkill'] >= 100].count()['iyear'],
                  self.data_interval[self.data_interval['nkill'] >= 100].count()['iyear']]
        except:
            data = [0,0,0,0]
        if abs(data[0] - self.curheight1[0]) > 500:
            delta = 100
        else:
            delta = 10
        for i, bar in enumerate(self.bars):
            if abs(self.curheight1[i] - data[i]) < delta:
                continue
            if self.curheight1[i] < data[i]:
                self.curheight1[i] = self.curheight1[i] + delta
                bar.set_width(self.curheight1[i])
            elif self.curheight1[i] > data[i]:
                self.curheight1[i] = self.curheight1[i] - delta
                bar.set_width(self.curheight1[i])

        self.iter_cnt = self.iter_cnt + 1
        if self.iter_cnt == 50:
            self.data_interval, y = self.data_iter.__next__()
            self.year.display(y)
            self.iter_cnt = 0

        if t == self.frame-3:
            self.curheight1 = data[:]
            num = ['10~30', '30~50', '50~100', '>100']
            self.bars = self.F.axes1.barh(num, data, picker=True, color=[self.colors[i] for i in range(4)])
            self.F.axes1.set_xlim([0, 1000])
            self.F.axes1.grid(True, linestyle='-.')
            self.F.axes1.set_ylabel('number of death')
            self.F.axes1.set_xlabel('number of cases')
            self.F.fig.canvas.draw()  # 最后一帧时精确绘图
            self.F.fig.canvas.mpl_connect('motion_notify_event', self.loss_move_event1)
            for i, x in enumerate(self.bars):  # 将两个相同大小的矩阵加入到画布中，为了之后便于显示标签
                # print(x)
                annotation = self.F.axes1.annotate(str(data[i]), (x.get_width(), x.get_xy()[1]))
                annotation.set_visible(False)
                r = Rectangle(x.get_xy(), x.get_width(), x.get_height(), color=self.colors_a_1[i])
                r.set_alpha(0.5)
                r.set_edgecolor('none')
                self.F.axes1.add_artist(r)
                self.annotation.append([r, annotation])
        return self.bars

    def loss_play1(self, t):
        if t == 0:
            y, _ = self.get_ym()
            self.data_iter1 = self.get_data(y)
            self.data_interval1, y = self.data_iter1.__next__()
            self.iter_cnt1 = -1
        try:
            data = [self.data_interval1[self.data_interval1['nwound'] >= 10].count()['iyear'] - self.data_interval1[self.data_interval1['nwound'] >= 30].count()['iyear'],
                  self.data_interval1[self.data_interval1['nwound'] >= 30].count()['iyear'] - self.data_interval1[self.data_interval1['nwound'] >= 50].count()['iyear'],
                  self.data_interval1[self.data_interval1['nwound'] >= 50].count()['iyear'] - self.data_interval1[self.data_interval1['nwound'] >= 100].count()['iyear'],
                  self.data_interval1[self.data_interval1['nwound'] >= 100].count()['iyear']]
        except:
            data = [0,0,0,0]
        if abs(data[0] - self.curheight2[0]) > 500:
            delta = 100
        else:
            delta = 10
        for i, bar in enumerate(self.bars1):
            if abs(self.curheight2[i] - data[i]) < delta:
                continue
            if self.curheight2[i] < data[i]:
                self.curheight2[i] = self.curheight2[i] + delta
                bar.set_width(self.curheight2[i])
            elif self.curheight2[i] > data[i]:
                self.curheight2[i] = self.curheight2[i] - delta
                bar.set_width(self.curheight2[i])

        self.iter_cnt1 = self.iter_cnt1 + 1
        if self.iter_cnt1 == 50:
            self.data_interval1, y = self.data_iter1.__next__()
            self.iter_cnt1 = 0

        if t == self.frame-3:
            self.curheight2 = data[:]
            num = ['10~30', '30~50', '50~100', '>100']
            self.bars1 = self.F.axes2.barh(num, data, picker=True, color=[self.colors[i] for i in range(4)])
            self.F.axes2.set_xlim([0, 1000])
            self.F.axes2.grid(True, linestyle='-.')
            self.F.axes2.set_ylabel('number of injuerd')
            self.F.axes2.set_xlabel('number of cases')
            self.F.fig.canvas.draw()  # 最后一帧时精确绘图
            self.F.fig.canvas.mpl_connect('motion_notify_event', self.loss_move_event2)
            for i, x in enumerate(self.bars1):  # 将两个相同大小的矩阵加入到画布中，为了之后便于显示标签
                # print(x)
                annotation = self.F.axes2.annotate(str(data[i]), (x.get_width(), x.get_xy()[1]))
                annotation.set_visible(False)
                r = Rectangle(x.get_xy(), x.get_width(), x.get_height(), color=self.colors_a_1[i])
                r.set_alpha(0.5)
                r.set_edgecolor('none')
                self.F.axes2.add_artist(r)
                self.annotation1.append([r, annotation])
        return self.bars1

    def loss_play2(self, t):
        if t == 0:
            y, _ = self.get_ym()
            self.data_iter2 = self.get_data(y)
            self.data_interval2, y = self.data_iter2.__next__()
            self.iter_cnt2 = -1
        try:
            prop = [1, 2, 3]
            data = [self.data_interval2[self.data_interval2['propextent'] == n].count()['iyear'] for n in prop]
        except:
            data = [0,0,0]

        for i, bar in enumerate(self.bars2):
            if abs(self.curheight3[i] - data[i]) < 100:
                continue
            if self.curheight3[i] < data[i]:
                self.curheight3[i] = self.curheight3[i] + 100
                bar.set_width(self.curheight3[i])
            elif self.curheight3[i] > data[i]:
                self.curheight3[i] = self.curheight3[i] - 100
                bar.set_width(self.curheight3[i])

        self.iter_cnt2 = self.iter_cnt2 + 1
        if self.iter_cnt2 == 50:
            self.data_interval2, y = self.data_iter2.__next__()
            self.iter_cnt2 = 0

        if t == self.frame-3:
            self.curheight3 = data[:]
            prop = ['<1', '1~1000', '>=1000']
            self.bars2 = self.F.axes3.barh(prop, data, picker=True, color=[self.colors[i] for i in range(3)])
            self.F.axes3.set_xlim([0, 6000])
            self.F.axes3.grid(True, linestyle='-.')
            self.F.axes3.set_ylabel('property loss extent(million dollars)')
            self.F.axes3.set_xlabel('number of cases')
            self.F.fig.canvas.draw()  # 最后一帧时精确绘图
            self.F.fig.canvas.mpl_connect('motion_notify_event', self.loss_move_event3)
            for i, x in enumerate(self.bars2):  # 将两个相同大小的矩阵加入到画布中，为了之后便于显示标签
                # print(x)
                annotation = self.F.axes3.annotate(str(data[i]), (x.get_width(), x.get_xy()[1]))
                annotation.set_visible(False)
                r = Rectangle(x.get_xy(), x.get_width(), x.get_height(), color=self.colors_a_1[i])
                r.set_alpha(0.5)
                r.set_edgecolor('none')
                self.F.axes3.add_artist(r)
                self.annotation2.append([r, annotation])
        return self.bars2

    def map_upd(self, t):
        print(t)
        y, m = self.get_ym()
        self.day.display(t+1)
        data = self.data[self.data['iyear'] == y]
        data = data[(data['imonth'] == m) & (data['iday'] == t+1)]
        x = data['longitude']
        y = data['latitude']
        self.scatter = self.map.scatter(x, y, marker='o', color=self.colors_a_1[0], s=10)
        return self.scatter,

    def map_play(self):
        print("play")
        y, m = self.get_ym()
        self.year.display(y)
        self.month.display(m)
        if m == 1 or m == 3 or m == 5 or m == 7 or m == 8 or m == 10 or m == 12:
            frame = 31
        elif m == 2:
            if y % 4 == 0 and y % 100 != 0:
                frame = 29
            else:
                frame = 28
        else:
            frame = 30
        if self.speed.value() == 2:
            sp = 50
        elif self.speed.value() == 1:
            sp = 500
        else:
            sp = 1000

        self.anim = animation.FuncAnimation(self.F.fig, self.map_upd, frames=frame, interval=sp, blit=True,
                                            repeat=False)

    def plot_success(self, type=0):
        print(">>>plot")
        self.pre = 'success'
        self.F = MyFigure()
        self.figure.addWidget(self.F)
        self.F.axes = self.F.fig.add_subplot(211)
        x = ['succeed', 'failed']                   # 首先数量从0开始绘图
        y = self.curheight

        self.bars = self.F.axes.bar(x, y, animated=True, color=[self.colors[0], self.colors[1]])
        self.F.axes.set_ylim([0, 15000])           # 设置动画，bar往上运动，直到达到上限，总共80帧，每帧0.0001ms
        self.F.axes.grid(True, linestyle='-.')
        self.F.axes.set_ylabel('number of cases')

        year, _ = self.get_ym()
        years = [i for i in range(1970, 2018)]
        s = []
        f = []
        for y in years:
            try:
                data = self.data[self.data['iyear']==y]
                success_num = data['success'].value_counts()[1]
                fail_num = data['success'].value_counts()[0]
                s.append(success_num)
                f.append(fail_num)
            except:
                s.append(0)
                f.append(0)
        self.F.axes1 = self.F.fig.add_subplot(212)
        self.F.axes1.plot(years, s, c=self.colors_a_1[0], marker='^')
        self.F.axes1.plot(years, f, c=self.colors_a_1[1], marker='.')
        self.F.axes1.grid(True, linestyle='-.')
        self.F.axes1.legend(['succeed', 'failed'])
        self.F.axes1.set_ylabel('number of cases')
        self.F.axes1.set_xlabel('years')
        self.F.axes1.set_xlim([1969, 2018])

        if type == 0:
            self.scatter1 = self.F.axes1.scatter(years[year - 1970], s[year - 1970],
                                                 c=self.colors_a_1[0],
                                                 marker='*', s=200)
            self.scatter2 = self.F.axes1.scatter(years[year - 1970], f[year - 1970],
                                                 c=self.colors_a_1[1],
                                                 marker='*', s=200)
            self.anim = animation.FuncAnimation(self.F.fig, self.success_upd, frames=160, interval=0.0001, blit=True, repeat=False)
        else:
            print(self.speed.value())
            if self.speed.value() == 2:
                sp = 1
            elif self.speed.value() == 1:
                sp = 25
            else:
                sp = 50
            self.scatter1 = self.F.axes1.scatter(years[year - 1970], s[year - 1970], animated=True,
                                                 c=self.colors_a_1[0],
                                                 marker='*', s=200)
            self.scatter2 = self.F.axes1.scatter(years[year - 1970], f[year - 1970], animated=True,
                                                 c=self.colors_a_1[1],
                                                 marker='*', s=200)
            y, _ = self.get_ym()
            self.data_iter = self.get_data(y)
            self.data_iter1 = self.get_data(y)
            self.frame = (2017-y+1) * 100/2
            print(self.frame)
            print(sp)
            self.anim = animation.FuncAnimation(self.F.fig, self.play_success, frames=int(self.frame), interval=sp, blit=True, repeat=False)
            self.anim1 = animation.FuncAnimation(self.F.fig, self.scatter_upd, frames=int(self.frame), interval=sp, blit=True, repeat=False)

    def plot_attacktype(self):
        data = []
        for s, e in zip(self.curangle1, self.curangle2):
            data.append((e-s)/360)
        self.F = MyFigure()
        self.figure.addWidget(self.F)
        self.F.axes = self.F.fig.add_subplot(211)
        self.pie = self.F.axes.pie(x=data, colors=self.colors)
        self.anim = animation.FuncAnimation(self.F.fig, self.attack_upd, frames=200, interval=0.01, blit=True, repeat=False)

        year, _ = self.get_ym()
        years = [i for i in range(1970, 2018)]
        tag = ['Bombing/Explosion', 'Armed Assault', 'Assassination', 'Facility/Infrastructure Attack',
               'Hostage Taking (Kidnapping)', 'Unknown', 'Unarmed Assault', 'Hostage Taking (Barricade Incident)',
               'Hijacking']
        num = [[] for i in range(len(tag))]
        for y in years:
            data = self.data[self.data['iyear']==y]
            for i, t in enumerate(tag):
                try:
                    num[i].append(data['attacktype1_txt'].value_counts()[t])
                except:
                    num[i].append(0)
        self.F.axes1 = self.F.fig.add_subplot(212)
        for i, n in enumerate(num):
            self.F.axes1.plot(years, n, c=self.colors_a_1[i], marker='.', alpha=0.5)
        self.F.axes1.grid(True, linestyle='-.')
        self.F.axes1.set_ylabel('number of cases')
        self.F.axes1.set_xlabel('years')
        for i in range(len(tag)):
            self.F.axes1.scatter(years[year-1970], num[i][year-1970], c=self.colors_a_1[i], marker='*', s=200)

    def plot_loss(self, type=0):
        self.pre = 'loss'
        print(">>>plot")
        self.F = MyFigure()
        self.figure.addWidget(self.F)
        self.F.axes1 = self.F.fig.add_subplot(311)
        self.F.axes2 = self.F.fig.add_subplot(312)
        self.F.axes3 = self.F.fig.add_subplot(313)
        num = ['10~30','30~50','50~100','>100']
        prop = ['<1', '1~1000', '>=1000']
        y1_init = self.curheight1[:]
        y2_init = self.curheight2[:]
        y3_init = self.curheight3[:]
        self.bars = self.F.axes1.barh(num, y1_init, animated=True, color=[self.colors[i] for i in range(4)])
        self.F.axes1.set_xlim([0, 1000])
        self.bars1 = self.F.axes2.barh(num, y2_init, animated=True, color=[self.colors[i] for i in range(4)])
        self.F.axes2.set_xlim([0, 1000])
        self.bars2 = self.F.axes3.barh(prop, y3_init, animated=True, color=[self.colors[i] for i in range(3)])
        self.F.axes3.set_xlim([0, 6000])
        self.F.axes1.grid(True, linestyle='-.')
        self.F.axes1.set_ylabel('number of death')
        self.F.axes1.set_xlabel('number of cases')
        self.F.axes2.grid(True, linestyle='-.')
        self.F.axes2.set_ylabel('number of injured')
        self.F.axes2.set_xlabel('number of cases')
        self.F.axes3.grid(True, linestyle='-.')
        self.F.axes3.set_ylabel('property loss extent(million dollars)')
        self.F.axes3.set_xlabel('number of cases')
        if type == 0:
            self.anim = animation.FuncAnimation(self.F.fig, self.loss_upd, frames=80, interval=0.0001, blit=True,
                                                repeat=False)
            self.anim1 = animation.FuncAnimation(self.F.fig, self.loss_upd1, frames=80, interval=0.0001, blit=True,
                                                repeat=False)
            self.anim2 = animation.FuncAnimation(self.F.fig, self.loss_upd2, frames=80, interval=0.0001, blit=True,
                                                repeat=False)
        else:
            if self.speed.value() == 2:
                sp = 1
            elif self.speed.value() == 1:
                sp = 25
            else:
                sp = 50
            y, _ = self.get_ym()
            self.data_iter = self.get_data(y)
            self.data_iter1 = self.get_data(y)
            self.data_iter2 = self.get_data(y)
            self.frame = int((2017 - y + 1) * 100 / 2)
            print(self.frame)
            self.anim = animation.FuncAnimation(self.F.fig, self.loss_play, frames=self.frame, interval=sp, blit=True,
                                                repeat=False)
            self.anim1 = animation.FuncAnimation(self.F.fig, self.loss_play1, frames=self.frame, interval=sp, blit=True,
                                                repeat=False)
            self.anim2 = animation.FuncAnimation(self.F.fig, self.loss_play2, frames=self.frame, interval=sp, blit=True,
                                                repeat=False)

    def plot_map(self):
        print(">>>plot")
        self.pre = 'map'
        self.F = MyFigure()
        self.figure.addWidget(self.F)
        self.F.axes = self.F.fig.add_subplot(111)
        self.map = Basemap(ax=self.F.axes, lat_0=0,lon_0=0)
        self.map.shadedrelief(scale=0.1)
        self.map.drawparallels(circles=np.linspace(-90, 90, 7),
                          labels=[1, 0, 0, 0], color='gray')
        self.map.drawmeridians(meridians=np.linspace(-180, 180, 13),
                          labels=[0, 0, 0, 1], color='gray')

    def plot_dynamicmap(self):
        y, m = self.get_ym()
        lon, lat = self.get_lon_lat()
        self.sub = folium_map(y, m, lon, lat)
        self.figure.addWidget(self.sub)
        self.sub.show()

    def get_ym(self):
        y = self.choose_year.value()
        m = self.choose_month.value()
        return y, m

    def get_lon_lat(self):
        lon = self.longitude.value()
        lat = self.latitude.value()
        return lon, lat

    def get_data(self, begin):
        for i in range(begin, 2018):
            yield self.data[self.data['iyear']==i], i

def make_rgb_transparent(rgb, bg_rgb, alpha):             # 将颜色转换为透明色
    return [alpha * c1 + (1 - alpha) * c2
            for (c1, c2) in zip(rgb, bg_rgb)]

def compute_md(d):
    cnt = 0
    sum = 0
    days = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    while sum < d:
        sum += days[cnt]
        cnt += 1
    else:
        sum = sum - days[cnt-1] if cnt - 1 > 0 else 0
    day = d-sum if cnt - 2 >= 0 else d
    return cnt, day

class folium_map(QMainWindow, Ui_MainWindow):
    def __init__(self, y, m, lon=-180, lat=-90):
        super(folium_map, self).__init__()
        self.setupUi(self)
        self.data = clean_data()
        self.browser = QtWebEngineWidgets.QWebEngineView()
        self.year = y
        self.month = m
        self.lon = lon
        self.lat = lat
        if self.lon != -180 and self.lat != -90:
            self.m = folium.Map(location=[self.lat, self.lon],
                            min_zoom=2.5,
                            zoom_start=6,
                            max_bounds=True,
                            tiles='http://webst02.is.autonavi.com/appmaptile?style=6&x={x}&y={y}&z={z}', # 高德卫星图
                            #tiles='https://mt.google.com/vt/lyrs=s&x={x}&y={y}&z={z}',  # google 卫星图
                            attr='default',
                            prefer_canvas=True)
        else:
            self.m = folium.Map(location=[0, 100],
                                min_zoom=2.5,
                                zoom_start=2.5,
                                max_bounds=True,
                                tiles='http://webst02.is.autonavi.com/appmaptile?style=6&x={x}&y={y}&z={z}', # 高德卫星图
                                #tiles='https://mt.google.com/vt/lyrs=s&x={x}&y={y}&z={z}',  # google 卫星图
                                attr='default',
                                prefer_canvas=True)
        self.add_mark()
        self.data = io.BytesIO()
        self.m.save(self.data, close_file=False)
        self.browser.setHtml(self.data.getvalue().decode())
        self.setCentralWidget(self.browser)

    def add_mark(self):
        print(self.year)
        print(self.month)
        data = self.data[(self.data['iyear']==self.year) & (self.data['imonth']==self.month)]
        for index, row in data.iterrows():
            succeed = 'yes' if getattr(row, 'success') else 'no'
            nkill = str(int(getattr(row, 'nkill'))) if getattr(row, 'nkill') != -1  else 'Unknown'
            nwound = str(int(getattr(row, 'nwound'))) if getattr(row, 'nwound') != -1 else 'Unknown'
            tip = '<p style="color: green">' + '<br>' + \
                   'longitude：' + str(round(getattr(row, 'longitude'), 2)) + '<br>' + \
                   'latitude：' + str(round(getattr(row, 'latitude'), 2)) + '<br>' + \
                   'city: ' + getattr(row, 'city') + '<br>' + \
                   'date: ' + str(self.year) + '.'+ str(self.month) +'.' + str(int(getattr(row, 'iday'))) + '<br>' + \
                   'succeed：' + succeed + '<br>' + \
                   'attack type: ' + getattr(row, 'attacktype1_txt') + '<br>' + \
                   'target: ' + getattr(row, 'targtype1_txt') + '<br>' + \
                   'Number of death: ' + nkill + '<br>' + \
                   'Number of injured: ' + nwound + \
                   '</p>'
            folium.Marker(location=[getattr(row, 'latitude'), getattr(row, 'longitude')],
                          tooltip=tip,
                          icon=folium.Icon(color='red')).add_to(self.m)


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    ex = main_plot()
    ex.show()
    sys.exit(app.exec_())