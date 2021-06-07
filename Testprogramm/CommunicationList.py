from datetime import datetime


class CommunicationList:
    """
    Funktionsweise der MessageQueue:
    Es wird grundsätzlich zwischen Sicheren (save=True) und nicht sicheren Nachrichten (ACK)
    unterschieden.

    Soll eine Nachricht verschickt werden -> put(msg, save)
        Daraufhin wird ein Zeitstempel der Nachricht hinzugefügt
        Anschließend wird die Nachricht als Array mit Zeitstempel in der Liste gespeichert -> [TxId, data, save, timestamp, count]

    Soll die Nachricht (save=True) aus dem Speicher gelöscht werden, z.b. bei ACK -> pop(RxId)
        Daraufhin wird die Nachricht mit dem passendem RxId-Wert aus der Liste gelöscht

    Soll die Nachricht ausgegeben werden, z.b. fürs versenden -> get()
        Gibt die letzte Nachricht aus bei (save=True)
        Wenn jedoch (save=False), dann wird die Nachricht zurückgeben und gelöscht.
    """
    def __init__(self):
        self.queue = list()

    def get(self):
        if len(self.queue) > 0:
            arr = self.queue[0]
            msg = arr[2]
            dlc = arr[1]
            id = bin(arr[0])
            self.queue.remove(arr)
            return id, dlc, msg
        return None, None, None

    def put(self, TxId, dlc, data, save, timestamp, count=0):
        if save is True:  # data
            pass
        else:  # ack
            timestamp = None
        self.queue.append([TxId, dlc, data, save, timestamp, count])
        return True

    def pop(self, RxId):
        for element in self.queue:
            if element[3] is True and element[0] == RxId:
                self.queue.remove(element)
                return True
        return False

    def size(self):
        return len(self.queue)

    def empty(self):
        if self.size() is 0:
            return True
        else:
            return False

    def clear(self):
        self.queue.clear()

    def ack_timeout(self):
        timelist = list()
        if self.empty():
            return 0
        else:
            try:
                for elem in self.queue:
                    if elem[2] is True:
                        timestamp = elem[3]
                        timelist.append(timestamp)

                last = max(timelist)
                now = datetime.now()
                elapsed = now - last
                return elapsed.total_seconds()
            except:
                return 0

    def __str__(self):
        return self.queue