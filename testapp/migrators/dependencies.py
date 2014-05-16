class Spam1:
    depends_on = ['dependencies.Ham1']

class Ham1:
    depends_on = ['dependencies.Ham2', 'dependencies.Spam2']

class Ham2:
    pass

class Spam2:
    depends_on = ['dependencies.Spam1']

