"""
Import 50 students data into MongoDB
Run this script to populate the database with student records
"""

from pymongo import MongoClient
from models import MONGO_URI, DB_NAME
import random

# Raw student data (tab-separated)
RAW_DATA = """231FA04001	Arjun Mehta	9876543211	Active	0	1	1	Programming in C	67	89	8.9	No		No	0	7.48	6.94
231FA04001	Arjun Mehta	9876543211	Active	0	1	1	Engineering Mathematics	95	36	3.6	Yes	Incomplete	No	0	7.48	6.94
231FA04001	Arjun Mehta	9876543211	Active	0	1	1	Engineering Physics	94	97	9.7	No		No	0	7.48	6.94
231FA04001	Arjun Mehta	9876543211	Active	0	1	1	Basic Electronics	82	55	5.5	No		No	0	7.48	6.94
231FA04001	Arjun Mehta	9876543211	Active	0	1	1	Communication Skills	67	97	9.7	No		No	0	7.48	6.94
231FA04001	Arjun Mehta	9876543211	Active	0	1	2	Data Structures	85	44	4.4	Yes	Incomplete	No	0	6.4	6.94
231FA04001	Arjun Mehta	9876543211	Active	0	1	2	Discrete Mathematics	88	40	4	Yes	Repeat Grade	No	0	6.4	6.94
231FA04001	Arjun Mehta	9876543211	Active	0	1	2	Digital Logic	73	80	8	No		No	0	6.4	6.94
231FA04001	Arjun Mehta	9876543211	Active	0	1	2	Environmental Science	89	88	8.8	No		No	0	6.4	6.94
231FA04001	Arjun Mehta	9876543211	Active	0	1	2	Python Programming	83	68	6.8	No		No	0	6.4	6.94
231FA04001	Arjun Mehta	9876543211	Active	0	2	3	DBMS	94	57	5.7	No		No	0	7.24	7.39
231FA04001	Arjun Mehta	9876543211	Active	0	2	3	Operating Systems	84	81	8.1	No		No	0	7.24	7.39
231FA04001	Arjun Mehta	9876543211	Active	0	2	3	Computer Organization	73	93	9.3	No		No	0	7.24	7.39
231FA04001	Arjun Mehta	9876543211	Active	0	2	3	Probability & Statistics	80	91	9.1	No		No	0	7.24	7.39
231FA04001	Arjun Mehta	9876543211	Active	0	2	3	Java Programming	89	40	4	Yes	Incomplete	No	0	7.24	7.39
231FA04001	Arjun Mehta	9876543211	Active	0	2	4	Computer Networks	80	52	5.2	No		No	0	7.54	7.39
231FA04001	Arjun Mehta	9876543211	Active	0	2	4	Software Engineering	77	73	7.3	No		No	0	7.54	7.39
231FA04001	Arjun Mehta	9876543211	Active	0	2	4	Theory of Computation	88	65	6.5	No		No	0	7.54	7.39
231FA04001	Arjun Mehta	9876543211	Active	0	2	4	Web Technologies	85	92	9.2	No		No	0	7.54	7.39
231FA04001	Arjun Mehta	9876543211	Active	0	2	4	Open Elective	92	95	9.5	No		No	0	7.54	7.39
231FA04001	Arjun Mehta	9876543211	Active	0	3	5	Artificial Intelligence	69	76	7.6	No		No	0	6.6	6.41
231FA04001	Arjun Mehta	9876543211	Active	0	3	5	Machine Learning	97	55	5.5	No		No	0	6.6	6.41
231FA04001	Arjun Mehta	9876543211	Active	0	3	5	Cloud Computing	79	87	8.7	No		No	0	6.6	6.41
231FA04001	Arjun Mehta	9876543211	Active	0	3	5	Data Mining	80	39	3.9	Yes	Incomplete	No	0	6.6	6.41
231FA04001	Arjun Mehta	9876543211	Active	0	3	5	Mini Project	96	73	7.3	No		No	0	6.6	6.41
231FA04001	Arjun Mehta	9876543211	Active	0	3	6	Big Data Analytics	69	45	4.5	Yes	Incomplete	No	0	6.22	6.41
231FA04001	Arjun Mehta	9876543211	Active	0	3	6	Internet of Things	89	82	8.2	No		No	0	6.22	6.41
231FA04001	Arjun Mehta	9876543211	Active	0	3	6	Cyber Security	74	49	4.9	Yes	Incomplete	No	0	6.22	6.41
231FA04001	Arjun Mehta	9876543211	Active	0	3	6	Major Project	93	56	5.6	No		No	0	6.22	6.41
231FA04001	Arjun Mehta	9876543211	Active	0	3	6	Professional Ethics	77	79	7.9	No		No	0	6.22	6.41
231FA04002	Priya Sharma	9823456780	Active	1	1	1	Programming in C	92	88	8.8	No		No	0	6.66	6.98
231FA04002	Priya Sharma	9823456780	Active	1	1	1	Engineering Mathematics	93	66	6.6	No		No	0	6.66	6.98
231FA04002	Priya Sharma	9823456780	Active	1	1	1	Engineering Physics	82	53	5.3	No		No	0	6.66	6.98
231FA04002	Priya Sharma	9823456780	Active	1	1	1	Basic Electronics	98	57	5.7	No		No	0	6.66	6.98
231FA04002	Priya Sharma	9823456780	Active	1	1	1	Communication Skills	72	69	6.9	No		No	0	6.66	6.98
231FA04002	Priya Sharma	9823456780	Active	1	1	2	Data Structures	94	73	7.3	No		No	0	7.3	6.98
231FA04002	Priya Sharma	9823456780	Active	1	1	2	Discrete Mathematics	75	57	5.7	No		No	0	7.3	6.98
231FA04002	Priya Sharma	9823456780	Active	1	1	2	Digital Logic	76	96	9.6	No		No	0	7.3	6.98
231FA04002	Priya Sharma	9823456780	Active	1	1	2	Environmental Science	87	76	7.6	No		No	0	7.3	6.98
231FA04002	Priya Sharma	9823456780	Active	1	1	2	Python Programming	92	63	6.3	No		No	0	7.3	6.98
231FA04002	Priya Sharma	9823456780	Active	1	2	3	DBMS	65	40	4	Yes	Repeat Grade	No	0	6.88	7.11
231FA04002	Priya Sharma	9823456780	Active	1	2	3	Operating Systems	85	66	6.6	No		No	0	6.88	7.11
231FA04002	Priya Sharma	9823456780	Active	1	2	3	Computer Organization	70	68	6.8	No		No	0	6.88	7.11
231FA04002	Priya Sharma	9823456780	Active	1	2	3	Probability & Statistics	93	86	8.6	No		No	0	6.88	7.11
231FA04002	Priya Sharma	9823456780	Active	1	2	3	Java Programming	75	84	8.4	No		No	0	6.88	7.11
231FA04002	Priya Sharma	9823456780	Active	1	2	4	Computer Networks	96	65	6.5	No		No	0	7.34	7.11
231FA04002	Priya Sharma	9823456780	Active	1	2	4	Software Engineering	98	69	6.9	No		No	0	7.34	7.11
231FA04002	Priya Sharma	9823456780	Active	1	2	4	Theory of Computation	98	96	9.6	No		No	0	7.34	7.11
231FA04002	Priya Sharma	9823456780	Active	1	2	4	Web Technologies	96	43	4.3	Yes	Incomplete	No	0	7.34	7.11
231FA04002	Priya Sharma	9823456780	Active	1	2	4	Open Elective	96	94	9.4	No		No	0	7.34	7.11
231FA04002	Priya Sharma	9823456780	Active	1	3	5	Artificial Intelligence	90	52	5.2	No		No	0	8.14	6.82
231FA04002	Priya Sharma	9823456780	Active	1	3	5	Machine Learning	91	79	7.9	No		No	0	8.14	6.82
231FA04002	Priya Sharma	9823456780	Active	1	3	5	Cloud Computing	89	97	9.7	No		No	0	8.14	6.82
231FA04002	Priya Sharma	9823456780	Active	1	3	5	Data Mining	75	91	9.1	No		No	0	8.14	6.82
231FA04002	Priya Sharma	9823456780	Active	1	3	5	Mini Project	71	88	8.8	No		No	0	8.14	6.82
231FA04002	Priya Sharma	9823456780	Active	1	3	6	Big Data Analytics	67	35	3.5	Yes	Repeat Grade	No	0	5.5	6.82
231FA04002	Priya Sharma	9823456780	Active	1	3	6	Internet of Things	69	41	4.1	Yes	Repeat Grade	No	0	5.5	6.82
231FA04002	Priya Sharma	9823456780	Active	1	3	6	Cyber Security	70	54	5.4	No		No	0	5.5	6.82
231FA04002	Priya Sharma	9823456780	Active	1	3	6	Major Project	71	93	9.3	No		No	0	5.5	6.82
231FA04002	Priya Sharma	9823456780	Active	1	3	6	Professional Ethics	96	52	5.2	No		No	0	5.5	6.82
231FA04003	Rahul Verma	9812345670	Active	2	1	1	Programming in C	94	90	9	No		No	0	7.86	7.29
231FA04003	Rahul Verma	9812345670	Active	2	1	1	Engineering Mathematics	97	92	9.2	No		No	0	7.86	7.29
231FA04003	Rahul Verma	9812345670	Active	2	1	1	Engineering Physics	86	68	6.8	No		No	0	7.86	7.29
231FA04003	Rahul Verma	9812345670	Active	2	1	1	Basic Electronics	94	89	8.9	No		No	0	7.86	7.29
231FA04003	Rahul Verma	9812345670	Active	2	1	1	Communication Skills	86	54	5.4	No		No	0	7.86	7.29
231FA04003	Rahul Verma	9812345670	Active	2	1	2	Data Structures	80	76	7.6	No		No	0	6.72	7.29
231FA04003	Rahul Verma	9812345670	Active	2	1	2	Discrete Mathematics	67	60	6	No		No	0	6.72	7.29
231FA04003	Rahul Verma	9812345670	Active	2	1	2	Digital Logic	95	38	3.8	Yes	Incomplete	No	0	6.72	7.29
231FA04003	Rahul Verma	9812345670	Active	2	1	2	Environmental Science	83	90	9	No		No	0	6.72	7.29
231FA04003	Rahul Verma	9812345670	Active	2	1	2	Python Programming	80	72	7.2	No		No	0	6.72	7.29
231FA04003	Rahul Verma	9812345670	Active	2	2	3	DBMS	70	40	4	Yes	Incomplete	No	0	6.26	6.43
231FA04003	Rahul Verma	9812345670	Active	2	2	3	Operating Systems	83	55	5.5	No		No	0	6.26	6.43
231FA04003	Rahul Verma	9812345670	Active	2	2	3	Computer Organization	95	53	5.3	No		No	0	6.26	6.43
231FA04003	Rahul Verma	9812345670	Active	2	2	3	Probability & Statistics	88	86	8.6	No		No	0	6.26	6.43
231FA04003	Rahul Verma	9812345670	Active	2	2	3	Java Programming	77	79	7.9	No		No	0	6.26	6.43
231FA04003	Rahul Verma	9812345670	Active	2	2	4	Computer Networks	76	45	4.5	Yes	Incomplete	No	0	6.6	6.43
231FA04003	Rahul Verma	9812345670	Active	2	2	4	Software Engineering	92	61	6.1	No		No	0	6.6	6.43
231FA04003	Rahul Verma	9812345670	Active	2	2	4	Theory of Computation	71	74	7.4	No		No	0	6.6	6.43
231FA04003	Rahul Verma	9812345670	Active	2	2	4	Web Technologies	94	89	8.9	No		No	0	6.6	6.43
231FA04003	Rahul Verma	9812345670	Active	2	2	4	Open Elective	93	61	6.1	No		No	0	6.6	6.43
231FA04003	Rahul Verma	9812345670	Active	2	3	5	Artificial Intelligence	82	81	8.1	No		No	0	7.04	7.07
231FA04003	Rahul Verma	9812345670	Active	2	3	5	Machine Learning	72	35	3.5	Yes	Incomplete	No	0	7.04	7.07
231FA04003	Rahul Verma	9812345670	Active	2	3	5	Cloud Computing	92	87	8.7	No		No	0	7.04	7.07
231FA04003	Rahul Verma	9812345670	Active	2	3	5	Data Mining	89	60	6	No		No	0	7.04	7.07
231FA04003	Rahul Verma	9812345670	Active	2	3	5	Mini Project	69	89	8.9	No		No	0	7.04	7.07
231FA04003	Rahul Verma	9812345670	Active	2	3	6	Big Data Analytics	70	42	4.2	Yes	Repeat Grade	No	0	7.1	7.07
231FA04003	Rahul Verma	9812345670	Active	2	3	6	Internet of Things	81	81	8.1	No		No	0	7.1	7.07
231FA04003	Rahul Verma	9812345670	Active	2	3	6	Cyber Security	94	89	8.9	No		No	0	7.1	7.07
231FA04003	Rahul Verma	9812345670	Active	2	3	6	Major Project	77	71	7.1	No		No	0	7.1	7.07
231FA04003	Rahul Verma	9812345670	Active	2	3	6	Professional Ethics	94	72	7.2	No		No	0	7.1	7.07
231FA04004	Sneha Patel	9898765430	Active (Scholar)	0	1	1	Programming in C	97	98	9.8	No		Yes	40000	8.64	7.48
231FA04004	Sneha Patel	9898765430	Active (Scholar)	0	1	1	Engineering Mathematics	97	68	6.8	No		Yes	40000	8.64	7.48
231FA04004	Sneha Patel	9898765430	Active (Scholar)	0	1	1	Engineering Physics	90	91	9.1	No		Yes	40000	8.64	7.48
231FA04004	Sneha Patel	9898765430	Active (Scholar)	0	1	1	Basic Electronics	86	79	7.9	No		Yes	40000	8.64	7.48
231FA04004	Sneha Patel	9898765430	Active (Scholar)	0	1	1	Communication Skills	82	96	9.6	No		Yes	40000	8.64	7.48
231FA04004	Sneha Patel	9898765430	Active (Scholar)	0	1	2	Data Structures	93	96	9.6	No		Yes	40000	6.32	7.48
231FA04004	Sneha Patel	9898765430	Active (Scholar)	0	1	2	Discrete Mathematics	95	45	4.5	Yes	Repeat Grade	Yes	40000	6.32	7.48
231FA04004	Sneha Patel	9898765430	Active (Scholar)	0	1	2	Digital Logic	90	56	5.6	No		Yes	40000	6.32	7.48
231FA04004	Sneha Patel	9898765430	Active (Scholar)	0	1	2	Environmental Science	91	43	4.3	Yes	Repeat Grade	Yes	40000	6.32	7.48
231FA04004	Sneha Patel	9898765430	Active (Scholar)	0	1	2	Python Programming	66	76	7.6	No		Yes	40000	6.32	7.48
231FA04004	Sneha Patel	9898765430	Active (Scholar)	0	2	3	DBMS	85	44	4.4	Yes	Repeat Grade	Yes	40000	5.9	7.13
231FA04004	Sneha Patel	9898765430	Active (Scholar)	0	2	3	Operating Systems	88	71	7.1	No		Yes	40000	5.9	7.13
231FA04004	Sneha Patel	9898765430	Active (Scholar)	0	2	3	Computer Organization	76	65	6.5	No		Yes	40000	5.9	7.13
231FA04004	Sneha Patel	9898765430	Active (Scholar)	0	2	3	Probability & Statistics	75	74	7.4	No		Yes	40000	5.9	7.13
231FA04004	Sneha Patel	9898765430	Active (Scholar)	0	2	3	Java Programming	71	41	4.1	Yes	Incomplete	Yes	40000	5.9	7.13
231FA04004	Sneha Patel	9898765430	Active (Scholar)	0	2	4	Computer Networks	69	88	8.8	No		Yes	40000	8.36	7.13
231FA04004	Sneha Patel	9898765430	Active (Scholar)	0	2	4	Software Engineering	77	91	9.1	No		Yes	40000	8.36	7.13
231FA04004	Sneha Patel	9898765430	Active (Scholar)	0	2	4	Theory of Computation	66	85	8.5	No		Yes	40000	8.36	7.13
231FA04004	Sneha Patel	9898765430	Active (Scholar)	0	2	4	Web Technologies	77	78	7.8	No		Yes	40000	8.36	7.13
231FA04004	Sneha Patel	9898765430	Active (Scholar)	0	2	4	Open Elective	77	76	7.6	No		Yes	40000	8.36	7.13
231FA04004	Sneha Patel	9898765430	Active (Scholar)	0	3	5	Artificial Intelligence	68	41	4.1	Yes	Incomplete	Yes	40000	5.76	6.61
231FA04004	Sneha Patel	9898765430	Active (Scholar)	0	3	5	Machine Learning	88	85	8.5	No		Yes	40000	5.76	6.61
231FA04004	Sneha Patel	9898765430	Active (Scholar)	0	3	5	Cloud Computing	85	56	5.6	No		Yes	40000	5.76	6.61
231FA04004	Sneha Patel	9898765430	Active (Scholar)	0	3	5	Data Mining	75	50	5	No		Yes	40000	5.76	6.61
231FA04004	Sneha Patel	9898765430	Active (Scholar)	0	3	5	Mini Project	87	56	5.6	No		Yes	40000	5.76	6.61
231FA04004	Sneha Patel	9898765430	Active (Scholar)	0	3	6	Big Data Analytics	66	100	10	No		Yes	40000	7.46	6.61
231FA04004	Sneha Patel	9898765430	Active (Scholar)	0	3	6	Internet of Things	87	46	4.6	Yes	Repeat Grade	Yes	40000	7.46	6.61
231FA04004	Sneha Patel	9898765430	Active (Scholar)	0	3	6	Cyber Security	93	79	7.9	No		Yes	40000	7.46	6.61
231FA04004	Sneha Patel	9898765430	Active (Scholar)	0	3	6	Major Project	68	53	5.3	No		Yes	40000	7.46	6.61
231FA04004	Sneha Patel	9898765430	Active (Scholar)	0	3	6	Professional Ethics	93	95	9.5	No		Yes	40000	7.46	6.61
231FA04005	Vikram Nair	9945678900	At Risk	3	1	1	Programming in C	93	91	9.1	No		No	0	8.02	7.44
231FA04005	Vikram Nair	9945678900	At Risk	3	1	1	Engineering Mathematics	76	80	8	No		No	0	8.02	7.44
231FA04005	Vikram Nair	9945678900	At Risk	3	1	1	Engineering Physics	92	78	7.8	No		No	0	8.02	7.44
231FA04005	Vikram Nair	9945678900	At Risk	3	1	1	Basic Electronics	97	93	9.3	No		No	0	8.02	7.44
231FA04005	Vikram Nair	9945678900	At Risk	3	1	1	Communication Skills	89	59	5.9	No		No	0	8.02	7.44
231FA04005	Vikram Nair	9945678900	At Risk	3	1	2	Data Structures	71	90	9	No		No	0	6.86	7.44
231FA04005	Vikram Nair	9945678900	At Risk	3	1	2	Discrete Mathematics	74	40	4	Yes	Incomplete	No	0	6.86	7.44
231FA04005	Vikram Nair	9945678900	At Risk	3	1	2	Digital Logic	77	89	8.9	No		No	0	6.86	7.44
231FA04005	Vikram Nair	9945678900	At Risk	3	1	2	Environmental Science	88	83	8.3	No		No	0	6.86	7.44
231FA04005	Vikram Nair	9945678900	At Risk	3	1	2	Python Programming	68	41	4.1	Yes	Incomplete	No	0	6.86	7.44
231FA04005	Vikram Nair	9945678900	At Risk	3	2	3	DBMS	84	63	6.3	No		No	0	7.18	6.89
231FA04005	Vikram Nair	9945678900	At Risk	3	2	3	Operating Systems	68	57	5.7	No		No	0	7.18	6.89
231FA04005	Vikram Nair	9945678900	At Risk	3	2	3	Computer Organization	71	81	8.1	No		No	0	7.18	6.89
231FA04005	Vikram Nair	9945678900	At Risk	3	2	3	Probability & Statistics	76	73	7.3	No		No	0	7.18	6.89
231FA04005	Vikram Nair	9945678900	At Risk	3	2	3	Java Programming	67	85	8.5	No		No	0	7.18	6.89
231FA04005	Vikram Nair	9945678900	At Risk	3	2	4	Computer Networks	92	44	4.4	Yes	Repeat Grade	No	0	6.6	6.89
231FA04005	Vikram Nair	9945678900	At Risk	3	2	4	Software Engineering	77	97	9.7	No		No	0	6.6	6.89
231FA04005	Vikram Nair	9945678900	At Risk	3	2	4	Theory of Computation	75	56	5.6	No		No	0	6.6	6.89
231FA04005	Vikram Nair	9945678900	At Risk	3	2	4	Web Technologies	90	94	9.4	No		No	0	6.6	6.89
231FA04005	Vikram Nair	9945678900	At Risk	3	2	4	Open Elective	86	39	3.9	Yes	Incomplete	No	0	6.6	6.89
231FA04005	Vikram Nair	9945678900	At Risk	3	3	5	Artificial Intelligence	76	88	8.8	No		No	0	7.78	7.62
231FA04005	Vikram Nair	9945678900	At Risk	3	3	5	Machine Learning	74	100	10	No		No	0	7.78	7.62
231FA04005	Vikram Nair	9945678900	At Risk	3	3	5	Cloud Computing	90	47	4.7	Yes	Repeat Grade	No	0	7.78	7.62
231FA04005	Vikram Nair	9945678900	At Risk	3	3	5	Data Mining	72	65	6.5	No		No	0	7.78	7.62
231FA04005	Vikram Nair	9945678900	At Risk	3	3	5	Mini Project	71	89	8.9	No		No	0	7.78	7.62
231FA04005	Vikram Nair	9945678900	At Risk	3	3	6	Big Data Analytics	84	72	7.2	No		No	0	7.46	7.62
231FA04005	Vikram Nair	9945678900	At Risk	3	3	6	Internet of Things	71	79	7.9	No		No	0	7.46	7.62
231FA04005	Vikram Nair	9945678900	At Risk	3	3	6	Cyber Security	98	95	9.5	No		No	0	7.46	7.62
231FA04005	Vikram Nair	9945678900	At Risk	3	3	6	Major Project	80	72	7.2	No		No	0	7.46	7.62
231FA04005	Vikram Nair	9945678900	At Risk	3	3	6	Professional Ethics	65	55	5.5	No		No	0	7.46	7.62"""

