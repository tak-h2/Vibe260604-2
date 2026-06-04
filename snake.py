import pygame
import random
import sys
from collections import deque

# 게임 초기화
pygame.init()

# 상수 설정
SCREEN_WIDTH = 640
SCREEN_HEIGHT = 480
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE

# 색상
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 100, 255)
YELLOW = (255, 255, 0)

# 방향
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

class Snake:
    def __init__(self, start_pos, color, is_ai=False):
        self.body = [start_pos]
        self.direction = RIGHT
        self.next_direction = RIGHT
        self.color = color
        self.is_ai = is_ai
    
    def move(self):
        self.direction = self.next_direction
        head_x, head_y = self.body[0]
        dx, dy = self.direction
        new_head = (head_x + dx, head_y + dy)
        self.body.insert(0, new_head)
    
    def shrink(self):
        if len(self.body) > 1:
            self.body.pop()
    
    def check_collision(self, other_snake=None):
        head = self.body[0]
        # 벽과의 충돌
        if head[0] < 0 or head[0] >= GRID_WIDTH or head[1] < 0 or head[1] >= GRID_HEIGHT:
            return True
        # 자기 몸과의 충돌
        if head in self.body[1:]:
            return True
        # 다른 뱀과의 충돌
        if other_snake and head in other_snake.body:
            return True
        return False
    
    def draw(self, screen):
        for i, segment in enumerate(self.body):
            rect = pygame.Rect(segment[0] * GRID_SIZE, segment[1] * GRID_SIZE, GRID_SIZE, GRID_SIZE)
            pygame.draw.rect(screen, self.color, rect)
            pygame.draw.rect(screen, WHITE, rect, 1)

