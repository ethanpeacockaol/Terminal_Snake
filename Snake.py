import os
import random
import time
import sys
import platform
import select

# --- Game Configuration ---
BOARD_WIDTH = 20
BOARD_HEIGHT = 10
INITIAL_SNAKE_LENGTH = 3
GAME_SPEED = 0.2  # Seconds per frame (smaller is faster)

# Characters for drawing
SNAKE_HEAD_CHAR = 'O'
SNAKE_BODY_CHAR = '@'
FOOD_CHAR = '*'
EMPTY_CHAR = ' '
BORDER_CHAR = '#'

# --- Global Variables ---
snake = []
food_pos = []
direction = 'right'
score = 0
game_over = False

# --- OS-specific screen clearing and input ---
def clear_screen():
    if platform.system() == "Windows":
        os.system('cls')
    else:
        os.system('clear')

# Non-blocking input setup
if platform.system() == "Windows":
    import msvcrt
    def get_char_non_blocking():
        if msvcrt.kbhit():
            return msvcrt.getch().decode('utf-8').lower()
        return None
else: # Unix-like systems
    import termios
    import tty
    old_settings = None

    def set_raw_mode():
        global old_settings
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
        except termios.error:
            # Handle cases where stdin is not a TTY (e.g., piping input)
            pass

    def restore_terminal_mode():
        global old_settings
        if old_settings:
            fd = sys.stdin.fileno()
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

    def get_char_non_blocking():
        if sys.stdin in select.select([sys.stdin], [], [], 0)[0]:
            try:
                char = sys.stdin.read(1)
                return char.lower()
            except IOError: # Handle cases where stdin is not a TTY (e.g., piping input)
                return None
        return None

# --- Game Functions ---
def initialize_game():
    global snake, food_pos, direction, score, game_over

    snake = []
    # Start snake in the middle-left
    start_x = BOARD_WIDTH // 4
    start_y = BOARD_HEIGHT // 2
    for i in range(INITIAL_SNAKE_LENGTH):
        snake.append([start_x - i, start_y])

    direction = 'right'
    score = 0
    game_over = False
    place_food()

def place_food():
    global food_pos
    while True:
        fx = random.randint(1, BOARD_WIDTH - 2)
        fy = random.randint(1, BOARD_HEIGHT - 2)
        if [fx, fy] not in snake:
            food_pos = [fx, fy]
            break

def draw_board():
    clear_screen()
    board = [[' ' for _ in range(BOARD_WIDTH)] for _ in range(BOARD_HEIGHT)]

    # Draw borders
    for i in range(BOARD_WIDTH):
        board[0][i] = BORDER_CHAR
        board[BOARD_HEIGHT - 1][i] = BORDER_CHAR
    for i in range(BOARD_HEIGHT):
        board[i][0] = BORDER_CHAR
        board[i][BOARD_WIDTH - 1] = BORDER_CHAR

    # Draw snake
    for i, segment in enumerate(snake):
        if 0 < segment[1] < BOARD_HEIGHT -1 and 0 < segment[0] < BOARD_WIDTH - 1: # Only draw if inside bounds
            board[segment[1]][segment[0]] = SNAKE_HEAD_CHAR if i == 0 else SNAKE_BODY_CHAR

    # Draw food
    if 0 < food_pos[1] < BOARD_HEIGHT -1 and 0 < food_pos[0] < BOARD_WIDTH - 1: # Only draw if inside bounds
        board[food_pos[1]][food_pos[0]] = FOOD_CHAR

    # Print the board
    for row in board:
        print("".join(row))

    print(f"\nScore: {score}")
    if game_over:
        print("\nGAME OVER!")
        print("Press 'r' to Restart or 'q' to Quit.")

def handle_input():
    global direction
    char = get_char_non_blocking()
    if char:
        if char == 'w' and direction != 'down':
            direction = 'up'
        elif char == 's' and direction != 'up':
            direction = 'down'
        elif char == 'a' and direction != 'right':
            direction = 'left'
        elif char == 'd' and direction != 'left':
            direction = 'right'
        elif char == 'q':
            sys.exit() # Directly exit if 'q' is pressed during active game
        return char # Return char to check for restart

def update_game_state():
    global snake, food_pos, score, game_over

    head_x, head_y = snake[0]
    new_head = list(snake[0]) # Make a copy

    if direction == 'up':
        new_head[1] -= 1
    elif direction == 'down':
        new_head[1] += 1
    elif direction == 'left':
        new_head[0] -= 1
    elif direction == 'right':
        new_head[0] += 1

    # Check for collisions
    # Wall collision
    if (new_head[0] <= 0 or new_head[0] >= BOARD_WIDTH - 1 or
        new_head[1] <= 0 or new_head[1] >= BOARD_HEIGHT - 1):
        game_over = True
        return

    # Self-collision
    if new_head in snake:
        game_over = True
        return

    snake.insert(0, new_head)

    # Check if food is eaten
    if new_head == food_pos:
        score += 1
        place_food()
    else:
        snake.pop() # Remove tail if no food eaten

# --- Main Game Loop ---
def game_loop():
    global game_over

    if platform.system() != "Windows":
        set_raw_mode() # Set terminal to raw mode for direct input

    try:
        initialize_game()
        while True:
            draw_board()
            key_press = handle_input() # Get any key presses

            if game_over:
                if key_press == 'r':
                    initialize_game()
                elif key_press == 'q':
                    break # Exit game loop

            if not game_over:
                update_game_state()
            time.sleep(GAME_SPEED)

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        if platform.system() != "Windows":
            restore_terminal_mode() # Restore terminal settings on exit

if __name__ == "__main__":
    print("Starting Snake Game...")
    print("Use W, A, S, D to move.")
    print("Press 'q' to quit at any time.")
    print("Press Enter to start...")
    input() # Wait for user to press Enter to start

    game_loop()
    print("Thanks for playing!")