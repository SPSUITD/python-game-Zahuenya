import arcade
import os
import math
import random

# Параметры

GAME_NAME = "Suzy"
PLAYER_NAME = "girl_left"
GRAVITY = 1.0
PLAYER_SPEED = 5.0
PLAYER_JUMP_SPEED = 25.0
INITAL_LIVES = 3
SHOT_SPEED = 10.0

GAME_WINDOW_HEIGHT = 800
GAME_WINDOW_WIDTH = 1024

LEVEL_START = 1

TILE_SCALING_BASE = 0.5

LAYER_NAME_PLAYER = "player"
LAYER_NAME_WALLS = "walls"
LAYER_NAME_PLATFORMS = "platforms"
LAYER_NAME_LADDERS = "ladders"
LAYER_NAME_COINS = "coins"
LAYER_NAME_BACKGROUND = "background"
LAYER_NAME_FOREGROUND = "foreground"
LAYER_NAME_ENEMIES = "enemies"
LAYER_NAME_SHOTS = "shots"


RESOURCES_DIR = os.path.dirname(os.path.abspath(__file__))
RESOURCES_DIR = os.path.join(RESOURCES_DIR, "res")

INFO_STRING_GAP = 10


def get_resource_file_name(file_name):
    return f"{RESOURCES_DIR}/{file_name}"


def get_resource_sprite_file_name(file_name):
    return get_resource_file_name(os.path.join("sprites", file_name))


def get_resource_map_file_name(file_name):
    return get_resource_file_name(os.path.join("maps", file_name))


MOVE_SIDE_LEFT = 0
MOVE_SIDE_RIGHT = 1

AGENT_STATE_IDLE = "idle"
AGENT_STATE_WALK = "walk"
AGENT_STATE_JUMP = "jump"
AGENT_STATE_FALL = "fall"
AGENT_STATE_CLIMB = "climb"

AGENT_STATES = [
    AGENT_STATE_IDLE,
    AGENT_STATE_WALK,
    AGENT_STATE_JUMP,
    AGENT_STATE_FALL,
    AGENT_STATE_CLIMB
]


class Agent(arcade.Sprite):
    def __init__(self, base_name, invert_side=False):
        super().__init__()
        self.base_name = base_name
        self.invert_side = invert_side
        self.move_side = MOVE_SIDE_LEFT

        self.states_textures = {}
        for state in AGENT_STATES:
            texs = self.load_state_textures(state)
            if texs:
                self.states_textures[state] = texs
            else:
                # по умолчанию если нет текстур для состояния - использовать idle
                self.states_textures[state] = self.states_textures[AGENT_STATE_IDLE]

        self.state = None
        self.texture_index = 0
        self.set_state(AGENT_STATE_IDLE)

    def set_state(self, state):
        if self.state != state:
            self.state = state
            self.texture_index = 0
            self.texture = self.states_textures[self.state][self.texture_index][self.move_side]

    def update_animation(self, delta_time: float = 1 / 60):
        # Figure out if we need to flip face left or right
        if self.change_x < 0:
            self.move_side = MOVE_SIDE_LEFT
            self.set_state(AGENT_STATE_WALK)
        elif self.change_x > 0:
            self.move_side = MOVE_SIDE_RIGHT
            self.set_state(AGENT_STATE_WALK)
        else:
            self.set_state(AGENT_STATE_IDLE)

        if self.change_y > 0:
            self.set_state(AGENT_STATE_JUMP)
        elif self.change_y < 0:
            self.set_state(AGENT_STATE_FALL)

        texs = self.states_textures[self.state]
        count = len(texs)
        index = self.texture_index % count
        self.texture = texs[index][self.move_side]

    def load_texture(self, file_name, flip_horizontally=False):
        return arcade.load_texture(file_name, flipped_horizontally=flip_horizontally)

    def load_texture_pair(self, state, index):
        file_name = get_resource_sprite_file_name(f"{self.base_name}.{state}.{index}.png")
        if not os.path.exists(file_name):
            return []
        return [
            self.load_texture(file_name, self.invert_side),
            self.load_texture(file_name, not self.invert_side)
        ]

    def load_state_textures(self, state):
        texs = []

        for index in range(100):
            tex = self.load_texture_pair(state, index)
            if not tex:
                break
            texs.append(tex)
        return texs

    def shoot(self, list_to_add=None):
        lazer_sprite_file_name = get_resource_sprite_file_name("lazer.png")
        shot = arcade.Sprite(lazer_sprite_file_name)
        direction = -1 if self.move_side == MOVE_SIDE_LEFT else 1
        shot.change_x = SHOT_SPEED * direction

        shot.center_x = self.center_x + direction * self.width
        shot.center_y = self.center_y + 20

        return shot


