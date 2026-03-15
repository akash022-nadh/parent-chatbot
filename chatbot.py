from models import *

def _sem_tabs():
    return '''<div class="sem-tabs">
<button type="button" class="sem-toggle active" data-view="current">Current semester</button>
<button type="button" class="sem-toggle" data-view="previous">Previous semesters</button>
</div>'''

def get_attendance_response(reg_no):
    rows, student = get_attendance(reg_no)
    if not rows:
        return "No attendance data found."

    overall = student.get("attendance_pct", 0)
    cur_sem = get_current_semester(reg_no)
    semesters = {}
    for r in rows:
        semesters.setdefault(r["semester"], []).append(r)

    current_rows = semesters.get(cur_sem, [])
    previous_rows = [r for s, subs in sorted(semesters.items()) if s != cur_sem for r in subs]

    def table_rows(subj_list):
        if not subj_list:
            return "<tr><td colspan='3'>No data</td></tr>"
        return "".join(
            f"<tr><td>{'⚠️' if s['attendance_pct'] < 75 else '✅'}</td><td>{s['subject']}</td><td><b>{s['attendance_pct']:.1f}%</b></td></tr>"
            for s in subj_list
        )

    cur_table = f"<table class='data-table'><thead><tr><th></th><th>Subject</th><th>Attendance</th></tr></thead><tbody>{table_rows(current_rows)}</tbody></table>"
    prev_table = f"<table class='data-table'><thead><tr><th></th><th>Subject</th><th>Attendance</th></tr></thead><tbody>{table_rows(previous_rows)}</tbody></table>"

    return f"""📊 <b>Attendance Report</b><br>Overall: <b>{overall:.1f}%</b>
{_sem_tabs()}
<div class="sem-view sem-current">{cur_table}</div>
<div class="sem-view sem-previous" style="display:none">{prev_table}</div>"""

def get_low_attendance_response(reg_no):
    rows, _ = get_attendance(reg_no)
    low = [r for r in rows if r["attendance_pct"] < 75]
    if not low:
        return "✅ Great news! No subjects with low attendance. All above 75%."
    rows_html = "".join(
        f"<tr><td>Sem {r['semester']}</td><td>{r['subject']}</td><td><b>{r['attendance_pct']:.1f}%</b></td></tr>"
        for r in low
    )
    return f"""⚠️ <b>Low Attendance Alert (Below 75%)</b>
<table class="data-table"><thead><tr><th>Semester</th><th>Subject</th><th>Attendance</th></tr></thead><tbody>{rows_html}</tbody></table>
<small>⚡ Please ensure regular attendance to avoid detention.</small>"""

def get_marks_response(reg_no):
    rows = get_marks(reg_no)
    if not rows:
        return "No marks data found."

    cur_sem = get_current_semester(reg_no)
    semesters = {}
    for r in rows:
        semesters.setdefault(r["semester"], []).append(r)

    def table_rows(subj_list):
        if not subj_list:
            return "<tr><td colspan='4'>No data</td></tr>"
        return "".join(
            f"<tr><td>{'🔴' if s['marks'] < 40 else '🟡' if s['marks'] < 60 else '🟢'}</td><td>{s['subject']}</td><td><b>{s['marks']}/100</b></td><td>{s['grade']}</td></tr>"
            for s in subj_list
        )

    current_rows = semesters.get(cur_sem, [])
    previous_rows = []
    for sem in sorted(semesters.keys()):
        if sem != cur_sem:
            previous_rows.extend(semesters[sem])

    cur_avg = sum(s["marks"] for s in current_rows) / len(current_rows) if current_rows else 0
    prev_avg = sum(s["marks"] for s in previous_rows) / len(previous_rows) if previous_rows else 0

    cur_table = f"<table class='data-table'><thead><tr><th></th><th>Subject</th><th>Marks</th><th>Grade</th></tr></thead><tbody>{table_rows(current_rows)}</tbody></table><small>Semester avg: <b>{cur_avg:.1f}</b></small>"
    prev_table = f"<table class='data-table'><thead><tr><th></th><th>Subject</th><th>Marks</th><th>Grade</th></tr></thead><tbody>{table_rows(previous_rows)}</tbody></table><small>Overall prev. avg: <b>{prev_avg:.1f}</b></small>"

    return f"""📝 <b>Subject-wise Marks</b>
{_sem_tabs()}
<div class="sem-view sem-current">{cur_table}</div>
<div class="sem-view sem-previous" style="display:none">{prev_table}</div>"""

def get_cgpa_response(reg_no):
    sem_data, student = get_cgpa_history(reg_no)
    current = student.get("cgpa", 0)
    cur_sem = get_current_semester(reg_no)
    current_sem_row = [r for r in sem_data if r["semester"] == cur_sem]
    previous_sem_rows = [r for r in sem_data if r["semester"] != cur_sem]

    def gpa_table(rows):
        if not rows:
            return "<table class='data-table'><tbody><tr><td>No data</td></tr></tbody></table>"
        body = "".join(
            f"<tr><td>Sem {r['semester']}</td><td><b>{round(r['sem_gpa'], 2)}</b></td><td class='gpa-bar'>{'█' * min(10, int(r['sem_gpa']))}{'░' * (10 - min(10, int(r['sem_gpa'])))}</td></tr>"
            for r in rows
        )
        return f"<table class='data-table'><thead><tr><th>Semester</th><th>GPA</th><th></th></tr></thead><tbody>{body}</tbody></table>"

    return f"""🎓 <b>Academic Performance</b><br>Current CGPA: <b>{current}</b>
{_sem_tabs()}
<div class="sem-view sem-current">{gpa_table(current_sem_row)}</div>
<div class="sem-view sem-previous" style="display:none">{gpa_table(previous_sem_rows)}</div>"""

