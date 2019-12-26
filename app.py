from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWebEngineWidgets import QWebEngineView
import Expert
import pprint
import sys


expert = None
ans_list = None

class UpWidget(QWebEngineView):
    '''结果框部件
    '''
    def __init__(self, father):
        super().__init__(father)

        with open('./css/up.html', 'r') as f:
            self.html_head = f.read()
        self.html_tail = '</body></html>'

        self.html_append = '''  <div style="text-align: center;">
                                    <div class="image">
                                        <img src="{url}" width="120" alt="没有图像记录...">
                                    </div>

                                    <div class="data-container">
                                        <div class="data">
                                            <strong>{name}</strong>
                                        </div>
                                        <div class="data">
                                            <strong>身高：</strong>{height} m<br><strong>体重：</strong>{weight} kg
                                        </div>
                                    </div>
                                </div>

                                <div class="intro">
                                        {intro}
                                </div>'''

        self.init_UI()
        
    def init_UI(self):
        self.setHtml( self.html_head 
                    + self.html_append.format(url='https://media.52poke.com/wiki/a/a6/%E5%AE%9D%E5%8F%AF%E6%A2%A6%E5%9B%BE%E9%89%B4_Pt.png',
                                              name='宝可梦图鉴',
                                              height='???',
                                              weight='???',
                                              intro='按工具栏搜索键 [开始/重新] 搜索；按记录键 [增添/覆盖] 宝可梦信息到图鉴中。')
                    + self.html_tail)

    def showPoke(self, url, name, height, weight, intro):
        url = "https://media.52poke.com/wiki/b/bb/Dream_%E8%83%86%E6%80%AF%E7%90%83_Sprite.png" if url is None else url
        height = "???" if height is None else str(height)
        weight = "???" if weight is None else str(weight)
        intro = "没有详细资料..." if intro is None or intro == '' else intro
        self.setHtml( self.html_head
                    + self.html_append.format(url=url, name=name, height=height, weight=weight, intro=intro)
                    + self.html_tail)



class DownWidget(QWebEngineView):
    '''询问框部件
    '''
    def __init__(self, father):
        super().__init__(father)

        with open('./css/down.html', 'r') as f:
            self.html_head = f.read()
        self.html_tail = '</div></body></html>'

        self.ques_head = '''<div class="LBubble-container">
                                <div class="LBubble">
                                    <p>
                                        <span class="msg">'''
        self.ques_tail = '''            </span>
                                        <span class="bottomLevel"></span>
                                        <span class="topLevel"></span>
                                    </p>
                                    <br>
                                </div>
                            </div>'''
        self.answer_head = '''  <div class="RBubble-container">
                                    <div class="RBubble">
                                        <p>
                                            <span class="msg">'''
        self.answer_tail = '''              </span>
                                            <span class="bottomLevel"></span>
                                            <span class="topLevel"></span>
                                        </p>
                                        <br>
                                    </div>
                                </div>'''

        self.append_html = ''
        self.init_UI()
        
    def init_UI(self):
        self.append_html = ''
        self.setHtml(self.html_head + self.html_tail)

    def addAns(self, msg):
        self.append_html += self.answer_head + msg + self.answer_tail
        self.__refresh()


    def addQues(self, msg):
        self.append_html += self.ques_head + msg + self.ques_tail
        self.__refresh()

    def __refresh(self):
        self.setHtml(self.html_head + self.append_html + self.html_tail)



