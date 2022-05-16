from time import sleep


class Light:
    def __init__(self, previous=None):
        self.previous = previous

    def run(self):
        raise NotImplementedError

    def __next__(self):
        raise NotImplementedError


class Red(Light):
    color = 'Red'
    wait = 2

    def run(self):
        print(self.color)
        sleep(self.wait)

    def __next__(self):
        return Amber(previous=self)


class Amber(Light):
    color = 'Amber'
    wait = 1

    def run(self):
        print(self.color)
        sleep(self.wait)

    def __next__(self):
        if isinstance(self.previous, Red):
            return Green(previous=self)
        else:
            return Red(previous=self)


class Green(Light):
    color = 'Green'
    wait = 2

    def run(self):
        print(self.color)
        sleep(self.wait)

    def __next__(self):
        return Amber(previous=self)


class TrafficLights:
    def __init__(self, initial_state=Green(), max_changes=10):
        self.state = initial_state
        self.max_changes = max_changes

    def __iter__(self):
        self.changes = 0
        return self

    def __next__(self):
        if self.changes >= self.max_changes:
            raise StopIteration

        self.changes += 1
        self.state.run()
        self.state = next(self.state)
        return self


for light in TrafficLights(max_changes=10):
    pass