def get_backlogs_response(reg_no):
    backlogs = get_backlogs(reg_no)
    student = get_student(reg_no)
    count = student.get("backlogs", 0)
    if not backlogs:
        return f"✅ No active backlogs! Course status: <b>{student.get('course_status','Active')}</b>"
    rows_html = "".join(
        f"<tr><td>Sem {b['semester']}</td><td>{b['subject']}</td><td><b>{b['marks']}</b></td><td>{b['grade']}</td></tr>"
        for b in backlogs
    )
    return f"""⚠️ <b>Backlog Summary</b> — Total: <b>{count}</b>
<table class="data-table"><thead><tr><th>Semester</th><th>Subject</th><th>Marks</th><th>Grade</th></tr></thead><tbody>{rows_html}</tbody></table>
<small>📌 Apply for supplementary exams through the academic office.</small>"""

def get_fees_response(reg_no):
    fees = get_fees(reg_no)
    if not fees:
        return "No fee records found."
    cur_sem = get_current_semester(reg_no)
    total_due = total_paid = total_schol = total_pending = 0
    current_fees = [f for f in fees if f["semester"] == cur_sem]
    previous_fees = [f for f in fees if f["semester"] != cur_sem]

    def fee_table(fee_list):
        if not fee_list:
            return "<table class='data-table'><tbody><tr><td>No data</td></tr></tbody></table>"
        rows = []
        for f in fee_list:
            icon = "✅" if f["status"] == "Paid" else "🟡" if f["status"] == "Partial" else "🔴"
            date_str = f["payment_date"] or "—"
            rows.append(f"<tr><td>{icon}</td><td>Sem {f['semester']}</td><td>₹{f['amount_due']:,.0f}</td><td>₹{f['amount_paid']:,.0f}</td><td>{f['status']}</td><td>{date_str}</td></tr>")
        return f"<table class='data-table'><thead><tr><th></th><th>Sem</th><th>Due</th><th>Paid</th><th>Status</th><th>Date</th></tr></thead><tbody>{''.join(rows)}</tbody></table>"

    # Recompute totals for summary
    total_paid = sum(f["amount_paid"] for f in fees)
    total_schol = sum(f.get("scholarship_amount", 0) for f in fees)
    total_pending = sum(max(0, f["amount_due"] - f["amount_paid"] - f.get("scholarship_amount", 0)) for f in fees)

    cur_html = fee_table(current_fees)
    prev_html = fee_table(previous_fees)

    summary = f"<small>📊 Total Paid: <b>₹{total_paid:,.0f}</b> | Pending: <b>₹{int(total_pending):,.0f}</b>"
    if total_schol > 0:
        summary += f" | 🏅 Scholarship: <b>₹{total_schol:,.0f}</b>"
    summary += "</small>"

    return f"""💰 <b>Fee Status</b>
{_sem_tabs()}
<div class="sem-view sem-current">{cur_html}</div>
<div class="sem-view sem-previous" style="display:none">{prev_html}</div>
{summary}"""

def get_notifications_response(reg_no):
    notifs = get_notifications(reg_no)
    if not notifs:
        return "📭 No notifications at this time."
    cat_icons = {"Exam": "📝", "Finance": "💰", "Academic": "📚", "Attendance": "📋", "General": "📢"}
    rows = "".join(
        f"<tr><td>{cat_icons.get(n['category'], '📢')}</td><td><b>{n['title']}</b></td><td>{n['message']}</td><td><i>{n['date']}</i></td></tr>"
        for n in notifs[:8]
    )
    return f"""🔔 <b>Notifications</b>
<table class="data-table"><thead><tr><th></th><th>Title</th><th>Message</th><th>Date</th></tr></thead><tbody>{rows}</tbody></table>"""

def get_faculty_response():
    faculty = get_faculty_contacts()
    rows = "".join(
        f"<tr><td><b>{f['name']}</b></td><td>{f['subject']}</td><td>{f['email']}</td><td>{f['phone']}</td><td>{f['cabin']}</td></tr>"
        for f in faculty
    )
    return f"""👨‍🏫 <b>Faculty Contacts</b>
<table class="data-table"><thead><tr><th>Name</th><th>Subject</th><th>Email</th><th>Phone</th><th>Cabin</th></tr></thead><tbody>{rows}</tbody></table>"""

def get_performance_insights(reg_no):
    rows = get_marks(reg_no)
    if not rows:
        return "No data available."
    sorted_rows = sorted(rows, key=lambda x: x["marks"])
    weak = sorted_rows[:3]
    strong = list(reversed(sorted_rows[-3:]))
    strong_rows = "".join(f"<tr><td>✅</td><td>{s['subject']}</td><td><b>{s['marks']}/100</b></td><td>{s['grade']}</td></tr>" for s in strong)
    weak_rows = "".join(f"<tr><td>🔴</td><td>{s['subject']}</td><td><b>{s['marks']}/100</b></td><td>{s['grade']}</td></tr>" for s in weak)
    avg = sum(r["marks"] for r in rows) / len(rows)
    if avg >= 80:
        tip = "🌟 Excellent performance! Keep up the great work."
    elif avg >= 60:
        tip = "📈 Good performance. Focus on weak subjects to improve further."
    else:
        tip = "⚡ Seek faculty guidance for weak subjects. Consider extra coaching."
    return f"""💡 <b>Performance Insights</b>
<table class="data-table"><thead><tr><th></th><th>Strong subjects</th><th>Marks</th><th>Grade</th></tr></thead><tbody>{strong_rows}</tbody></table>
<table class="data-table"><thead><tr><th></th><th>Needs improvement</th><th>Marks</th><th>Grade</th></tr></thead><tbody>{weak_rows}</tbody></table>
<small>{tip}</small>"""

