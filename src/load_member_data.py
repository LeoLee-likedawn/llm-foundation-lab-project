from common import DB_TUNIVERSE, TABLE_TUNIVERSE_MEM_LIST, f_print_log

import pandas as pd
import sqlite3

#로그 출력 여부
f_print_log = True

aff_hist_file = "data/PRJ_MEM_LISTS_CSV.csv"
aff_hist_data = pd.read_csv(aff_hist_file)

print(f"load completed...FILE[{aff_hist_file}] CNT[{aff_hist_data.shape[0]}]")
aff_hist_data.head(2)
print("-"*80)

aff_hist_data.columns = ['MBR_NUM', 'MBR_NM', 'MPHON_NUM', 'EMIL_ADDR']
# 데이터 타입 변환
def convert_to_numeric_safely(value):
    try:
        return pd.to_numeric(value)
    except:
        return None

def convert_to_datetime_safely(value):
    try:
        return pd.to_datetime(value)
    except:
        return None

def remove_dot_zero(s: str) -> str:
    """
    문자열이 '.0'으로 끝나면 그 부분을 제거한 문자열을 반환합니다.
    그렇지 않으면 원래 문자열을 그대로 반환합니다.
    """
    if s.endswith(".0"):
        return s[:-2]
    return s

def add_leading_zero(s: str) -> str:
    """
    문자열이 11자리가 아니고, 0으로 시작하지 않으면
    문자열 앞에 '0'을 추가해서 반환
    """
    if len(s) != 11 and not s.startswith("0"):
        return "0" + s
    return s

# 각 컬럼의 데이터 타입 변환
aff_hist_data['MBR_NUM'] = aff_hist_data['MBR_NUM'].apply(lambda x: str(x).strip())
aff_hist_data['MBR_NM'] = aff_hist_data['MBR_NM'].apply(lambda x: str(x).strip())
aff_hist_data['MPHON_NUM'] = aff_hist_data['MPHON_NUM'].apply(lambda x: str(x).strip())
aff_hist_data['EMIL_ADDR'] = aff_hist_data['EMIL_ADDR'].apply(lambda x: str(x).strip())

print("convert type of column completed...")
aff_hist_data.info()
print("-"*80)

# SQLite 데이터베이스 생성
conn = sqlite3.connect(DB_TUNIVERSE)
cursor = conn.cursor()

if f_print_log:
    print(f"connect database completed...DB[{DB_TUNIVERSE}]")
    print("-"*80)

# 테이블 삭제 (if exists)
cursor.execute(f"DROP TABLE IF EXISTS {TABLE_TUNIVERSE_MEM_LIST}")

# 테이블 생성
cursor.execute("""
CREATE TABLE mem_info_list (
    MBR_NUM TEXT,
    MBR_NM TEXT,
    MPHON_NUM TEXT,
    EMIL_ADDR TEXT
)
""")

if f_print_log:
    print(f"create table completed...TBL[{TABLE_TUNIVERSE_MEM_LIST}]")
    print("--- table info. ---")
    aff_hist_data.info()
    print("-"*80)

# 데이터 삽입
for _, row in aff_hist_data.iterrows():
    try:
        cursor.execute(f"""
        INSERT INTO {TABLE_TUNIVERSE_MEM_LIST} VALUES (?, ?, ?, ?)
        """, (
            str(remove_dot_zero(row['MBR_NUM'])),
            str(remove_dot_zero(row['MBR_NM'])),
            str(add_leading_zero(remove_dot_zero(row['MPHON_NUM']))),
            str(remove_dot_zero(row['EMIL_ADDR']))
        ))
    except Exception as e:
        print(f"Error inserting row: {row}")
        print(f"Error message: {str(e)}")
        continue

# 변경사항 저장
conn.commit()

# 데이터베이스 상태 확인
cursor.execute("SELECT COUNT(*) FROM mem_info_list")
aff_if_hist_count = cursor.fetchone()[0]

if f_print_log:
    print(f"insert table completed...TOT_CNT[{aff_if_hist_count}]")
    cursor.execute(f"SELECT * FROM {TABLE_TUNIVERSE_MEM_LIST} LIMIT 3")
    print("--- sample data ---")
    for fetch in cursor.fetchall():
        print("- ", fetch)
    print("-"*80)