class MainWidget(QWidget):
    '''主部件

    负责安排各部件的布局
    '''
    def __init__(self, father):
        super().__init__(father)
        self.up_widget = UpWidget(self)
        self.down_widget = DownWidget(self)
        self.sld = QSlider(Qt.Horizontal, self)
        self.current_key = ''
        self.current_val = ''
        self.turn_num = 0
        self.isJudge = True
        self.isDone = True
        self.initUI()

    def clean_all(self):
        self.sld.setValue(0)
        self.turn_num = 0
        self.isJudge = False
        self.isDone = False


    def initUI(self):                 
        # 布局
        vbox = QVBoxLayout()
        vbox.addWidget(self.up_widget, stretch=5)
        vbox.addWidget(self.down_widget, stretch=5)

        hbox = QHBoxLayout()
        submitButton = QPushButton()
        submitButton.setStyleSheet( "QPushButton{width:25px; height:25px; border-image: url(./image/ok.ico)}"
                                    "QPushButton:hover{border-image: url(./image/ok_h.ico)}"
                                    "QPushButton:pressed{border-image: url(./image/ok_h.ico)}")
        submitButton.clicked.connect(self.submit)

        self.sld.setFocusPolicy(Qt.NoFocus)
        # self.sld.valueChanged[int].connect(self.changeValue)

        hbox.addStretch(1)
        hbox.addWidget(self.sld, stretch=12)
        hbox.setSpacing(20)
        hbox.addWidget(submitButton)
        hbox.addStretch(1)

        vbox.addLayout(hbox)
        self.setLayout(vbox) 
        self.show()


    def submit(self):
        '''循环问答
        '''
        if self.isDone: # 任务结束状态
            return

        self.turn_num += 1
        val = self.sld.value()
        cf = val / 100 * 2 - 1
        print(f'用户确信度:{cf}')
        if self.isJudge: # 评判状态
            self.judge(cf)
            return

        global expert
        ans = expert.get_language_ans(cf)
        self.down_widget.addAns(ans)
        expert.update_pokemons_cf(self.current_key, self.current_val, cf)
        if not expert.enough(self.turn_num):
            next_ques, self.current_key, self.current_val = expert.get_next_question()
            self.down_widget.addQues(next_ques)
        else:
            global ans_list
            ans_list = expert.get_ans_list()
            self.down_widget.addQues('特征收集完毕')
            # 展示宝可梦
            self.refresh_ans()
            self.isJudge = True


    def refresh_ans(self):
        global ans_list
        # 展示宝可梦
        if ans_list is None or len(ans_list) == 0:
            self.down_widget.addQues("图鉴中没有这只宝可梦...快记录新精灵吧～")
            self.isDone = True
            return
        else:
            ans_cf, name, url, height, weight, intro = ans_list[0]
            self.up_widget.showPoke(url, name, height, weight, intro)
            self.display_track(name, ans_cf)
            self.down_widget.addQues('是这只宝可梦吗？')


    def display_track(self, name, cf):
        global expert
        trace_list = list()
        trace_list.append(f'<strong>{name} {round(cf, 3)}</strong>')
        for judgement, delta in expert.get_track_box(name):
            prefix = '<strong style="color:red;">+' if delta >= 0 else '<strong style="color:blue;">'
            suffix = '</strong>'
            trace_list.append(f'{judgement}  {prefix}{round(delta, 3)}{suffix}')
        self.down_widget.addQues('<br>'.join(trace_list))


    def judge(self, cf):
        global ans_list
        if cf > 0:
            self.down_widget.addQues("搜索完成～")
            self.isDone = True
        elif ans_list is None or len(ans_list) <= 1:
            self.down_widget.addQues("图鉴中没有这只宝可梦...快记录新精灵吧～")
            self.isDone = True
        else:
            ans_list.pop(0)
            self.refresh_ans()



class MainWin(QMainWindow):
    '''主界面
    '''
    def __init__(self):
        super().__init__()
        # 初始化主窗口
        self.main_widget = MainWidget(self)
        self.setCentralWidget(self.main_widget)
        self.adder = AdderWidget()
        global expert
        expert = Expert.Expert()
        self.initUI()

    def initUI(self):
        # 基本信息
        self.setGeometry(480, 160, 345, 555)
        self.setWindowTitle('宝可梦图鉴')    
        self.setStyleSheet("QMainWindow {background: #EF2929;}")

        # 重新搜索
        searchAct = QAction(QIcon('./image/search.ico'), 'Search a pokemon', self)
        searchAct.setShortcut('Ctrl+S')
        searchAct.triggered.connect(self.search)
        self.toolbar = self.addToolBar('Search a pokemon') # 直接退出
        self.toolbar.addAction(searchAct)

        # 增加图鉴
        addAct = QAction(QIcon('./image/add.ico'), 'Add a pokemon', self)
        addAct.setShortcut('Ctrl+A')
        addAct.triggered.connect(self.add)
        self.toolbar = self.addToolBar('Add a pokemon') # 直接退出
        self.toolbar.addAction(addAct)

        self.show()


    def search(self):
        # 清空界面 重置专家
        self.main_widget.up_widget.init_UI()
        self.main_widget.down_widget.init_UI()
        self.main_widget.clean_all()
        global expert, ans_list
        del expert
        expert = Expert.Expert()
        ans_list = None
        # 第一个问题
        ques, self.main_widget.current_key, self.main_widget.current_val = expert.get_next_question()
        self.main_widget.down_widget.addQues(ques)
        

    def add(self):
        self.adder.show()
        pass