def get_course_status_response(reg_no):
    student = get_student_full(reg_no)
    rows = get_marks(reg_no)
    total_subjects = len(rows)
    cleared = sum(1 for r in rows if r["backlog_status"] == 0)
    return f"""📋 <b>Course Completion Status</b>
<table class="data-table">
<tbody>
<tr><td><b>Student</b></td><td>{student['name']} ({student['reg_no']})</td></tr>
<tr><td><b>Branch</b></td><td>{student['branch']}</td></tr>
<tr><td><b>Year</b></td><td>{student['year']}</td></tr>
<tr><td><b>Status</b></td><td>{student['course_status']}</td></tr>
<tr><td><b>Subjects Cleared</b></td><td>{cleared} / {total_subjects}</td></tr>
<tr><td><b>Active Backlogs</b></td><td>{student['backlogs']}</td></tr>
<tr><td><b>CGPA</b></td><td>{student['cgpa']}</td></tr>
<tr><td><b>Class Advisor</b></td><td>{student['class_advisor']}</td></tr>
<tr><td><b>Advisor Phone</b></td><td>{student['advisor_phone']}</td></tr>
</tbody>
</table>"""

def get_calendar_response():
    return """📅 <b>Academic Calendar 2024-25</b>
<table class="data-table">
<thead><tr><th></th><th>Event</th><th>Date</th></tr></thead>
<tbody>
<tr><td>📝</td><td>Mid-Semester Exams</td><td>15 Mar – 22 Mar 2025</td></tr>
<tr><td>📅</td><td>Spring Break</td><td>24 Mar – 31 Mar 2025</td></tr>
<tr><td>🎓</td><td>End-Semester Exams</td><td>20 Apr – 5 May 2025</td></tr>
<tr><td>📋</td><td>Result Declaration</td><td>20 May 2025</td></tr>
<tr><td>🏖️</td><td>Summer Break</td><td>21 May – 30 Jun 2025</td></tr>
<tr><td>🆕</td><td>New Semester Starts</td><td>1 Jul 2025</td></tr>
<tr><td>⚠️</td><td>Fee Payment (Last Date)</td><td>31 Mar 2025</td></tr>
<tr><td>📝</td><td>Exam Form Submission</td><td>10 Apr 2025</td></tr>
</tbody>
</table>"""

def get_repeated_subjects_response(reg_no):
    rows = get_marks(reg_no)
    backlogs = get_backlogs(reg_no)
    if not backlogs:
        return "✅ No repeated subjects. All subjects cleared on first attempt!"
    repeated = {}
    for b in backlogs:
        subj = b["subject"]
        if subj not in repeated:
            repeated[subj] = {"attempts": 1, "best_marks": b["marks"], "semesters": [b["semester"]]}
        else:
            repeated[subj]["attempts"] += 1
            repeated[subj]["semesters"].append(b["semester"])
            if b["marks"] > repeated[subj]["best_marks"]:
                repeated[subj]["best_marks"] = b["marks"]
    rows_html = "".join(
        f"<tr><td>{subj}</td><td>{data['attempts']}</td><td>{', '.join(map(str, data['semesters']))}</td><td><b>{data['best_marks']}</b></td></tr>"
        for subj, data in repeated.items()
    )
    return f"""🔄 <b>Repeated Subjects</b> — Total: <b>{len(repeated)}</b>
<table class="data-table"><thead><tr><th>Subject</th><th>Attempts</th><th>Semesters</th><th>Best Marks</th></tr></thead><tbody>{rows_html}</tbody></table>
<small>📌 Apply for supplementary exams to clear these subjects.</small>"""

def get_incomplete_subjects_response(reg_no):
    rows = get_marks(reg_no)
    if not rows:
        return "No subject data found."
    incomplete = [r for r in rows if r["backlog_status"] == 1]
    in_progress = [r for r in rows if r["marks"] == 0 or r["marks"] is None]
    if not incomplete and not in_progress:
        return "✅ All subjects are complete! No pending subjects."
    rows_html = ""
    for subj in incomplete:
        rows_html += f"<tr><td>🔴</td><td>{subj['subject']}</td><td>Sem {subj['semester']}</td><td>Backlog</td></tr>"
    for subj in in_progress:
        rows_html += f"<tr><td>🟡</td><td>{subj['subject']}</td><td>Sem {subj['semester']}</td><td>In Progress</td></tr>"
    return f"""⏳ <b>Incomplete Subjects</b> — Total: <b>{len(incomplete) + len(in_progress)}</b>
<table class="data-table"><thead><tr><th></th><th>Subject</th><th>Semester</th><th>Status</th></tr></thead><tbody>{rows_html}</tbody></table>
<small>⚡ Please complete these subjects before graduation.</small>"""

def get_academic_office_response():
    return """🏛️ <b>Academic Office Contacts</b>
<table class="data-table">
<thead><tr><th>Department</th><th>Contact</th><th>Email</th><th>Timing</th></tr></thead>
<tbody>
<tr><td>Academic Dean</td><td>040-12345678</td><td>dean.academic@college.edu</td><td>Mon-Fri 9AM-5PM</td></tr>
<tr><td>Examination Cell</td><td>040-12345679</td><td>exam@college.edu</td><td>Mon-Fri 10AM-4PM</td></tr>
<tr><td>Student Affairs</td><td>040-12345680</td><td>student.affairs@college.edu</td><td>Mon-Fri 9AM-5PM</td></tr>
<tr><td>Accounts Office</td><td>040-12345681</td><td>accounts@college.edu</td><td>Mon-Fri 9AM-4PM</td></tr>
<tr><td>Admission Office</td><td>040-12345682</td><td>admissions@college.edu</td><td>Mon-Sat 9AM-5PM</td></tr>
</tbody>
</table>
<small>📍 Visit Block A, Ground Floor for all academic inquiries.</small>"""

