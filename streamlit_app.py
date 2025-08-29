#######################
# Import libraries
import streamlit as st
import pandas as pd
import altair as alt
import plotly.express as px

#######################
# Page configuration
st.set_page_config(
    page_title="US Population Dashboard",
    page_icon="🏂",
    layout="wide",
    initial_sidebar_state="expanded")

alt.themes.enable("default")

#######################
# CSS styling
st.markdown("""
<style>

[data-testid="block-container"] {
    padding-left: 2rem;
    padding-right: 2rem;
    padding-top: 1rem;
    padding-bottom: 0rem;
    margin-bottom: -7rem;
}

[data-testid="stVerticalBlock"] {
    padding-left: 0rem;
    padding-right: 0rem;
}

[data-testid="stMetric"] {
    background-color: #393939;
    text-align: center;
    padding: 15px 0;
}

[data-testid="stMetricLabel"] {
  display: flex;
  justify-content: center;
  align-items: center;
}

[data-testid="stMetricDeltaIcon-Up"] {
    position: relative;
    left: 38%;
    transform: translateX(-50%);
}

[data-testid="stMetricDeltaIcon-Down"] {
    position: relative;
    left: 38%;
    transform: translateX(-50%);
}

/* 이름 목록 스타일 */
.name-list { list-style: none; padding-left: 0; margin: 0; }
.name-item { 
    background:#f7f7f9; 
    margin: 8px 0; 
    padding: 12px 14px; 
    border-radius: 10px; 
    border: 1px solid #e3e5ea;
    font-weight: 600;
    color:#1f2937;
    cursor: default;
    transition: all .15s ease;
    white-space: nowrap;
    overflow: hidden; 
    text-overflow: ellipsis;
}
.name-item:hover { 
    background:#eef2ff; 
    border-color:#c7d2fe; 
}

</style>
""", unsafe_allow_html=True)

#######################
# Load data
df_reshaped = pd.read_csv('titanic.csv')  # 분석 데이터 넣기

#######################
# Sidebar
with st.sidebar:
    st.title("Titanic Data Dashboard")
    st.caption("필터를 선택해 보세요. 선택값은 메인 패널의 지표와 차트에 반영됩니다.")
    st.divider()

    # ---- Theme / Display ----
    scheme = st.selectbox(
        "차트 색상 스킴",
        ["blues", "greens", "purples", "magma", "viridis", "plasma", "inferno", "turbo"],
        index=0
    )
    st.session_state["color_scheme"] = scheme

    st.subheader("데이터 필터")

    survived_label = {"전체": None, "생존": 1, "사망": 0}
    survived_choice = st.radio("생존 여부", list(survived_label.keys()), horizontal=True, index=0)

    sex_opts = sorted(df_reshaped["Sex"].dropna().unique().tolist())
    sex_sel = st.multiselect("성별", options=sex_opts, default=sex_opts)

    pclass_opts = sorted(df_reshaped["Pclass"].dropna().unique().tolist())
    pclass_sel = st.multiselect("선실 등급 (Pclass)", options=pclass_opts, default=pclass_opts)

    age_min = int(df_reshaped["Age"].min() if pd.notnull(df_reshaped["Age"].min()) else 0)
    age_max = int(df_reshaped["Age"].max() if pd.notnull(df_reshaped["Age"].max()) else 80)
    age_range = st.slider("나이 범위", min_value=age_min, max_value=age_max, value=(age_min, age_max))
    include_age_na = st.checkbox("나이 결측 포함", value=True)

    fare_min = float(df_reshaped["Fare"].min() if pd.notnull(df_reshaped["Fare"].min()) else 0.0)
    fare_max = float(df_reshaped["Fare"].max() if pd.notnull(df_reshaped["Fare"].max()) else 600.0)
    fare_range = st.slider("요금(Fare) 범위", min_value=float(fare_min), max_value=float(fare_max),
                           value=(float(fare_min), float(fare_max)))
    include_fare_na = st.checkbox("요금 결측 포함", value=True)

    embarked_opts = [e for e in df_reshaped["Embarked"].dropna().unique().tolist() if e != ""]
    embarked_sel = st.multiselect("승선 항구(Embarked)", options=sorted(embarked_opts),
                                  default=sorted(embarked_opts))

    # ---- Apply filters ----
    _df = df_reshaped.copy()

    s_val = survived_label[survived_choice]
    if s_val is not None and "Survived" in _df.columns:
        _df = _df[_df["Survived"] == s_val]

    if sex_sel:
        _df = _df[_df["Sex"].isin(sex_sel)]

    if pclass_sel:
        _df = _df[_df["Pclass"].isin(pclass_sel)]

    if "Age" in _df.columns:
        age_mask = (_df["Age"].between(age_range[0], age_range[1]))
        if include_age_na:
            age_mask = age_mask | _df["Age"].isna()
        _df = _df[age_mask]

    if "Fare" in _df.columns:
        fare_mask = (_df["Fare"].between(fare_range[0], fare_range[1]))
        if include_fare_na:
            fare_mask = fare_mask | _df["Fare"].isna()
        _df = _df[fare_mask]

    if embarked_sel and "Embarked" in _df.columns:
        _df = _df[_df["Embarked"].isin(embarked_sel)]

    st.session_state["df_filtered"] = _df.reset_index(drop=True)
    st.caption(f"필터 적용 후 행 수: **{len(st.session_state['df_filtered']):,}** / 원본: {len(df_reshaped):,}")

