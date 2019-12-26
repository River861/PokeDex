import sqlite3
import pprint
import math
import Pokemon


conn = sqlite3.connect('./data/Pokemon.db', check_same_thread=False)
cursor = conn.cursor()


class Expert:
    '''专家类 维护了pokemons字典
    '''

    def __init__(self):
        self.__feature_list = ['name', 'color', 'eye_color', 'ear_color', 'limb_num', 'wing_num', 'habitat', 'detail', 'super_class', 'url', 'intro', 'height', 'weight']
        self.__father_feature_list = ['limb_num', 'wing_num', 'detail']
        self.pokemons = dict()
        self.__load_pokemons()

    def __load_pokemons(self):
        global conn, cursor
        LOAD_ALL_SQL = "select " + ','.join(self.__feature_list) + " from InstanceFeature"
        cursor.execute(LOAD_ALL_SQL)
        results = cursor.fetchall()
        for row in results:
            poke = Pokemon.Pokemon(name=row[0], url=row[-4], intro=row[-3], height=row[-2], weight=row[-1])
            # 先加载加载父类槽值
            LOAD_FATHER_SQL = "select " + ','.join(self.__father_feature_list) + f" from ClassFeature where name='{row[-5]}' "
            cursor.execute(LOAD_FATHER_SQL)
            res = cursor.fetchone()
            if res is not None:
                for index, col in enumerate(res):
                    poke.init_slot(self.__father_feature_list[index], col)

            # 再加载子类槽值
            for index, col in enumerate(row[1:-5], start=1):
                poke.init_slot(self.__feature_list[index], col)

            self.pokemons[poke.name] = poke

        # for poke in self.pokemons.values():
        #     poke.debug()


    def update_pokemon(self, info_list):
        '''name color eye-color ear-color limb_num wing_num habitat detail super_class url intro height weight
        '''
        global conn, cursor
        val_list = ["Null" if info == '' else f"'{info}'" for info in info_list]
        SELECT_SQL = f'''select count(*)
                        from InstanceFeature
                        where name == {val_list[0]} '''
        cursor.execute(SELECT_SQL)
        res = cursor.fetchone()[0]
        if res == 0:
            INSERT_SQL = f'''insert into InstanceFeature values({','.join(val_list)})'''
            cursor.execute(INSERT_SQL)
            conn.commit()
        else:
            set_list = list()
            for key, val in zip(self.__feature_list[1:], val_list[1:]):
                set_list.append(key + '=' + val)
            UPDATE_SQL = f'''update InstanceFeature
                             set {','.join(set_list)}
                             where name = {val_list[0]} '''
            cursor.execute(UPDATE_SQL)
            conn.commit()


    def get_ans_list(self):
        '''获取结果列表 按可能性从大到小排列

        每个结果包含四元组(cf, name, 身高, 体重, 简介)
        '''
        ans, cf = None, 0
        cf_list = list()
        for poke in self.pokemons.values():
            cf_list.append((poke.cf, poke.name, poke.url, poke.height, poke.weight, poke.intro))
            if poke.cf > cf:
                ans = poke
                cf = poke.cf
        # pprint.pprint(sorted(cf_list))
        # print("Best-fit is:")
        # ans.debug() 
        return sorted(cf_list, key=lambda x:x[0], reverse=True)




    def __calculate_info(self, key, val):
        '''计算信息熵
        '''
        p_yes = 0.0
        p_no = 0.0
        info_yes = 0.0
        info_no = 0.0
        entr_yes = 0.0
        entr_no = 0.0
        
        for poke in self.pokemons.values():
            if poke.have_key_val(key, val): 
                p_yes += pow(math.e, poke.cf)             # 用户给出Yes回答的概率
            else:
                p_no += pow(math.e, poke.cf)              # 用户给出No 回答的概率
                
        for poke in self.pokemons.values():
            new_p = poke.new_cf(key, val, cf=1.0) 
            info_yes += pow(math.e, new_p)
            new_p = poke.new_cf(key, val, cf=-1.0)  
            info_no += pow(math.e, new_p)
        
        for poke in self.pokemons.values():
            new_p = poke.new_cf(key, val, cf=1.0) 
            p = pow(math.e, new_p) / info_yes              # 若用户给出Yes回答后，每个pokemon的概率
            entr_yes -= p * math.log2(p)
            new_p = poke.new_cf(key, val, cf=-1.0)
            p = pow(math.e, new_p) / info_no               # 若用户给出No 回答后，每个pokemon的概率
            entr_no -= p * math.log2(p)
        
        return (entr_yes * p_yes + entr_no * p_no) / (p_yes + p_no + 1e-6)
    
        
    def next_question(self) :
        key_chosen = val_chosen = ''
        min_entrophy = math.inf
        for key in self.__feature_list[1:-5]:
            for val in Pokemon.val_box[key]:
                info = self.__calculate_info(key, val)
                if info < min_entrophy:
                    min_entrophy = info
                    key_chosen = key
                    val_chosen = val
        Pokemon.val_box[key_chosen].remove(val_chosen)
        return key_chosen, val_chosen

    def get_next_question(self):
        '''形成问题
        '''
        key, val = self.next_question()
        return Pokemon.question_box[key].format(val=val), key, val


    def get_language_ans(self, cf):
        '''形成语言应答
        '''
        if cf <= -0.5:
            return '才不是！'
        elif cf < 0:
            return '好像不是...'
        elif cf < 0.5:
            return '有点像...'
        else:
            return '对的！'

    def update_pokemons_cf(self, key, val, cf):
        del_list = list()
        for poke in self.pokemons.values():
            poke.update_cf(key, val, float(cf))
            if poke.is_out():
                del_list.append(poke.name)
                # print(f'{poke.name} is out')
                if len(self.get_track_box(poke.name)) >= 5:
                    print(poke.name)
                    pprint.pprint(self.get_track_box(poke.name))
        for name in del_list:
            self.pokemons.pop(name)

    def enough(self, turn_num):
        '''结束条件
        '''
        # return turn_num >= 15
        return len(self.pokemons) <= 1 or turn_num >= 10


    def get_track_box(self, name):
        return self.pokemons[name].track_box



    def play(self, n=8):
        for _ in range(n):
            if len(self.pokemons) < 5:
                return self.get_ans()

            key, val = self.next_question()
            cf = input(Pokemon.question_box[key].format(val=val)) # 绝对不是：-1 好像不是 -0.5 有点像：0.5 很确信：1
            del_list = list()
            for poke in self.pokemons.values():
                poke.update_cf(key, val, float(cf))
                if poke.is_out():
                    del_list.append(poke.name)
            for name in del_list:
                self.pokemons.pop(name)

        return self.get_ans_list()


if __name__ == '__main__':
    expert = Expert()
    pprint.pprint(expert.play())