def get_counselor_response(reg_no):
    student = get_student_full(reg_no)
    year = student.get('year', 1)
    branch = student.get('branch', 'CSE')
    
    # Counselor data based on year and branch
    counselors = {
        1: {
            'name': 'Dr. Ananya Sharma',
            'designation': 'Student Counselor (First Year)',
            'email': 'counselor.fy@college.edu',
            'phone': '040-12345700',
            'cabin': 'Block A, Room 101',
            'timing': 'Mon-Fri 10AM-4PM',
            'specialization': 'Academic adjustment, Study skills, Time management'
        },
        2: {
            'name': 'Dr. Rajesh Kumar',
            'designation': 'Student Counselor (Second Year)',
            'email': 'counselor.sy@college.edu',
            'phone': '040-12345701',
            'cabin': 'Block A, Room 102',
            'timing': 'Mon-Fri 10AM-4PM',
            'specialization': 'Career guidance, Internship support, Skill development'
        },
        3: {
            'name': 'Dr. Priya Nair',
            'designation': 'Student Counselor (Third Year)',
            'email': 'counselor.ty@college.edu',
            'phone': '040-12345702',
            'cabin': 'Block A, Room 103',
            'timing': 'Mon-Fri 10AM-4PM',
            'specialization': 'Placement preparation, Higher studies, Industry readiness'
        },
        4: {
            'name': 'Dr. Vikram Singh',
            'designation': 'Student Counselor (Final Year)',
            'email': 'counselor.fy@college.edu',
            'phone': '040-12345703',
            'cabin': 'Block A, Room 104',
            'timing': 'Mon-Fri 10AM-4PM',
            'specialization': 'Career counseling, Job placement, Higher education guidance'
        }
    }
    
    counselor = counselors.get(year, counselors[1])
    
    return f"""🧑‍⚕️ <b>Student Counselor Details</b>
<table class="data-table">
<tbody>
<tr><td><b>Counselor</b></td><td>{counselor['name']}</td></tr>
<tr><td><b>Designation</b></td><td>{counselor['designation']}</td></tr>
<tr><td><b>Department</b></td><td>{branch} Department</td></tr>
<tr><td><b>Email</b></td><td>📧 {counselor['email']}</td></tr>
<tr><td><b>Phone</b></td><td>📞 {counselor['phone']}</td></tr>
<tr><td><b>Cabin</b></td><td>📍 {counselor['cabin']}</td></tr>
<tr><td><b>Timing</b></td><td>🕐 {counselor['timing']}</td></tr>
<tr><td><b>Specialization</b></td><td>{counselor['specialization']}</td></tr>
</tbody>
</table>
<small>💡 Book an appointment via email or visit during office hours for academic guidance.</small>"""

def get_class_advisor_response(reg_no):
    """Get class advisor details for the student"""
    student = get_student_full(reg_no)
    year = student.get('year', 1)
    branch = student.get('branch', 'CSE')
    section = student.get('section', 'A')
    
    # Class advisors based on year and branch
    advisors = {
        (1, 'CSE'): {'name': 'Prof. Suresh Kumar', 'phone': '9876501234', 'email': 'suresh.kumar@college.edu', 'cabin': 'Block B, Room 201'},
        (1, 'ECE'): {'name': 'Prof. Lakshmi Devi', 'phone': '9876501235', 'email': 'lakshmi.devi@college.edu', 'cabin': 'Block B, Room 202'},
        (2, 'CSE'): {'name': 'Prof. Ramesh Rao', 'phone': '9876501236', 'email': 'ramesh.rao@college.edu', 'cabin': 'Block B, Room 203'},
        (2, 'ECE'): {'name': 'Prof. Priya Sharma', 'phone': '9876501237', 'email': 'priya.sharma@college.edu', 'cabin': 'Block B, Room 204'},
        (3, 'CSE'): {'name': 'Prof. Venkat Reddy', 'phone': '9876501238', 'email': 'venkat.reddy@college.edu', 'cabin': 'Block B, Room 205'},
        (3, 'ECE'): {'name': 'Prof. Anjali Menon', 'phone': '9876501239', 'email': 'anjali.menon@college.edu', 'cabin': 'Block B, Room 206'},
        (4, 'CSE'): {'name': 'Prof. Krishnan Nair', 'phone': '9876501240', 'email': 'krishnan.nair@college.edu', 'cabin': 'Block B, Room 207'},
        (4, 'ECE'): {'name': 'Prof. Deepa Iyer', 'phone': '9876501241', 'email': 'deepa.iyer@college.edu', 'cabin': 'Block B, Room 208'},
    }
    
    advisor = advisors.get((year, branch), {'name': 'Prof. T. Krishna', 'phone': '9876501000', 'email': 'advisor@college.edu', 'cabin': 'Block B, Room 101'})
    
    return f"""👨‍🏫 <b>Class Advisor Details</b>
<table class="data-table">
<tbody>
<tr><td><b>Student</b></td><td>{student['name']} ({student['reg_no']})</td></tr>
<tr><td><b>Year</b></td><td>{year}st Year</td></tr>
<tr><td><b>Branch</b></td><td>{branch}</td></tr>
<tr><td><b>Section</b></td><td>{section}</td></tr>
<tr><td colspan="2" style="background:rgba(0,201,167,0.1);"><b>Class Advisor</b></td></tr>
<tr><td><b>Name</b></td><td>{advisor['name']}</td></tr>
<tr><td><b>Email</b></td><td>📧 {advisor['email']}</td></tr>
<tr><td><b>Phone</b></td><td>📞 {advisor['phone']}</td></tr>
<tr><td><b>Cabin</b></td><td>📍 {advisor['cabin']}</td></tr>
<tr><td><b>Office Hours</b></td><td>🕐 Mon-Fri 2PM-5PM</td></tr>
</tbody>
</table>
<small>💡 Contact your class advisor for attendance issues, leave applications, and academic guidance.</small>"""

