from __init__ import CURSOR, CONN
from department import Department
from employee import Employee


class Review:

    # Dictionary of objects saved to the database.
    all = {}

    def __init__(self, year, summary, employee_id, id=None):
        self.id = id
        self._year = None
        self.year = year
        self._summary = None
        self.summary = summary
        self._employee_id = None
        self.employee_id = employee_id
        
    @property
    def employee_id(self):
        return self._employee_id
    
    @employee_id.setter
    def employee_id(self, employee_id):
        if not isinstance(employee_id, int) or not Employee.find_by_id(employee_id):
            raise ValueError("employee_id must be a valid employee id")
        self._employee_id = employee_id
        
    @property
    def summary(self):
        return self._summary
    
    @summary.setter
    def summary(self, summary):
        if not isinstance(summary, str) or len(summary) == 0:
            raise ValueError("summary must be a non-empty string")
        self._summary = summary
        
    @property
    def year(self):
        return self._year
    
    @year.setter
    def year(self, year):
        if not isinstance(year, int):
            raise ValueError("year must be an integer")
        if year < 2000:
            raise ValueError("year must be at least 2000")
        self._year = year

    def __repr__(self):
        return (
            f"<Review {self.id}: {self.year}, {self.summary}, "
            + f"Employee: {self.employee_id}>"
        )

    @classmethod
    def create_table(cls):
        """ Create a new table to persist the attributes of Review instances """
        sql = """
            CREATE TABLE IF NOT EXISTS reviews (
            id INTEGER PRIMARY KEY,
            year INT,
            summary TEXT,
            employee_id INTEGER,
            FOREIGN KEY (employee_id) REFERENCES employee(id))
        """
        CURSOR.execute(sql)
        CONN.commit()

    @classmethod
    def drop_table(cls):
        """ Drop the table that persists Review  instances """
        sql = """
            DROP TABLE IF EXISTS reviews;
        """
        CURSOR.execute(sql)
        CONN.commit()

    def save(self):
        if self.id is None:
            sql = """
                INSERT INTO reviews (year, summary, employee_id)
                VALUES (?,?,?)
            """
            CURSOR.execute(sql, (self.year, self.summary, self.employee_id))
            CONN.commit()
            self.id = CURSOR.lastrowid

    @classmethod
    def create(cls, year, summary, employee_id):
        review = cls(year, summary, employee_id)
        review.save()
        return review
   
    @classmethod
    def instance_from_db(cls, row):
        # Check the dictionary for  existing instance using the row's primary key
        review_id, year, summary, employee_id = row
        if review_id in cls.all:
            review = cls.all[review_id]
            review.year, review.summary, review. employee_id = year, summary, employee_id
        else:
            review = cls(year, summary, employee_id, review_id)
            cls.all[review_id] = review
        return review
   

    @classmethod
    def find_by_id(cls, id):
        sql = "Select * FROM reviews WHERE id= ?"
        CURSOR.execute(sql, (id,))
        row = CURSOR.fetchone()
        if row:
            return cls.instance_from_db(row)
        return None

    def update(self):
        if self.id is not None:
            sql = """
                UPDATE reviews
                SET year = ?, summary = ?, employee_id = ?
                WHERE id = ?
            """
            CURSOR.execute(sql, (self.year, self.summary, self.employee_id, self.id))
            CONN.commit()
        else:
            raise ValueError("This review does not have an ID and cannot be updated.")

    def delete(self):
        if self.id is not None:
            sql = """
                DELETE FROM reviews
                WHERE id = ?
            """
            CURSOR.execute(sql, (self.id,))
            CONN.commit()
            if self.id in Review.all:
                del Review.all[self.id]
            self.id = None
        else:
            raise ValueError("This review does not have an ID and cannot be deleted.")

    @classmethod
    def get_all(cls):
        sql = "SELECT * FROM reviews"
        CURSOR.execute(sql)
        rows = CURSOR.fetchall()
        return [cls.instance_from_db(row) for row in rows]

