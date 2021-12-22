#!/usr/bin/env python3

__strict__ = True


class InvalidEnvironmentVariable(Exception):
    def __init__(self, *args):
        super().__init__(*args)


class TypeCheckException(Exception):
    def __init__(self, t: str, n: str, v: any, ):
        """
            Handle error where object (n) expects type (t) but gets type (v)
            :param t: expected type
            :param n: object name
            :param v: actual type
        """
        super().__init__(f"Expected {t} value in {n}, encountered {v}")


class IntegerMinBoundCheckError(Exception):
    def __init__(self, n: str, v: int, m: int):
        """
            Handle error where object (n) expects value (v) >= bound (m)
            :param n: str object name
            :param v: int object value
            :param m: int minimum value
        """
        super().__init__(f"Bounds Check Error: {n} value {v} less than {m}")


class IntegerMaxBoundCheckError(Exception):
    def __init__(self, n: str, v: int, m: int):
        """
            Handle error where object (n) expects value (v) <= bound (m)
            :param n: str object name
            :param v: int object value
            :param m: int maximum value
        """
        super().__init__(f"Bounds Check Error: {n} value {v} greater than {m}")


class StringValidationError(Exception):
    def __init__(self, n: str, p: str):
        super().__init__(f"{n} does not match expected pattern {p}")
