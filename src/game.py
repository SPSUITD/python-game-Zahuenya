import arcade
import os

GAME_NAME = "Suzy"
GAME_WINDOW_HEIGHT = 800
GAME_WINDOW_WIDTH = 1024


class GameView(arcade.View):
    """
    Главный класс игры
    """

    def __init__(self):
        """
        Функция инициализатор для объекта игры
        """
        super().__init__()

        self.root_dir = os.path.dirname(os.path.abspath(__file__))

        self.tile_map = None
        self.scene = None
        self.level = 1

    def setup(self):
        """Инициализировать уровень игры"""

        map_name = f"{self.root_dir}/level_{self.level}.map.tmx"

        self.tile_map = arcade.load_tilemap(map_name, 0.5)
        self.scene = arcade.Scene.from_tilemap(self.tile_map)

    def on_key_release(self, key, modifiers):
        # проверка
        self.game_over()

    def on_show_view(self):
        self.setup()

    def on_draw(self):
        """Нарисовать кадр"""
        self.clear()
        self.scene.draw()

    def game_over(self):
        game_over_view = GameOverView()
        self.window.show_view(game_over_view)


class GameOverView(arcade.View):
    """Вью для проигрыша"""

    def on_show_view(self):
        arcade.set_background_color(arcade.color.RED)

    def on_draw(self):
        self.clear()
        arcade.draw_text(
            "Потрачено",
            GAME_WINDOW_WIDTH / 2,
            GAME_WINDOW_HEIGHT / 2,
            arcade.color.BLACK,
            40,
            anchor_x="center",
        )

    def on_mouse_press(self, _x, _y, _button, _modifiers):
        game_view = GameView()
        self.window.show_view(game_view)


def main():
    window = arcade.Window(GAME_WINDOW_WIDTH, GAME_WINDOW_HEIGHT, GAME_NAME)
    game_view = GameView()
    window.show_view(game_view)
    arcade.run()


if __name__ == "__main__":
    main()