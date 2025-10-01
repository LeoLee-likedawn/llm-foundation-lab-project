from common import DB_TUNIVERSE, TABLE_TUNIVERSE_AFF_HIST, f_print_log

import pandas as pd
import sqlite3

#로그 출력 여부
f_print_log = True

aff_hist_file = "data/PRJ_AFFC_HIST_EN_CSV.csv"

#df_qa_test = pd.read_excel("data/PRJ_AFFC_HIST_XLS.xls")
aff_hist_data = pd.read_csv(aff_hist_file)

print(f"load completed...FILE[{aff_hist_file}] CNT[{aff_hist_data.shape[0]}]")
aff_hist_data.head(2)
print("-"*80)


aff_hist_data.columns = ['AUDIT_DTM', 'AUDIT_ID', 'MBR_NUM', 'MBR_NM', 'CTR_NUM', 'CTR_SVC_NUM', 'AFFC_BZR_NM', 'AFFC_LNKG_TSK_CD', 'AFFC_LNKG_TRMS_CD', 'TRMS_RSLT_CD', 'TRMS_ERR_CD', 'TRMS_ERR_MSG_CTT', 'TRMS_REQ_CNTT', 'TRMS_RES_CNTT', 'PRD_ID', 'PRD_NM', 'SKU_ID', 'SKU_NM']
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

# 각 컬럼의 데이터 타입 변환
aff_hist_data['AUDIT_DTM'] = aff_hist_data['AUDIT_DTM'].apply(convert_to_datetime_safely)
aff_hist_data['AUDIT_ID'] = aff_hist_data['AUDIT_ID'].apply(lambda x: str(x).strip())
aff_hist_data['MBR_NUM'] = aff_hist_data['MBR_NUM'].apply(lambda x: str(x).strip())
aff_hist_data['MBR_NM'] = aff_hist_data['MBR_NM'].apply(lambda x: str(x).strip())
aff_hist_data['CTR_NUM'] = aff_hist_data['CTR_NUM'].apply(lambda x: str(x).strip())
aff_hist_data['CTR_SVC_NUM'] = aff_hist_data['CTR_SVC_NUM'].apply(lambda x: str(x).strip())
aff_hist_data['AFFC_BZR_NM'] = aff_hist_data['AFFC_BZR_NM'].apply(lambda x: str(x).strip())
aff_hist_data['AFFC_LNKG_TSK_CD'] = aff_hist_data['AFFC_LNKG_TSK_CD'].apply(lambda x: str(x).strip())
aff_hist_data['AFFC_LNKG_TRMS_CD'] = aff_hist_data['AFFC_LNKG_TRMS_CD'].apply(lambda x: str(x).strip())
aff_hist_data['TRMS_RSLT_CD'] = aff_hist_data['TRMS_RSLT_CD'].apply(lambda x: str(x).strip())
aff_hist_data['TRMS_ERR_CD'] = aff_hist_data['TRMS_ERR_CD'].apply(lambda x: str(x).strip())
aff_hist_data['TRMS_ERR_MSG_CTT'] = aff_hist_data['TRMS_ERR_MSG_CTT'].apply(lambda x: str(x).strip())
aff_hist_data['TRMS_REQ_CNTT'] = aff_hist_data['TRMS_REQ_CNTT'].apply(lambda x: str(x).strip())
aff_hist_data['TRMS_RES_CNTT'] = aff_hist_data['TRMS_RES_CNTT'].apply(lambda x: str(x).strip())
aff_hist_data['PRD_ID'] = aff_hist_data['PRD_ID'].apply(lambda x: str(x).strip())
aff_hist_data['PRD_NM'] = aff_hist_data['PRD_NM'].apply(lambda x: str(x).strip())
aff_hist_data['SKU_ID'] = aff_hist_data['SKU_ID'].apply(lambda x: str(x).strip())
aff_hist_data['SKU_NM'] = aff_hist_data['SKU_NM'].apply(lambda x: str(x).strip())

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
cursor.execute(f"DROP TABLE IF EXISTS {TABLE_TUNIVERSE_AFF_HIST}")

# 테이블 생성
cursor.execute("""
CREATE TABLE aff_if_hist (
    AUDIT_DTM DATETIME,
    AUDIT_ID TEXT,
    MBR_NUM TEXT,
    MBR_NM TEXT,
    CTR_NUM TEXT,
    CTR_SVC_NUM TEXT,
    AFFC_BZR_NM TEXT,
    AFFC_LNKG_TSK_CD TEXT,
    AFFC_LNKG_TRMS_CD TEXT,
    TRMS_RSLT_CD TEXT,
    TRMS_ERR_CD TEXT,
    TRMS_ERR_MSG_CTT TEXT,
    TRMS_REQ_CNTT TEXT,
    TRMS_RES_CNTT TEXT,
    PRD_ID TEXT,
    PRD_NM TEXT,
    SKU_ID TEXT,
    SKU_NM TEXT
)
""")

if f_print_log:
    print(f"create table completed...TBL[{TABLE_TUNIVERSE_AFF_HIST}]")
    print("--- table info. ---")
    aff_hist_data.info()
    print("-"*80)

# 데이터 삽입
for _, row in aff_hist_data.iterrows():
    try:
        cursor.execute(f"""
        INSERT INTO {TABLE_TUNIVERSE_AFF_HIST} VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            str(row['AUDIT_DTM']),
            str(row['AUDIT_ID']),
            str(row['MBR_NUM']),
            str(row['MBR_NM']),
            str(row['CTR_NUM']),
            str(row['CTR_SVC_NUM']),
            str(row['AFFC_BZR_NM']),
            str(row['AFFC_LNKG_TSK_CD']),
            str(row['AFFC_LNKG_TRMS_CD']),
            str(row['TRMS_RSLT_CD']),
            str(row['TRMS_ERR_CD']),
            str(row['TRMS_ERR_MSG_CTT']),
            str(row['TRMS_REQ_CNTT']),
            str(row['TRMS_RES_CNTT']),
            str(row['PRD_ID']),
            str(row['PRD_NM']),
            str(row['SKU_ID']),
            str(row['SKU_NM'])
        ))
    except Exception as e:
        print(f"Error inserting row: {row}")
        print(f"Error message: {str(e)}")
        continue

# 변경사항 저장
conn.commit()

# 데이터베이스 상태 확인
cursor.execute("SELECT COUNT(*) FROM aff_if_hist")
aff_if_hist_count = cursor.fetchone()[0]

if f_print_log:
    print(f"insert table completed...TOT_CNT[{aff_if_hist_count}]")
    cursor.execute(f"SELECT * FROM {TABLE_TUNIVERSE_AFF_HIST} LIMIT 3")
    print("--- sample data ---")
    for fetch in cursor.fetchall():
        print("- ", fetch)
    print("-"*80)