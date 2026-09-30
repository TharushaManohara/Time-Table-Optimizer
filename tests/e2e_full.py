import sys, os, time
sys.path.insert(0, r'c:\Users\Victus\Desktop\AI-Timetable-Optimizer')
import pandas as pd, random
random.seed(42)
from src.constraints import parse_time_to_minutes
from src.timetable import format_intake_program_mapping

# ── Data ──────────────────────────────────────────────────────────────
subjects = pd.DataFrame({
    'course_id':['CS22023','CS22993','SE22013','SE22022','COE22012','COE22023','COE22032','CM22112','CS22012','DL4162'],
    'subject_name':['Artificial Intelligence','Group Project in SD','Software Architecture',
                    'Software Project Mgmt','Adv Computer Arch','Engineering Drawing',
                    'Computer Interfacing','Numerical Methods','ADSA','Research Writing Skills'],
    'lecturer_id':['L001','L002','L003','L003','L004','L005','L006','L007','L008','L009'],
    'duration_hours':[2.0,3.0,2.0,2.0,2.0,3.0,2.0,2.0,2.0,1.5],
    'credits':[3,3,3,2,2,2,2,2,2,2],'student_count':[0]*10
})
rooms     = pd.read_csv(r'c:\Users\Victus\Desktop\AI-Timetable-Optimizer\data\rooms.csv')
lecs      = pd.read_csv(r'c:\Users\Victus\Desktop\AI-Timetable-Optimizer\data\lecturers.csv')
timeslots = pd.read_csv(r'c:\Users\Victus\Desktop\AI-Timetable-Optimizer\data\timeslots.csv')
sg = pd.DataFrame([
    ('CS22023','43','CS'),('CS22023','43','SE'),('CS22023','42','CE'),('CS22023','41','CS'),
    ('CS22993','41','CS'),('CS22993','41','SE'),('CS22993','42','CE'),
    ('SE22013','42','CS'),('SE22013','42','SE'),
    ('SE22022','42','CS'),('SE22022','42','SE'),
    ('COE22012','42','CE'),('COE22023','42','CE'),
    ('COE22032','43','CE'),('COE22032','42','CE'),('COE22032','41','CE'),('COE22032','40','CE'),
    ('CM22112','42','CS'),('CM22112','42','SE'),('CM22112','42','CE'),
    ('CS22012','42','CS'),('CS22012','42','SE'),('CS22012','42','CE'),
    ('DL4162','43','CS'),('DL4162','42','CS'),('DL4162','41','SE'),('DL4162','40','CE'),
], columns=['course_id','intake_id','program_id'])
ip = pd.DataFrame([
    ('40_CE','40','CE',30),('40_CS','40','CS',30),('40_SE','40','SE',30),
    ('41_CE','41','CE',25),('41_CS','41','CS',25),('41_SE','41','SE',25),
    ('42_CE','42','CE',24),('42_CS','42','CS',28),('42_SE','42','SE',30),
    ('43_CE','43','CE',20),('43_CS','43','CS',20),('43_SE','43','SE',20),
], columns=['group_id','intake_id','program_id','student_count'])

# ── GA Setup ──────────────────────────────────────────────────────────
from src.genetic_algorithm import GeneticAlgorithm
from src.constraints import (check_room_clash,check_lecturer_clash,
    check_student_group_clash,check_room_capacity,check_lecturer_availability)

print('=== STEP 1: INITIAL POPULATION ===')
t0=time.time()
ga=GeneticAlgorithm(subjects,rooms,lecs,timeslots,sg,ip,50)
ga.create_initial_population()
print(f'Init pop created: {time.time()-t0:.2f}s, N={len(ga.population)}')

scores=ga.evaluate_population()
init_best=min(scores); init_worst=max(scores)
print(f'Initial fitness: best={init_best:,}  worst={init_worst:,}  mean={sum(scores)/len(scores):,.0f}')

bi=scores.index(min(scores)); btt=ga.population[bi]
btt.course_info=ga.course_info; btt.timeslots_dict=ga.timeslots_dict
rc0=check_room_clash(btt); lc0=check_lecturer_clash(btt,ga.course_info)
sc0=check_student_group_clash(btt); cap0=check_room_capacity(btt,ga.course_info,ga.room_capacities,ga.group_capacities)
la0=check_lecturer_availability(btt,ga.course_info,ga.lecturers_set,timeslots)
print(f'Best initial violations: RC={rc0} LC={lc0} SC={sc0} Cap={cap0} LA={la0} TOTAL={rc0+lc0+sc0+cap0+la0}')

print('\n=== STEP 2: GA 100 GENERATIONS ===')
t_ga=time.time(); fh=[]; best_ever=None; best_ever_f=float('inf')
for gen in range(100):
    fs=ga.evaluate_population(); bf=min(fs); fh.append(bf)
    if bf<best_ever_f:
        best_ever_f=bf; idx=fs.index(bf); best_ever=ga.copy_timetable(ga.population[idx])
    ga.create_new_generation()
    if gen%25==0: print(f'  Gen {gen:3d}: best={bf:,}',flush=True)
