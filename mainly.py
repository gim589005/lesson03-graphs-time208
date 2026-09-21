import pandas as pd
import plotly.express as px
import streamlit as st

# ─────────────────────────────────────────────
# 기본 설정
# ─────────────────────────────────────────────
st.set_page_config(page_title="영화 데이터 그래프 도감 1 - 시간", layout="wide")

DATA_URL = (
    "https://raw.githubusercontent.com/greatsong/modudata/main/data/kobis_daily.csv"
)


# ─────────────────────────────────────────────
# 데이터 불러오기
# ─────────────────────────────────────────────
@st.cache_data(show_spinner="데이터를 불러오는 중입니다...")
def load_data(url: str) -> pd.DataFrame:
    try:
        df = pd.read_csv(url, encoding="utf-8-sig")
    except UnicodeDecodeError:
        df = pd.read_csv(url, encoding="cp949")

    df.columns = df.columns.str.strip()

    # 하이픈 없는 여덟 자리 숫자(예: 20240101)를 진짜 날짜로 바꾸기
    df["날짜"] = pd.to_datetime(df["날짜"].astype(str), format="%Y%m%d")

    return df.sort_values(["날짜", "순위"]).reset_index(drop=True)


# ─────────────────────────────────────────────
# 공통 도우미
# ─────────────────────────────────────────────
def show_takeaway(text: str = "") -> None:
    """그래프 아래에 '이 그래프로 알 수 있는 것' 한 문장을 보여 주는 자리."""
    if text.strip():
        st.info(f"**이 그래프로 알 수 있는 것** · {text}")
    else:
        st.info("**이 그래프로 알 수 있는 것** · (여기에 한 문장을 적어 주세요)")


# ─────────────────────────────────────────────
# 구역 1: 영화별 일관객 변화
# ─────────────────────────────────────────────
def section_daily_audience(df: pd.DataFrame) -> None:
    st.header("1. 영화 한 편의 일관객 변화")

    # 이 그래프 아래에 보여 줄 한 문장 (직접 채워 넣으세요)
    takeaway = ""

    # 관객을 많이 모은 영화가 위에 오도록 정렬
    movie_order = (
        df.groupby("영화명")["일관객"].sum().sort_values(ascending=False).index.tolist()
    )
    movie = st.selectbox("영화를 골라 보세요", movie_order, key="s1_movie")

    movie_df = df[df["영화명"] == movie].sort_values("날짜")

    fig = px.line(
        movie_df,
        x="날짜",
        y="일관객",
        markers=True,
        title=f"{movie} - 날짜별 일관객",
    )
    fig.update_traces(
        hovertemplate="날짜: %{x|%Y-%m-%d}<br>일관객: %{y:,}명<extra></extra>"
    )
    fig.update_layout(
        xaxis_title="날짜",
        yaxis_title="일관객(명)",
        yaxis_tickformat=",",
        hovermode="closest",
    )

    st.plotly_chart(fig, use_container_width=True)
    st.caption("박스오피스 10위권에 든 날만 기록되어 있어서, 그 밖의 날은 점이 없습니다.")
    show_takeaway(takeaway)


# ─────────────────────────────────────────────
# 구역 목록 - 새 그래프는 함수를 만들고 여기에 추가하세요
# ─────────────────────────────────────────────
SECTIONS = [
    section_daily_audience,
    # section_...,
]


# ─────────────────────────────────────────────
# 화면 그리기
# ─────────────────────────────────────────────
st.title("영화 데이터 그래프 도감 1 - 시간")

df = load_data(DATA_URL)

for i, section in enumerate(SECTIONS):
    if i > 0:
        st.divider()
    section(df)
