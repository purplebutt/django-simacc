from django.test import TestCase
from utils import DEFPATH
from utils import auto_number_generator


def test_DEFPATH():
    DP = DEFPATH("BasePath")
    x  = DP / "nice"
    print(x)
    print("Test Result: ", x=="BasePath/nice")

def test_auto_number_generator():
    x = auto_number_generator()
    print(x)


#! program main entrance
if __name__ == '__main__':
    test_auto_number_generator()