import os
import random
import sys
import time
import pygame as pg


WIDTH = 1100  # ゲームウィンドウの幅
HEIGHT = 650  # ゲームウィンドウの高さ
NUM_OF_BOMBS = 5  # 爆弾の数
os.chdir(os.path.dirname(os.path.abspath(__file__)))


def check_bound(obj_rct: pg.Rect) -> tuple[bool, bool]:
    """
    オブジェクトが画面内or画面外を判定し，真理値タプルを返す関数
    引数：こうかとんや爆弾，ビームなどのRect
    戻り値：横方向，縦方向のはみ出し判定結果（画面内：True／画面外：False）
    """
    yoko, tate = True, True
    if obj_rct.left < 0 or WIDTH < obj_rct.right:
        yoko = False
    if obj_rct.top < 0 or HEIGHT < obj_rct.bottom:
        tate = False
    return yoko, tate


class Bird:
    """
    ゲームキャラクター（こうかとん）に関するクラス
    """
    delta = {  # 押下キーと移動量の辞書
        pg.K_UP: (0, -5),
        pg.K_DOWN: (0, +5),
        pg.K_LEFT: (-5, 0),
        pg.K_RIGHT: (+5, 0),
    }
    img0 = pg.transform.rotozoom(pg.image.load("fig/3.png"), 0, 0.9)
    img = pg.transform.flip(img0, True, False)  # デフォルトのこうかとん（右向き）
    imgs = {  # 0度から反時計回りに定義
        (+5, 0): img,  # 右
        (+5, -5): pg.transform.rotozoom(img, 45, 0.9),  # 右上
        (0, -5): pg.transform.rotozoom(img, 90, 0.9),  # 上
        (-5, -5): pg.transform.rotozoom(img0, -45, 0.9),  # 左上
        (-5, 0): img0,  # 左
        (-5, +5): pg.transform.rotozoom(img0, 45, 0.9),  # 左下
        (0, +5): pg.transform.rotozoom(img, -90, 0.9),  # 下
        (+5, +5): pg.transform.rotozoom(img, -45, 0.9),  # 右下
    }

    def __init__(self, xy: tuple[int, int]):
        self.img = __class__.imgs[(+5, 0)]
        self.rct: pg.Rect = self.img.get_rect()
        self.rct.center = xy

    def change_img(self, num: int, screen: pg.Surface):
        self.img = pg.transform.rotozoom(pg.image.load(f"fig/{num}.png"), 0, 0.9)
        screen.blit(self.img, self.rct)

    def update(self, key_lst: list[bool], screen: pg.Surface):
        sum_mv = [0, 0]
        for k, mv in __class__.delta.items():
            if key_lst[k]:
                sum_mv[0] += mv[0]
                sum_mv[1] += mv[1]
        self.rct.move_ip(sum_mv)
        if check_bound(self.rct) != (True, True):
            self.rct.move_ip(-sum_mv[0], -sum_mv[1])
        if not (sum_mv[0] == 0 and sum_mv[1] == 0):
            self.img = __class__.imgs[tuple(sum_mv)]
        screen.blit(self.img, self.rct)


class Beam:
    """
    こうかとんが放つビームに関するクラス
    """
    def __init__(self, bird:"Bird"):
        self.img = pg.image.load("fig/beam.png")
        self.rct = self.img.get_rect()
        self.rct.centery = bird.rct.centery
        self.rct.left = bird.rct.right
        self.vx, self.vy = +5, 0

    def update(self, screen: pg.Surface):
        self.rct.move_ip(self.vx, self.vy)
        screen.blit(self.img, self.rct)    


class Bomb:
    """
    爆弾に関するクラス
    """
    def __init__(self, color: tuple[int, int, int], rad: int):
        self.img = pg.Surface((2*rad, 2*rad))
        pg.draw.circle(self.img, color, (rad, rad), rad)
        self.img.set_colorkey((0, 0, 0))
        self.rct = self.img.get_rect()
        self.rct.center = random.randint(0, WIDTH), random.randint(0, HEIGHT)
        self.vx, self.vy = +5, +5

    def update(self, screen: pg.Surface):
        yoko, tate = check_bound(self.rct)
        if not yoko:
            self.vx *= -1
        if not tate:
            self.vy *= -1
        self.rct.move_ip(self.vx, self.vy)
        screen.blit(self.img, self.rct)


