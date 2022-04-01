import arcade
import os


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

    def setup(self):
        """Init game world"""

        map_name = f"{self.root_dir}/map.tmx"

        self.tile_map = arcade.load_tilemap(map_name, 0.5)
        self.scene = arcade.Scene.from_tilemap(self.tile_map)


    def on_show_view(self):
        self.setup()


    def on_draw(self):
        """Render game frame"""
        self.clear()
        self.scene.draw()


def main():
    window = arcade.Window(1024, 800, "Suzy")
    game_view = GameView()
    window.show_view(game_view)
    arcade.run()


if __name__ == "__main__":
    main()