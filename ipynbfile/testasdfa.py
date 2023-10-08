class appple:
    School_Name = 'Aayaan'
    def __init__(self,m1,m2) -> None:
        self.apple = '12'
        self.m1 = m1
        self.m2 = m2
    def add(self):
        return (self.m1+self.m2)

    # @classmethod
    # def setter()

    @classmethod
    def info(cls):
        cls.School_Name = 'Pratham'
        return cls.School_Name

a = appple(2,3)
print(a.add())
print(appple.info())
