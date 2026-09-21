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

# ── 그래프 3. 하루 10위권 관객 합계 ──────────────────────────
st.divider()
st.header("3. 하루 10위권 관객 합계")

# 날짜별로 그날 10위권 일관객을 모두 더합니다.
daily = df.groupby("날짜", as_index=False)["일관객"].sum().sort_values("날짜")

fig3 = px.area(daily, x="날짜", y="일관객")
fig3.update_traces(
    hovertemplate="날짜 %{x|%Y-%m-%d}<br>10위권 합계 %{y:,}명<extra></extra>"
)

# 합계가 가장 컸던 3일을 점과 날짜로 표시합니다.
# 붙어 있는 날짜끼리 글자가 겹치지 않게, 날짜 순서대로 글자 위치를 나눕니다.
top3 = daily.nlargest(3, "일관객").sort_values("날짜")
fig3.add_scatter(
    x=top3["날짜"],
    y=top3["일관객"],
    mode="markers+text",
    text=top3["날짜"].dt.strftime("%Y-%m-%d"),
    textposition=["top left", "top center", "top right"],
    marker=dict(size=11, color="red"),
    cliponaxis=False,
    showlegend=False,
    hovertemplate="날짜 %{x|%Y-%m-%d}<br>10위권 합계 %{y:,}명<extra></extra>",
)
fig3.update_layout(yaxis_title="10위권 일관객 합계(명)", yaxis_tickformat=",")
# 위쪽 글자가 잘리지 않도록 y축 위쪽에 여유를 둡니다.
fig3.update_yaxes(range=[0, daily["일관객"].max() * 1.15])
st.plotly_chart(fig3, width="stretch")

st.caption("빨간 점은 10위권 관객 합계가 가장 컸던 3일입니다.")
st.caption("이 그래프로 알 수 있는 것: (한 문장으로 적어 보세요)")

# ── 그래프 4. 관객 합계 TOP 10 영화 ──────────────────────────
st.divider()
st.header("4. 관객 합계 TOP 10 영화")

# 영화별로 일관객을 모두 더하고, 10위권에 든 날수도 함께 셉니다.
summary = df.groupby("영화명", as_index=False).agg(
    관객합계=("일관객", "sum"),
    순위권일수=("날짜", "nunique"),
)
top10 = summary.nlargest(10, "관객합계")  # 관객 많은 순서

fig4 = px.bar(
    top10,
    x="관객합계",
    y="영화명",
    orientation="h",
    custom_data=["순위권일수"],
)
fig4.update_traces(
    hovertemplate="%{y}<br>관객 합계 %{x:,}명<br>10위권에 든 날 %{customdata[0]}일<extra></extra>"
)
# 가로 막대는 기본이 아래부터 쌓이므로, 뒤집어서 관객이 많은 영화가 위에 오게 합니다.
fig4.update_yaxes(autorange="reversed", title_text="")
fig4.update_layout(xaxis_title="일관객 합계(명)", xaxis_tickformat=",")
st.plotly_chart(fig4, width="stretch")

st.caption("이 그래프로 알 수 있는 것: (한 문장으로 적어 보세요)")

# ── 그래프 5. 월 × 요일별 관객 합계 ──────────────────────────
st.divider()
st.header("5. 월 × 요일별 관객 합계")

# 날짜에서 월과 요일을 뽑습니다. (요일: 월요일=0 ... 일요일=6)
heat = df.assign(월=df["날짜"].dt.month, 요일=df["날짜"].dt.dayofweek)

# 요일(행) × 월(열) 표를 만들어 일관객을 더합니다.
pivot = heat.pivot_table(
    index="요일", columns="월", values="일관객", aggfunc="sum", fill_value=0
).reindex(range(7), fill_value=0)  # 월~일 일곱 줄이 모두 있도록
pivot.index = ["월", "화", "수", "목", "금", "토", "일"]  # 월요일부터 일요일 순서
pivot.columns = [f"{m}월" for m in pivot.columns]

# 색이 진할수록 관객이 많습니다.
fig5 = px.imshow(
    pivot,
    color_continuous_scale="Blues",
    aspect="auto",
    labels=dict(color="일관객 합계(명)"),
)
fig5.update_traces(
    hovertemplate="%{x} %{y}요일<br>관객 합계 %{z:,}명<extra></extra>"
)
fig5.update_layout(
    xaxis_title="월",
    yaxis_title="요일",
    coloraxis_colorbar_tickformat=",",
)
st.plotly_chart(fig5, width="stretch")

st.caption("이 그래프로 알 수 있는 것: (한 문장으로 적어 보세요)")

# ── 앞으로 그래프가 더 생기면 이 아래에 추가합니다 ──────────
