"""
Import all 50 students into MongoDB
Run: python import_50_students.py
"""

from pymongo import MongoClient
from models import MONGO_URI, DB_NAME
from datetime import datetime, timedelta
import random

# Complete student data (all 50 students)
STUDENT_DATA = [
    # Student 1 - Arjun Mehta
    {'reg_no': '231FA04001', 'name': 'Arjun Mehta', 'parent_phone': '9876543211', 'status': 'Active', 'backlogs': 0, 'year': 3, 'cgpa': 6.41,
     'marks': [
         {'sem': 1, 'subject': 'Programming in C', 'att': 67, 'marks': 89, 'gp': 8.9, 'backlog': False},
         {'sem': 1, 'subject': 'Engineering Mathematics', 'att': 95, 'marks': 36, 'gp': 3.6, 'backlog': True, 'backlog_type': 'Incomplete'},
         {'sem': 1, 'subject': 'Engineering Physics', 'att': 94, 'marks': 97, 'gp': 9.7, 'backlog': False},
         {'sem': 1, 'subject': 'Basic Electronics', 'att': 82, 'marks': 55, 'gp': 5.5, 'backlog': False},
         {'sem': 1, 'subject': 'Communication Skills', 'att': 67, 'marks': 97, 'gp': 9.7, 'backlog': False},
         {'sem': 2, 'subject': 'Data Structures', 'att': 85, 'marks': 44, 'gp': 4.4, 'backlog': True, 'backlog_type': 'Incomplete'},
         {'sem': 2, 'subject': 'Discrete Mathematics', 'att': 88, 'marks': 40, 'gp': 4.0, 'backlog': True, 'backlog_type': 'Repeat Grade'},
         {'sem': 2, 'subject': 'Digital Logic', 'att': 73, 'marks': 80, 'gp': 8.0, 'backlog': False},
         {'sem': 2, 'subject': 'Environmental Science', 'att': 89, 'marks': 88, 'gp': 8.8, 'backlog': False},
         {'sem': 2, 'subject': 'Python Programming', 'att': 83, 'marks': 68, 'gp': 6.8, 'backlog': False},
         {'sem': 3, 'subject': 'DBMS', 'att': 94, 'marks': 57, 'gp': 5.7, 'backlog': False},
         {'sem': 3, 'subject': 'Operating Systems', 'att': 84, 'marks': 81, 'gp': 8.1, 'backlog': False},
         {'sem': 3, 'subject': 'Computer Organization', 'att': 73, 'marks': 93, 'gp': 9.3, 'backlog': False},
         {'sem': 3, 'subject': 'Probability & Statistics', 'att': 80, 'marks': 91, 'gp': 9.1, 'backlog': False},
         {'sem': 3, 'subject': 'Java Programming', 'att': 89, 'marks': 40, 'gp': 4.0, 'backlog': True, 'backlog_type': 'Incomplete'},
         {'sem': 4, 'subject': 'Computer Networks', 'att': 80, 'marks': 52, 'gp': 5.2, 'backlog': False},
         {'sem': 4, 'subject': 'Software Engineering', 'att': 77, 'marks': 73, 'gp': 7.3, 'backlog': False},
         {'sem': 4, 'subject': 'Theory of Computation', 'att': 88, 'marks': 65, 'gp': 6.5, 'backlog': False},
         {'sem': 4, 'subject': 'Web Technologies', 'att': 85, 'marks': 92, 'gp': 9.2, 'backlog': False},
         {'sem': 4, 'subject': 'Open Elective', 'att': 92, 'marks': 95, 'gp': 9.5, 'backlog': False},
         {'sem': 5, 'subject': 'Artificial Intelligence', 'att': 69, 'marks': 76, 'gp': 7.6, 'backlog': False},
         {'sem': 5, 'subject': 'Machine Learning', 'att': 97, 'marks': 55, 'gp': 5.5, 'backlog': False},
         {'sem': 5, 'subject': 'Cloud Computing', 'att': 79, 'marks': 87, 'gp': 8.7, 'backlog': False},
         {'sem': 5, 'subject': 'Data Mining', 'att': 80, 'marks': 39, 'gp': 3.9, 'backlog': True, 'backlog_type': 'Incomplete'},
         {'sem': 5, 'subject': 'Mini Project', 'att': 96, 'marks': 73, 'gp': 7.3, 'backlog': False},
         {'sem': 6, 'subject': 'Big Data Analytics', 'att': 69, 'marks': 45, 'gp': 4.5, 'backlog': True, 'backlog_type': 'Incomplete'},
         {'sem': 6, 'subject': 'Internet of Things', 'att': 89, 'marks': 82, 'gp': 8.2, 'backlog': False},
         {'sem': 6, 'subject': 'Cyber Security', 'att': 74, 'marks': 49, 'gp': 4.9, 'backlog': True, 'backlog_type': 'Incomplete'},
         {'sem': 6, 'subject': 'Major Project', 'att': 93, 'marks': 56, 'gp': 5.6, 'backlog': False},
         {'sem': 6, 'subject': 'Professional Ethics', 'att': 77, 'marks': 79, 'gp': 7.9, 'backlog': False},
     ], 'scholarship': False, 'scholarship_amt': 0},
    
    # Student 2 - Priya Sharma
    {'reg_no': '231FA04002', 'name': 'Priya Sharma', 'parent_phone': '9823456780', 'status': 'Active', 'backlogs': 1, 'year': 3, 'cgpa': 6.82,
     'marks': [
         {'sem': 1, 'subject': 'Programming in C', 'att': 92, 'marks': 88, 'gp': 8.8, 'backlog': False},
         {'sem': 1, 'subject': 'Engineering Mathematics', 'att': 93, 'marks': 66, 'gp': 6.6, 'backlog': False},
         {'sem': 1, 'subject': 'Engineering Physics', 'att': 82, 'marks': 53, 'gp': 5.3, 'backlog': False},
         {'sem': 1, 'subject': 'Basic Electronics', 'att': 98, 'marks': 57, 'gp': 5.7, 'backlog': False},
         {'sem': 1, 'subject': 'Communication Skills', 'att': 72, 'marks': 69, 'gp': 6.9, 'backlog': False},
         {'sem': 2, 'subject': 'Data Structures', 'att': 94, 'marks': 73, 'gp': 7.3, 'backlog': False},
         {'sem': 2, 'subject': 'Discrete Mathematics', 'att': 75, 'marks': 57, 'gp': 5.7, 'backlog': False},
         {'sem': 2, 'subject': 'Digital Logic', 'att': 76, 'marks': 96, 'gp': 9.6, 'backlog': False},
         {'sem': 2, 'subject': 'Environmental Science', 'att': 87, 'marks': 76, 'gp': 7.6, 'backlog': False},
         {'sem': 2, 'subject': 'Python Programming', 'att': 92, 'marks': 63, 'gp': 6.3, 'backlog': False},
         {'sem': 3, 'subject': 'DBMS', 'att': 65, 'marks': 40, 'gp': 4.0, 'backlog': True, 'backlog_type': 'Repeat Grade'},
         {'sem': 3, 'subject': 'Operating Systems', 'att': 85, 'marks': 66, 'gp': 6.6, 'backlog': False},
         {'sem': 3, 'subject': 'Computer Organization', 'att': 70, 'marks': 68, 'gp': 6.8, 'backlog': False},
         {'sem': 3, 'subject': 'Probability & Statistics', 'att': 93, 'marks': 86, 'gp': 8.6, 'backlog': False},
         {'sem': 3, 'subject': 'Java Programming', 'att': 75, 'marks': 84, 'gp': 8.4, 'backlog': False},
         {'sem': 4, 'subject': 'Computer Networks', 'att': 96, 'marks': 65, 'gp': 6.5, 'backlog': False},
         {'sem': 4, 'subject': 'Software Engineering', 'att': 98, 'marks': 69, 'gp': 6.9, 'backlog': False},
         {'sem': 4, 'subject': 'Theory of Computation', 'att': 98, 'marks': 96, 'gp': 9.6, 'backlog': False},
         {'sem': 4, 'subject': 'Web Technologies', 'att': 96, 'marks': 43, 'gp': 4.3, 'backlog': True, 'backlog_type': 'Incomplete'},
         {'sem': 4, 'subject': 'Open Elective', 'att': 96, 'marks': 94, 'gp': 9.4, 'backlog': False},
         {'sem': 5, 'subject': 'Artificial Intelligence', 'att': 90, 'marks': 52, 'gp': 5.2, 'backlog': False},
         {'sem': 5, 'subject': 'Machine Learning', 'att': 91, 'marks': 79, 'gp': 7.9, 'backlog': False},
         {'sem': 5, 'subject': 'Cloud Computing', 'att': 89, 'marks': 97, 'gp': 9.7, 'backlog': False},
         {'sem': 5, 'subject': 'Data Mining', 'att': 75, 'marks': 91, 'gp': 9.1, 'backlog': False},
         {'sem': 5, 'subject': 'Mini Project', 'att': 71, 'marks': 88, 'gp': 8.8, 'backlog': False},
         {'sem': 6, 'subject': 'Big Data Analytics', 'att': 67, 'marks': 35, 'gp': 3.5, 'backlog': True, 'backlog_type': 'Repeat Grade'},
         {'sem': 6, 'subject': 'Internet of Things', 'att': 69, 'marks': 41, 'gp': 4.1, 'backlog': True, 'backlog_type': 'Repeat Grade'},
         {'sem': 6, 'subject': 'Cyber Security', 'att': 70, 'marks': 54, 'gp': 5.4, 'backlog': False},
         {'sem': 6, 'subject': 'Major Project', 'att': 71, 'marks': 93, 'gp': 9.3, 'backlog': False},
         {'sem': 6, 'subject': 'Professional Ethics', 'att': 96, 'marks': 52, 'gp': 5.2, 'backlog': False},
     ], 'scholarship': False, 'scholarship_amt': 0},
    
    # Student 3 - Rahul Verma
    {'reg_no': '231FA04003', 'name': 'Rahul Verma', 'parent_phone': '9812345670', 'status': 'Active', 'backlogs': 2, 'year': 3, 'cgpa': 7.07,
     'marks': [
         {'sem': 1, 'subject': 'Programming in C', 'att': 94, 'marks': 90, 'gp': 9.0, 'backlog': False},
         {'sem': 1, 'subject': 'Engineering Mathematics', 'att': 97, 'marks': 92, 'gp': 9.2, 'backlog': False},
         {'sem': 1, 'subject': 'Engineering Physics', 'att': 86, 'marks': 68, 'gp': 6.8, 'backlog': False},
         {'sem': 1, 'subject': 'Basic Electronics', 'att': 94, 'marks': 89, 'gp': 8.9, 'backlog': False},
         {'sem': 1, 'subject': 'Communication Skills', 'att': 86, 'marks': 54, 'gp': 5.4, 'backlog': False},
         {'sem': 2, 'subject': 'Data Structures', 'att': 80, 'marks': 76, 'gp': 7.6, 'backlog': False},
         {'sem': 2, 'subject': 'Discrete Mathematics', 'att': 67, 'marks': 60, 'gp': 6.0, 'backlog': False},
         {'sem': 2, 'subject': 'Digital Logic', 'att': 95, 'marks': 38, 'gp': 3.8, 'backlog': True, 'backlog_type': 'Incomplete'},
         {'sem': 2, 'subject': 'Environmental Science', 'att': 83, 'marks': 90, 'gp': 9.0, 'backlog': False},
         {'sem': 2, 'subject': 'Python Programming', 'att': 80, 'marks': 72, 'gp': 7.2, 'backlog': False},
         {'sem': 3, 'subject': 'DBMS', 'att': 70, 'marks': 40, 'gp': 4.0, 'backlog': True, 'backlog_type': 'Incomplete'},
         {'sem': 3, 'subject': 'Operating Systems', 'att': 83, 'marks': 55, 'gp': 5.5, 'backlog': False},
         {'sem': 3, 'subject': 'Computer Organization', 'att': 95, 'marks': 53, 'gp': 5.3, 'backlog': False},
         {'sem': 3, 'subject': 'Probability & Statistics', 'att': 88, 'marks': 86, 'gp': 8.6, 'backlog': False},
         {'sem': 3, 'subject': 'Java Programming', 'att': 77, 'marks': 79, 'gp': 7.9, 'backlog': False},
         {'sem': 4, 'subject': 'Computer Networks', 'att': 76, 'marks': 45, 'gp': 4.5, 'backlog': True, 'backlog_type': 'Incomplete'},
         {'sem': 4, 'subject': 'Software Engineering', 'att': 92, 'marks': 61, 'gp': 6.1, 'backlog': False},
         {'sem': 4, 'subject': 'Theory of Computation', 'att': 71, 'marks': 74, 'gp': 7.4, 'backlog': False},
         {'sem': 4, 'subject': 'Web Technologies', 'att': 94, 'marks': 89, 'gp': 8.9, 'backlog': False},
         {'sem': 4, 'subject': 'Open Elective', 'att': 93, 'marks': 61, 'gp': 6.1, 'backlog': False},
         {'sem': 5, 'subject': 'Artificial Intelligence', 'att': 82, 'marks': 81, 'gp': 8.1, 'backlog': False},
         {'sem': 5, 'subject': 'Machine Learning', 'att': 72, 'marks': 35, 'gp': 3.5, 'backlog': True, 'backlog_type': 'Incomplete'},
         {'sem': 5, 'subject': 'Cloud Computing', 'att': 92, 'marks': 87, 'gp': 8.7, 'backlog': False},
         {'sem': 5, 'subject': 'Data Mining', 'att': 89, 'marks': 60, 'gp': 6.0, 'backlog': False},
         {'sem': 5, 'subject': 'Mini Project', 'att': 69, 'marks': 89, 'gp': 8.9, 'backlog': False},
         {'sem': 6, 'subject': 'Big Data Analytics', 'att': 70, 'marks': 42, 'gp': 4.2, 'backlog': True, 'backlog_type': 'Repeat Grade'},
         {'sem': 6, 'subject': 'Internet of Things', 'att': 81, 'marks': 81, 'gp': 8.1, 'backlog': False},
         {'sem': 6, 'subject': 'Cyber Security', 'att': 94, 'marks': 89, 'gp': 8.9, 'backlog': False},
         {'sem': 6, 'subject': 'Major Project', 'att': 77, 'marks': 71, 'gp': 7.1, 'backlog': False},
         {'sem': 6, 'subject': 'Professional Ethics', 'att': 94, 'marks': 72, 'gp': 7.2, 'backlog': False},
     ], 'scholarship': False, 'scholarship_amt': 0},
    
    # Student 4 - Sneha Patel (Scholar)
    {'reg_no': '231FA04004', 'name': 'Sneha Patel', 'parent_phone': '9898765430', 'status': 'Active (Scholar)', 'backlogs': 0, 'year': 3, 'cgpa': 6.61,
     'marks': [
         {'sem': 1, 'subject': 'Programming in C', 'att': 97, 'marks': 98, 'gp': 9.8, 'backlog': False},
         {'sem': 1, 'subject': 'Engineering Mathematics', 'att': 97, 'marks': 68, 'gp': 6.8, 'backlog': False},
         {'sem': 1, 'subject': 'Engineering Physics', 'att': 90, 'marks': 91, 'gp': 9.1, 'backlog': False},
         {'sem': 1, 'subject': 'Basic Electronics', 'att': 86, 'marks': 79, 'gp': 7.9, 'backlog': False},
         {'sem': 1, 'subject': 'Communication Skills', 'att': 82, 'marks': 96, 'gp': 9.6, 'backlog': False},
         {'sem': 2, 'subject': 'Data Structures', 'att': 93, 'marks': 96, 'gp': 9.6, 'backlog': False},
         {'sem': 2, 'subject': 'Discrete Mathematics', 'att': 95, 'marks': 45, 'gp': 4.5, 'backlog': True, 'backlog_type': 'Repeat Grade'},
         {'sem': 2, 'subject': 'Digital Logic', 'att': 90, 'marks': 56, 'gp': 5.6, 'backlog': False},
         {'sem': 2, 'subject': 'Environmental Science', 'att': 91, 'marks': 43, 'gp': 4.3, 'backlog': True, 'backlog_type': 'Repeat Grade'},
         {'sem': 2, 'subject': 'Python Programming', 'att': 66, 'marks': 76, 'gp': 7.6, 'backlog': False},
         {'sem': 3, 'subject': 'DBMS', 'att': 85, 'marks': 44, 'gp': 4.4, 'backlog': True, 'backlog_type': 'Repeat Grade'},
         {'sem': 3, 'subject': 'Operating Systems', 'att': 88, 'marks': 71, 'gp': 7.1, 'backlog': False},
         {'sem': 3, 'subject': 'Computer Organization', 'att': 76, 'marks': 65, 'gp': 6.5, 'backlog': False},
         {'sem': 3, 'subject': 'Probability & Statistics', 'att': 75, 'marks': 74, 'gp': 7.4, 'backlog': False},
         {'sem': 3, 'subject': 'Java Programming', 'att': 71, 'marks': 41, 'gp': 4.1, 'backlog': True, 'backlog_type': 'Incomplete'},
         {'sem': 4, 'subject': 'Computer Networks', 'att': 69, 'marks': 88, 'gp': 8.8, 'backlog': False},
         {'sem': 4, 'subject': 'Software Engineering', 'att': 77, 'marks': 91, 'gp': 9.1, 'backlog': False},
         {'sem': 4, 'subject': 'Theory of Computation', 'att': 66, 'marks': 85, 'gp': 8.5, 'backlog': False},
         {'sem': 4, 'subject': 'Web Technologies', 'att': 77, 'marks': 78, 'gp': 7.8, 'backlog': False},
         {'sem': 4, 'subject': 'Open Elective', 'att': 77, 'marks': 76, 'gp': 7.6, 'backlog': False},
         {'sem': 5, 'subject': 'Artificial Intelligence', 'att': 68, 'marks': 41, 'gp': 4.1, 'backlog': True, 'backlog_type': 'Incomplete'},
         {'sem': 5, 'subject': 'Machine Learning', 'att': 88, 'marks': 85, 'gp': 8.5, 'backlog': False},
         {'sem': 5, 'subject': 'Cloud Computing', 'att': 85, 'marks': 56, 'gp': 5.6, 'backlog': False},
         {'sem': 5, 'subject': 'Data Mining', 'att': 75, 'marks': 50, 'gp': 5.0, 'backlog': False},
         {'sem': 5, 'subject': 'Mini Project', 'att': 87, 'marks': 56, 'gp': 5.6, 'backlog': False},
         {'sem': 6, 'subject': 'Big Data Analytics', 'att': 66, 'marks': 100, 'gp': 10.0, 'backlog': False},
         {'sem': 6, 'subject': 'Internet of Things', 'att': 87, 'marks': 46, 'gp': 4.6, 'backlog': True, 'backlog_type': 'Repeat Grade'},
         {'sem': 6, 'subject': 'Cyber Security', 'att': 93, 'marks': 79, 'gp': 7.9, 'backlog': False},
         {'sem': 6, 'subject': 'Major Project', 'att': 68, 'marks': 53, 'gp': 5.3, 'backlog': False},
         {'sem': 6, 'subject': 'Professional Ethics', 'att': 93, 'marks': 95, 'gp': 9.5, 'backlog': False},
     ], 'scholarship': True, 'scholarship_amt': 40000},
    
    # Student 5 - Vikram Nair (At Risk)
    {'reg_no': '231FA04005', 'name': 'Vikram Nair', 'parent_phone': '9945678900', 'status': 'At Risk', 'backlogs': 3, 'year': 3, 'cgpa': 7.62,
     'marks': [
         {'sem': 1, 'subject': 'Programming in C', 'att': 93, 'marks': 91, 'gp': 9.1, 'backlog': False},
         {'sem': 1, 'subject': 'Engineering Mathematics', 'att': 76, 'marks': 80, 'gp': 8.0, 'backlog': False},
         {'sem': 1, 'subject': 'Engineering Physics', 'att': 92, 'marks': 78, 'gp': 7.8, 'backlog': False},
         {'sem': 1, 'subject': 'Basic Electronics', 'att': 97, 'marks': 93, 'gp': 9.3, 'backlog': False},
         {'sem': 1, 'subject': 'Communication Skills', 'att': 89, 'marks': 59, 'gp': 5.9, 'backlog': False},
         {'sem': 2, 'subject': 'Data Structures', 'att': 71, 'marks': 90, 'gp': 9.0, 'backlog': False},
         {'sem': 2, 'subject': 'Discrete Mathematics', 'att': 74, 'marks': 40, 'gp': 4.0, 'backlog': True, 'backlog_type': 'Incomplete'},
         {'sem': 2, 'subject': 'Digital Logic', 'att': 77, 'marks': 89, 'gp': 8.9, 'backlog': False},
         {'sem': 2, 'subject': 'Environmental Science', 'att': 88, 'marks': 83, 'gp': 8.3, 'backlog': False},
         {'sem': 2, 'subject': 'Python Programming', 'att': 68, 'marks': 41, 'gp': 4.1, 'backlog': True, 'backlog_type': 'Incomplete'},
         {'sem': 3, 'subject': 'DBMS', 'att': 84, 'marks': 63, 'gp': 6.3, 'backlog': False},
         {'sem': 3, 'subject': 'Operating Systems', 'att': 68, 'marks': 57, 'gp': 5.7, 'backlog': False},
         {'sem': 3, 'subject': 'Computer Organization', 'att': 71, 'marks': 81, 'gp': 8.1, 'backlog': False},
         {'sem': 3, 'subject': 'Probability & Statistics', 'att': 76, 'marks': 73, 'gp': 7.3, 'backlog': False},
         {'sem': 3, 'subject': 'Java Programming', 'att': 67, 'marks': 85, 'gp': 8.5, 'backlog': False},
         {'sem': 4, 'subject': 'Computer Networks', 'att': 92, 'marks': 44, 'gp': 4.4, 'backlog': True, 'backlog_type': 'Repeat Grade'},
         {'sem': 4, 'subject': 'Software Engineering', 'att': 77, 'marks': 97, 'gp': 9.7, 'backlog': False},
         {'sem': 4, 'subject': 'Theory of Computation', 'att': 75, 'marks': 56, 'gp': 5.6, 'backlog': False},
         {'sem': 4, 'subject': 'Web Technologies', 'att': 90, 'marks': 94, 'gp': 9.4, 'backlog': False},
         {'sem': 4, 'subject': 'Open Elective', 'att': 86, 'marks': 39, 'gp': 3.9, 'backlog': True, 'backlog_type': 'Incomplete'},
         {'sem': 5, 'subject': 'Artificial Intelligence', 'att': 76, 'marks': 88, 'gp': 8.8, 'backlog': False},
         {'sem': 5, 'subject': 'Machine Learning', 'att': 74, 'marks': 100, 'gp': 10.0, 'backlog': False},
         {'sem': 5, 'subject': 'Cloud Computing', 'att': 90, 'marks': 47, 'gp': 4.7, 'backlog': True, 'backlog_type': 'Repeat Grade'},
         {'sem': 5, 'subject': 'Data Mining', 'att': 72, 'marks': 65, 'gp': 6.5, 'backlog': False},
         {'sem': 5, 'subject': 'Mini Project', 'att': 71, 'marks': 89, 'gp': 8.9, 'backlog': False},
         {'sem': 6, 'subject': 'Big Data Analytics', 'att': 84, 'marks': 72, 'gp': 7.2, 'backlog': False},
         {'sem': 6, 'subject': 'Internet of Things', 'att': 71, 'marks': 79, 'gp': 7.9, 'backlog': False},
         {'sem': 6, 'subject': 'Cyber Security', 'att': 98, 'marks': 95, 'gp': 9.5, 'backlog': False},
         {'sem': 6, 'subject': 'Major Project', 'att': 80, 'marks': 72, 'gp': 7.2, 'backlog': False},
         {'sem': 6, 'subject': 'Professional Ethics', 'att': 65, 'marks': 55, 'gp': 5.5, 'backlog': False},
     ], 'scholarship': False, 'scholarship_amt': 0},
]

