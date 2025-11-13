import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
from PIL import Image
import datetime
import time


st.set_page_config(page_title="Streamlit 요소 예시", layout="wide")

st.title("🎈 Streamlit — 단일 페이지 요소 예시")  # [1]

st.write("아래는 한 페이지에 넣을 수 있는 여러 Streamlit 요소의 예시입니다.")  # [2]

# --- 성적 데이터 업로드 및 대화형 시각화
st.markdown("## 🎓 성적 데이터 시각화 도구")
st.write(
    "CSV 파일을 업로드하면 해당 데이터의 열(변수)을 기반으로 히스토그램, 막대그래프, 산점도, 상자그림을 그릴 수 있습니다."
)

uploaded_csv = st.file_uploader("CSV 파일 업로드 (예: 성적 데이터)", type=["csv"])  # 사용자가 올릴 CSV

if uploaded_csv is not None:
    try:
        df_uploaded = pd.read_csv(uploaded_csv)
    except Exception as e:
        st.error(f"CSV를 읽는 중 오류가 발생했습니다: {e}")
        df_uploaded = None

    if df_uploaded is not None:
        st.success("CSV가 업로드되어 데이터프레임으로 로드되었습니다.")
        st.dataframe(df_uploaded.head())

        # 열 타입 분류
        numeric_cols = df_uploaded.select_dtypes(include=[np.number]).columns.tolist()
        categorical_cols = df_uploaded.select_dtypes(include=["object", "category"]).columns.tolist()

        if len(numeric_cols) == 0:
            st.warning("데이터에 숫자형 열이 없습니다. 히스토그램/산점도/상자그림을 사용하려면 숫자형 열이 필요합니다.")

        tab_hist, tab_bar, tab_scatter, tab_box = st.tabs(["히스토그램", "막대그래프", "산점도", "상자그림"])

        # 히스토그램
        with tab_hist:
            st.write("히스토그램: 숫자형 변수를 선택해 분포를 확인하세요.")
            if numeric_cols:
                hist_col = st.selectbox("히스토그램 변수", numeric_cols)
                bins = st.slider("빈 개수", 5, 200, 30)
                chart = alt.Chart(df_uploaded).mark_bar().encode(
                    x=alt.X(f"{hist_col}:Q", bin=alt.Bin(maxbins=bins)),
                    y="count():Q",
                ).properties(height=350)
                st.altair_chart(chart, use_container_width=True)
            else:
                st.info("숫자형 열이 없습니다.")

        # 막대그래프
        with tab_bar:
            st.write("막대그래프: 범주형(또는 집계)과 숫자형 변수를 선택합니다.")
            if categorical_cols:
                bar_cat = st.selectbox("범주형 변수 (X)", categorical_cols)
                agg_func = st.selectbox("집계 함수", ["mean", "sum", "median", "count"], index=0)
                if agg_func == "count":
                    agg_chart = alt.Chart(df_uploaded).mark_bar().encode(
                        x=alt.X(f"{bar_cat}:N"),
                        y=alt.Y("count():Q"),
                    ).properties(height=350)
                else:
                    # 숫자형 선택 항목
                    if numeric_cols:
                        bar_num = st.selectbox("숫자형 변수 (Y)", numeric_cols)
                        agg_chart = alt.Chart(df_uploaded).mark_bar().encode(
                            x=alt.X(f"{bar_cat}:N"),
                            y=alt.Y(f"{bar_num}:Q", aggregate=agg_func),
                        ).properties(height=350)
                    else:
                        st.info("집계할 숫자형 열이 없습니다.")
                        agg_chart = None

                if 'agg_chart' in locals() and agg_chart is not None:
                    st.altair_chart(agg_chart, use_container_width=True)
            else:
                st.info("범주형(문자열/카테고리) 열이 없습니다.")

        # 산점도
        with tab_scatter:
            st.write("산점도: X, Y 숫자형 변수를 선택하세요. 색상은 선택적입니다.")
            if len(numeric_cols) >= 2:
                x_col = st.selectbox("X 변수", numeric_cols, index=0)
                y_col = st.selectbox("Y 변수", [c for c in numeric_cols if c != x_col], index=0)
                color_col = None
                if categorical_cols:
                    color_col = st.selectbox("색상(선택) - 범주형", [None] + categorical_cols)
                scatter_chart = alt.Chart(df_uploaded).mark_point().encode(
                    x=alt.X(f"{x_col}:Q"),
                    y=alt.Y(f"{y_col}:Q"),
                    color=alt.Color(f"{color_col}:N") if color_col else None,
                    tooltip=[x_col, y_col] + ([color_col] if color_col else []),
                ).properties(height=400)
                st.altair_chart(scatter_chart, use_container_width=True)
            else:
                st.info("산점도는 최소 2개의 숫자형 열이 필요합니다.")

        # 상자그림
        with tab_box:
            st.write("상자그림(Boxplot): 숫자형 변수와(선택적으로) 그룹별 비교용 범주형 변수를 선택하세요.")
            if numeric_cols:
                box_num = st.selectbox("상자그림 숫자형 변수", numeric_cols)
                box_group = None
                if categorical_cols:
                    box_group = st.selectbox("그룹(선택)", [None] + categorical_cols)

                if box_group:
                    box_chart = alt.Chart(df_uploaded).mark_boxplot().encode(
                        x=alt.X(f"{box_group}:N"),
                        y=alt.Y(f"{box_num}:Q"),
                    ).properties(height=350)
                else:
                    # 전체 데이터에 대한 상자그림 (단일 그룹)
                    df_tmp = df_uploaded.copy()
                    df_tmp["__all"] = "all"
                    box_chart = alt.Chart(df_tmp).mark_boxplot().encode(
                        x=alt.X("__all:N", title="All"),
                        y=alt.Y(f"{box_num}:Q"),
                    ).properties(height=350)

                st.altair_chart(box_chart, use_container_width=True)
            else:
                st.info("상자그림을 그리려면 숫자형 열이 필요합니다.")

