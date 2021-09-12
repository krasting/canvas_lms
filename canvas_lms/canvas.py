""" Canvas LMS Tools """

import pandas as pd
import numpy as np


class Student:
    """Object relating a student with a grade"""

    def __init__(self, name, idnum, sisid, sislogin, section, assignment, grade=0.0):
        """Initializes the object"""
        self.name = name
        name = name.replace("`", "").replace("-", "_")
        self.last = str(name.split(",")[0]).capitalize()
        self.first = str(name.split(",")[1].split(" ")[1]).capitalize()
        self.idnum = int(idnum)
        self.sisid = sisid
        self.sislogin = sislogin
        self.section = section
        self.key = f"{self.last}_{self.first}"
        self.assignment = assignment
        if isinstance(grade, np.float64):
            self.grade = 0.0 if np.isnan(grade) else grade
        else:
            self.grade = grade

    def update_grade(self, grade, verbose=True):
        """Updates a student's grade"""
        _old_grade = self.grade
        self.grade = float(grade)
        if verbose:
            print(f"{self.key} <{self.assignment}>:   {_old_grade} --> {self.grade}")

    def to_dict(self):
        """Returns a dictionary of data"""
        return {
            "Student": self.name,
            "ID": self.idnum,
            "SIS User ID": self.sisid,
            "SIS Login ID": self.sislogin,
            "Section": self.section,
            self.assignment: self.grade,
        }

    def __str__(self):
        return f"{self.last}, {self.first}  {self.sislogin} <{self.assignment}>:  {self.grade}"

    def __lt__(self, other):
        return self.key < other.key

    def __gt__(self, other):
        return self.key > other.key

    def __repr__(self):
        return self.key


class Assignment:
    """Object relating an assignment to a set of students"""

    def __init__(self, name, studentlist):
        self.name = name
        for student in studentlist:
            self.__dict__[student.key] = student

    def _formatter(self):
        result = ""
        for key in list(self.__dict__.keys()):
            result = result + (f"{str(self.__dict__[key])}\n")
        return result

    def to_dataframe(self):
        """Returns a Pandas DataFrame"""
        return pd.DataFrame(
            [v.to_dict() for k, v in self.__dict__.items() if k != "name"]
        ).set_index("Student")

    def __str__(self):
        return self._formatter()

    def __repr__(self):
        return self.name


class Gradebook:
    """Reads a CSV file containing a Canvas Gradebook"""

    def __init__(self, path):
        self.grades = pd.read_csv(path)
        self.path = path

        # assignments = list(self.grades.columns[5:])
        # assignment = assignments[0]

        self.assignments = [
            Assignment(
                assignment,
                [
                    Student(
                        self.grades.iloc[x]["Student"],
                        self.grades.iloc[x]["ID"],
                        self.grades.iloc[x]["SIS User ID"],
                        self.grades.iloc[x]["SIS Login ID"],
                        self.grades.iloc[x]["Section"],
                        assignment,
                        self.grades.iloc[x][assignment],
                    )
                    for x in range(1, len(self.grades) - 1)
                ],
            )
            for assignment in list(self.grades.columns[5:])
        ]

    def __repr__(self):
        return self.path

    def __str__(self):
        return str(self.grades)


class Group:
    """Object for a Group Assignment"""

    def __init__(
        self,
        assignment,
        number,
        prep=5.0,
        met=5.0,
        create=5.0,
        pres=5.0,
        bonus=0.0,
        members=None,
    ):
        self.assignment = assignment
        self.number = number
        self.prep = prep
        self.met = met
        self.create = create
        self.pres = pres
        self.members = [] if members is None else members
        self.bonus = bonus
        self.total = prep + met + create + pres + bonus

    def update(self, verbose=True):
        """Updates grades for group assignment"""
        if verbose:
            print(f"Updating group {self.number}")
            print("----------------------------")
        _ = [x.update_grade(self.total, verbose=verbose) for x in sorted(self.members)]
        if verbose:
            print("")

    def to_dict(self):
        """Returns a dictionary"""
        return {
            "Group Number": str(self.number),
            "Meteorology": str(int(self.met)),
            "Preparation": str(int(self.prep)),
            "Creativity": str(int(self.create)),
            "Presentation": str(int(self.pres)),
        }

    def __repr__(self):
        return f"<Group {self.number}>"

    def __lt__(self, other):
        return self.number < other.number

    def __gt__(self, other):
        return self.number > other.number