t_ga2=time.time()-t_ga
print(f'GA done in {t_ga2:.2f}s, best={best_ever_f:,}')
print(f'History first 5: {fh[:5]}')
print(f'History last  5: {fh[-5:]}')

print('\n=== STEP 3: FINAL CONSTRAINT CHECK ===')
best_ever.course_info=ga.course_info; best_ever.timeslots_dict=ga.timeslots_dict
rc=check_room_clash(best_ever); lc=check_lecturer_clash(best_ever,ga.course_info)
sc=check_student_group_clash(best_ever); cap=check_room_capacity(best_ever,ga.course_info,ga.room_capacities,ga.group_capacities)
la=check_lecturer_availability(best_ever,ga.course_info,ga.lecturers_set,timeslots)
tot=rc+lc+sc+cap+la
print(f'RC={rc}  LC={lc}  SC={sc}  Cap={cap}  LA={la}  TOTAL={tot}')
if tot==0: print('=> TIMETABLE IS 100% CONSTRAINT-VALID')
else: print(f'=> {tot} violation(s) remain')

print('\n=== STEP 4: TIMETABLE ENTRIES ===')
tsd=ga.timeslots_dict; ci=ga.course_info
entries=[]
for entry in best_ever.entries:
    slot=tsd.get(str(entry.timeslot_id).strip(),{})
    dur=float(ci.get(entry.course_id,{}).get('duration_hours',1.0))
    sm=parse_time_to_minutes(slot.get('start_time','08:00'))
    em=sm+int(dur*60)
    entries.append({'cid':entry.course_id,'day':slot.get('day','?'),
                    'start':slot.get('start_time','?'),'end':f'{em//60:02d}:{em%60:02d}',
                    'dur':dur,'room':entry.room_id,
                    'mapping':format_intake_program_mapping(entry.student_groups),
                    'groups':entry.student_groups})
day_o=['Monday','Tuesday','Wednesday','Thursday','Friday']
print(f'Total entries: {len(entries)}')
for e in sorted(entries,key=lambda x:(day_o.index(x['day']) if x['day'] in day_o else 99,x['start'])):
    print(f'  {e["cid"]:12s} | {e["day"]:9s} {e["start"]}-{e["end"]} ({e["dur"]}h) | {e["room"]:15s} | {e["mapping"]}')
all_starts=[e['start'] for e in entries]; all_ends=[e['end'] for e in entries]
print(f'Earliest start={min(all_starts)}  Latest start={max(all_starts)}  Latest end={max(all_ends)}')
dur_c={}
for e in entries: dur_c[e['dur']]=dur_c.get(e['dur'],0)+1
print(f'Duration breakdown: {dur_c}')

print('\n=== STEP 5: TIMETABLE DF + INTAKE VIEWS ===')
rows=[]
for entry in best_ever.entries:
    slot=tsd.get(str(entry.timeslot_id).strip(),{})
    sub=subjects[subjects['course_id'].astype(str)==str(entry.course_id)]
    if sub.empty: continue
    sub=sub.iloc[0]
    dur=float(ci.get(entry.course_id,{}).get('duration_hours',1.0))
    sm=parse_time_to_minutes(slot.get('start_time','08:00'))
    em=sm+int(dur*60)
    intakes=list(set(str(i).strip() for i,p in entry.intake_programs))
    rows.append({'Course':entry.course_id,'Subject':sub['subject_name'],'Lecturer':sub['lecturer_id'],
                 'Intake':','.join(sorted(intakes)),
                 'Intake -> Programs':format_intake_program_mapping(entry.student_groups),
                 'Student Group(s)':', '.join(entry.student_groups),'Student Count':0,
                 'Day':slot.get('day','?'),'Start Time':slot.get('start_time','?'),
                 'End Time':f'{em//60:02d}:{em%60:02d}','Room':entry.room_id})
tdf=pd.DataFrame(rows)
print(f'timetable_df: {len(tdf)} rows x {len(tdf.columns)} cols')
for iv in ['40','41','42','43']:
    fdf=tdf[tdf['Intake'].apply(lambda v: iv in [p.strip() for p in str(v).split(',')])]
    print(f'  Intake {iv}: {len(fdf)} entries  {list(fdf["Course"].values)}')
print(f'  Global  : {len(tdf)} entries')

print('\n=== STEP 6: LUNCH BREAK ===')
cands=['12:00 - 12:30','12:30 - 13:00','11:30 - 12:00','11:00 - 11:30','13:00 - 13:30','13:30 - 14:00']
days_l=['Monday','Tuesday','Wednesday','Thursday','Friday']
def find_lunch(df):
    for cand in cands:
        cs,ce=cand.split(' - ')
        cst=parse_time_to_minutes(cs); cen=parse_time_to_minutes(ce)
        ok=True
        for day in days_l:
            for _,row in df[df['Day'].str.strip().str.lower()==day.lower()].iterrows():
                ls=parse_time_to_minutes(str(row.get('Start Time',''))); le=parse_time_to_minutes(str(row.get('End Time','')))
                if ls<cen and cst<le: ok=False; break
            if not ok: break
        if ok: return cand,True
    return '12:00 - 12:30(fallback)',False
