import tkinter as tk
import random

class BrickBreakerGame:
    def __init__(self, root):
        self.root = root
        self.root.title("블록깨기 게임 - Brick Breaker")
        self.root.geometry("600x700")
        self.root.resizable(False, False)
        
        # 게임 상태
        self.width = 600
        self.height = 700
        self.score = 0
        self.lives = 3
        self.game_over = False
        self.game_won = False
        
        # 캔버스 생성
        self.canvas = tk.Canvas(
            self.root, 
            width=self.width, 
            height=self.height - 80, 
            bg="black"
        )
        self.canvas.pack()
        
        # 정보 표시 레이블
        self.info_frame = tk.Frame(self.root, bg="gray20")
        self.info_frame.pack(fill=tk.X)
        
        self.score_label = tk.Label(
            self.info_frame, 
            text=f"점수: {self.score}", 
            font=("Arial", 14),
            fg="white",
            bg="gray20"
        )
        self.score_label.pack(side=tk.LEFT, padx=20, pady=10)
        
        self.lives_label = tk.Label(
            self.info_frame, 
            text=f"생명: {self.lives}", 
            font=("Arial", 14),
            fg="white",
            bg="gray20"
        )
        self.lives_label.pack(side=tk.LEFT, padx=20, pady=10)
        
        self.status_label = tk.Label(
            self.info_frame, 
            text="게임 시작!", 
            font=("Arial", 14),
            fg="yellow",
            bg="gray20"
        )
        self.status_label.pack(side=tk.RIGHT, padx=20, pady=10)
        
        # 패들
        self.paddle_width = 80
        self.paddle_height = 15
        self.paddle_x = self.width // 2 - self.paddle_width // 2
        self.paddle = self.canvas.create_rectangle(
            self.paddle_x, self.height - 100,
            self.paddle_x + self.paddle_width, self.height - 100 + self.paddle_height,
            fill="cyan", outline="white"
        )
        
        # 공
        self.ball_size = 8
        self.ball_x = self.width // 2
        self.ball_y = self.height - 150
        self.ball_dx = 3
        self.ball_dy = -3
        self.ball = self.canvas.create_oval(
            self.ball_x - self.ball_size, self.ball_y - self.ball_size,
            self.ball_x + self.ball_size, self.ball_y + self.ball_size,
            fill="white", outline="white"
        )
        
        # 벽돌 생성
        self.bricks = []
        self.create_bricks()
        
        # 마우스 모션 바인딩
        self.canvas.bind("<Motion>", self.move_paddle)
        
        # 게임 루프 시작
        self.update_game()
        
    def create_bricks(self):
        """벽돌 생성"""
        brick_width = 70
        brick_height = 15
        brick_padding = 5
        rows = 4
        cols = 8
        
        colors = ["red", "orange", "yellow", "green", "blue", "purple"]
        
        for row in range(rows):
            for col in range(cols):
                x1 = col * (brick_width + brick_padding) + 10
                y1 = row * (brick_height + brick_padding) + 20
                x2 = x1 + brick_width
                y2 = y1 + brick_height
                
                color = colors[row % len(colors)]
                brick = self.canvas.create_rectangle(
                    x1, y1, x2, y2,
                    fill=color, outline="white", width=1
                )
                self.bricks.append({
                    "id": brick,
                    "x1": x1,
                    "y1": y1,
                    "x2": x2,
                    "y2": y2
                })
    
    def move_paddle(self, event):
        """패들 움직임"""
        if self.game_over or self.game_won:
            return
        
        mouse_x = event.x
        new_x = mouse_x - self.paddle_width // 2
        
        # 화면 범위 내로 제한
        new_x = max(0, min(new_x, self.width - self.paddle_width))
        
        self.paddle_x = new_x
        self.canvas.coords(
            self.paddle,
            new_x, self.height - 100,
            new_x + self.paddle_width, self.height - 100 + self.paddle_height
        )
    
    def check_collision(self):
        """충돌 검사"""
        # 벽 충돌
        if self.ball_x - self.ball_size <= 0 or self.ball_x + self.ball_size >= self.width:
            self.ball_dx = -self.ball_dx
        
        if self.ball_y - self.ball_size <= 0:
            self.ball_dy = -self.ball_dy
        
        # 패들 충돌
        if (self.height - 100 <= self.ball_y + self.ball_size <= self.height - 100 + self.paddle_height and
            self.paddle_x <= self.ball_x <= self.paddle_x + self.paddle_width):
            self.ball_dy = -self.ball_dy
            # 패들의 위치에 따라 공의 각도 조정
            hit_pos = (self.ball_x - self.paddle_x) / self.paddle_width
            self.ball_dx = (hit_pos - 0.5) * 8
        
        # 게임 오버 (공이 아래로 떨어짐)
        if self.ball_y > self.height:
            self.lives -= 1
            if self.lives <= 0:
                self.game_over = True
                self.status_label.config(text="게임 오버!", fg="red")
            else:
                self.reset_ball()
        
        # 벽돌 충돌
        bricks_to_remove = []
        for brick in self.bricks:
            if (brick["x1"] <= self.ball_x <= brick["x2"] and
                brick["y1"] - self.ball_size <= self.ball_y <= brick["y2"] + self.ball_size):
                self.ball_dy = -self.ball_dy
                self.canvas.delete(brick["id"])
                bricks_to_remove.append(brick)
                self.score += 10
                self.score_label.config(text=f"점수: {self.score}")
        
        for brick in bricks_to_remove:
            self.bricks.remove(brick)
        
        # 게임 승리 (모든 벽돌 파괴)
        if len(self.bricks) == 0:
            self.game_won = True
            self.status_label.config(text="승리!", fg="lime")
    
    def reset_ball(self):
        """공 초기화"""
        self.ball_x = self.width // 2
        self.ball_y = self.height - 150
        self.ball_dx = random.choice([-3, 3])
        self.ball_dy = -3
    
    def update_game(self):
        """게임 루프"""
        if not self.game_over and not self.game_won:
            # 공의 위치 업데이트
            self.ball_x += self.ball_dx
            self.ball_y += self.ball_dy
            
            # 공 그리기
            self.canvas.coords(
                self.ball,
                self.ball_x - self.ball_size, self.ball_y - self.ball_size,
                self.ball_x + self.ball_size, self.ball_y + self.ball_size
            )
            
            # 충돌 검사
            self.check_collision()
            
            # 생명 업데이트
            self.lives_label.config(text=f"생명: {self.lives}")
        
        # 계속해서 게임 루프 실행
        self.root.after(30, self.update_game)

# 메인 윈도우 생성 및 게임 시작
if __name__ == "__main__":
    root = tk.Tk()
    game = BrickBreakerGame(root)
    root.mainloop()
    
