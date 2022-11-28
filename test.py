import pyxel
import webbrowser

SCENE_TITLE = 0 #タイトル画面
SCENE_PLAY = 1 #プレー画面
SCENE_GAMEOVER = 2 #ゲームオーバー画面

BUTTON_X = 44 #ボタンのx軸
BUTTON_Y = 115 #ボタンのy軸

peace_count = 0 #電車が事故せずに走ったフレーム数
peaceful_time = 0 #電車が事故せずに走った時間

SHINKSEN = 6 #新幹線が登場する時間
HAYABUSA = 20 #はやぶさが登場する時間
CHICK_FRAME_COUNT = 60 #ひよこが登場するフレームカウント数
CHICKEN_TIME = 12 #ニワトリが登場する時間

BLAST_START_RADIUS = 1
BLAST_END_RADIUS = 8
BLAST_COLOR_IN = 7
BLAST_COLOR_OUT = 10

## 関数の定義
#サイレンの描画
def draw_siren(x,y):
    if pyxel.frame_count % 6 == 0 and 3:
        pyxel.blt(x,y,0,0,64,16,8,0)
    elif pyxel.frame_count % 6 == 1:
        pyxel.blt(x,y,0,16,64,16,8,0)
    elif pyxel.frame_count % 6 == 2:
        pyxel.blt(x,y,0,16,72,16,8,0)
    elif pyxel.frame_count % 6 == 4:
        pyxel.blt(x,y,0,32,64,16,8,0)
    elif pyxel.frame_count % 6 == 5:
        pyxel.blt(x,y,0,32,72,16,8,0)

#当たり判定
def hit_judge(animal,train):
    hit_place_x = False #横方向
    hit_place_y = False #縦方向
    if animal.x < train.x < animal.x+animal.w and train.y < animal.y+animal.h and animal.y < train.y+train.h: #電車の左横にぶつかったとき
        hit_place_x = True

    if animal.x < train.x+train.w < animal.x+animal.w and train.y < animal.y+animal.h and animal.y < train.y+train.h: #電車の右横
        hit_place_x = True

    if animal.y < train.y < animal.y+animal.h and train.x < animal.x+animal.w and animal.x < train.x+train.w: #電車の上
        hit_place_y = True

    if animal.y < train.y+train.h < animal.y+animal.h and train.x < animal.x+animal.w and animal.x < train.x+train.w: #電車の下
        hit_place_y = True

    return hit_place_x, hit_place_y

## クラスの定義
#爆発の描画
class Blast:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = BLAST_START_RADIUS
        self.is_alive = True

    def update(self):
        self.radius += 1
        if self.radius > BLAST_END_RADIUS:
            self.is_alive = False

    def draw(self):
        pyxel.circ(self.x, self.y, self.radius, BLAST_COLOR_IN)
        pyxel.circb(self.x, self.y, self.radius, BLAST_COLOR_OUT)

class Train:
    def __init__(self, x, y, u, v, w, h, s, d):
        self.x = x #画面上における電車のx座標
        self.y = y #画面上における電車のy座標
        self.u = u #イメージバンクにおける電車のx座標
        self.v = v #イメージバンクにおける電車のy座標
        self.w = w #車体の幅
        self.h = h #車体の高さ
        self.dir_x = 1 #x軸の進行方向
        self.dir_y = 1 #y軸の進行方向
        self.speed_init = s #初期スピード
        self.speed = s #スピード
        self.d = d #x軸方向に進むか、y軸方向に進むか
        # self.stop = False

    def update(self):
        if self.d == 'x': #x軸方向に進むとき
            self.x += self.speed * self.dir_x
            if self.x+self.w < pyxel.width*(-0.3) or pyxel.width * 1.3 < self.x: #横方向にはみ出たら反転
                self.dir_x *= -1
        elif self.d == 'y': #y軸方向に進むとき
            self.y += self.speed * self.dir_y
            if self.y+self.h < pyxel.height*(-0.3) or pyxel.height * 1.3 < self.y: #縦方向にはみ出たら反転
                self.dir_y *= -1 #反転
                if pyxel.rndi(0,1) == 0: #横にずれる
                    self.x = pyxel.rndi(0,BUTTON_X-self.w) #ボタンよりも左の範囲の中でランダム
                else:
                    self.x = pyxel.rndi(BUTTON_X+32, pyxel.width-self.w) #ボタンよりも右の範囲の中でランダム

    def speed_down(self):
        self.speed = max(0, self.speed-1)

    def speed_up(self):
        self.speed = min(self.speed_init, self.speed+1)

    def draw(self):
        pyxel.blt(self.x, self.y, 0, self.u, self.v, self.w * self.dir_x, self.h * self.dir_y, 0)