def get_year_cgpa_response(reg_no):
    """Show year-wise CGPA breakdown"""
    student = get_student_full(reg_no)
    sem_data, _ = get_cgpa_history(reg_no)
    current_cgpa = student.get('cgpa', 0)
    year = student.get('year', 1)
    
    if not sem_data:
        return "No CGPA data available."
    
    # Group semesters by year (2 semesters per year)
    year_gpas = {}
    for s in sem_data:
        sem = s['semester']
        yr = (sem + 1) // 2  # Convert semester to year
        if yr not in year_gpas:
            year_gpas[yr] = {'semesters': [], 'total_gpa': 0, 'count': 0}
        year_gpas[yr]['semesters'].append({'sem': sem, 'gpa': s['sem_gpa']})
        year_gpas[yr]['total_gpa'] += s['sem_gpa']
        year_gpas[yr]['count'] += 1
    
    # Calculate year-wise averages
    rows_html = ""
    for yr in sorted(year_gpas.keys()):
        avg_gpa = year_gpas[yr]['total_gpa'] / year_gpas[yr]['count']
        sem_details = ", ".join([f"Sem {s['sem']}: {s['gpa']:.2f}" for s in year_gpas[yr]['semesters']])
        bar = "█" * min(10, int(avg_gpa)) + "░" * (10 - min(10, int(avg_gpa)))
        status = "🏆" if avg_gpa >= 9 else "🌟" if avg_gpa >= 8 else "📈" if avg_gpa >= 7 else "⚠️" if avg_gpa >= 6 else "🚨"
        rows_html += f"<tr><td>{status}</td><td><b>Year {yr}</b></td><td>{avg_gpa:.2f}</td><td class='gpa-bar'>{bar}</td><td><small>{sem_details}</small></td></tr>"
    
    return f"""📊 <b>Year-wise CGPA Analysis</b>
<table class="data-table">
<thead><tr><th></th><th>Year</th><th>Avg GPA</th><th>Progress</th><th>Semester Details</th></tr></thead>
<tbody>{rows_html}</tbody>
</table>
<div style="margin-top:15px;padding:15px;background:rgba(0,201,167,0.1);border-radius:10px;">
<b>Current Overall CGPA: {current_cgpa}</b><br>
<small>Year {year} student | Target: Maintain CGPA ≥ 8.0 for merit scholarship eligibility</small>
</div>
<style>
.gpa-bar {{ font-family: monospace; color: var(--teal); }}
</style>"""

def get_suggestions_response(reg_no):
    """Generate personalized suggestions based on academic performance"""
    student = get_student_full(reg_no)
    marks = get_marks(reg_no)
    attendance_rows, attendance_student = get_attendance(reg_no)
    backlogs = get_backlogs(reg_no)
    cgpa = student.get('cgpa', 0)
    year = student.get('year', 1)
    
    suggestions = []
    
    # CGPA-based suggestions
    if cgpa >= 9.0:
        suggestions.append({
            'category': '🏆 Excellence',
            'suggestion': 'Outstanding academic performance! Consider research projects, paper publications, and leadership roles in technical clubs.',
            'priority': 'high'
        })
    elif cgpa >= 8.0:
        suggestions.append({
            'category': '🌟 Very Good',
            'suggestion': 'Strong academic standing. Focus on industry certifications, internships, and competitive programming.',
            'priority': 'medium'
        })
    elif cgpa >= 7.0:
        suggestions.append({
            'category': '📈 Good',
            'suggestion': 'Good progress. Identify weak subjects and seek faculty guidance. Consider additional coaching for difficult subjects.',
            'priority': 'medium'
        })
    elif cgpa >= 6.0:
        suggestions.append({
            'category': '⚠️ Needs Improvement',
            'suggestion': 'Academic performance needs attention. Schedule meeting with counselor immediately. Focus on fundamental concepts.',
            'priority': 'high'
        })
    else:
        suggestions.append({
            'category': '🚨 Critical',
            'suggestion': 'URGENT: Meet with counselor and class advisor immediately. Consider tutoring support and study group participation.',
            'priority': 'critical'
        })
    
    # Attendance-based suggestions
    overall_attendance = attendance_student.get('attendance_pct', 0)
    if overall_attendance < 75:
        suggestions.append({
            'category': '📋 Attendance Alert',
            'suggestion': f'Overall attendance ({overall_attendance:.1f}%) is below 75%. Risk of detention. Attend all classes regularly.',
            'priority': 'critical'
        })
    elif overall_attendance < 85:
        suggestions.append({
            'category': '📋 Attendance Warning',
            'suggestion': f'Attendance ({overall_attendance:.1f}%) needs improvement. Maintain regular attendance to avoid issues.',
            'priority': 'high'
        })
    
    # Backlog-based suggestions
    backlog_count = len(backlogs) if backlogs else 0
    if backlog_count > 0:
        backlog_subjects = ', '.join([b['subject'] for b in backlogs[:3]])
        suggestions.append({
            'category': f'📚 Backlogs ({backlog_count})',
            'suggestion': f'Active backlogs in: {backlog_subjects}. Register for supplementary exams immediately. Focus on clearing before next semester.',
            'priority': 'critical'
        })
    
    # Repeated subjects check
    repeated = {}
    for b in backlogs:
        subj = b['subject']
        if subj in repeated:
            repeated[subj]['attempts'] += 1
        else:
            repeated[subj] = {'attempts': 1, 'marks': b['marks']}
    
    if repeated:
        repeated_names = ', '.join([f"{s} ({d['attempts']} attempts)" for s, d in list(repeated.items())[:3]])
        suggestions.append({
            'category': '🔄 Repeated Subjects',
            'suggestion': f'Subjects with multiple attempts: {repeated_names}. Seek special coaching and faculty guidance for these subjects.',
            'priority': 'high'
        })
    
    # Incomplete subjects check
    incomplete = [m for m in marks if m.get('backlog_status') == 1]
    in_progress = [m for m in marks if m.get('marks') == 0 or m.get('marks') is None]
    
    if incomplete:
        incomplete_names = ', '.join([s['subject'] for s in incomplete[:3]])
        suggestions.append({
            'category': '⏳ Incomplete Subjects',
            'suggestion': f'Incomplete subjects: {incomplete_names}. Complete all requirements before graduation deadline.',
            'priority': 'high'
        })
    
    # Subject-specific suggestions
    weak_subjects = [m for m in marks if m['marks'] < 50]
    if weak_subjects:
        weak_names = ', '.join([s['subject'] for s in weak_subjects[:3]])
        suggestions.append({
            'category': '📖 Weak Subjects',
            'suggestion': f'Struggling in: {weak_names}. Seek faculty help, join study groups, practice more problems.',
            'priority': 'high'
        })
    
    # Year-specific suggestions
    if year == 1:
        suggestions.append({
            'category': '🎯 First Year Focus',
            'suggestion': 'Build strong foundations in programming and mathematics. Join coding clubs. Develop good study habits.',
            'priority': 'medium'
        })
    elif year == 2:
        suggestions.append({
            'category': '🎯 Second Year Focus',
            'suggestion': 'Start exploring specialization areas. Apply for summer internships. Build projects for portfolio.',
            'priority': 'medium'
        })
    elif year == 3:
        suggestions.append({
            'category': '🎯 Third Year Focus',
            'suggestion': 'Prepare for placements. Practice aptitude and coding interviews. Apply for 6-month internships.',
            'priority': 'high'
        })
    elif year == 4:
        suggestions.append({
            'category': '🎯 Final Year Focus',
            'suggestion': 'Complete all backlogs. Focus on final project. Apply for jobs/higher studies. Prepare for GATE/CAT if applicable.',
            'priority': 'high'
        })
    
    # Sort by priority
    priority_order = {'critical': 0, 'high': 1, 'medium': 2}
    suggestions.sort(key=lambda x: priority_order.get(x['priority'], 3))
    
    rows_html = "".join(
        f"<tr><td>{s['category']}</td><td>{s['suggestion']}</td><td><b class='priority-{s['priority']}'>{s['priority'].upper()}</b></td></tr>"
        for s in suggestions
    )
    
    # Academic summary box
    summary_html = f"""
<div style="margin-top:15px;padding:15px;background:rgba(0,201,167,0.1);border-radius:10px;">
<b>📋 Academic Summary for {student['name']}</b><br>
<span style="display:inline-block;margin:5px 10px 5px 0;">🎓 CGPA: <b>{cgpa}</b></span>
<span style="display:inline-block;margin:5px 10px 5px 0;">📊 Attendance: <b>{overall_attendance:.1f}%</b></span>
<span style="display:inline-block;margin:5px 10px 5px 0;">📚 Backlogs: <b>{backlog_count}</b></span>
<span style="display:inline-block;margin:5px 10px 5px 0;">⚠️ Weak Subjects: <b>{len(weak_subjects)}</b></span>
</div>"""
    
    return f"""💡 <b>Personalized Academic Improvement Suggestions</b>
<small>Based on {student['name']}'s comprehensive performance analysis</small>
<table class="data-table">
<thead><tr><th>Category</th><th>Suggestion</th><th>Priority</th></tr></thead>
<tbody>{rows_html}</tbody>
</table>
{summary_html}
<small>📌 Schedule a meeting with your class advisor or counselor for detailed guidance. Type "class advisor" or "counselor" for contact info.</small>
<style>
.priority-critical {{ color: #ff4444; font-weight: bold; }}
.priority-high {{ color: #ff9944; }}
.priority-medium {{ color: #44aa44; }}
</style>"""