# 演習1で追加
class Score:
    """
    スコア表示に関するクラス
    """
    def __init__(self):
        self.font = pg.font.SysFont("hgp創英角ポップ体", 30)
        self.color = (0, 0, 255)
        self.score = 0
        self.img = self.font.render(f"Score: {self.score}", True, self.color)
        self.rct = self.img.get_rect(center=(100, HEIGHT-50))

    def update(self, screen: pg.Surface):
        self.img = self.font.render(f"Score: {self.score}", True, self.color)
        screen.blit(self.img, self.rct)


# --- 演習3 ここから追加 ---
class Explosion:
    """
    爆発エフェクトに関するクラス
    """
    def __init__(self, center: tuple[int, int]):
        # 爆発エフェクト用の画像をロードし、リストに格納
        self.img = pg.image.load("fig/explosion.gif")
        self.imgs = [self.img, pg.transform.flip(self.img, True, True)] # flipは元の画像を改変しないのでOK
        self.rct = self.imgs[0].get_rect(center=center)
        self.life = 20  # 爆発の表示時間
        self.img_index = 0

    def update(self, screen: pg.Surface):
        self.life -= 1
        if self.life > 0:
            # ちらつきを表現するために、画像を交互に切り替える
            self.img_index = (self.img_index + 1) % len(self.imgs)
            screen.blit(self.imgs[self.img_index], self.rct)
# --- 演習3 ここまで追加 ---


def main():
    pg.display.set_caption("たたかえ！こうかとん")
    screen = pg.display.set_mode((WIDTH, HEIGHT))    
    bg_img = pg.image.load("fig/pg_bg.jpg")
    bird = Bird((300, 200))
    bombs = [Bomb((255, 0, 0), 10) for _ in range(NUM_OF_BOMBS)]
    beams = []  # 演習2：ビームをリストで管理
    score = Score() # 演習1：Scoreインスタンスを生成
    explosions = [] # 演習3：爆発リストを初期化

    clock = pg.time.Clock()
    tmr = 0
    game_over = False # ゲームオーバー状態を管理するフラグを追加

    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                return
            if event.type == pg.KEYDOWN and event.key == pg.K_SPACE:
                if not game_over: # ゲームオーバー中はビームを発射しない
                    beams.append(Beam(bird))            
        
        screen.blit(bg_img, [0, 0])
        
        # ゲームオーバー判定と処理
        if not game_over: # ゲームオーバー中でない場合のみ衝突判定を行う
            for bomb in bombs:
                if bomb is not None and bird.rct.colliderect(bomb.rct):
                    bird.change_img(8, screen)
                    game_over = True # ゲームオーバー状態に設定
                    # ゲームオーバー時のテキスト表示はループの最後に移動して、常に表示されるようにする
                    break # 衝突したらループを抜ける

        if game_over: # ゲームオーバー中の描画処理
            fonto = pg.font.Font(None, 80)
            txt = fonto.render("GAME OVER", True, (255, 0, 0))
            screen.blit(txt, [WIDTH//2 - txt.get_width()//2, HEIGHT//2 - txt.get_height()//2]) # 中央寄せ
            score.update(screen) # スコアは常に更新・表示
            pg.display.update()
            # ここでゲームを完全に終了させずに、タイトル画面に戻るなどの処理を追加することも可能
            # ただし、今回はシンプルに終了するようにします
            time.sleep(1) # 一定時間表示後、終了
            return


        # ゲームオーバー中でない場合のみ、ゲームの進行を更新
        if not game_over:
            for i in range(len(beams) - 1, -1, -1): # 逆順でイテレート
                beam = beams[i]
                if beam is not None:
                    for j in range(len(bombs) - 1, -1, -1): # 逆順でイテレート
                        bomb = bombs[j]
                        if bomb is not None and beam.rct.colliderect(bomb.rct):
                            explosions.append(Explosion(bomb.rct.center)) # 演習3：爆発インスタンス生成
                            beams[i] = None
                            bombs[j] = None
                            bird.change_img(6, screen)
                            score.score += 1 
                            break 
            
            bombs = [bomb for bomb in bombs if bomb is not None]
            beams = [beam for beam in beams if beam is not None and check_bound(beam.rct) == (True, True)]
            explosions = [exp for exp in explosions if exp.life > 0] # 演習3：ライフが残っている爆発のみ残す

            key_lst = pg.key.get_pressed()
            bird.update(key_lst, screen)

            for beam in beams:
                beam.update(screen)
            for bomb in bombs:
                bomb.update(screen)
            for exp in explosions: # 演習3：爆発を描画
                exp.update(screen)

            score.update(screen) 

        pg.display.update()
        tmr += 1
        clock.tick(50)


if __name__ == "__main__":
    pg.init()
    main()
    pg.quit()
    sys.exit()