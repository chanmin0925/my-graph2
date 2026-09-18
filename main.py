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

    df["openDt"] = pd.to_datetime(
        df["openDt"].astype(str),
        format="%Y%m%d",
        errors="coerce"
    )

    df["genre"] = (
        df["genre"]
        .fillna("미분류")
        .astype(str)
        .str.split("|")
        .str[0]
        .str.strip()
    )

    df["nation"] = (
        df["nation"]
        .fillna("미분류")
        .astype(str)
        .str.split("|")
        .str[0]
        .str.strip()
    )

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
except Exception as e:
    st.error(f"데이터를 불러오는 중 오류가 발생했습니다: {e}")
    st.stop()


# 그래프 1
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
    hovertemplate="<b>%{label}</b><br>영화 편수: %{value}편<br>비율: %{percent}<extra></extra>"
)

st.plotly_chart(fig1, use_container_width=True)

st.subheader("이 그래프로 알 수 있는 것")

st.text_area(
    "",
    key="graph1_note",
    height=80,
    label_visibility="collapsed"
)

st.divider()


# 그래프 2
st.header("그래프 2. 장르별 영화 총 관객 트리맵")

treemap_data = data[
    ["genre", "movieNm", "total_audi"]
].dropna()

treemap_data = treemap_data[
    treemap_data["total_audi"] > 0
]

fig2 = px.treemap(
    treemap_data,
    path=["genre", "movieNm"],
    values="total_audi",
    title="장르별 영화 총 관객"
)

fig2.update_traces(
    hovertemplate="<b>%{label}</b><br>총 관객: %{value:,.0f}명<extra></extra>"
)

st.plotly_chart(fig2, use_container_width=True)

st.subheader("이 그래프로 알 수 있는 것")

st.text_area(
    "",
    key="graph2_note",
    height=80,
    label_visibility="collapsed"
)

st.divider()


# 그래프 3
st.header("그래프 3. 총 관객 분포")

hist_data = data[
    ["movieNm", "total_audi"]
].dropna()

hist_data = hist_data[
    hist_data["total_audi"] >= 0
]

fig3 = px.histogram(
    hist_data,
    x="total_audi",
    nbins=20,
    title="영화별 총 관객 분포"
)

fig3.update_traces(
    hovertemplate="구간: %{x}<br>영화 수: %{y}편<extra></extra>"
)

fig3.update_layout(
    xaxis_title="총 관객",
    yaxis_title="영화 수"
)

st.plotly_chart(fig3, use_container_width=True)

bins = pd.cut(
    hist_data["total_audi"],
    bins=20,
    include_lowest=True
)

bin_counts = bins.value_counts().sort_index()

if not bin_counts.empty:
    most_common_bin = bin_counts.idxmax()

    bin_start = int(most_common_bin.left)
    bin_end = int(most_common_bin.right)

    st.write(
        f"**대부분의 영화가 몰려 있는 구간:** "
        f"총 관객 {bin_start:,}명 ~ {bin_end:,}명 구간에 가장 많은 영화가 몰려 있습니다."
    )

if not hist_data.empty:
    top_movie = hist_data.loc[
        hist_data["total_audi"].idxmax()
    ]

    st.write(
        f"**가장 관객이 많은 영화:** "
        f"{top_movie['movieNm']} — 총 관객 {top_movie['total_audi']:,.0f}명"
    )

st.subheader("이 그래프로 알 수 있는 것")

st.text_area(
    "",
    key="graph3_note",
    height=80,
    label_visibility="collapsed"
)

st.divider()


# 그래프 4
st.header("그래프 4. 개봉일 스크린수와 총 관객의 관계")

scatter_data = data[
    ["movieNm", "genre", "first_scrn", "total_audi"]
].dropna()

scatter_data = scatter_data[
    (scatter_data["first_scrn"] >= 0) &
    (scatter_data["total_audi"] >= 0)
]

fig4 = px.scatter(
    scatter_data,
    x="first_scrn",
    y="total_audi",
    color="genre",
    hover_name="movieNm",
    hover_data={
        "first_scrn": ":,",
        "total_audi": ":,",
        "genre": True
    },
    title="개봉일 스크린수와 총 관객의 관계"
)

fig4.update_traces(
    marker=dict(
        size=9,
        opacity=0.75
    )
)