def get_year_semester_response(reg_no):
    """Show year-wise and semester-wise academic data"""
    student = get_student_full(reg_no)
    marks = get_marks(reg_no)
    attendance_rows, _ = get_attendance(reg_no)
    fees = get_fees(reg_no)
    year = student.get('year', 1)
    branch = student.get('branch', 'CSE')
    
    # Organize data by year and semester
    # Assuming 2 semesters per year
    years_data = {}
    for m in marks:
        sem = m['semester']
        yr = (sem + 1) // 2  # Convert semester to year
        if yr not in years_data:
            years_data[yr] = {'semesters': {}, 'total_marks': 0, 'count': 0}
        if sem not in years_data[yr]['semesters']:
            years_data[yr]['semesters'][sem] = {'marks': [], 'attendance': [], 'fees': []}
        years_data[yr]['semesters'][sem]['marks'].append(m)
        years_data[yr]['total_marks'] += m['marks']
        years_data[yr]['count'] += 1
    
    # Add attendance data
    for a in attendance_rows:
        sem = a['semester']
        yr = (sem + 1) // 2
        if yr not in years_data:
            years_data[yr] = {'semesters': {}, 'total_marks': 0, 'count': 0}
        if sem not in years_data[yr]['semesters']:
            years_data[yr]['semesters'][sem] = {'marks': [], 'attendance': [], 'fees': []}
        years_data[yr]['semesters'][sem]['attendance'].append(a)
    
    # Add fee data
    for f in fees:
        sem = f['semester']
        yr = (sem + 1) // 2
        if yr not in years_data:
            years_data[yr] = {'semesters': {}, 'total_marks': 0, 'count': 0}
        if sem not in years_data[yr]['semesters']:
            years_data[yr]['semesters'][sem] = {'marks': [], 'attendance': [], 'fees': []}
        years_data[yr]['semesters'][sem]['fees'].append(f)
    
    if not years_data:
        return "No academic data found."
    
    year_sections = []
    for yr in sorted(years_data.keys()):
        sem_sections = []
        for sem in sorted(years_data[yr]['semesters'].keys()):
            sem_data = years_data[yr]['semesters'][sem]
            
            # Marks table for semester
            marks_rows = "".join(
                f"<tr><td>{m['subject']}</td><td><b>{m['marks']}/100</b></td><td>{m['grade']}</td><td>{'✅' if m['backlog_status'] == 0 else '🔴'}</td></tr>"
                for m in sem_data['marks']
            )
            
            # Attendance for semester
            avg_att = sum(a['attendance_pct'] for a in sem_data['attendance']) / len(sem_data['attendance']) if sem_data['attendance'] else 0
            
            # Fee status for semester
            fee_status = "—"
            if sem_data['fees']:
                fee = sem_data['fees'][0]
                fee_status = f"{fee['status']} (₹{fee['amount_paid']:,.0f}/{fee['amount_due']:,.0f})"
            
            sem_sections.append(f"""
<div class="sem-section">
<b>📚 Semester {sem}</b>
<table class="data-table"><thead><tr><th>Subject</th><th>Marks</th><th>Grade</th><th>Status</th></tr></thead><tbody>{marks_rows}</tbody></table>
<div class="sem-summary">
<span>📊 Avg Attendance: <b>{avg_att:.1f}%</b></span>
<span>💰 Fee: <b>{fee_status}</b></span>
</div>
</div>""")
        
        yr_avg = years_data[yr]['total_marks'] / years_data[yr]['count'] if years_data[yr]['count'] > 0 else 0
        year_sections.append(f"""
<div class="year-view">
<h3>📅 Year {yr} Academic Summary</h3>
<div class="year-avg">Average Score: <b>{yr_avg:.1f}%</b></div>
{''.join(sem_sections)}
</div>""")
    
    return f"""📊 <b>Year-wise & Semester-wise Academic Data</b>
<small>Student: {student['name']} | Year: {year} | Branch: {branch}</small>
{''.join(year_sections)}
<style>
.year-view {{ display: block; margin: 15px 0; padding: 15px; background: var(--card-bg); border-radius: 12px; border: 1px solid var(--card-border); }}
.year-view h3 {{ margin: 0 0 10px 0; color: var(--teal); }}
.sem-section {{ background: rgba(0,0,0,0.2); padding: 12px; border-radius: 8px; margin: 8px 0; }}
.sem-section b {{ font-size: 0.95rem; }}
.sem-summary {{ display: flex; gap: 15px; margin-top: 8px; font-size: 0.85rem; flex-wrap: wrap; }}
.year-avg {{ font-size: 1rem; margin: 8px 0; padding: 8px 12px; background: rgba(0,201,167,0.15); border-radius: 6px; display: inline-block; }}
</style>"""

