from gui import BgRemoverApp

def run():
    """
    GUI 환경으로 프로그램을 시작하는 메인 진입점.
    """
    app = BgRemoverApp()
    app.mainloop()

if __name__ == "__main__":
    run()