else:
    st.info("성적 데이터 CSV를 업로드하면 자동으로 변수 선택 UI가 나타나고, 선택한 변수로 그래프를 그립니다.")


# --- 상단 텍스트와 마크다운
st.header("텍스트와 마크다운")  # [3]
st.subheader("간단한 설명")  # [4]
st.write("일반 텍스트는 `st.write`로 출력할 수 있습니다.")  # [5]
st.markdown("**Markdown** 문장과 링크: [Streamlit docs](https://docs.streamlit.io)")  # [6]

# --- 대시보드형 요소
st.header("대시보드 요소")  # [7]
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("매출", "$12.4k", delta="+3.2%")  # [8]
with col2:
    st.metric("사용자", "1,204", delta="-1.1%")  # [9]
with col3:
    st.metric("전환율", "4.2%", delta="+0.4%")  # [10]

# --- 입력 위젯
st.header("입력 위젯")  # [11]
left, right = st.columns(2)
with left:
    agree = st.checkbox("이용약관에 동의합니다")  # [12]
    choice = st.radio("옵션 선택", ("옵션 A", "옵션 B", "옵션 C"))  # [13]
    sel = st.selectbox("셀렉트박스", ["사과", "바나나", "오렌지"])  # [14]
with right:
    val = st.slider("슬라이더", 0, 100, 25)  # [15]
    n = st.number_input("숫자 입력", min_value=0, max_value=1000, value=10)  # [16]
    text = st.text_input("한 줄 입력")  # [17]
    area = st.text_area("여러 줄 입력", "여기에 내용을 입력하세요")  # [18]

# --- 날짜/시간 / 파일 업로드
st.header("날짜, 시간, 파일")  # [19]
cold1, cold2, cold3 = st.columns(3)
with cold1:
    d = st.date_input("날짜 선택", datetime.date.today())  # [20]
with cold2:
    t = st.time_input("시간 선택", datetime.datetime.now().time())  # [21]
with cold3:
    uploaded = st.file_uploader("이미지 업로드", type=["png", "jpg", "jpeg"])  # [22]
    if uploaded is not None:
        img = Image.open(uploaded)
        st.image(img, caption="업로드된 이미지", use_column_width=True)

# --- 버튼 & 상호작용
st.header("버튼과 진행 상태")  # [23]
if st.button("클릭해서 메시지 보기"):  # [24]
    st.success("버튼이 클릭되었습니다!")

progress_text = st.empty()
progress_bar = st.progress(0)
for i in range(0, 101, 10):
    progress_text.text(f"진행률: {i}%")
    progress_bar.progress(i)
    time.sleep(0.02)

