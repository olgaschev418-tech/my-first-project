"""Задание 1. Вариант 2: сотрудники компании."""
from itertools import count


class Employee:
    _ids = count(1)

    def __init__(self):
        self.id = next(Employee._ids)


class ManagerSkills:
    def work(self):
        return f"{self.id}-й управляет"


class DeveloperSkills:
    def work(self):
        return f"{self.id}-й программирует"


class Manager(Employee, ManagerSkills):
    pass


class Developer(Employee, DeveloperSkills):
    pass


class TeamLead(Employee, ManagerSkills, DeveloperSkills):
    def work(self):
        # Явно объединяем одноимённые методы двух родителей.
        return (ManagerSkills.work(self) + "; "
                + DeveloperSkills.work(self))


def main():
    group = [Manager(), Developer(), Manager(), Developer()]
    print("Сотрудники компании")
    for employee in group:
        print(employee.work())
    print("MRO Manager:",
          " -> ".join(c.__name__ for c in Manager.__mro__))
    print("MRO Developer:",
          " -> ".join(c.__name__ for c in Developer.__mro__))
    lead = TeamLead()
    print("Совмещение обязанностей:", lead.work())
    print("MRO TeamLead:",
          " -> ".join(c.__name__ for c in TeamLead.__mro__))


if __name__ == "__main__":
    main()