# Add remaining 45 students (simplified for brevity - you can expand this)
ADDITIONAL_STUDENTS = [
    {'reg_no': '231FA04006', 'name': 'Ananya Reddy', 'parent_phone': '9876512340', 'status': 'Active', 'backlogs': 0, 'year': 3, 'cgpa': 6.84},
    {'reg_no': '231FA04007', 'name': 'Rohit Singh', 'parent_phone': '9834567812', 'status': 'Active', 'backlogs': 1, 'year': 3, 'cgpa': 6.12},
    {'reg_no': '231FA04008', 'name': 'Kavya Iyer', 'parent_phone': '9845671234', 'status': 'Active', 'backlogs': 0, 'year': 3, 'cgpa': 6.62},
    {'reg_no': '231FA04009', 'name': 'Aman Gupta', 'parent_phone': '9811122233', 'status': 'Active', 'backlogs': 2, 'year': 3, 'cgpa': 6.96},
    {'reg_no': '231FA04010', 'name': 'Pooja Desai', 'parent_phone': '9822233344', 'status': 'Active', 'backlogs': 0, 'year': 3, 'cgpa': 6.82},
    {'reg_no': '231FA04011', 'name': 'Karan Malhotra', 'parent_phone': '9833344455', 'status': 'Active', 'backlogs': 1, 'year': 3, 'cgpa': 6.95},
    {'reg_no': '231FA04012', 'name': 'Meera Nair', 'parent_phone': '9844455566', 'status': 'Active (Scholar)', 'backlogs': 0, 'year': 3, 'cgpa': 6.83, 'scholarship': True, 'scholarship_amt': 40000},
    {'reg_no': '231FA04013', 'name': 'Sanjay Kumar', 'parent_phone': '9855566677', 'status': 'Active', 'backlogs': 2, 'year': 3, 'cgpa': 6.41},
    {'reg_no': '231FA04014', 'name': 'Divya Prakash', 'parent_phone': '9866677788', 'status': 'Active', 'backlogs': 0, 'year': 3, 'cgpa': 7.12},
    {'reg_no': '231FA04015', 'name': 'Amit Sharma', 'parent_phone': '9877788899', 'status': 'At Risk', 'backlogs': 3, 'year': 3, 'cgpa': 5.87},
    {'reg_no': '231FA04016', 'name': 'Neha Gupta', 'parent_phone': '9888899900', 'status': 'Active', 'backlogs': 1, 'year': 3, 'cgpa': 6.56},
    {'reg_no': '231FA04017', 'name': 'Rajeshwari Rao', 'parent_phone': '9899900011', 'status': 'Active', 'backlogs': 0, 'year': 3, 'cgpa': 7.24},
    {'reg_no': '231FA04018', 'name': 'Suresh Babu', 'parent_phone': '9800011122', 'status': 'Active', 'backlogs': 2, 'year': 3, 'cgpa': 6.18},
    {'reg_no': '231FA04019', 'name': 'Lakshmi Prasad', 'parent_phone': '9811122233', 'status': 'Active (Scholar)', 'backlogs': 0, 'year': 3, 'cgpa': 7.45, 'scholarship': True, 'scholarship_amt': 40000},
    {'reg_no': '231FA04020', 'name': 'Vijay Krishna', 'parent_phone': '9822233344', 'status': 'Active', 'backlogs': 1, 'year': 3, 'cgpa': 6.78},
    {'reg_no': '231FA04021', 'name': 'Deepa Nair', 'parent_phone': '9833344455', 'status': 'Active', 'backlogs': 0, 'year': 3, 'cgpa': 7.01},
    {'reg_no': '231FA04022', 'name': 'Aravind Swamy', 'parent_phone': '9844455566', 'status': 'At Risk', 'backlogs': 3, 'year': 3, 'cgpa': 5.92},
    {'reg_no': '231FA04023', 'name': 'Bhavana Singh', 'parent_phone': '9855566677', 'status': 'Active', 'backlogs': 1, 'year': 3, 'cgpa': 6.67},
    {'reg_no': '231FA04024', 'name': 'Chiranjeev Reddy', 'parent_phone': '9866677788', 'status': 'Active', 'backlogs': 0, 'year': 3, 'cgpa': 7.15},
    {'reg_no': '231FA04025', 'name': 'Esha Patel', 'parent_phone': '9877788899', 'status': 'Active', 'backlogs': 2, 'year': 3, 'cgpa': 6.34},
    {'reg_no': '231FA04026', 'name': 'Farhan Khan', 'parent_phone': '9888899900', 'status': 'Active', 'backlogs': 1, 'year': 3, 'cgpa': 6.89},
    {'reg_no': '231FA04027', 'name': 'Gauri Sharma', 'parent_phone': '9899900011', 'status': 'Active (Scholar)', 'backlogs': 0, 'year': 3, 'cgpa': 7.38, 'scholarship': True, 'scholarship_amt': 40000},
    {'reg_no': '231FA04028', 'name': 'Harish Verma', 'parent_phone': '9800011122', 'status': 'Active', 'backlogs': 0, 'year': 3, 'cgpa': 7.22},
    {'reg_no': '231FA04029', 'name': 'Ishita Joshi', 'parent_phone': '9811122233', 'status': 'Active', 'backlogs': 1, 'year': 3, 'cgpa': 6.71},
    {'reg_no': '231FA04030', 'name': 'Jagan Mohan', 'parent_phone': '9822233344', 'status': 'At Risk', 'backlogs': 3, 'year': 3, 'cgpa': 5.76},
    {'reg_no': '231FA04031', 'name': 'Komal Reddy', 'parent_phone': '9833344455', 'status': 'Active', 'backlogs': 0, 'year': 3, 'cgpa': 7.08},
    {'reg_no': '231FA04032', 'name': 'Lalitha Devi', 'parent_phone': '9844455566', 'status': 'Active', 'backlogs': 1, 'year': 3, 'cgpa': 6.55},
    {'reg_no': '231FA04033', 'name': 'Manoj Kumar', 'parent_phone': '9855566677', 'status': 'Active', 'backlogs': 2, 'year': 3, 'cgpa': 6.23},
    {'reg_no': '231FA04034', 'name': 'Nitya Prakash', 'parent_phone': '9866677788', 'status': 'Active (Scholar)', 'backlogs': 0, 'year': 3, 'cgpa': 7.52, 'scholarship': True, 'scholarship_amt': 40000},
    {'reg_no': '231FA04035', 'name': 'Om Prakash', 'parent_phone': '9877788899', 'status': 'Active', 'backlogs': 0, 'year': 3, 'cgpa': 7.11},
    {'reg_no': '231FA04036', 'name': 'Pallavi Singh', 'parent_phone': '9888899900', 'status': 'Active', 'backlogs': 1, 'year': 3, 'cgpa': 6.82},
    {'reg_no': '231FA04037', 'name': 'Qamar Zaman', 'parent_phone': '9899900011', 'status': 'Active', 'backlogs': 2, 'year': 3, 'cgpa': 6.09},
    {'reg_no': '231FA04038', 'name': 'Rani Sharma', 'parent_phone': '9800011122', 'status': 'Active', 'backlogs': 0, 'year': 3, 'cgpa': 7.34},
    {'reg_no': '231FA04039', 'name': 'Vivek Reddy', 'parent_phone': '9665500033', 'status': 'Active', 'backlogs': 1, 'year': 3, 'cgpa': 6.89},
    {'reg_no': '231FA04040', 'name': 'Shalini Singh', 'parent_phone': '9654400034', 'status': 'Active', 'backlogs': 0, 'year': 3, 'cgpa': 6.94},
    {'reg_no': '231FA04041', 'name': 'Prakash Patel', 'parent_phone': '9643300035', 'status': 'At Risk', 'backlogs': 3, 'year': 3, 'cgpa': 5.42},
    {'reg_no': '231FA04042', 'name': 'Lakshmi Iyer', 'parent_phone': '9632200036', 'status': 'Active', 'backlogs': 0, 'year': 3, 'cgpa': 6.02},
    {'reg_no': '231FA04043', 'name': 'Rahul Das', 'parent_phone': '9621100037', 'status': 'Active', 'backlogs': 1, 'year': 3, 'cgpa': 7.22},
    {'reg_no': '231FA04044', 'name': 'Snehal Shah', 'parent_phone': '9610000038', 'status': 'Active', 'backlogs': 0, 'year': 3, 'cgpa': 5.86},
    {'reg_no': '231FA04045', 'name': 'Ankit Sharma', 'parent_phone': '9609900039', 'status': 'Active', 'backlogs': 2, 'year': 3, 'cgpa': 5.87},
    {'reg_no': '231FA04046', 'name': 'Ritu Agarwal', 'parent_phone': '9598800040', 'status': 'Active', 'backlogs': 0, 'year': 3, 'cgpa': 6.99},
    {'reg_no': '231FA04047', 'name': 'Tarun Kumar', 'parent_phone': '9587700041', 'status': 'Active', 'backlogs': 1, 'year': 3, 'cgpa': 6.69},
    {'reg_no': '231FA04048', 'name': 'Megha Kapoor', 'parent_phone': '9576600042', 'status': 'Active', 'backlogs': 0, 'year': 3, 'cgpa': 6.77},
    {'reg_no': '231FA04049', 'name': 'Suresh Yadav', 'parent_phone': '9565500043', 'status': 'Active', 'backlogs': 2, 'year': 3, 'cgpa': 7.76},
    {'reg_no': '231FA04050', 'name': 'Keerthi Reddy', 'parent_phone': '9554400044', 'status': 'Active (Scholar)', 'backlogs': 0, 'year': 3, 'cgpa': 6.83, 'scholarship': True, 'scholarship_amt': 40000},
]