class Animal:
    def __init__(self, x, y, u, v, w, h, s):
        self.x = x #画面上における動物のx座標
        self.y = y #画面上における動物のy座標
        self.u = u #イメージバンクにおける動物のx座標
        self.v = v #イメージバンクにおける動物のy座標
        self.w = w #動物の幅
        self.h = h #動物の高さ
        self.dir_x = 1 #x軸の進行方向
        self.dir_y = 1 #y軸の進行方向
        self.speed = s #スピード
        self.hit_place_x = False #Trueのとき,横方向にぶつかった
        self.hit_place_y = False #Trueのとき,縦方向にぶつかった
        self.is_alive = True #生死判定

    def update(self):
        self.x += self.speed * self.dir_x
        self.y += self.speed * self.dir_y

        if self.x < 0 or pyxel.width < self.x + self.w: #横方向にはみ出たら反転
            self.dir_x *= -1

        if self.y < 0 or pyxel.height < self.y + self.h: #縦方向にはみ出たら反転
            self.dir_y *= -1

        if self.x < BUTTON_X < self.x+self.w and BUTTON_Y < self.y+self.h and self.y < BUTTON_Y+40: #ボタンの左横にぶつかったら反転
            self.dir_x *= -1

        if self.x < BUTTON_X+32 < self.x+self.w and BUTTON_Y < self.y+self.h and self.y < BUTTON_Y+40: #ボタンの右横にぶつかったら反転
            self.dir_x *= -1

        if BUTTON_X < self.x+self.w and self.x < BUTTON_X+32 and self.y < BUTTON_Y < self.y+self.h: #ボタンの上にぶつかったら反転
            self.dir_y *= -1

        if BUTTON_X < self.x+self.w and self.x < BUTTON_X+32 and self.y < BUTTON_Y+40 < self.y+self.h: #ボタンの下にぶつかったら反転
            self.dir_y *= -1

    def draw(self):
        pyxel.blt(self.x, self.y, 0, self.u, self.v, self.w * self.dir_x, self.h, 0)

