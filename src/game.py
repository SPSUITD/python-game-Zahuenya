import arcade
import os

# Параметры

GAME_NAME = "Suzy"
GRAVITY = 1.0
PLAYER_SPEED = 5.0
PLAYER_JUMP_SPEED = 25.0

GAME_WINDOW_HEIGHT = 800
GAME_WINDOW_WIDTH = 1024

LEVEL_START = 1
TILE_SCALING = 0.5


RESOURCES_DIR = os.path.dirname(os.path.abspath(__file__))

LAYER_NAME_PLAYER = "player"
LAYER_NAME_WALLS = "walls"


def get_resource_file_name(file_name):
    return f"{RESOURCES_DIR}/{file_name}"


class Player(arcade.Sprite):
    def __init__(self, base_name):
        super().__init__()
        self.base_name = base_name
        self.texture = self.load_texture()

    def load_texture(self):
        file_name = get_resource_file_name(f"{self.base_name}.png")
        return arcade.load_texture(file_name)


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

        map_name = get_resource_file_name(f"level_{self.level}.map.tmx")

        if not os.path.exists(map_name):
            self.win()
            return

        self.camera = arcade.Camera(self.window.width, self.window.height)

        self.tile_map = arcade.load_tilemap(map_name, TILE_SCALING)
        self.scene = arcade.Scene.from_tilemap(self.tile_map)

        self.next_level_x_position = self.tile_map.width * self.tile_map.tile_width

        if self.tile_map.background_color:
            arcade.set_background_color(self.tile_map.background_color)

        self.player = Player("girl")
        self.player.position = [100, 190]
        self.scene.add_sprite(LAYER_NAME_PLAYER, self.player)

        self.physics_engine = arcade.PhysicsEnginePlatformer(
            self.player,
            #platforms=self.scene[LAYER_NAME_MOVING_PLATFORMS],
            gravity_constant=GRAVITY,
            #ladders=self.scene[LAYER_NAME_LADDERS],
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
            self.camera_y_shift = 150

    def on_key_release(self, key: int, modifiers: int):
        # проверка
        if key == arcade.key.Q:
            self.game_over()

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

    def center_camera_on_sprite(self, camera, sprite, aux_y_shift, speed=0.2):
        x = max(0, camera.scale * (sprite.center_x - (camera.viewport_width / 2)))
        y = max(0, camera.scale * (sprite.center_y - (camera.viewport_height / 2) - aux_y_shift))
        camera.move_to((x, y), speed)

    def on_update(self, delta_time: float):
        """Обновить измерения координат и пр."""
        self.physics_engine.update()

        if self.player.center_x >= self.next_level_x_position:
            self.next_level()

        self.center_camera_on_sprite(self.camera, self.player, self.camera_y_shift)

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