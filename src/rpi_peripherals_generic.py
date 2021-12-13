import log

logger = log.get()

def init():
    logger.info("[RPI]: init begin")
    logger.info("[RPI]: init end")


def register_on_button_state_changed(func):
    pass


def loop():
    pass


def loop_test():
    init()
    while True:
        loop()


if __name__ == "__main__":
    import readline
    import rlcompleter
    import code

    readline.parse_and_bind("tab: complete")
    code.interact(local=locals())
