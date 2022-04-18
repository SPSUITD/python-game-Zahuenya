import arcade
import os

GAME_NAME = "Suzy"
GRAVITY = 1.0

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

        self.player = None
        self.physics_engine = None


    def setup(self):
        """Инициализировать уровень игры"""

        map_name = get_resource_file_name(f"level_{self.level}.map.tmx")

        if not os.path.exists(map_name):
            self.win()
            return

        self.tile_map = arcade.load_tilemap(map_name, TILE_SCALING)
        self.scene = arcade.Scene.from_tilemap(self.tile_map)

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

    def on_key_release(self, key, modifiers):
        # проверка
        if key == arcade.key.ENTER:
            self.win()
        if key == arcade.key.Q:
            self.game_over()
        if key == arcade.key.UP:
            self.next_level()

    def on_show_view(self):
        self.setup()

    def on_draw(self):
        """Нарисовать кадр"""
        self.clear()
        self.scene.draw()

    def on_update(self, delta_time: float):
        self.physics_engine.update()

    def game_over(self):
        self.window.show_view(GameOverView())

    def win(self):
        self.window.show_view(WinView())

    def next_level(self):
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