# encoding: utf8

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from twisted.internet import reactor

import threading

import Queue

class FileEventHandler(FileSystemEventHandler):

    def on_moved(self, event):
        e = ["moved", event.src_path, event.dest_path]
        self.queue(e)

    def on_created(self, event):
        e = ["created", event.src_path]
        self.queue(e)

    def on_deleted(self, event):
        e = ["deleted", event.src_path]
        self.queue(e)

    def on_modified(self, event):
        e = ["modify", event.src_path]
        self.queue(e)

    def queue(self, event):
        # 回调函数不在主线程 通过queue通知主线程
        Q.put(event)

observer, event_handler = None, None
# 不限制队列大小
Q = Queue.Queue()

def start_watch():
    global observer, event_handler
    observer = Observer()
    event_handler = FileEventHandler()
    observer.start()
    reactor.callLater(1, watcher)

def watch(path):
    print "watch", path
    global observer, event_handler
    observer.schedule(event_handler, path, True)

def watcher():
    reactor.callLater(1, watcher)
    try:
        import core
        while True:
            event = Q.get_nowait()
            path = event[1]
            project = core.Project.find(path)
            project.reinit()
    except Queue.Empty:
        return 

def stop_watch():
    observer.stop()
    observer.join()
    event_handler.stop()


