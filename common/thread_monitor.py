import threading
from typing import List, Type
import sys, os
from time import sleep
import traceback
import sdnotify

class ThreadMonitorExitStrategy:
    def _strategy_name(self):
        return ""

    def _log(self, message: str):
        print("[THREADMON.EXIT]" + message)

    def _on_check(self, dead: List[threading.Thread]):
        pass

class ThreadMonitorExitStrategyKillProcess(ThreadMonitorExitStrategy):
    def _strategy_name(self):
        return "KILL PROCESS"

    def _on_check(self, dead: List[threading.Thread]):
        if len(dead) > 0:
            self._log("[KILL]: killing process: os.kill(0, 9)")
            os.kill(0, 9)

class ThreadMonitorExitStrategyExitProcess(ThreadMonitorExitStrategy):
    def _strategy_name(self):
        return "EXIT PROCESS"

    def _on_check(self, dead: List[threading.Thread]):
        if len(dead) > 0:
            self._log("[EXIT]: exiting process: sys.exit(1)")
            sys.exit(1)

class ThreadMonitorExitStrategySystemdWatchdog(ThreadMonitorExitStrategy):
    def _strategy_name(self):
        return "SYSTEMD WATCHDOG TRIGGER"

    def __init__(self):
        self._systemd = sdnotify.SystemdNotifier()
        self._systemd.notify("READY=1")

    def _on_check(self, dead: List[threading.Thread]):
        if len(dead) > 0:
            self._log("[SYSTEMD]: stopping systemd notify and triggering systemd watchdog...")
            self._systemd.notify("WATCHDOG=trigger")
        else:
            self._systemd.notify("WATCHDOG=1")

class _ThreadMonitor:
    _DEFAULT_PERIOD = 5.0
    _DEFAULT_EXIT_STRATEGY = ThreadMonitorExitStrategyKillProcess()

    _instance = None
    _running = False

    @classmethod
    def instance(cls):
        if cls._instance is None:
            # create
            cls._instance = cls.__new__(cls)

            # initialize
            cls._instance._period = cls._DEFAULT_PERIOD
            cls._instance._exit_strategy = cls._DEFAULT_EXIT_STRATEGY

            strparams = ""
            strparams += "\tperiod = %.1fs\n" % (cls._instance._period)
            strparams += "\tstrategy = %s" % (cls._instance._exit_strategy._strategy_name())
            print("[THREADMON]: initializing:\n" + strparams)

            cls._instance._monitored = []
            cls._instance._mutex = threading.RLock()

            cls._instance._running = True
            cls._instance._thread = threading.Thread(target=cls._instance._loop)
            cls._instance._thread.start()
        return cls._instance

    def __init__(self):
        raise RuntimeError("ThreadMonitor is a singleton!")

    def set_period(self, period: float):
        self._period = period
        self._log("set period = %.1fs" % (self._period))

    def set_exit_strategy(self, exit_strategy: Type[ThreadMonitorExitStrategy]):
        self._exit_strategy = exit_strategy
        self._log("set exit strategy = %s" % (exit_strategy._strategy_name()))

    def _log(self, message: str):
        print("[THREADMON]: " + message)

    def _thrstr(self, thread: threading.Thread):
        return "{ name=%s; native_id=%s; ident=%s }" % (thread.name, thread.native_id, thread.ident)

    def _check(self, thread: threading.Thread):
        alive = thread.is_alive()
        if not alive:
            self._log("DEAD: " + self._thrstr(thread))
        return alive

    def _loop(self):
        while self._running:
            dead = []
            try:
                self._mutex.acquire()
                for thread in self._monitored:
                    if not self._check(thread):
                        dead.append(thread)
                self._mutex.release()
                if self._exit_strategy is not None:
                    self._exit_strategy._on_check(dead)
            except:
                self._log("Error! Thread check failed!")
                traceback.print_exc()
            sleep(self._period)

    def _watch(self, thread: threading.Thread):
        if thread not in self._monitored:
            self._monitored.append(thread)
            self._log("WATCH[total=%03d]: %s" % (len(self._monitored), self._thrstr(thread)))

    def watch_main_thread(self):
        self.watch(threading.main_thread())

    def watch(self, thread: threading.Thread):
        self._mutex.acquire()
        self._watch(thread)
        self._mutex.release()

    def watch_all(self, threads: List[threading.Thread]):
        self._mutex.acquire()
        for thread in threads:
            self._watch(thread)
        self._mutex.release()

    def stop(self):
        self._running = False

    def join(self):
        self._thread.join()

class ThreadMonitor:
    def __init__(self):
        raise RuntimeError("Cannot instantiate ThreadMonitor! Use the static methods directly!")

    @staticmethod
    def set_period(period: float):
        _ThreadMonitor.instance().set_period(period)

    @staticmethod
    def set_exit_strategy(exit_strategy: Type[ThreadMonitorExitStrategy]):
        _ThreadMonitor.instance().set_exit_strategy(exit_strategy)

    @staticmethod
    def watch_main_thread():
        _ThreadMonitor.instance().watch_main_thread()

    @staticmethod
    def watch(thread: threading.Thread):
        _ThreadMonitor.instance().watch(thread)

    @staticmethod
    def watch_all(threads: List[threading.Thread]):
        _ThreadMonitor.instance().watch_all(threads)

    @staticmethod
    def stop():
        _ThreadMonitor.instance().stop()

    @staticmethod
    def join():
        _ThreadMonitor.instance().join()