#######################
# Helpers
def plotly_scale(name: str) -> str:
    mapping = {
        "blues": "Blues",
        "greens": "Greens",
        "purples": "Purples",
        "magma": "Magma",
        "viridis": "Viridis",
        "plasma": "Plasma",
        "inferno": "Inferno",
        "turbo": "Turbo",
    }
    return mapping.get(name.lower(), "Blues")

#######################
# Dashboard Main Panel
col = st.columns((1.5, 4.5, 2), gap='medium')

with col[0]:
    st.markdown("### 🚢 주요 지표 요약")
    st.write("")
    df_filtered = st.session_state.get("df_filtered", df_reshaped)

    total_passengers = len(df_filtered)
    survived_count = int(df_filtered["Survived"].sum())
    deceased_count = total_passengers - survived_count
    survival_rate = (survived_count / total_passengers * 100) if total_passengers > 0 else 0

    st.markdown(
        f"""
        <div style="background-color:#f5f5f5; padding:20px; border-radius:12px; margin-bottom:10px; text-align:center;">
            <h4>전체 승객 수</h4>
            <h2 style="color:#333;">{total_passengers:,} 명</h2>
        </div>
        """, unsafe_allow_html=True
    )
    st.markdown(
        f"""
        <div style="background-color:#e8f5e9; padding:20px; border-radius:12px; margin-bottom:10px; text-align:center;">
            <h4>생존자 수</h4>
            <h2 style="color:#2e7d32;">{survived_count:,} 명</h2>
        </div>
        """, unsafe_allow_html=True
    )
    st.markdown(
        f"""
        <div style="background-color:#ffebee; padding:20px; border-radius:12px; margin-bottom:10px; text-align:center;">
            <h4>사망자 수</h4>
            <h2 style="color:#c62828;">{deceased_count:,} 명</h2>
        </div>
        """, unsafe_allow_html=True
    )
    st.markdown(
        f"""
        <div style="background-color:#e3f2fd; padding:20px; border-radius:12px; margin-bottom:10px; text-align:center;">
            <h4>생존율</h4>
            <h2 style="color:#1565c0;">{survival_rate:.1f}%</h2>
        </div>
        """, unsafe_allow_html=True
    )

