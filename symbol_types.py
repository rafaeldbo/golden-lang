from typing import Union, Tuple
from datetime import datetime, date, time, timedelta

NUMBER = "number"
STRING = "string"
BOOLEAN = "boolean"
DATE = "date"
TIME = "time"
LIST = "list"

class Date:
    value: date
    
    def __init__(self, value:str) -> None:
        self.value = datetime.strptime(value, "%Y-%m-%d").date()
    
    def __str__(self) -> str:
        return self.value.strftime("%Y-%m-%d")
    
    def __repr__(self) -> str:
        return f"Date(value={self.value})"
    
    def __add__(self, other: Union[int, float]) -> 'Date':
        if isinstance(other, (int, float)):
            return Date((self.value + timedelta(days=int(other))).strftime("%Y-%m-%d"))
        raise TypeError(f"Cannot sum {type(other)} to Date")
    
    def __sub__(self, other: Union[int, float, 'Date']) -> Union[int, 'Date']:
        if isinstance(other, int) or isinstance(other, float):
            return Date((self.value - timedelta(days=int(other))).strftime("%Y-%m-%d"))
        elif isinstance(other, Date):
            return (self.value - other.value).days
        raise TypeError(f"Cannot subtract {type(other)} from Date")
    
    def __eq__(self, other: 'Date') -> bool:
        if not isinstance(other, Date):
            raise TypeError(f"Expected Date, got {type(other)}")
        return self.value == other.value
    
    def __ne__(self, other: 'Date') -> bool:
        if not isinstance(other, Date):
            raise TypeError(f"Expected Date, got {type(other)}")
        return self.value != other.value
    
    def __lt__(self, other: 'Date') -> bool:
        if not isinstance(other, Date):
            raise TypeError(f"Expected Date, got {type(other)}")
        return self.value < other.value
    
    def __le__(self, other: 'Date') -> bool:
        if not isinstance(other, Date):
            raise TypeError(f"Expected Date, got {type(other)}")
        return self.value <= other.value
    
    def __gt__(self, other: 'Date') -> bool:
        if not isinstance(other, Date):
            raise TypeError(f"Expected Date, got {type(other)}")
        return self.value > other.value
    
    def __ge__(self, other: 'Date') -> bool:
        if not isinstance(other, Date):
            raise TypeError(f"Expected Date, got {type(other)}")
        return self.value >= other.value
    
    def dump(self) -> str:
        return self.value.strftime("%Y-%m-%d")