class App:
    '''初期化'''
    def __init__(self,x,y): #初期化
        self.x = x #画面の横幅
        self.y = y #画面の縦幅
        pyxel.init(self.x, self.y, title="Emergency Button", fps=20) #ウィンドウサイズとタイトルを指定
        pyxel.load("assets/my_resource.pyxres") #データの読み込み
        pyxel.mouse(visible=True) #カーソルの可視化

        self.scene = SCENE_TITLE #シーン選択
        self.button = False #ボタンが押されているかどうかの判定
        self.is_alive = True #事故の有無（Falseで事故有り）

        self.train = Train(0,40,1,40,10,10,2,'x') #電車のインスタンス化
        self.train2 = Train(-25,84,13,43,21,6,6,'x') #新幹線のインスタンス化
        self.train3 = Train(10,-16,35,40,7,15,6,'y') #はやぶさのインスタンス化
        self.trains = [self.train,self.train2,self.train3] #電車のリスト

        self.chick = Animal(pyxel.rndi(0,pyxel.width-10),pyxel.rndi(0,20),1,56,6,6,1) #ひよこのインスタンス化 #rndi(a,b) a以上b以下のランダムな整数
        self.chicken = Animal(pyxel.rndi(0,pyxel.width-10),pyxel.rndi(90,100),8,56,7,8,1) #ニワトリのインスタンス化
        self.animals = [self.chick,self.chicken]#動物のリスト

        self.peace_count = peace_count #ボタンを押していないフレーム数
        self.peaceful_time = peaceful_time #ボタンを押していない時間
        self.final_score = 0 #最終的なスコア

        pyxel.run(self.update, self.draw) #アプリの実行

    '''フレームの更新'''
    def update(self): #フレームの更新処理
        #終了処理
        if pyxel.btnp(pyxel.KEY_Q): #そのフレームに"Q"が押されたらTrue、押されなければFalseを返す。
            # print(pyxel.frame_count)
            pyxel.quit() #アプリの終了

        #シーンごとに更新処理を切り替え
        if self.scene == SCENE_TITLE:
            self.update_title_scene()
        elif self.scene == SCENE_PLAY:
            self.update_play_scene()
        elif self.scene == SCENE_GAMEOVER:
            self.update_gameover_scene()

    def update_title_scene(self):
        self.button_operation() #ボタン操作
        self.siren_operation() #サイレンの操作
        if pyxel.frame_count == CHICK_FRAME_COUNT:
            self.scene = SCENE_PLAY

    def update_play_scene(self):
        self.button_operation() #ボタン操作
        self.bgm_operation() #BGMの操作
        self.siren_operation() #サイレンの操作
        self.hit_operation() #動物と電車が当たった時の操作
        self.blast_sound_operation() #爆発音の操作
        self.train_speed_operation() #電車の速度調整処理
        self.train_operation() #電車の更新処理
        self.animal_operation() #動物の更新処理
        self.score_operation() #スコア更新処理
        self.blast_operation() #爆発処理

    def update_gameover_scene(self):
        self.hit_operation() #動物と電車が当たった時の操作
        self.train_speed_operation() #電車の速度調整処理
        self.train_operation() #電車の更新処理
        self.animal_operation() #動物の更新処理
        self.blast_operation() #爆発処理
        self.restart_operation() #リスタート処理
        self.link_operation() #リンクに飛ぶ処理

    '''update関数集'''
    def button_operation(self): #ボタン操作の関数（ボタンを押し続けているとself.button=True)
        if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT): #クリック
            if BUTTON_X + 3 < pyxel.mouse_x < BUTTON_X + 29 and BUTTON_Y + 8 < pyxel.mouse_y < BUTTON_Y + 37: #ボタンの枠内
                self.button = True

        if pyxel.btnr(pyxel.MOUSE_BUTTON_LEFT): #クリックが離されたとき
            self.button = False

    def bgm_operation(self): #BGM操作の関数
        pyxel.play(0,2, loop=True)

    def siren_operation(self): #サイレン音の操作の関数
        if self.button:
            pyxel.play(0,1)

    def blast_sound_operation(self): #爆発音の操作の関数
        if self.is_alive == False:
            pyxel.play(0,0) #爆発音を流す

    def hit_operation(self): #動物と電車が当たった時の操作（当たったときに進行方向を反転するか、爆発する）の関数
        for animal in self.animals:
            for train in self.trains:
                animal.hit_place_x, animal.hit_place_y = hit_judge(animal,train) #当たった場所
                if animal.hit_place_x or animal.hit_place_y: #当たっているとき
                    if self.button and train.speed<=0: #かつボタンが押されて、電車のスピードが0以下のとき
                        if animal.hit_place_x: #左右に当たったらx軸反転
                            animal.dir_x *= -1
                        if animal.hit_place_y: #上下に当たったらy軸反転
                            animal.dir_y *= -1

                    else: #そうでないとき（当たっていて、ボタンが押されていないとき、あるいは電車のスピードが0でないとき）
                        self.blast = Blast(animal.x + animal.w/2,animal.y + animal.h/2) #爆発のインスタンス化
                        self.is_alive = False #事故あり
                        animal.is_alive = False #動物の生死判定
                        self.final_score = self.peaceful_time
                        self.scene = SCENE_GAMEOVER #GAMEOVERのシーン

    def train_speed_operation(self): #電車の速度調節の関数
        if self.button: #ボタンが押されているとき減速
            for train in self.trains:
                train.speed_down()
        else: #ボタンが離されているとき加速or定速
            for train in self.trains:
                train.speed_up()

    def train_operation(self): #電車の更新処理の関数
        self.train.update() #電車の更新
        if self.peaceful_time > SHINKSEN:
            self.train2.update() #新幹線の更新
        if self.peaceful_time > HAYABUSA:
            self.train3.update()

    def score_operation(self): #スコア更新処理の関数
        if not self.button: #ボタンが押されていないとき
            self.peace_count += 1
            self.peaceful_time = self.peace_count // 20 #事故を起こしていない秒数

    def animal_operation(self): #動物の更新処理の関数
        #ひよこの登場
        self.chick.update() #ひよこの更新
        #ニワトリの登場
        if self.peaceful_time >= CHICKEN_TIME:
            self.chicken.update() #ニワトリの更新

    def blast_operation(self): #爆発処理の関数
        if not self.is_alive: #事故したとき
            if self.blast.is_alive: #爆発がTrueのとき
                self.blast.update()

    def link_operation(self): #リンクに飛ぶための関数
        if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT): #クリック
            if 1 <= pyxel.mouse_x <= 17 and 143 <= pyxel.mouse_y <= 159: #ボタンの枠内
                #ツイート用のリンク
                webbrowser.open(f'https://twitter.com/intent/tweet?text=%E7%B7%8A%E6%80%A5%E9%9D%9E%E5%B8%B8%E5%81%9C%E6%AD%A2%E3%83%9C%E3%82%BF%E3%83%B3%E3%82%B2%E3%83%BC%E3%83%A0%0A%E3%82%B9%E3%82%B3%E3%82%A2%E3%81%AF{self.final_score}%E3%81%A7%E3%81%97%E3%81%9F%EF%BC%81%0Ahttps://emergency-button.com/%0A%23%E9%9D%9E%E5%B8%B8%E5%81%9C%E6%AD%A2%E3%83%9C%E3%82%BF%E3%83%B3%E3%82%B2%E3%83%BC%E3%83%A0')

            #Home画面へのリンク
            if 52 <= pyxel.mouse_x <= 68 and 143 <= pyxel.mouse_y <= 159: #ボタンの枠内
                webbrowser.open('https://emergency-button.com/')

            #buy me a coffeeのリンク
            if 103 <= pyxel.mouse_x <= 119 and 143 <= pyxel.mouse_y <= 159: #ボタンの枠内
                webbrowser.open('https://www.buymeacoffee.com/tokoroteen')

    def restart_operation(self): #ゲームのリスタート操作の関数
        if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT): #クリック
            if 42 <= pyxel.mouse_x <= 78 and 97 <= pyxel.mouse_y <= 108: #ボタンの枠内
                self.scene = SCENE_PLAY #シーン選択
                self.button = False #ボタンが押されているかどうかの判定
                self.is_alive = True #事故の有無（Falseで事故有り）

                self.train = Train(0,40,1,40,10,10,2,'x') #電車のインスタンス化
                self.train2 = Train(-25,80,13,43,21,6,6,'x') #新幹線のインスタンス化
                self.train3 = Train(10,-16,35,40,7,15,6,'y') #はやぶさのインスタンス化
                self.trains = [self.train,self.train2,self.train3] #電車のリスト

                self.chick = Animal(pyxel.rndi(0,pyxel.width-10),pyxel.rndi(0,20),1,56,6,6,1) #ひよこのインスタンス化 #rndi(a,b) a以上b以下のランダムな整数
                self.chicken = Animal(pyxel.rndi(0,pyxel.width-10),pyxel.rndi(90,100),8,56,7,8,1) #ニワトリのインスタンス化
                self.animals = [self.chick,self.chicken]#動物のリスト

                self.peace_count = peace_count #ボタンを押していないフレーム数
                self.peaceful_time = peaceful_time #ボタンを押していない時間
                self.final_score = 0 #最終的なスコア

    '''描画'''
    def draw(self): #描画処理
        #シーンごとに更新処理を切り替え
        if self.scene == SCENE_TITLE:
            self.draw_title_scene()
        elif self.scene == SCENE_PLAY:
            self.draw_play_scene()
        elif self.scene == SCENE_GAMEOVER:
            self.draw_gameover_scene()

    def draw_title_scene(self):
        pyxel.cls(0) #画面を指定された色でクリアする（今回は黒）
        pyxel.text(51, 2, f'Peaceful Time:{self.peaceful_time}', 7) #スコア表示
        pyxel.text(30, 70, "Push the Button!", pyxel.frame_count % 16) #座標 (x, y) に"Hello, Pyxellを描画する #pyxel.frame_count % 16で色をフレームごとに変更
        self.button_draw()

    def draw_play_scene(self):
        self.draw_init()
        self.animal_draw()
        self.train_draw()
        self.button_draw()
        self.blast_draw()

    def draw_gameover_scene(self):
        self.draw_init()
        self.animal_draw()
        self.train_draw()
        self.blast_draw()
        self.gameover_draw()

    '''draw関数集'''
    def draw_init(self): #最初に描くものを決める関数
        pyxel.cls(0) #画面を指定された色でクリアする（今回は黒）
        pyxel.text(51, 2, f'Peaceful Time:{self.peaceful_time}', 7) #スコア表示
        if pyxel.frame_count < CHICK_FRAME_COUNT:
            pyxel.text(30, 70, "Push the Button!", pyxel.frame_count % 16) #座標 (x, y) に"Hello, Pyxellを描画する #pyxel.frame_count % 16で色をフレームごとに変更

    def animal_draw(self): #動物を描画する関数
        if pyxel.frame_count >= CHICK_FRAME_COUNT and self.chick.is_alive: #指定されたフレーム数以上でかつ生存判定のとき
            self.chick.draw() #ひよこ
        if self.peaceful_time >= CHICKEN_TIME and self.chicken.is_alive: #指定された時間以上でかつ生存判定のとき
            self.chicken.draw() #ニワトリ

    def train_draw(self): #電車を描画する関数
        for train in self.trains:
            train.draw()

    def button_draw(self): #ボタンとサイレンを描画する関数
        if self.button: #ボタンが押されているとき
            pyxel.blt(BUTTON_X, BUTTON_Y, 0, 32, 0, 32, 40) #ボタンの描画
            draw_siren(30,2) #サイレンの描画
        else: #押されていないとき
            pyxel.blt(BUTTON_X, BUTTON_Y, 0, 0, 0, 32, 40) #ボタンの描画

    def blast_draw(self): #爆発を描画する関数
        if not self.is_alive: #爆発がTrueのとき
            self.blast.draw()

    def gameover_draw(self): #ゲームオーバー表示，得点表示等
        if pyxel.rndi(0,2) >= 1:
            pyxel.text(46, 60, "GAME OVER", 8)
        draw_siren(20,57) #サイレンの描画
        draw_siren(87,57) #サイレンの描画
        pyxel.text(46, 70, f'Score: {self.final_score}', 7) #スコア表示

        if pyxel.frame_count % 30 >= 10:
            pyxel.text(42, 100, '- REPLAY -', 7)

        pyxel.blt(1, 143, 0, 0, 72, 16, 16) #Twitterの描画

        pyxel.blt(52, 143, 0, 0, 104, 16, 16) #ホームアイコンの描画

        # pyxel.text(16, 134, "I'd be happy to buy me", 7)
        # pyxel.text(41, 140, "a cup of coffee!", 7)
        pyxel.blt(103, 143, 0, 0, 88, 16, 16) #コーヒーの描画

App(120,160)