def get_exams_response():
    return """📝 <b>Upcoming Exams & Schedule</b>
<table class="data-table">
<thead><tr><th>Exam</th><th>Dates</th><th>Registration</th><th>Status</th></tr></thead>
<tbody>
<tr><td>Mid-Semester</td><td>15-22 Mar 2025</td><td>Auto-registered</td><td>🟡 Upcoming</td></tr>
<tr><td>End-Semester</td><td>20 Apr-5 May 2025</td><td>10-15 Apr 2025</td><td>🔴 Registration Open Soon</td></tr>
<tr><td>Supplementary</td><td>10-20 Jun 2025</td><td>1-15 May 2025</td><td>⚪ Not Open</td></tr>
<tr><td>Re-evaluation</td><td>25-30 May 2025</td><td>Online Only</td><td>⚪ Not Open</td></tr>
</tbody>
</table>
<small>📌 Check student portal for hall tickets and exam centers.</small>"""

def get_assignments_response():
    return """📚 <b>Assignment Deadlines</b>
<table class="data-table">
<thead><tr><th>Subject</th><th>Assignment</th><th>Deadline</th><th>Status</th></tr></thead>
<tbody>
<tr><td>DBMS</td><td>ER Diagram Project</td><td>20 Mar 2025</td><td>🟡 5 days left</td></tr>
<tr><td>Data Structures</td><td>Sorting Algorithm Analysis</td><td>25 Mar 2025</td><td>🟢 10 days left</td></tr>
<tr><td>Computer Networks</td><td>Protocol Implementation</td><td>15 Mar 2025</td><td>🔴 Due Tomorrow</td></tr>
<tr><td>Operating Systems</td><td>Process Scheduling Simulator</td><td>30 Mar 2025</td><td>🟢 15 days left</td></tr>
<tr><td>Web Technologies</td><td>Responsive Website Design</td><td>5 Apr 2025</td><td>🟢 21 days left</td></tr>
</tbody>
</table>
<small>⚡ Submit before deadline to avoid late submission penalties.</small>"""

def get_scholarship_response(reg_no):
    fees = get_fees(reg_no)
    total_schol = sum(f.get("scholarship_amount", 0) for f in fees)
    student = get_student_full(reg_no)
    if total_schol > 0:
        return f"""🏅 <b>Scholarship Status</b>
<table class="data-table">
<tbody>
<tr><td><b>Student</b></td><td>{student['name']}</td></tr>
<tr><td><b>CGPA</b></td><td>{student['cgpa']}</td></tr>
<tr><td><b>Status</b></td><td>✅ Merit Scholarship Active</td></tr>
<tr><td><b>Total Received</b></td><td>₹{total_schol:,.0f}</td></tr>
<tr><td colspan="2"><small>Eligibility: CGPA ≥ 8.5 (Merit). Contact accounts office for renewal.</small></td></tr>
</tbody>
</table>"""
    else:
        cgpa = student.get("cgpa", 0)
        if cgpa >= 8.5:
            msg = "✅ Eligible for Merit Scholarship! Contact accounts office."
        else:
            msg = f"CGPA {cgpa} — not currently eligible for merit scholarship (need ≥ 8.5). 📌 Other government schemes may apply."
        return f"""🏅 <b>Scholarship Status</b>
<table class="data-table"><tbody><tr><td><b>Student</b></td><td>{student['name']}</td></tr><tr><td><b>Status</b></td><td>{msg}</td></tr></tbody></table>"""