sg_l,com_g=find_lunch(tdf)
print(f'Global : common={com_g}  slot={sg_l}')
for iv in ['40','41','42','43']:
    fdf2=tdf[tdf['Intake'].apply(lambda v: iv in [p.strip() for p in str(v).split(',')])]
    sl_iv,com_iv=find_lunch(fdf2)
    print(f'Intake {iv}: common={com_iv}  slot={sl_iv}')

print('\n=== STEP 7: EXPORTS ===')
from src.export_engine import generate_timetable_pdf,generate_timetable_excel
def build_grid(df,lbd,com):
    ts2=timeslots.copy(); ts2['sm']=ts2['start_time'].apply(parse_time_to_minutes)
    ts2=ts2.sort_values('sm')
    us=[]; seen=set()
    for _,r in ts2.iterrows():
        t=f"{r['start_time']} - {r['end_time']}"
        if t not in seen: seen.add(t); us.append(t)
    g=pd.DataFrame('',index=us,columns=days_l)
    gd={}
    for day in days_l:
        for t in us: gd[(t,day)]={'rowspan':1,'text':'','is_start':True,'is_lunch':False}
    for day in days_l:
        ls2=lbd.get(day)
        if ls2 and ls2 in g.index:
            gd[(ls2,day)]={'rowspan':1,'text':'LUNCH BREAK','is_start':True,'is_lunch':True}
    for _,row in df.iterrows():
        day=str(row['Day']).strip(); start=str(row['Start Time']).strip(); end=str(row['End Time']).strip()
        sn=(parse_time_to_minutes(end)-parse_time_to_minutes(start))//30
        ss=next((t for t in us if t.startswith(start)),None)
        if not ss or day not in days_l: continue
        try: si=us.index(ss)
        except: continue
        mapping_col='Intake -> Programs'
        content=f"**{row['Subject']}**\n*{row['Room']}*\n{row['Lecturer']}\n{row.get(mapping_col,'')}"
        gd[(ss,day)]={'rowspan':sn,'text':content,'is_start':True,'is_lunch':False}
        for off in range(1,sn):
            if si+off<len(us):
                sp=us[si+off]; gd[(sp,day)]={'rowspan':0,'text':'','is_start':False,'is_lunch':False}
    return g,gd,us

hi={'university_name':'KDU','faculty_name':'FOC','semester_name':'Sem IV','week_name':'Week 7','validity_period':'Aug 2026','title_label':'Global'}
leg=pd.DataFrame([{'Course Code':e['cid'],'Subject Name':e['mapping'],'Lecturer':'','Duration':f"{e['dur']}h",'Intake -> Programs':e['mapping']} for e in entries])
lbd_g={d:sg_l for d in days_l}
gdf,gdet,usl=build_grid(tdf,lbd_g,com_g)

tdf2=tdf.rename(columns={'Intake -> Programs':'Intake \u2192 Programs'})
# rename leg too
leg2=leg.rename(columns={'Intake -> Programs':'Intake \u2192 Programs'})
for _,r in tdf2.iterrows(): r['Intake \u2192 Programs']=r.get('Intake \u2192 Programs','')

try:
    csv_b=tdf2.to_csv(index=False).encode('utf-8')
    print(f'  CSV  : {len(csv_b):,}B  OK')
except Exception as ex: print(f'  CSV FAIL: {ex}')

try:
    pdf_b=generate_timetable_pdf(tdf2,gdf,gdet,usl,lbd_g,com_g,hi,leg2)
    print(f'  PDF  : {len(pdf_b):,}B  OK')
except Exception as ex: print(f'  PDF FAIL: {ex}')

try:
    xl_b=generate_timetable_excel(tdf2,gdf,gdet,usl,lbd_g,com_g,hi,leg2)
    print(f'  Excel: {len(xl_b):,}B  OK')
except Exception as ex: print(f'  Excel FAIL: {ex}')

for iv in ['40','41','42','43']:
    fdf3=tdf2[tdf2['Intake'].apply(lambda v: iv in [p.strip() for p in str(v).split(',')])].copy()
    if fdf3.empty: print(f'  Intake {iv}: no entries'); continue
    sl3,com3=find_lunch(fdf3); lbd3={d:sl3 for d in days_l}
    g3,gd3,us3=build_grid(fdf3,lbd3,com3); h3=hi.copy(); h3['title_label']=f'Intake {iv}'
    try:
        c3=fdf3.to_csv(index=False).encode('utf-8')
        p3=generate_timetable_pdf(fdf3,g3,gd3,us3,lbd3,com3,h3,leg2)
        x3=generate_timetable_excel(fdf3,g3,gd3,us3,lbd3,com3,h3,leg2)
        print(f'  Intake {iv}: CSV={len(c3):,}B  PDF={len(p3):,}B  Excel={len(x3):,}B  OK')
    except Exception as ex: print(f'  Intake {iv} EXPORT FAIL: {ex}')

print('\nVALIDATION COMPLETE')
