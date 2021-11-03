# TO-DO list

- [x] logger decorator
- [x] move default used methods inside classes, like here:

```python
class This:

    def __init__(self):
        self.items = []
        self.__init_data()

    def __init_data(self):
        self.items = [... do somethings importent...]
```

- [x] **use multiprocessing for evaluate function** (test example of learning 13153.485339403152)
- [x] change and test crossower method (now it simple stohastic)
  - [ ] as idea - switch genome position only in one-day-line to one-day-line
- [x] change fitness function
  - [x] as idea - calculate function by period day + night. Then summarise all functions across all periods
- [ ] more precision for board data
  - [ ] collision calculation for units
  - [ ] calculate resource coldown needed for cities and workers for nonstohastic resource storage

![evolution](images/evolution.png)