# --- 데이터 표시와 차트
st.header("데이터와 시각화")  # [25]
df = pd.DataFrame(np.random.randn(50, 3), columns=["x", "y", "z"])  # [26]
st.dataframe(df.head())  # [27]
st.line_chart(df)  # [28]

chart = alt.Chart(df.reset_index()).transform_fold(
    ["x", "y", "z"], as_=["series", "value"]
).mark_line().encode(x="index", y="value", color="series")
st.altair_chart(chart, use_container_width=True)  # [29]

# --- 지도
st.header("지도")  # [30]
map_data = pd.DataFrame(
    np.array([[37.76, -122.4], [37.77, -122.41], [37.75, -122.43]]), columns=["lat", "lon"]
)
st.map(map_data)  # [31]

# --- 레이아웃: 확장자, 탭, 사이드바
st.header("레이아웃 구성요소")  # [32]
with st.expander("추가 정보 보기"):
    st.write("여기는 확장 영역(expander)입니다.")  # [33]

tab1, tab2 = st.tabs(["탭 1", "탭 2"])  # [34]
with tab1:
    st.write("탭 1 내용")
with tab2:
    st.write("탭 2 내용")

st.sidebar.header("사이드바")
st.sidebar.write("사이드바에 설정을 넣을 수 있습니다.")  # [35]

# --- 미디어와 코드, JSON
st.header("미디어, 코드, JSON")  # [36]
st.image(Image.new("RGB", (200, 100), color=(73, 109, 137)), caption="샘플 이미지")  # [37]
st.code("print('Hello Streamlit')", language="python")  # [38]
st.json({"key": "value", "number": 123})  # [39]

# --- 각주 (페이지 하단)
st.markdown("---")
st.subheader("각주")
footnotes = {
    1: "메인 타이틀 — 페이지 식별자.",
    2: "설명 텍스트 — 페이지 목적을 간단히 서술.",
    3: "헤더 — 섹션을 구분하는 큰 제목.",
    4: "서브헤더 — 작은 제목.",
    5: "일반 텍스트 출력 예시.",
    6: "Markdown 예시 — 링크와 강조 사용 가능.",
    7: "대시보드에서 자주 쓰는 섹션 타입.",
    8: "`st.metric` — 주요 숫자와 변화량을 보여줌.",
    9: "여러 개의 `st.metric`을 열로 배치 가능.",
    10: "Delta(변화량)을 함께 표시해 KPI 추적에 용이.",
    11: "입력 위젯 모음 — 유저와 상호작용하는 요소들.",
    12: "체크박스 — 불리언 입력값.",
    13: "라디오 버튼 — 단일 선택 입력.",
    14: "셀렉트박스 — 드롭다운 선택.",
    15: "슬라이더 — 연속적 값 선택.",
    16: "숫자 입력 — 정밀한 수치 입력에 적합.",
    17: "단일 행 텍스트 입력.",
    18: "다중 행 텍스트 영역.",
    19: "날짜/시간/파일 업로드 예시.",
    20: "날짜 입력 — 달력 선택.",
    21: "시간 입력 — 시/분/초 선택.",
    22: "파일 업로드 — 이미지나 CSV 등을 업로드 가능.",
    23: "버튼과 진행 표시 — 즉시성 피드백 제공.",
    24: "버튼 클릭시 이벤트 트리거.",
    25: "데이터와 시각화 — 표와 차트 표시.",
    26: "샘플 데이터프레임 생성.",
    27: "`st.dataframe` — 스크롤 가능한 표.",
    28: "`st.line_chart` — 빠른 시계열 차트.",
    29: "Altair로 커스텀 차트 생성 가능.",
    30: "지도 시각화 섹션.",
    31: "`st.map` — 간단한 위치 표시.",
    32: "레이아웃 구성요소(Expander/Tabs/Sidebar).",
    33: "Expander — 접었다 폈다 가능한 영역.",
    34: "Tabs — 탭 기반 UI.",
    35: "Sidebar — 페이지와 별개로 설정 배치.",
    36: "미디어/코드/JSON 예시.",
    37: "샘플 이미지 출력.",
    38: "코드 블록 출력 예시.",
    39: "JSON 출력 예시.",
}

for k in sorted(footnotes.keys()):
    st.caption(f"[{k}] {footnotes[k]}")

st.write("원하시면 이 파일을 더 간단하게 하거나, 특정 요소의 동작 예시(예: CSV 업로드 처리)를 추가해 드릴게요.")