with col[1]:
    st.markdown("### 📊 메인 시각화")
    df_filtered = st.session_state.get("df_filtered", df_reshaped).copy()

    if df_filtered.empty:
        st.info("필터 결과가 없습니다. 사이드바에서 조건을 조정해 주세요.")
    else:
        scale = plotly_scale(st.session_state.get("color_scheme", "blues"))

        # -------------------------------
        # 1) Pclass × Sex 생존율 히트맵 (Plotly)
        # -------------------------------
        st.markdown("#### 🔥 Pclass × 성별 생존율 히트맵")
        heat_df = (
            df_filtered.dropna(subset=["Pclass", "Sex"])
            .groupby(["Pclass", "Sex"], as_index=False)["Survived"]
            .mean()
        )
        heat_df["survival_rate"] = (heat_df["Survived"] * 100).round(1)
        # 피벗해서 이미지 히트맵
        pivot = heat_df.pivot(index="Sex", columns="Pclass", values="survival_rate").sort_index()
        fig_heat = px.imshow(
            pivot,
            text_auto=True,
            color_continuous_scale=scale,
            aspect="auto",
            labels=dict(color="생존율(%)")
        )
        fig_heat.update_layout(height=320, template="plotly_white", margin=dict(l=10, r=10, t=10, b=10))
        st.plotly_chart(fig_heat, use_container_width=True)

        st.divider()

        # -------------------------------
        # 2) 연령대별 생존율 막대 그래프 (Plotly)
        # -------------------------------
        st.markdown("#### 👶 연령대별 생존율")
        age_min = int(df_filtered["Age"].min()) if pd.notnull(df_filtered["Age"].min()) else 0
        age_max = int(df_filtered["Age"].max()) if pd.notnull(df_filtered["Age"].max()) else 80
        bins = list(range((age_min // 10) * 10, ((age_max // 10) + 1) * 10 + 10, 10))
        labels = [f"{b}–{b+9}" for b in bins[:-1]]
        df_age = df_filtered.copy()
        df_age["AgeBin"] = pd.cut(df_age["Age"], bins=bins, labels=labels, right=False)
        age_surv = (
            df_age.dropna(subset=["AgeBin"])
            .groupby("AgeBin", as_index=False)["Survived"]
            .mean()
        )
        age_surv["survival_rate"] = (age_surv["Survived"] * 100).round(1)

        fig_age = px.bar(
            age_surv,
            x="AgeBin", y="survival_rate",
            labels={"AgeBin": "연령대", "survival_rate": "생존율(%)"},
            text="survival_rate",
        )
        fig_age.update_traces(texttemplate="%{text:.1f}", hovertemplate="연령대: %{x}<br>생존율: %{y:.1f}%<extra></extra>")
        fig_age.update_yaxes(range=[0, 100])
        fig_age.update_layout(height=320, template="plotly_white", margin=dict(l=10, r=10, t=10, b=10))
        st.plotly_chart(fig_age, use_container_width=True)

        st.divider()

        # -------------------------------
        # 3) Pclass별 생존/사망 인원 분포 (Plotly)
        # -------------------------------
        st.markdown("#### 🧱 Pclass별 생존/사망 인원 분포")
        stack_df = (
            df_filtered.dropna(subset=["Pclass", "Survived"])
            .assign(Status=lambda d: d["Survived"].map({1: "Survived", 0: "Deceased"}))
            .groupby(["Pclass", "Status"], as_index=False)
            .size()
            .rename(columns={"size": "count"})
        )
        fig_stack = px.bar(
            stack_df, x="Pclass", y="count", color="Status",
            barmode="stack",
            labels={"Pclass": "Pclass", "count": "인원수"},
        )
        fig_stack.update_traces(hovertemplate="Pclass %{x}<br>%{legendgroup}: %{y}명<extra></extra>")
        fig_stack.update_layout(height=340, template="plotly_white", margin=dict(l=10, r=10, t=10, b=10))
        st.plotly_chart(fig_stack, use_container_width=True)

with col[2]:
    st.markdown("### 🔎 상세 분석")
    df_filtered = st.session_state.get("df_filtered", df_reshaped).copy()

    if df_filtered.empty:
        st.info("필터 결과가 없습니다. 사이드바에서 조건을 조정해 주세요.")
    else:
        # 1) 성별 × Pclass 그룹별 생존율 상위 (정적 표로 교체)
        st.markdown("#### 🏆 그룹별 생존율 Top")
        group_df = (
            df_filtered.dropna(subset=["Pclass", "Sex"])
            .groupby(["Sex", "Pclass"], as_index=False)["Survived"]
            .mean()
            .rename(columns={"Survived": "survival_rate"})
        )
        group_df["survival_rate"] = (group_df["survival_rate"] * 100).round(1)
        group_df = group_df.sort_values("survival_rate", ascending=False).head(5)
        st.table(group_df)   # st.dataframe -> st.table 로 교체 (동적 모듈 회피)

        st.divider()

        # 2) 요금 Top 5 승객 - 이름만 목록 + Hover Tooltip (동일 유지)
        st.markdown("#### 💰 요금(Fare) Top 5 승객 (이름 목록 • Hover 툴팁)")
        if "Fare" in df_filtered.columns:
            top_fare = (
                df_filtered[["Name", "Sex", "Age", "Pclass", "Fare", "Survived"]]
                .dropna(subset=["Fare"])
                .sort_values("Fare", ascending=False)
                .head(5)
                .reset_index(drop=True)
            )
            top_fare["Survived"] = top_fare["Survived"].map({1: "Yes", 0: "No"})

            items_html = []
            for _, r in top_fare.iterrows():
                tooltip = (
                    f"Name: {r['Name']}\n"
                    f"Sex: {r['Sex']}\n"
                    f"Age: {int(r['Age']) if pd.notnull(r['Age']) else 'NA'}\n"
                    f"Pclass: {r['Pclass']}\n"
                    f"Fare: {r['Fare']:.2f}\n"
                    f"Survived: {r['Survived']}"
                )
                items_html.append(f'<li class="name-item" title="{tooltip}">{r["Name"]}</li>')
            st.markdown('<ul class="name-list">' + "".join(items_html) + "</ul>", unsafe_allow_html=True)
            st.caption("이름에 마우스를 올리면 상세 정보(성별, 나이, Pclass, Fare, 생존 여부)가 툴팁으로 표시됩니다.")
        else:
            st.write("요금(Fare) 데이터가 없습니다.")

        st.divider()

        # 3) 데이터셋 설명 / About
        st.markdown("#### ℹ️ About")
        st.info(
            """
            - 데이터 출처: [Kaggle Titanic Dataset](https://www.kaggle.com/c/titanic)
            - **Survived**: 1 = 생존, 0 = 사망  
            - **Pclass**: 선실 등급 (1 = 최고, 3 = 최하)  
            - **Embarked**: 탑승 항구 (C = Cherbourg, Q = Queenstown, S = Southampton)  
            - **목적**: 승객 특성(성별, 연령, 클래스 등)에 따른 생존율 분석  
            """
        )