class Food:
    def __init__(self):
        self.position = self.generate_position()
    
    def generate_position(self, snake1=None, snake2=None):
        while True:
            pos = (random.randint(0, GRID_WIDTH - 1), random.randint(0, GRID_HEIGHT - 1))
            # 뱀의 몸과 겹치지 않는 위치에 생성
            if (snake1 and pos in snake1.body) or (snake2 and pos in snake2.body):
                continue
            return pos
    
    def draw(self, screen):
        rect = pygame.Rect(self.position[0] * GRID_SIZE, self.position[1] * GRID_SIZE, GRID_SIZE, GRID_SIZE)
        pygame.draw.rect(screen, RED, rect)
        pygame.draw.circle(screen, YELLOW, (rect.centerx, rect.centery), GRID_SIZE // 3)

class AISnake:
    @staticmethod
    def find_path_to_food(snake, food, other_snake, width, height):
        """BFS를 사용해 사과까지의 경로 찾기"""
        start = snake.body[0]
        target = food.position
        
        queue = deque([(start, [start])])
        visited = {start}
        
        while queue:
            (x, y), path = queue.popleft()
            
            if (x, y) == target:
                if len(path) > 1:
                    return path[1]
                return (x, y)
            
            for dx, dy in [UP, DOWN, LEFT, RIGHT]:
                nx, ny = x + dx, y + dy
                next_pos = (nx, ny)
                
                if next_pos in visited:
                    continue
                if nx < 0 or nx >= width or ny < 0 or ny >= height:
                    continue
                # 자신의 몸이나 다른 뱀의 몸을 피함
                if next_pos in snake.body[:-1] or next_pos in other_snake.body:
                    continue
                
                visited.add(next_pos)
                queue.append((next_pos, path + [next_pos]))
        
        # 경로를 찾지 못하면 사과 방향으로 이동
        return AISnake.move_toward_target(snake.body[0], target)
    
    @staticmethod
    def move_toward_target(current, target):
        """현재 위치에서 목표 위치 방향으로 다음 위치 반환"""
        x, y = current
        tx, ty = target
        
        if tx < x:
            return (x - 1, y)
        elif tx > x:
            return (x + 1, y)
        elif ty < y:
            return (x, y - 1)
        else:
            return (x, y + 1)

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("뱀 게임 - 플레이어 vs AI")
        self.clock = pygame.time.Clock()
        
        # 두 뱀 생성
        self.player_snake = Snake((GRID_WIDTH // 4, GRID_HEIGHT // 2), GREEN, is_ai=False)
        self.ai_snake = Snake((3 * GRID_WIDTH // 4, GRID_HEIGHT // 2), BLUE, is_ai=True)
        
        self.food = Food()
        self.player_score = 0
        self.ai_score = 0
        self.game_over = False
        self.winner = None
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
    
    def handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP and self.player_snake.direction != DOWN:
                    self.player_snake.next_direction = UP
                elif event.key == pygame.K_DOWN and self.player_snake.direction != UP:
                    self.player_snake.next_direction = DOWN
                elif event.key == pygame.K_LEFT and self.player_snake.direction != RIGHT:
                    self.player_snake.next_direction = LEFT
                elif event.key == pygame.K_RIGHT and self.player_snake.direction != LEFT:
                    self.player_snake.next_direction = RIGHT
                elif event.key == pygame.K_SPACE and self.game_over:
                    self.__init__()
        return True
    
    def update_ai(self):
        """AI 뱀 업데이트"""
        next_pos = AISnake.find_path_to_food(self.ai_snake, self.food, self.player_snake, GRID_WIDTH, GRID_HEIGHT)
        head_x, head_y = self.ai_snake.body[0]
        next_x, next_y = next_pos
        
        dx, dy = next_x - head_x, next_y - head_y
        
        if (dx, dy) == UP and self.ai_snake.direction != DOWN:
            self.ai_snake.next_direction = UP
        elif (dx, dy) == DOWN and self.ai_snake.direction != UP:
            self.ai_snake.next_direction = DOWN
        elif (dx, dy) == LEFT and self.ai_snake.direction != RIGHT:
            self.ai_snake.next_direction = LEFT
        elif (dx, dy) == RIGHT and self.ai_snake.direction != LEFT:
            self.ai_snake.next_direction = RIGHT
    
    def update(self):
        if self.game_over:
            return
        
        # AI 업데이트
        self.update_ai()
        
        # 두 뱀 이동
        self.player_snake.move()
        self.ai_snake.move()
        
        # 플레이어 뱀이 사과를 먹었는지 확인
        if self.player_snake.body[0] == self.food.position:
            self.player_score += 10
            self.food.position = self.food.generate_position(self.player_snake, self.ai_snake)
        else:
            self.player_snake.shrink()
        
        # AI 뱀이 사과를 먹었는지 확인
        if self.ai_snake.body[0] == self.food.position:
            self.ai_score += 10
            self.food.position = self.food.generate_position(self.player_snake, self.ai_snake)
        else:
            self.ai_snake.shrink()
        
        # 충돌 확인
        player_collision = self.player_snake.check_collision(self.ai_snake)
        ai_collision = self.ai_snake.check_collision(self.player_snake)
        
        if player_collision and ai_collision:
            self.game_over = True
            self.winner = "동점"
        elif player_collision:
            self.game_over = True
            self.winner = "AI 승리!"
        elif ai_collision:
            self.game_over = True
            self.winner = "플레이어 승리!"
    
    def draw(self):
        self.screen.fill(BLACK)
        
        # 뱀 그리기
        self.player_snake.draw(self.screen)
        self.ai_snake.draw(self.screen)
        
        # 사과 그리기
        self.food.draw(self.screen)
        
        # 점수 표시
        player_score_text = self.small_font.render(f"Player: {self.player_score}", True, GREEN)
        ai_score_text = self.small_font.render(f"AI: {self.ai_score}", True, BLUE)
        self.screen.blit(player_score_text, (10, 10))
        self.screen.blit(ai_score_text, (SCREEN_WIDTH - 150, 10))
        
        # 게임 오버 메시지
        if self.game_over:
            game_over_text = self.font.render(self.winner, True, YELLOW)
            restart_text = self.small_font.render("Press SPACE to restart", True, WHITE)
            
            text_rect = game_over_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 20))
            restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 30))
            
            pygame.draw.rect(self.screen, BLACK, text_rect.inflate(40, 40))
            pygame.draw.rect(self.screen, BLACK, restart_rect.inflate(40, 40))
            
            self.screen.blit(game_over_text, text_rect)
            self.screen.blit(restart_text, restart_rect)
        
        pygame.display.flip()
    
    def run(self):
        running = True
        fps = 8
        
        while running:
            running = self.handle_input()
            self.update()
            self.draw()
            self.clock.tick(fps)
        
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = Game()
    game.run()