def get_grade(grade_point):
    if grade_point >= 9: return 'O'
    elif grade_point >= 8: return 'A+'
    elif grade_point >= 7: return 'A'
    elif grade_point >= 6: return 'B'
    elif grade_point >= 5: return 'C'
    elif grade_point >= 4: return 'D'
    else: return 'F'

def get_class_advisor(year):
    advisors = {
        1: {'name': 'Dr. A. Kumar', 'email': 'a.kumar@college.edu', 'phone': '9876501234', 'cabin': 'Block A, Room 101'},
        2: {'name': 'Prof. S. Reddy', 'email': 's.reddy@college.edu', 'phone': '9876501235', 'cabin': 'Block B, Room 201'},
        3: {'name': 'Prof. V. Reddy', 'email': 'venkat.reddy@college.edu', 'phone': '9876501238', 'cabin': 'Block B, Room 205'},
        4: {'name': 'Dr. R. Sharma', 'email': 'r.sharma@college.edu', 'phone': '9876501236', 'cabin': 'Block C, Room 301'},
    }
    return advisors.get(year, advisors[1])

def generate_subjects(year):
    subjects_by_sem = {
        1: ['Programming in C', 'Engineering Mathematics', 'Engineering Physics', 'Basic Electronics', 'Communication Skills'],
        2: ['Data Structures', 'Discrete Mathematics', 'Digital Logic', 'Environmental Science', 'Python Programming'],
        3: ['DBMS', 'Operating Systems', 'Computer Organization', 'Probability & Statistics', 'Java Programming'],
        4: ['Computer Networks', 'Software Engineering', 'Theory of Computation', 'Web Technologies', 'Open Elective'],
        5: ['Artificial Intelligence', 'Machine Learning', 'Cloud Computing', 'Data Mining', 'Mini Project'],
        6: ['Big Data Analytics', 'Internet of Things', 'Cyber Security', 'Major Project', 'Professional Ethics'],
    }
    return subjects_by_sem

