import pprint

val_box = {
    'color': set(),
    'eye_color': set(),
    'ear_color': set(),
    'limb_num': set(),
    'wing_num': set(),
    'habitat': set(),
    'detail': set(),
}

question_box = {
    'color': '它的身体是不是有{val}的部分？',
    'eye_color': '它的眼睛是{val}的吗？',
    'ear_color': '它的耳朵是{val}的吗？',
    'limb_num': '它一共有{val}只手和脚吗？',
    'wing_num': '它是不是有{val}只翅膀？',
    'habitat': '它是不是生活在{val}附近？',
    'detail': '它是不是{val}？',
}


format_box = {
    'color':     '皮肤颜色',
    'eye_color': '眼睛颜色',
    'ear_color': '耳朵颜色',
    'limb_num':  '手脚个数',
    'wing_num':  '翅膀个数',
    'habitat':   '栖息地点',
    'detail':    '显著特征',
}


class Pokemon:
    '''每个pokemon维护一个框架
    
    每个框架都可以导出后项为该pokemon的若干规则
    '''
    def __init__(self, name, url, height, weight, intro):
        '''框架的所有槽值
        '''
        self.cf = 0.0
        self.name = name
        self.url = url       # 图片网址
        self.intro = intro   # 图鉴介绍
        self.height = height   # 身高
        self.weight = weight   # 体重
        self.track_box = []  # 搜索过程: (key, val, cf变化量)
        self.slot = {
            'color': dict(),
            'eye_color': dict(),
            'ear_color': dict(),
            'limb_num': dict(),
            'wing_num': dict(),
            'habitat': dict(),
            'detail': dict(),
        }
        self.false_cnt = 0
        self.cnt = 0

    def init_slot(self, mark, text):
        '''从外部库中导入数据，并赋予相应规则的确信因子

        隐式地形成了规则集
        '''
        if text is None:
            return

        cf = [0.4, 0.3, 0.2, 0.2, 0.2]
        for index, val in enumerate(text.split(' ')):
            if index < 5 and val != '':
                val_box[mark].add(val)
                if mark == 'detail':
                    self.slot[mark][val] = 0.9
                else:
                    self.slot[mark][val] = cf[index]
        # print(f'color:{len(val_box["color"])}')
        # print(f'eye_color:{len(val_box["eye_color"])}')
        # print(f'ear_color:{len(val_box["ear_color"])}')
        # print(f'limb_num:{len(val_box["limb_num"])}')
        # print(f'wing_num:{len(val_box["wing_num"])}')
        # print(f'habitat:{len(val_box["habitat"])}')
        # print(f'detail:{len(val_box["detail"])}')


    def debug(self):
        print(self.name)
        pprint.pprint(self.slot)
        pprint.pprint(self.track_box)


    def update_cf(self, key, val, cf) :
        # 更新cf值
        new_cf = self.__merge_cf(self.cf, self.new_cf(key, val, cf))
        # 记录track
        if cf <= 0:
            self.track_box.append((f'{format_box[key]} 不是 {val}', new_cf - self.cf))
        else:
            self.track_box.append((f'{format_box[key]} &nbsp;&nbsp;是&nbsp;&nbsp; {val}', new_cf - self.cf))

        self.cf = new_cf
        self.cnt += 1
        if self.cf < 0.5:
            self.false_cnt += 1

    def new_cf(self, key, val, cf):
        '''IF color IS 黄色{cf}
           THEN IS 皮卡丘{self.slot[key][val]}
        '''
        if len(self.slot[key]) == 0:
            return 0 * cf
        elif val not in self.slot[key]:
            if cf >= 0:
                if key == 'detail':
                    return -1.0 * cf
                return -0.7 * cf
            else:
                if key == 'detail':
                    return 0 * cf
                return -0.3 * cf
        else :
            if key == 'detail':
                return 0.9 * cf
            elif cf >= 0:
                return self.slot[key][val] * cf # 0.4 0.3
            else:
                return (self.slot[key][val] + 0.3) * cf # 0.7 0.6


    def have_key_val(self, key, val):
        return len(self.slot[key]) != 0 and val in self.slot[key]


    def is_out(self) :
        if self.false_cnt > 2:# or (self.cnt > 5 and self.false_cnt > 1) :
            return True
        return False


    def __merge_cf(self, cf1, cf2):
        if cf1 > 0 and cf2 > 0:
            return cf1 + cf2 * (1 - cf1)
        elif cf1 < 0 and cf2 < 0:
            return cf1 + cf2 * (1 + cf1)
        else:
            return (cf1 + cf2) / (1 - min(abs(cf1), abs(cf2)) + 1e-6)  