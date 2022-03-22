import arcade


class GameView(arcade.View):
    """
    Главный класс игры
    """

    def __init__(self):
        """
        Функция инициализатор для объекта игры
        """
        super().__init__()


def main():
    window = arcade.Window(1024, 800, "Suzy")
    game_view = GameView()
    window.show_view(game_view)
    arcade.run()


if __name__ == "__main__":
    main()