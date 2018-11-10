from rpidisplay import configuration
from rpidisplay import data
from rpidisplay import display


def main():
    configuration.setup_logging()
    configuration.setup_config()

    d = data.Data()
    d.schedule_data_download()

    dp = display.Display(d)
    dp.start()


if __name__ == '__main__':
    main()
