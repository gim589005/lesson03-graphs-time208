# 영화 데이터 그래프 도감 1 - 시간
import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="영화 데이터 그래프 도감 1 - 시간", layout="wide")
st.title("영화 데이터 그래프 도감 1 - 시간")

DATA_URL = "https://raw.githubusercontent.com/greatsong/modudata/main/data/kobis_daily.csv"


@st.cache_data
def load_data():
    # 1년치(365일) 일별 박스오피스 10위권 기록을 불러옵니다.
    df = pd.read_csv(DATA_URL)
    # 여덟 자리 숫자로 된 날짜 열을 진짜 날짜로 바꿉니다.
    df["날짜"] = pd.to_datetime(df["날짜"], format="%Y%m%d")
    return df


df = load_data()

# ── 그래프 1. 영화 하나의 흥행 곡선 ──────────────────────────
st.header("1. 한 영화의 흥행 곡선")

# 드롭다운으로 영화를 고릅니다.
movie_list = sorted(df["영화명"].unique())
movie = st.selectbox("영화를 고르세요", movie_list)

one = df[df["영화명"] == movie].sort_values("날짜")
fig = px.line(one, x="날짜", y="일관객", markers=True)
fig.update_traces(hovertemplate="날짜 %{x|%Y-%m-%d}<br>관객 %{y:,}명<extra></extra>")
st.plotly_chart(fig, width="stretch")

st.caption("이 그래프로 알 수 있는 것: (한 문장으로 적어 보세요)")

# ── 그래프 2. 일관객 합계 상위 5편 비교 ──────────────────────
st.divider()
st.header("2. 관객이 가장 많았던 5편 비교")

# 이 기간 일관객 합계가 가장 큰 5편을 고릅니다 (큰 순서대로).
top5 = df.groupby("영화명")["일관객"].sum().nlargest(5).index.tolist()
top5_df = df[df["영화명"].isin(top5)].sort_values("날짜")

# 영화마다 색을 다르게 그립니다. 범례를 누르면 그 영화를 켜고 끌 수 있어요.
fig2 = px.line(
    top5_df,
    x="날짜",
    y="일관객",
    color="영화명",
    markers=True,
    category_orders={"영화명": top5},  # 범례도 관객 합계 순서로 정렬
)
fig2.update_traces(
    hovertemplate="%{fullData.name}<br>날짜 %{x|%Y-%m-%d}<br>관객 %{y:,}명<extra></extra>"
)
fig2.update_layout(legend_title_text="영화 (누르면 켜고 끄기)", yaxis_tickformat=",")
st.plotly_chart(fig2, width="stretch")

st.caption("범례의 영화 이름을 한 번 누르면 그 선이 꺼지고, 두 번 누르면 그 영화만 보여요.")
st.caption("이 그래프로 알 수 있는 것: (한 문장으로 적어 보세요)")

# ── 앞으로 그래프 3, 4, 5가 이 아래에 추가됩니다 ──────────
