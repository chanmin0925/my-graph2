import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="영화 데이터 그래프 도감 2 - 분포와 관계",
    layout="wide"
)

st.title("영화 데이터 그래프 도감 2 - 분포와 관계")

DATA_URL = "https://raw.githubusercontent.com/greatsong/modudata/main/data/kobis_movies.csv"


@st.cache_data
def load_data():
    df = pd.read_csv(DATA_URL)

    # 개봉일: 여덟 자리 숫자 → 날짜
    df["openDt"] = pd.to_datetime(
        df["openDt"].astype(str),
        format="%Y%m%d",
        errors="coerce"
    )

    # 여러 장르가 있으면 첫 번째 장르만 사용
    df["genre"] = (
        df["genre"]
        .fillna("미분류")
        .astype(str)
        .str.split("|")
        .str[0]
        .str.strip()
    )

    # 숫자형 열 변환
    numeric_columns = [
        "first_scrn",
        "first_show",
        "first_week_audi",
        "total_audi",
        "days_in_top10"
    ]

    for col in numeric_columns:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    return df


try:
    data = load_data()
except Exception:
    st.error("데이터를 불러오는 중 오류가 발생했습니다.")
    st.stop()


# --------------------------------------------------
# 그래프 1. 장르별 영화 편수
# --------------------------------------------------

st.header("그래프 1. 장르별 영화 편수")

genre_counts = (
    data["genre"]
    .value_counts()
    .reset_index()
)

genre_counts.columns = ["장르", "영화 편수"]

fig1 = px.pie(
    genre_counts,
    names="장르",
    values="영화 편수",
    hole=0.55,
    title="장르별 영화 편수"
)

fig1.update_traces(
    textposition="inside",
    textinfo="percent",
    hovertemplate=(
        "<b>%{label}</b><br>"
        "영화 편수: %{value}편<br>"
        "비율: %{percent}<extra></extra>"
    )
)

fig1.update_layout(
    showlegend=True,
    legend_title_text="장르"
)

st.plotly_chart(fig1, use_container_width=True)

st.subheader("이 그래프로 알 수 있는 것")

st.text_area(
    "그래프 1 설명",
    placeholder="이 그래프로 알 수 있는 내용을 한 문장으로 써 보세요.",
    key="graph1_note",
    height=80,
    label_visibility="collapsed"
)

st.markdown("---")


# --------------------------------------------------
# 그래프 2. 장르별 영화 총 관객 트리맵
# --------------------------------------------------

st.header("그래프 2. 장르별 영화 총 관객 트리맵")

treemap_data = data[
    ["genre", "movieNm", "total_audi"]
].dropna(subset=["genre", "movieNm", "total_audi"]).copy()

treemap_data = treemap_data[treemap_data["total_audi"] > 0]

fig2 = px.treemap(
    treemap_data,
    path=["genre", "movieNm"],
    values="total_audi",
    title="장르별 영화 총 관객"
)

fig2.update_traces(
    hovertemplate=(
        "<b>%{label}</b><br>"
        "총 관객: %{value:,.0f}명"
        "<extra></extra>"
    )
)

fig2.update_layout(
    margin=dict(t=50, l=10, r=10, b=10)
)

st.plotly_chart(fig2, use_container_width=True)

st.subheader("이 그래프로 알 수 있는 것")

st.text_area(
    "그래프 2 설명",
    placeholder="이 그래프로 알 수 있는 내용을 한 문장으로 써 보세요.",
    key="graph2_note",
    height=80,
    label_visibility="collapsed"
)

st.markdown("---")


# --------------------------------------------------
# 그래프 3. 총 관객 히스토그램
# --------------------------------------------------

st.header("그래프 3. 총 관객 분포")

histogram_data = data[
    ["movieNm", "total_audi"]
].dropna(subset=["movieNm", "total_audi"]).copy()

histogram_data = histogram_data[histogram_data["total_audi"] >= 0]

fig3 = px.histogram(
    histogram_data,
    x="total_audi",
    nbins=20,
    title="영화별 총 관객 분포",
    labels={
        "total_audi": "총 관객",
        "count": "영화 편수"
    }
)

fig3.update_traces(
    hovertemplate=(
        "총 관객 구간: %{x}<br>"
        "영화 편수: %{y}편"
        "<extra></extra>"
    )
)

fig3.update_layout(
    xaxis_title="총 관객",
    yaxis_title="영화 편수"
)

st.plotly_chart(fig3, use_container_width=True)


# 대부분의 영화가 몰려 있는 구간 계산
q1 = histogram_data["total_audi"].quantile(0.25)
q3 = histogram_data["total_audi"].quantile(0.75)

most_movies_min = histogram_data["total_audi"].min()
most_movies_max = histogram_data["total_audi"].max()

# 히스토그램의 실제 구간을 기준으로 가장 많은 구간 계산
counts, bin_edges = pd.cut(
    histogram_data["total_audi"],
    bins=20,
    include_lowest=True,
    retbins=True
)

bin_counts = counts.value_counts().sort_index()

most_common_bin = bin_counts.idxmax()

bin_start = most_common_bin.left
bin_end = most_common_bin.right

# 총 관객이 가장 많은 영화
top_movie = histogram_data.loc[
    histogram_data["total_audi"].idxmax()
]

top_movie_name = top_movie["movieNm"]
top_movie_audi = int(top_movie["total_audi"])


st.markdown(
    f"""
**대부분의 영화가 몰려 있는 구간:**  
총 관객 **{bin_start:,.0f}명 ~ {bin_end:,.0f}명** 구간에 가장 많은 영화가 몰려 있습니다.

**가장 관객이 많은 영화:**  
**{top_movie_name}** — 총 관객 **{top_movie_audi:,.0f}명**
"""
)

st.subheader("이 그래프로 알 수 있는 것")

st.text_area(
    "그래프 3 설명",
    placeholder="이 그래프로 알 수 있는 내용을 한 문장으로 써 보세요.",
    key="graph3_note",
    height=80,
    label_visibility="collapsed"
)

st.markdown("---")