class AdderWidget(QWidget):
    '''记录界面

    增添新宝可梦信息到数据库中
    '''
    def __init__(self):
        super().__init__()

        self.init_UI()
        
    def init_UI(self):
    
        self.setWindowTitle('Record New Pokemon')
        self.setGeometry(450, 260, 400, 350)
        self.setStyleSheet("AdderWidget{background-color:#404040;}")

        self.nameLine = QLineEdit(self)
        self.nameLine.setPlaceholderText('宝可梦名字')
        self.colorLine = QLineEdit(self)
        self.colorLine.setPlaceholderText('整体颜色(多种用空格隔开)')
        self.eyeLine = QLineEdit(self)
        self.eyeLine.setPlaceholderText('眼睛颜色(多种用空格隔开)')
        self.earLine = QLineEdit(self)
        self.earLine.setPlaceholderText('耳朵颜色(多种用空格隔开)')
        self.limbLine = QLineEdit(self)
        self.limbLine.setPlaceholderText('手和脚的个数')
        self.wingLine = QLineEdit(self)
        self.wingLine.setPlaceholderText('翅膀个数')
        self.habitatLine = QLineEdit(self)
        self.habitatLine.setPlaceholderText('栖息地(多种用空格隔开)')
        self.detailLine = QLineEdit(self)
        self.detailLine.setPlaceholderText('细节特点')
        self.superClassLine = QLineEdit(self)
        self.superClassLine.setPlaceholderText('所属类')
        self.urlLine = QLineEdit(self)
        self.urlLine.setPlaceholderText('图片源(网址)')
        self.introLine = QLineEdit(self)
        self.introLine.setPlaceholderText('简介')
        self.heightLine = QLineEdit(self)
        self.heightLine.setPlaceholderText('身高(m)')
        self.weightLine = QLineEdit(self)
        self.weightLine.setPlaceholderText('体重(kg)')
        self.Btn = QPushButton('写入', self)
        self.Btn.clicked.connect(self.writeInRepo)

        hbox1 = QHBoxLayout()
        hbox1.addWidget(self.nameLine)
        hbox1.addWidget(self.heightLine)
        hbox1.addWidget(self.weightLine)

        hbox2 = QHBoxLayout()
        hbox2.addWidget(self.limbLine)
        hbox2.addWidget(self.wingLine)
        hbox2.addWidget(self.superClassLine)

        hbox3 = QHBoxLayout()
        hbox3.addWidget(self.colorLine)
        hbox3.addWidget(self.habitatLine)

        hbox4 = QHBoxLayout()
        hbox4.addWidget(self.eyeLine)
        hbox4.addWidget(self.earLine)


        hbox5 = QHBoxLayout()
        hbox5.addWidget(self.detailLine)
        hbox5.addWidget(self.urlLine)

        hbox6 = QHBoxLayout()
        hbox6.addWidget(self.introLine)
        hbox6.addWidget(self.Btn)

        vbox = QVBoxLayout()
        vbox.addLayout(hbox1)
        vbox.addLayout(hbox2)
        vbox.addLayout(hbox3)
        vbox.addLayout(hbox4)
        vbox.addLayout(hbox5)
        vbox.addLayout(hbox6)
        

        self.setLayout(vbox)



    def writeInRepo(self):
        '''name color eye-color ear-color limb_num wing_num habitat detail super_class url intro height weight
        '''
        if self.nameLine.text() == '':
            QMessageBox.warning(self, "Warning", "宝可梦名字不能为空")
            return
        global expert
        expert.update_pokemon([ self.nameLine.text(), self.colorLine.text(), self.eyeLine.text(),
                                self.earLine.text(), self.limbLine.text(), self.wingLine.text(),
                                self.habitatLine.text(), self.detailLine.text(), self.superClassLine.text(),
                                self.urlLine.text(), self.introLine.text(), self.heightLine.text(),
                                self.weightLine.text()])
        QMessageBox.information(self, "success", "写入成功")
        self.close()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    PokemonMap = MainWin()
    app.exec_()