class Time:
    def __init__(self, value: str) -> None:
        self.value = datetime.strptime(value, "%H:%M").time()
        
    def __str__(self) -> str:
        return self.value.strftime("%H:%M")
    
    def __repr__(self) -> str:
        return f"Time(value={self.value})"
    
    def __add__(self, other: Union[int, float, 'Time']) -> 'Time':
        self_timedelta = timedelta(hours=self.value.hour, minutes=self.value.minute)
        if isinstance(other, (int, float)):
            seconds = (self_timedelta + timedelta(minutes=int(other))).seconds
            return Time(time((seconds//3600)%24, (seconds//60)%60, seconds%60).strftime("%H:%M"))
        elif isinstance(other, Time):
            self_timedelta += timedelta(hours=other.value.hour, minutes=other.value.minute)
            return Time(time((seconds//3600)%24, (seconds//60)%60, seconds%60).strftime("%H:%M"))
        raise TypeError(f"Cannot sum {type(other)} to Time")
    
    def __sub__(self, other: Union[int, float, 'Time']) -> 'Time':
        self_timedelta = timedelta(hours=self.value.hour, minutes=self.value.minute)
        if isinstance(other, (int, float)):
            seconds = (self_timedelta - timedelta(minutes=int(other))).seconds
            return Time(time((seconds//3600)%24, (seconds//60)%60, seconds%60).strftime("%H:%M"))
        elif isinstance(other, Time):
            seconds = (self_timedelta - timedelta(hours=other.value.hour, minutes=other.value.minute)).seconds
            return Time(time((seconds//3600)%24, (seconds//60)%60, seconds%60).strftime("%H:%M"))
        raise TypeError(f"Cannot subtract {type(other)} from Time")
    
    def __eq__(self, other: 'Time') -> bool:
        if not isinstance(other, Time):
            raise TypeError(f"Expected Time, got {type(other)}")
        return self.value == other.value
    
    def __ne__(self, other: 'Time') -> bool:
        if not isinstance(other, Time):
            raise TypeError(f"Expected Time, got {type(other)}")
        return self.value != other.value
    
    def __lt__(self, other: 'Time') -> bool:
        if not isinstance(other, Time):
            raise TypeError(f"Expected Time, got {type(other)}")
        return self.value < other.value
    
    def __le__(self, other: 'Time') -> bool:
        if not isinstance(other, Time):
            raise TypeError(f"Expected Time, got {type(other)}")
        return self.value <= other.value
    
    def __gt__(self, other: 'Time') -> bool:
        if not isinstance(other, Time):
            raise TypeError(f"Expected Time, got {type(other)}")
        return self.value > other.value
    
    def __ge__(self, other: 'Time') -> bool:
        if not isinstance(other, Time):
            raise TypeError(f"Expected Time, got {type(other)}")
        return self.value >= other.value
    
    def dump(self) -> str:
        return self.value.strftime("%H:%M")

class Symbol:
    type: str
    value: Union[float, str, bool]
    
    def __init__(self, symbol_type: str, value: Union[float, str, bool, Date, Time]=None) -> None:
        self.type = symbol_type
        self.value = value
    
    def __type_check(self, other: 'Symbol') -> str:
        if not isinstance(other, Symbol):
            raise TypeError(f"Expected Symbol, got {type(other)}")
        if self.type != other.type:
            raise TypeError(f"Type mismatch: expected {self.type}, got {other.type}")    
        return self.type
    
    def __eq__(self, other: 'Symbol') -> bool:
        self.__type_check(other)
        return Symbol(BOOLEAN, self.value == other.value)
    
    def __ne__(self, other: 'Symbol') -> bool:
        self.type_check(other)
        return Symbol(BOOLEAN, self.value != other.value)
    
    def __gt__(self, other: 'Symbol') -> bool:
        self.__type_check(other)
        return Symbol(BOOLEAN, self.value > other.value)
    
    def __lt__(self, other: 'Symbol') -> bool:
        self.__type_check(other)
        return Symbol(BOOLEAN, self.value < other.value)
    
    def __ge__(self, other: 'Symbol') -> bool:
        self.__type_check(other)
        return Symbol(BOOLEAN, self.value >= other.value)
    
    def __le__(self, other: 'Symbol') -> bool:
        self.__type_check(other)
        return Symbol(BOOLEAN, self.value <= other.value)
    
    def __add__(self, other: 'Symbol') -> 'Symbol':
        if not isinstance(other, Symbol):
            raise TypeError(f"Expected Symbol, got {type(other)}")
        
        elif self.type == STRING or other.type == STRING:
            return Symbol(STRING, str(self.value) + str(other.value))
        
        elif (self.type == DATE and other.type == NUMBER):
            return Symbol(DATE, self.value + other.value) 
        elif (self.type == NUMBER and other.type == DATE):
            return Symbol(DATE, other.value + self.value)
        
        elif (self.type == TIME and other.type == NUMBER):
            return Symbol(TIME, self.value + other.value)
        elif (self.type == NUMBER and other.type == TIME):
            return Symbol(TIME, other.value + self.value)
        
        elif self.type != other.type and self.type not in [NUMBER, TIME, LIST]:
            raise TypeError(f"Type mismatch: cannot add {self.type} and {other.type}")
        
        return Symbol(self.type, self.value + other.value)
    
    def __sub__(self, other: 'Symbol') -> 'Symbol':
        if not isinstance(other, Symbol):
            raise TypeError(f"Expected Symbol, got {type(other)}")
        if (self.type == DATE and other.type == NUMBER):
            return Symbol(DATE, self.value - other.value)
        elif (self.type == TIME and other.type == NUMBER):
            return Symbol(TIME, self.value - other.value)
        elif self.type != other.type and self.type not in [NUMBER, TIME]:
            raise TypeError(f"Type mismatch: cannot subtract {self.type} and {other.type}")
        return Symbol(self.type, self.value - other.value)
    
    def __mul__(self, other: 'Symbol') -> 'Symbol':
        symbol_type = self.__type_check(other)
        if symbol_type != NUMBER:
            raise TypeError(f"Cannot multiply {symbol_type} values")
        return Symbol(symbol_type, self.value * other.value)
    
    def __truediv__(self, other: 'Symbol') -> 'Symbol':
        symbol_type = self.__type_check(other)
        if symbol_type != NUMBER:
            raise TypeError(f"Cannot divide {symbol_type} values")
        if other.value == 0:
            raise ZeroDivisionError("Division by zero is not allowed")
        return Symbol(symbol_type, self.value / other.value)
    
    def __contains__(self, item: 'Symbol') -> bool:
        if self.type not in [STRING, LIST]:
            raise TypeError(f"Cannot use 'in' operator with {self.type} type")
        return item.value in self.value
    
    def __getitem__(self, index: Union[int, slice]) -> 'Symbol':
        if self.type not in [STRING, LIST]:
            raise TypeError(f"Cannot use indexing with {self.type} type")
        return Symbol(self.type, self.value[index])
        
    def __bool__(self) -> bool:
        if  self.type != BOOLEAN:
            raise TypeError(f"Cannot convert {self.type} to boolean")
        return self.value
    
    def __neg__(self) -> 'Symbol':
        if self.type != NUMBER:
            raise TypeError(f"Cannot negate {self.type} type")
        return Symbol(self.type, -self.value)
    
    def dump(self) -> Tuple[str, Union[float, str, bool, Date, Time]]:
        return (self.type, self.value)
    
    def __str__(self):
        if self.value is None:
            return "null"
        if self.type == BOOLEAN:
            return "true" if self.value else "false"
        return str(self.value)
    
    def __repr__(self) -> str:
        if self.value is None:
            return f"<{self.type.upper()}: UNINITIALIZED>"
        return f"<{self.type.upper()}: {self.value}>"