class Player(Agent):
    def __init__(self, base_name, invert_side=False):
        super().__init__(base_name, invert_side)


class Enemy(Agent):
    def __init__(self):
        super().__init__("girl", False)


class GameView(arcade.View):
    """Главный класс игры"""

    def __init__(self):
        """Функция инициализатор для объекта игры"""
        super().__init__()
        self.tile_map = None
        self.scene = None
        self.level = LEVEL_START
        self.camera = None
        self.player = None
        self.physics_engine = None
        self.map_pixel_width = 0
        self.camera_y_shift = 0
        self.score = 0
        self.lives = INITAL_LIVES

    def setup(self):
        """Инициализировать уровень игры"""

        level_map_file_name = get_resource_map_file_name(f"level_{self.level}.map.tmx")

        if not os.path.exists(level_map_file_name):
            self.win()
            return

        self.camera = arcade.Camera(self.window.width, self.window.height)
        self.camera_origin = arcade.Camera(self.window.width, self.window.height)

        self.tile_map = arcade.load_tilemap(level_map_file_name, TILE_SCALING_BASE)
        self.scene = arcade.Scene.from_tilemap(self.tile_map)

        self.map_pixel_width = (self.tile_map.width * self.tile_map.tile_width) * TILE_SCALING_BASE

        if self.tile_map.background_color:
            arcade.set_background_color(self.tile_map.background_color)
        else:
            arcade.set_background_color(arcade.color.BLACK)

        self.player = Player(PLAYER_NAME, True)
        self.player.scale = 96.0 / self.player.width
        for point in self.tile_map.object_lists[LAYER_NAME_PLAYER]:
            self.player.position = point.shape
            break

        self.scene.add_sprite(LAYER_NAME_PLAYER, self.player)

        # враги
        for point in self.tile_map.object_lists[LAYER_NAME_ENEMIES]:
            xy = self.tile_map.get_cartesian(point.shape[0], point.shape[1])
            enemy = Enemy()
            enemy.center_x = math.floor(xy[0] * (self.tile_map.tile_width * TILE_SCALING_BASE))
            enemy.center_y = math.floor((xy[1] + 2) * (self.tile_map.tile_height * TILE_SCALING_BASE))
            self.scene.add_sprite(LAYER_NAME_ENEMIES, enemy)

        # движок
        self.physics_engine = arcade.PhysicsEnginePlatformer(
            self.player,
            platforms=self.scene[LAYER_NAME_PLATFORMS],
            gravity_constant=GRAVITY,
            ladders=self.scene[LAYER_NAME_LADDERS],
            walls=self.scene[LAYER_NAME_WALLS]
        )

        self.score = 0
        self.scene.add_sprite_list(LAYER_NAME_SHOTS)

        self.scene.move_sprite_list_before(LAYER_NAME_PLAYER, LAYER_NAME_FOREGROUND)

    def make_agent_shoot(self, agent):
        self.scene.add_sprite(LAYER_NAME_SHOTS, agent.shoot())

    def on_key_press(self, key: int, modifiers: int):
        if key == arcade.key.LEFT:
            self.player.change_x = -PLAYER_SPEED
        elif key == arcade.key.RIGHT:
            self.player.change_x = PLAYER_SPEED
        elif key == arcade.key.UP:
            self.player.change_y = PLAYER_JUMP_SPEED
        elif key == arcade.key.DOWN:
            self.camera_y_shift = 250
        elif key == arcade.key.SPACE:
            self.make_agent_shoot(self.player)

    def on_key_release(self, key: int, modifiers: int):
        if key == arcade.key.LEFT or key == arcade.key.RIGHT:
            self.player.change_x = 0
        elif key == arcade.key.UP or key == arcade.key.DOWN:
            self.player.change_y = 0
            self.camera_y_shift = 0

    def on_show_view(self):
        self.setup()

    def on_draw(self):
        """Нарисовать кадр"""
        self.clear()
        self.camera.use()
        self.scene.draw()

        self.draw_info()

    def draw_info_string(self, x, y, text, anchor_x):
        self.camera_origin.use()
        arcade.draw_text(
            text, x, y,
            arcade.csscolor.GREEN, 18,
            anchor_x=anchor_x
        )

    def draw_info(self):
        self.camera_origin.use()
        y = self.window.height - INFO_STRING_GAP * 2
        self.draw_info_string(
            INFO_STRING_GAP, y,
            f"Score: {self.score}",
            "left")
        self.draw_info_string(
            self.window.width - INFO_STRING_GAP, y,
            f"Lives: {self.lives}",
            "right")
        self.draw_info_string(
            self.window.width / 2, y,
            f"LEVEL: {self.level}",
            "center")

    def center_camera_on_sprite(self, camera, sprite, aux_y_shift, speed=0.1):
        """Центривать камеру на спрайте"""
        x = max(0, camera.scale * (sprite.center_x - (camera.viewport_width / 2)))
        y = max(0, camera.scale * (sprite.center_y - (camera.viewport_height / 2) - aux_y_shift))
        camera.move_to((x, y), speed)

    def on_update(self, delta_time: float):
        """Обновить измерения координат и пр."""
        self.physics_engine.update()

        if self.player.center_x >= self.map_pixel_width:
            self.next_level()
            return

        self.center_camera_on_sprite(self.camera, self.player, self.camera_y_shift)

        self.scene.update_animation(
            delta_time,
            [LAYER_NAME_PLAYER],
        )

        self.scene.update(
            [LAYER_NAME_PLATFORMS, LAYER_NAME_ENEMIES, LAYER_NAME_SHOTS]
        )

        if self.player.center_y < 0:
            self.game_over()
            return

        self.check_player_collisions()
        self.update_shots()

        for enemy in self.scene[LAYER_NAME_ENEMIES]:
            if random.random() < 0.01:
                self.make_agent_shoot(enemy)

    def update_shots(self):
        for shot in self.scene[LAYER_NAME_SHOTS]:
            # если вышел за экран
            if (shot.right < 0) or (shot.left > self.map_pixel_width):
                shot.remove_from_sprite_lists()
                continue

            # куда попали?
            hits = arcade.check_for_collision_with_lists(
                shot,
                [
                    self.scene[LAYER_NAME_PLAYER],
                    self.scene[LAYER_NAME_ENEMIES],
                    self.scene[LAYER_NAME_WALLS],
                    self.scene[LAYER_NAME_PLATFORMS],
                ],
            )

            if not hits:
                continue

            shot.remove_from_sprite_lists()

            for target in hits:
                if self.scene[LAYER_NAME_ENEMIES] in target.sprite_lists:
                    target.remove_from_sprite_lists()
                if self.scene[LAYER_NAME_PLAYER] in target.sprite_lists:
                    self.game_over()

    def check_player_collisions(self):
        layer_coins = self.scene[LAYER_NAME_COINS]
        layer_enemies = self.scene[LAYER_NAME_ENEMIES]

        collidable_layers = [
            layer_coins,
            layer_enemies
        ]
        collision = arcade.check_for_collision_with_lists(
            self.player, collidable_layers
        )

        for collision in collision:
            if layer_enemies in collision.sprite_lists:
                self.game_over()
                return
            if layer_coins in collision.sprite_lists:
                # сбор монет
                collision.remove_from_sprite_lists()
                self.score += 10

    def game_over(self):
        """Проигрышь"""
        if self.lives > 1:
            self.lives -= 1
            self.setup()
        else:
            self.window.show_view(GameOverView())

    def win(self):
        """Игра пройдена"""
        self.window.show_view(WinView())

    def next_level(self):
        """Начать новый уровень"""
        self.level += 1
        self.setup()