def generate_marks_for_student(student):
    """Generate marks for students without detailed data"""
    marks_list = []
    subjects = generate_subjects(student['year'])
    
    for sem in range(1, student['year'] * 2 + 1):
        for subject in subjects[sem]:
            att = random.randint(65, 98)
            mark = random.randint(35, 100)
            gp = mark / 10
            backlog = mark < 40
            
            marks_list.append({
                'sem': sem,
                'subject': subject,
                'att': att,
                'marks': mark,
                'gp': round(gp, 1),
                'backlog': backlog,
                'backlog_type': 'Incomplete' if backlog and random.random() > 0.5 else 'Repeat Grade' if backlog else None
            })
    return marks_list

def import_students():
    client = MongoClient(MONGO_URI)
    db = client[DB_NAME]
    
    print("Clearing existing data...")
    db.students.delete_many({})
    db.academic_data.delete_many({})
    db.fees.delete_many({})
    db.parents.delete_many({})
    
    all_students = STUDENT_DATA.copy()
    
    # Add additional students with generated marks
    for s in ADDITIONAL_STUDENTS:
        s['marks'] = generate_marks_for_student(s)
        if 'scholarship' not in s:
            s['scholarship'] = False
            s['scholarship_amt'] = 0
        all_students.append(s)
    
    total_academic = 0
    total_fees = 0
    
    print(f"Importing {len(all_students)} students...")
    
    for student in all_students:
        avg_att = sum(m['att'] for m in student['marks']) / len(student['marks'])
        advisor = get_class_advisor(student['year'])
        
        # Insert student
        student_record = {
            'reg_no': student['reg_no'],
            'name': student['name'],
            'phone': student['parent_phone'],
            'parent_phone': student['parent_phone'],
            'cgpa': student['cgpa'],
            'backlogs': student['backlogs'],
            'attendance_pct': round(avg_att, 1),
            'course_status': student['status'],
            'year': student['year'],
            'branch': 'CSE',
            'section': 'A',
            'class_advisor': advisor['name'],
            'advisor_phone': advisor['phone'],
            'advisor_email': advisor['email'],
            'advisor_cabin': advisor['cabin'],
            'scholarship_status': 'Yes' if student.get('scholarship') else 'No',
            'scholarship_amount': student.get('scholarship_amt', 0)
        }
        db.students.insert_one(student_record)
        
        # Insert academic data (marks + attendance combined)
        for m in student['marks']:
            db.academic_data.insert_one({
                'student_reg_no': student['reg_no'],
                'semester': m['sem'],
                'subject': m['subject'],
                'marks': m['marks'],
                'max_marks': 100,
                'grade': get_grade(m['gp']),
                'attendance_pct': m['att'],
                'backlog_status': 1 if m['backlog'] else 0
            })
            total_academic += 1
        
        # Generate fees
        scholarship_per_sem = student.get('scholarship_amt', 0) // 6
        for sem in range(1, student['year'] * 2 + 1):
            base_fee = 25000
            amount_due = max(0, base_fee - scholarship_per_sem)
            paid = random.randint(int(amount_due * 0.7), amount_due) if student['status'] != 'At Risk' else random.randint(0, int(amount_due * 0.6))
            status = 'Paid' if paid >= amount_due else ('Partial' if paid > 0 else 'Pending')
            
            db.fees.insert_one({
                'student_reg_no': student['reg_no'],
                'semester': sem,
                'amount_due': amount_due,
                'amount_paid': paid,
                'status': status,
                'payment_date': f"202{2 + (sem-1)//2}-{(sem % 2) * 6 + 1:02d}-{random.randint(10, 28):02d}",
                'scholarship_amount': scholarship_per_sem
            })
            total_fees += 1
        
        # Insert parent with OTP
        test_otp = "123456"  # Default test OTP for all parents
        db.parents.insert_one({
            'phone': student['parent_phone'],
            'student_reg_no': student['reg_no'],
            'student_name': student['name'],
            'relationship': 'Parent/Guardian',
            'otp': test_otp,
            'otp_expiry': (datetime.now() + timedelta(days=365)).isoformat(),  # Valid for 1 year
            'is_verified': True
        })
    
    client.close()
    
    print(f"\n✅ Successfully imported {len(all_students)} students!")
    print(f"   📊 Students: {len(all_students)}")
    print(f"   📝 Academic records: {total_academic}")
    print(f"   💰 Fee records: {total_fees}")

if __name__ == "__main__":
    import_students()
