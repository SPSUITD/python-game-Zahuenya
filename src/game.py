import arcade
import os

# Параметры

GAME_NAME = "Suzy"
PLAYER_NAME = "girl"
GRAVITY = 1.0
PLAYER_SPEED = 5.0
PLAYER_JUMP_SPEED = 25.0

GAME_WINDOW_HEIGHT = 800
GAME_WINDOW_WIDTH = 1024

LEVEL_START = 1
TILE_SCALING = 0.5

LAYER_NAME_PLAYER = "player"
LAYER_NAME_WALLS = "walls"
LAYER_NAME_PLATFORMS = "platforms"
LAYER_NAME_LADDERS = "ladders"
LAYER_NAME_COINS = "coins"
LAYER_NAME_BACKGROUND = "background"
LAYER_NAME_FOREGROUND = "foreground"


RESOURCES_DIR = os.path.dirname(os.path.abspath(__file__))
RESOURCES_DIR = os.path.join(RESOURCES_DIR, "res")


def get_resource_file_name(file_name):
    return f"{RESOURCES_DIR}/{file_name}"


def get_resource_sprite_file_name(file_name):
    return get_resource_file_name(os.path.join("sprites", file_name))


def get_resource_map_file_name(file_name):
    return get_resource_file_name(os.path.join("maps", file_name))


MOVE_SIDE_LEFT = 0
MOVE_SIDE_RIGHT = 1


class Agent(arcade.Sprite):
    def __init__(self, base_name):
        super().__init__()
        self.base_name = base_name
        self.tex_idle = self.load_texture_pair()
        self.move_side = MOVE_SIDE_LEFT
        self.texture = self.tex_idle[self.move_side]

    def update_animation(self, delta_time: float = 1 / 60):
        # Figure out if we need to flip face left or right
        if self.change_x < 0:
            self.move_side = MOVE_SIDE_LEFT
        elif self.change_x > 0:
            self.move_side = MOVE_SIDE_RIGHT

        self.texture = self.tex_idle[self.move_side]

    def load_texture(self, flip_horizontally=False):
        file_name = get_resource_sprite_file_name(f"{self.base_name}.png")
        return arcade.load_texture(file_name, flipped_horizontally=flip_horizontally)

    def load_texture_pair(self):
        return [self.load_texture(), self.load_texture(True)]


class Player(Agent):
    def __init__(self, base_name):
        super().__init__(base_name)


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
        self.next_level_x_position = 0
        self.camera_y_shift = 0

    def setup(self):
        """Инициализировать уровень игры"""

        level_map_file_name = get_resource_map_file_name(f"level_{self.level}.map.tmx")

        if not os.path.exists(level_map_file_name):
            self.win()
            return

        self.camera = arcade.Camera(self.window.width, self.window.height)
        self.camera_origin = arcade.Camera(self.window.width, self.window.height)

        self.tile_map = arcade.load_tilemap(level_map_file_name, TILE_SCALING)
        self.scene = arcade.Scene.from_tilemap(self.tile_map)

        self.next_level_x_position = (self.tile_map.width * self.tile_map.tile_width) * TILE_SCALING

        if self.tile_map.background_color:
            arcade.set_background_color(self.tile_map.background_color)
        else:
            arcade.set_background_color(arcade.color.BLACK)

        self.player = Player(PLAYER_NAME)
        self.player.position = [100, 190]
        self.scene.add_sprite(LAYER_NAME_PLAYER, self.player)

        self.physics_engine = arcade.PhysicsEnginePlatformer(
            self.player,
            platforms=self.scene[LAYER_NAME_PLATFORMS],
            gravity_constant=GRAVITY,
            ladders=self.scene[LAYER_NAME_LADDERS],
            walls=self.scene[LAYER_NAME_WALLS]
        )

    def on_key_press(self, key: int, modifiers: int):
        if key == arcade.key.LEFT:
            self.player.change_x = -PLAYER_SPEED
        elif key == arcade.key.RIGHT:
            self.player.change_x = PLAYER_SPEED
        elif key == arcade.key.UP:
            self.player.change_y = PLAYER_JUMP_SPEED
        elif key == arcade.key.DOWN:
            self.camera_y_shift = 250

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
        self.camera_origin.use()

    def center_camera_on_sprite(self, camera, sprite, aux_y_shift, speed=0.2):
        x = max(0, camera.scale * (sprite.center_x - (camera.viewport_width / 2)))
        y = max(0, camera.scale * (sprite.center_y - (camera.viewport_height / 2) - aux_y_shift))
        camera.move_to((x, y), speed)

    def on_update(self, delta_time: float):
        """Обновить измерения координат и пр."""
        self.physics_engine.update()

        if self.player.center_x >= self.next_level_x_position:
            self.next_level()
            return

        self.center_camera_on_sprite(self.camera, self.player, self.camera_y_shift)

        # Update Animations
        self.scene.update_animation(
            delta_time,
            [LAYER_NAME_PLAYER],
        )

        if self.player.center_y < 0:
            self.game_over()
            return

        self.check_player_collisions()

    def check_player_collisions(self):
        layer_coins = self.scene[LAYER_NAME_COINS]
        collidable_layers = [
            layer_coins
        ]
        collision = arcade.check_for_collision_with_lists(
            self.player, collidable_layers
        )

        for collision in collision:
            if layer_coins in collision.sprite_lists:
                # сбор монет
                collision.remove_from_sprite_lists()

    def game_over(self):
        """Проигрышь"""
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