class RestartGameView(arcade.View):
    """Вью для перезапуска игры"""

    def __init__(self, text, bg_color, fg_color):
        super().__init__()
        self.text = text
        self.bg_color = bg_color
        self.fg_color = fg_color

    def on_show_view(self):
        arcade.set_background_color(self.bg_color)

    def on_draw(self):
        self.clear()
        arcade.draw_text(
            self.text,
            GAME_WINDOW_WIDTH / 2,
            GAME_WINDOW_HEIGHT / 2,
            self.fg_color,
            40,
            anchor_x="center",
        )
        arcade.draw_text(
            "Кликните чтобы начать заново",
            GAME_WINDOW_WIDTH / 2,
            GAME_WINDOW_HEIGHT / 4,
            self.fg_color,
            10,
            anchor_x="center",
        )

    def on_mouse_press(self, _x, _y, _button, _modifiers):
        game_view = GameView()
        self.window.show_view(game_view)


class GameOverView(RestartGameView):
    """Вью для проигрыша"""

    def __init__(self):
        super().__init__("Потрачено", arcade.color.RED, arcade.color.BLACK)


class WinView(RestartGameView):
    """Вью для выигрыша"""

    def __init__(self):
        super().__init__("Потрачено с умом", arcade.color.GREEN, arcade.color.BLACK)


def main():
    window = arcade.Window(GAME_WINDOW_WIDTH, GAME_WINDOW_HEIGHT, GAME_NAME)
    game_view = GameView()
    window.show_view(game_view)
    arcade.run()


if __name__ == "__main__":
    main()