fig4.update_layout(
    xaxis_title="개봉일 스크린수",
    yaxis_title="총 관객"
)

st.plotly_chart(fig4, use_container_width=True)

st.subheader("이 그래프로 알 수 있는 것")

st.text_area(
    "",
    key="graph4_note",
    height=80,
    label_visibility="collapsed"
)

st.divider()


# 그래프 5
st.header("그래프 5. 장르별 총 관객 분포")

boxplot_data = data[
    ["movieNm", "genre", "total_audi"]
].dropna()

boxplot_data = boxplot_data[
    boxplot_data["total_audi"] >= 0
]

genre_movie_counts = boxplot_data["genre"].value_counts()

selected_genres = genre_movie_counts[
    genre_movie_counts >= 10
].index

boxplot_data = boxplot_data[
    boxplot_data["genre"].isin(selected_genres)
]

fig5 = px.box(
    boxplot_data,
    x="genre",
    y="total_audi",
    points="outliers",
    hover_name="movieNm",
    hover_data={
        "genre": False,
        "total_audi": ":,"
    },
    labels={
        "genre": "장르",
        "total_audi": "총 관객"
    },
    title="영화가 10편 이상인 장르의 총 관객 분포"
)

fig5.update_traces(
    hovertemplate="<b>%{hovertext}</b><br>총 관객: %{y:,.0f}명<extra></extra>"
)

st.plotly_chart(fig5, use_container_width=True)

st.subheader("이 그래프로 알 수 있는 것")

st.text_area(
    "",
    key="graph5_note",
    height=80,
    label_visibility="collapsed"
)

st.divider()


# 그래프 6
st.header("그래프 6. 개봉일 스크린수와 총 관객의 관계 - 첫 주 관객 버블 그래프")

bubble_data = data[
    [
        "movieNm",
        "genre",
        "first_scrn",
        "total_audi",
        "first_week_audi"
    ]
].dropna()

bubble_data = bubble_data[
    (bubble_data["first_scrn"] >= 0) &
    (bubble_data["total_audi"] >= 0) &
    (bubble_data["first_week_audi"] >= 0)
]

fig6 = px.scatter(
    bubble_data,
    x="first_scrn",
    y="total_audi",
    color="genre",
    size="first_week_audi",
    size_max=60,
    hover_name="movieNm",
    hover_data={
        "first_scrn": ":,",
        "total_audi": ":,",
        "first_week_audi": ":,",
        "genre": True
    },
    labels={
        "first_scrn": "개봉일 스크린수",
        "total_audi": "총 관객",
        "first_week_audi": "개봉 첫 주 관객",
        "genre": "장르"
    },
    title="개봉일 스크린수와 총 관객의 관계 - 버블 크기는 개봉 첫 주 관객"
)

fig6.update_traces(
    marker=dict(
        opacity=0.7,
        line=dict(width=0.5)
    )
)

fig6.update_layout(
    xaxis_title="개봉일 스크린수",
    yaxis_title="총 관객"
)

st.plotly_chart(fig6, use_container_width=True)

st.subheader("이 그래프로 알 수 있는 것")

st.text_area(
    "",
    key="graph6_note",
    height=80,
    label_visibility="collapsed"
)

st.divider()


# 그래프 7
st.header("그래프 7. 제작 국가에서 장르로 내려가는 선버스트 그래프")

sunburst_data = data[
    ["nation", "genre"]
].dropna()

sunburst_data = (
    sunburst_data
    .groupby(["nation", "genre"])
    .size()
    .reset_index(name="영화 편수")
)

fig7 = px.sunburst(
    sunburst_data,
    path=["nation", "genre"],
    values="영화 편수",
    title="제작 국가 → 장르별 영화 편수",
    labels={
        "nation": "제작 국가",
        "genre": "장르",
        "영화 편수": "영화 편수"
    }
)

fig7.update_traces(
    hovertemplate=(
        "<b>%{label}</b>"
        "<br>영화 편수: %{value}편"
        "<extra></extra>"
    )
)

st.plotly_chart(fig7, use_container_width=True)

st.subheader("이 그래프로 알 수 있는 것")

st.text_area(
    "",
    key="graph7_note",
    height=80,
    label_visibility="collapsed"
)
