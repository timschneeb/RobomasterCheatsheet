from collections import deque


class ActionStack:
    def __init__(self):
        self.stack = deque()

    # Befehl auf Stack legen
    def push(self, command):
        self.stack.append(command)

    # Von Stack herunternehmen und zurückgeben
    def pop(self):
        return self.stack.pop()

    # Oberstes Objekt auf Stack zurückgeben, ohne es zu entfernen
    def peek(self):
        return self.stack[len(self.stack) - 1]

    def count(self):
        return len(self.stack)

    # Letzter Befehl rückgängig machen
    def undo(self):
        if self.count() > 0:
            self.pop().undo()
        else:
            print("ActionStack.undo(): Undo-Stack ist bereits leer")

    # Alles rückgängig machen
    def undo_all(self):
        while self.count() > 0:
            self.pop().undo()

    # Solange rückgängig machen, bis ein Checkpoint-Objekt auf dem Stack liegt
    def undo_until_checkpoint(self):
        while self.count() > 0:
            if self.peek().is_checkpoint():
                break
            self.pop().undo()