def parse_data(raw_data):
    """Parse raw tab-separated data into structured format"""
    students = {}
    
    for line in raw_data.strip().split('\n'):
        parts = line.split('\t')
        if len(parts) < 16:
            continue
            
        reg_no = parts[0]
        student_name = parts[1]
        parent_phone = parts[2]
        status = parts[3]
        total_backlogs = int(parts[4])
        year = int(parts[5])
        semester = int(parts[6])
        subject = parts[7]
        attendance_pct = float(parts[8])
        marks = int(parts[9])
        grade_point = float(parts[10])
        backlog = parts[11]
        backlog_type = parts[12] if len(parts) > 12 else ""
        scholarship_status = parts[13] if len(parts) > 13 else "No"
        scholarship_amount = int(parts[14]) if len(parts) > 14 and parts[14].isdigit() else 0
        sem_cgpa = float(parts[15]) if len(parts) > 15 else 0.0
        year_cgpa = float(parts[16]) if len(parts) > 16 else 0.0
        
        if reg_no not in students:
            students[reg_no] = {
                'reg_no': reg_no,
                'name': student_name,
                'parent_phone': parent_phone,
                'phone': parent_phone,  # Same as parent for simplicity
                'status': status,
                'total_backlogs': total_backlogs,
                'year': year,
                'branch': 'CSE',
                'section': 'A',
                'cgpa': year_cgpa,
                'attendance_pct': 0,  # Will calculate average
                'course_status': status,
                'scholarship_status': scholarship_status,
                'scholarship_amount': scholarship_amount,
                'marks_data': [],
                'attendance_data': [],
                'fee_data': [],
                'sem_cgpa': {},
                'year_cgpa': {}
            }
        
        # Add marks data
        backlog_status = 1 if backlog == "Yes" else 0
        students[reg_no]['marks_data'].append({
            'semester': semester,
            'subject': subject,
            'marks': marks,
            'max_marks': 100,
            'grade': get_grade(grade_point),
            'grade_point': grade_point,
            'backlog_status': backlog_status,
            'backlog_type': backlog_type if backlog == "Yes" else None
        })
        
        # Add attendance data
        students[reg_no]['attendance_data'].append({
            'semester': semester,
            'subject': subject,
            'attendance_pct': attendance_pct
        })
        
        # Track semester CGPA
        students[reg_no]['sem_cgpa'][semester] = sem_cgpa
        students[reg_no]['year_cgpa'][year] = year_cgpa
    
    return students

