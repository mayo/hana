import operator
import re

class MDMeta(type):
    def __getattr__(self, *args, **kwargs):
        return MD(*args, **kwargs)

    def __getitem__(self, name):
        return MD(name)

    # TODO: dates: between (times, dates) - is this simply > x, < x ?
    # TODO: dates: in the last x days
    # TODO: key name is defined/undefined

    # TODO: logic "key == x or key == y" etc.
    # TODO: more complex logic: [ [ 'title' == 'x' | title == 'y' ] & published_on < 1234 ]
        #                          [ [ KEY('title) == 'x' | KEY(title) == 'y' ] &

class MD(object, metaclass=MDMeta):

    def __init__(self, name, op=None, value=None, order='asc'):
        self.name = name

        if isinstance(name, str):
            self.name = (name,)

        self.op = op
        #TODO: this should be special None, so we can recognize it
        self.value = value
        self.order = order

    def __getitem__(self, item):
        #FIXME: this doesn't work in python2
        #self.name = (*self.name, item)
        name = list(self.name)
        name.append(item)
        self.name = tuple(name)
        return self

    def __hash__(self):
        return hash((self.name, self.value))

    # Predicates

    def __eq__(self, other):
        self.value = other
        self.op = operator.__eq__
        return self

    def __ne__(self, other):
        self.value = other
        self.op = operator.__ne__
        return self

    def __lt__(self, other):
        self.value = other
        self.op = operator.__lt__
        return self

    def __le__(self, other):
        self.value = other
        self.op = operator.__le__
        return self

    def __gt__(self, other):
        self.value = other
        self.op = operator.__gt__
        return self

    def __ge__(self, other):
        self.value = other
        self.op = operator.__ge__
        return self

    def in_(self, value):
        """Test membership
        """
        # NOTE: not defining __contains__, as the return value is forced to bool
        self.value = value
        self.op = operator.__contains__
        return self

    def nin(self, value):
        self.value = value
        self.op = lambda x, y: not operator.__contains__(x, y)
        return self

    def startswith(self, value):
        """String specific comparison
        """
        self.value = value
        self.op = lambda x, y: str(y).startswith(str(x))
        return self

    def endswith(self, value):
        """String specific comparison
        """
        self.value = value
        self.op = lambda x, y: str(y).endswith(str(x))
        return self

    def match(self, pattern, flags=0):
        """Matches regular expression.

        Takes same parameters as re.match()
        """
        self.value = re.compile(pattern, flags)
        self.op = lambda x, y: bool(x.match(str(y)))
        return self

    # Order

    def asc(self):
        self.order = 'asc'

    def desc(self):
        self.order = 'desc'

    # Evaluation

    def eval(self, value):
        return self.op(self.value, value)


