import sys, os, random
sys.path.insert(0, r'c:\Users\Victus\Desktop\AI-Timetable-Optimizer')
import pandas as pd
from src.generator import generate_random_timetable
from src.timetable import format_intake_program_mapping
from src.constraints import get_timeslots_dict, check_student_group_clash, check_lecturer_clash, check_room_clash, parse_time_to_minutes

courses = pd.DataFrame([
    {'course_id':'CS22023','course_name':'Artificial Intelligence','lecturer_id':'L001','student_count':0,'duration_hours':2.0},
    {'course_id':'CS22993','course_name':'Group Project in SD','lecturer_id':'L002','student_count':0,'duration_hours':3.0},
    {'course_id':'SE22013','course_name':'Software Architecture','lecturer_id':'L003','student_count':0,'duration_hours':2.0},
    {'course_id':'SE22022','course_name':'Software Project Mgmt','lecturer_id':'L003','student_count':0,'duration_hours':2.0},
    {'course_id':'COE22012','course_name':'Adv Computer Arch','lecturer_id':'L004','student_count':0,'duration_hours':2.0},
    {'course_id':'COE22023','course_name':'Engineering Drawing','lecturer_id':'L005','student_count':0,'duration_hours':3.0},
    {'course_id':'COE22032','course_name':'Computer Interfacing','lecturer_id':'L006','student_count':0,'duration_hours':2.0},
    {'course_id':'CM22112','course_name':'Numerical Methods','lecturer_id':'L007','student_count':0,'duration_hours':2.0},
    {'course_id':'CS22012','course_name':'ADSA','lecturer_id':'L008','student_count':0,'duration_hours':2.0},
    {'course_id':'DL4162','course_name':'Research Writing Skills','lecturer_id':'L009','student_count':0,'duration_hours':1.5},
])
rooms = pd.DataFrame([
    {'room_id':'FGS_3-1','capacity':100},
    {'room_id':'LT-A/LT-B','capacity':150},
    {'room_id':'FOE_2-4','capacity':40},
])
days=['Monday','Tuesday','Wednesday','Thursday','Friday']
times=[('08:00','08:30'),('08:30','09:00'),('09:00','09:30'),('09:30','10:00'),
       ('10:00','10:30'),('10:30','11:00'),('11:00','11:30'),('11:30','12:00'),
       ('12:00','12:30'),('12:30','13:00'),('13:00','13:30'),('13:30','14:00'),
       ('14:00','14:30'),('14:30','15:00'),('15:00','15:30'),('15:30','16:00')]
ts_rows=[]
for d in days:
    for s,e in times:
        key=d[:3]+'_'+s.replace(':','')
        ts_rows.append({'slot_id':key,'day':d,'start_time':s,'end_time':e})
timeslots=pd.DataFrame(ts_rows)

mappings=pd.DataFrame([
    ('CS22023','43','CS'),('CS22023','43','SE'),('CS22023','42','CE'),('CS22023','41','CS'),
    ('CS22993','41','CS'),('CS22993','41','SE'),('CS22993','42','CE'),
    ('SE22013','42','CS'),('SE22013','42','SE'),
    ('SE22022','42','CS'),('SE22022','42','SE'),
    ('COE22012','42','CE'),
    ('COE22023','42','CE'),
    ('COE22032','43','CE'),('COE22032','42','CE'),('COE22032','41','CE'),('COE22032','40','CE'),
    ('CM22112','42','CS'),('CM22112','42','SE'),('CM22112','42','CE'),
    ('CS22012','42','CS'),('CS22012','42','SE'),('CS22012','42','CE'),
    ('DL4162','43','CS'),('DL4162','42','CS'),('DL4162','41','SE'),('DL4162','40','CE'),
],columns=['course_id','intake_id','program_id'])

random.seed(42)
tt=generate_random_timetable(courses,rooms,timeslots,mappings)
course_info={}
for _,row in courses.iterrows():
    cid=str(row['course_id']).strip()
    course_info[cid]={'lecturer_id':str(row['lecturer_id']).strip(),'student_count':0,'duration_hours':float(row['duration_hours'])}
tt.course_info=course_info
tt.timeslots_dict=get_timeslots_dict(timeslots)
tsd=get_timeslots_dict(timeslots)

print(f'Total entries: {len(tt.entries)} (expected: {len(courses)})')
print()
for entry in tt.entries:
    slot=tsd.get(str(entry.timeslot_id).strip(),{})
    dur=course_info.get(entry.course_id,{}).get('duration_hours',1.0)
    sm=parse_time_to_minutes(slot.get('start_time','08:00'))
    em=sm+int(dur*60)
    mapping=format_intake_program_mapping(entry.student_groups)
    groups=', '.join(entry.student_groups)
    cname=courses[courses['course_id']==entry.course_id]['course_name'].values[0]
    print(f'Course:           {entry.course_id} - {cname}')
    print(f'Intake->Programs: {mapping}')
    print(f'Student Groups:   {groups}')
    print(f'Duration:         {dur}h')
    print(f'Day:              {slot.get("day","?")}')
    print(f'Start:            {slot.get("start_time","?")}')
    print(f'End:              {em//60:02d}:{em%60:02d}')
    print(f'Room:             {entry.room_id}')
    print()

print('--- CONSTRAINT CHECK (random, not GA-optimized) ---')
rc=check_room_clash(tt)
lc=check_lecturer_clash(tt,courses)
sc=check_student_group_clash(tt)
print(f'Room clashes:          {rc}')
print(f'Lecturer clashes:      {lc}')
print(f'Student group clashes: {sc}')