INTENT_MAP = {
    # More-specific intents FIRST to avoid partial matches
    "low_attendance": ["low attendance", "below 75", "short attendance", "attendance alert", "low att"],
    "year_cgpa": ["year cgpa", "year-wise cgpa", "year wise cgpa", "cgpa by year", "year gpa"],
    "year_semester": ["year wise", "semester wise", "year-wise", "semester-wise", "all semester", "all year", "complete data", "full data"],
    "suggestions": ["suggestion", "recommendation", "advice", "improve", "how to improve", "what should", "guidance", "academic suggestion", "academic improvement"],
    "class_advisor": ["class advisor", "advisor details", "my advisor", "class teacher"],
    "counselor": ["counselor", "counsellor", "counseling", "guidance counselor", "student counselor", "counselor details"],
    "course_status": ["course status", "course completion", "completion status", "year branch"],
    "scholarship": ["scholarship", "merit scholarship", "financial aid"],
    "insights": ["insight", "strong subject", "weak subject", "improvement suggestion", "performance insight", "analyse", "analysis", "strong and weak"],
    "calendar": ["academic calendar", "exam schedule", "upcoming exam", "deadline", "calendar"],
    "repeated_subjects": ["repeated subject", "subject repeated", "attempted multiple", "failed multiple times"],
    "incomplete_subjects": ["incomplete subject", "pending subject", "subject not completed", "subject in progress"],
    "academic_office": ["academic office", "administration", "exam cell", "student affairs", "contact office"],
    "exams": ["upcoming exam", "exam schedule", "exam date", "mid sem", "end sem", "supplementary exam"],
    "assignments": ["assignment", "homework", "project deadline", "submission"],
    # General intents after specifics
    "attendance": ["attendance", "present", "absent"],
    "marks": ["marks", "score", "result", "grades", "subject marks"],
    "cgpa": ["cgpa", "gpa", "grade point", "semester cgpa"],
    "backlogs": ["backlog", "arrear", "fail", "failed subject", "number of backlogs"],
    "fees": ["fee", "fees", "payment", "paid", "pending fee", "due"],
    "notifications": ["notification", "notice", "alert", "announcement"],
    "faculty": ["faculty", "teacher", "professor", "contact", "staff"],
    "help": ["help", "menu", "options", "what can you do", "commands", "hi", "hello", "hey"],
    "logout": ["logout", "exit", "bye", "goodbye", "end session"],
}

def detect_intent(text):
    text = text.lower().strip()
    for intent, keywords in INTENT_MAP.items():
        for kw in keywords:
            if kw in text:
                return intent
    return "unknown"

def get_help_menu():
    return """👋 <b>Hello! I'm your Parent Information Assistant.</b>

Here's what I can help you with:

📊 <b>Academic Monitoring</b>
   • "Show attendance" — Overall & subject-wise
   • "Low attendance alert" — Below 75% warning

📝 <b>Academic Performance</b>
   • "Show marks" — Subject-wise marks
   • "Show CGPA" — Current & semester-wise
   • "Year-wise CGPA" — CGPA by year with progress

⚠️ <b>Academic Status</b>
   • "Show backlogs" — Number of backlogs
   • "Repeated subjects" — Multiple attempts
   • "Incomplete subjects" — Pending/In progress
   • "Course status" — Completion details

📅 <b>Year-wise & Semester-wise Data</b>
   • "Year-wise data" — All years with semesters
   • "Semester-wise" — Complete semester breakdown

📢 <b>Academic Notifications</b>
   • "Upcoming exams" — Exam schedule
   • "Assignments" — Deadlines & submissions
   • "Show notifications" — Alerts & announcements
   • "Academic calendar" — Important dates

💰 <b>Financial Information</b>
   • "Fee status" — Payment history
   • "Scholarship" — Status & eligibility

👨‍🏫 <b>Communication Support</b>
   • "Faculty contacts" — Teacher details
   • "Academic office" — Administration contacts
   • "Class advisor" — Advisor details with contact
   • "Counselor details" — Student counselor info

💡 <b>Performance & Guidance</b>
   • "Performance insights" — Strong/weak subjects
   • "Suggestions" — Academic improvement advice

🚪 <b>System Utilities</b>
   • "Logout" — End session

Just type naturally — I understand plain English!"""
def handle_chat(intent, reg_no):
    handlers = {
        "attendance": lambda: get_attendance_response(reg_no),
        "low_attendance": lambda: get_low_attendance_response(reg_no),
        "marks": lambda: get_marks_response(reg_no),
        "cgpa": lambda: get_cgpa_response(reg_no),
        "year_cgpa": lambda: get_year_cgpa_response(reg_no),
        "backlogs": lambda: get_backlogs_response(reg_no),
        "repeated_subjects": lambda: get_repeated_subjects_response(reg_no),
        "incomplete_subjects": lambda: get_incomplete_subjects_response(reg_no),
        "fees": lambda: get_fees_response(reg_no),
        "scholarship": lambda: get_scholarship_response(reg_no),
        "notifications": lambda: get_notifications_response(reg_no),
        "faculty": lambda: get_faculty_response(),
        "academic_office": lambda: get_academic_office_response(),
        "insights": lambda: get_performance_insights(reg_no),
        "course_status": lambda: get_course_status_response(reg_no),
        "calendar": lambda: get_calendar_response(),
        "exams": lambda: get_exams_response(),
        "assignments": lambda: get_assignments_response(),
        "suggestions": lambda: get_suggestions_response(reg_no),
        "counselor": lambda: get_counselor_response(reg_no),
        "class_advisor": lambda: get_class_advisor_response(reg_no),
        "year_semester": lambda: get_year_semester_response(reg_no),
        "help": lambda: get_help_menu(),
        "logout": lambda: "LOGOUT",
        "unknown": lambda: "🤔 I didn't quite get that. Type <b>help</b> to see what I can do!",
    }
    return handlers.get(intent, handlers["unknown"])()
