# TO-DO list

- [x] logger decorator
- [ ] move default used methods inside classes, like here:

```python
class This:

    def __init__(self):
        self.items = []
        self.__init_data()

    def __init_data(self):
        self.items = [... do somethings importent...]
```

- [ ] **use multiprocessing for evaluate function** (test example of learning 13153.485339403152)
- [ ] change and test crossower method (now it simple stohastic)
  - [ ] as idea - switch genome position only in one-day-line to one-day-line
- [ ] change fitness function
  - [ ] as idea - calculate function by period day + night. Then summarise all functions across all periods
- [ ] more precision for board data
  - [ ] collision calculation for units
  - [ ] calculate resource coldown needed for cities and workers for nonstohastic resource storage

![evolution](images/evolution.png)