def get_grade(grade_point):
    """Convert grade point to letter grade"""
    if grade_point >= 9:
        return 'O'
    elif grade_point >= 8:
        return 'A+'
    elif grade_point >= 7:
        return 'A'
    elif grade_point >= 6:
        return 'B'
    elif grade_point >= 5:
        return 'C'
    elif grade_point >= 4:
        return 'D'
    else:
        return 'F'

def generate_fee_data(student):
    """Generate fee data for each semester"""
    fees = []
    for sem in range(1, student['year'] * 2 + 1):
        fee_amount = 25000
        # Scholarship students get discount
        if student['scholarship_status'] == 'Yes':
            fee_amount = max(0, fee_amount - student['scholarship_amount'] // 6)
        
        # Random payment status
        paid = random.randint(int(fee_amount * 0.6), fee_amount)
        status = 'Paid' if paid >= fee_amount else ('Partial' if paid > 0 else 'Pending')
        
        fees.append({
            'semester': sem,
            'amount_due': fee_amount,
            'amount_paid': paid,
            'status': status,
            'payment_date': f"202{2 + (sem-1)//2}-{(sem % 2) * 6 + 1:02d}-{random.randint(10, 28):02d}",
            'scholarship_amount': student['scholarship_amount'] // 6 if student['scholarship_status'] == 'Yes' else 0
        })
    return fees

def get_class_advisor(year, section='A'):
    """Get class advisor details based on year"""
    advisors = {
        1: {'name': 'Dr. A. Kumar', 'email': 'a.kumar@college.edu', 'phone': '9876501234', 'cabin': 'Block A, Room 101'},
        2: {'name': 'Prof. S. Reddy', 'email': 's.reddy@college.edu', 'phone': '9876501235', 'cabin': 'Block B, Room 201'},
        3: {'name': 'Prof. V. Reddy', 'email': 'venkat.reddy@college.edu', 'phone': '9876501238', 'cabin': 'Block B, Room 205'},
        4: {'name': 'Dr. R. Sharma', 'email': 'r.sharma@college.edu', 'phone': '9876501236', 'cabin': 'Block C, Room 301'},
    }
    return advisors.get(year, advisors[1])

def import_students():
    """Import all students into MongoDB"""
    client = MongoClient(MONGO_URI)
    db = client[DB_NAME]
    
    # Clear existing data
    db.students.delete_many({})
    db.marks.delete_many({})
    db.attendance.delete_many({})
    db.fees.delete_many({})
    db.parents.delete_many({})
    
    # Parse data
    students_data = parse_data(RAW_DATA)
    
    inserted_count = 0
    
    for reg_no, student in students_data.items():
        # Calculate average attendance
        avg_attendance = sum(a['attendance_pct'] for a in student['attendance_data']) / len(student['attendance_data'])
        
        # Get class advisor
        advisor = get_class_advisor(student['year'])
        
        # Create student record
        student_record = {
            'reg_no': reg_no,
            'name': student['name'],
            'phone': student['phone'],
            'parent_phone': student['parent_phone'],
            'cgpa': student['cgpa'],
            'backlogs': student['total_backlogs'],
            'attendance_pct': round(avg_attendance, 1),
            'course_status': student['status'],
            'year': student['year'],
            'branch': student['branch'],
            'section': student['section'],
            'class_advisor': advisor['name'],
            'advisor_phone': advisor['phone'],
            'advisor_email': advisor['email'],
            'advisor_cabin': advisor['cabin'],
            'scholarship_status': student['scholarship_status'],
            'scholarship_amount': student['scholarship_amount']
        }
        db.students.insert_one(student_record)
        
        # Insert marks
        for mark in student['marks_data']:
            mark['reg_no'] = reg_no
            db.marks.insert_one(mark)
        
        # Insert attendance
        for att in student['attendance_data']:
            att['reg_no'] = reg_no
            db.attendance.insert_one(att)
        
        # Generate and insert fees
        fee_data = generate_fee_data(student)
        for fee in fee_data:
            fee['reg_no'] = reg_no
            db.fees.insert_one(fee)
        
        # Create parent record
        parent_record = {
            'phone': student['parent_phone'],
            'student_reg_no': reg_no,
            'student_name': student['name'],
            'relationship': 'Parent/Guardian'
        }
        db.parents.insert_one(parent_record)
        
        inserted_count += 1
    
    client.close()
    print(f"✅ Successfully imported {inserted_count} students!")
    print(f"   - Students: {inserted_count}")
    print(f"   - Marks records: {sum(len(s['marks_data']) for s in students_data.values())}")
    print(f"   - Attendance records: {sum(len(s['attendance_data']) for s in students_data.values())}")
    print(f"   - Fee records: {sum(len(generate_fee_data(s)) for s in students_data.values())}")
    
    return inserted_count

if __name__ == "__main__":
    import_students()
