import streamlit as st
import pandas as pd
import math

st.set_page_config(page_title="OMEGA DRAW ONLY - Dixon-Cole", layout="wide")
st.title("OMEGA SOVEREIGN - DRAW ONLY (Dixon-Cole 1997)")

st.sidebar.header("Dixon-Cole Tau")
tau = st.sidebar.slider("Tau (draw correction)", 0.0, 0.3, 0.10, 0.01)
st.sidebar.write("Standard value = 0.10 - 0.13 for low scores")

def dixon_cole_adjusted_probs(lam, mu, tau):
    def poisson(k, l):
        return (l**k * math.exp(-l)) / math.factorial(k)

    p00 = poisson(0,lam)*poisson(0,mu)*(1 - lam*mu*tau)
    p11 = poisson(1,lam)*poisson(1,mu)*(1 - tau)
    p01 = poisson(0,lam)*poisson(1,mu)*(1 + mu*tau)
    p10 = poisson(1,lam)*poisson(0,mu)*(1 + lam*tau)

    # All draws 0-0,1-1,2-2
    p22 = poisson(2,lam)*poisson(2,mu)
    p_draw = (p00 + p11 + p22) * 100

    # Basic Poisson 0-0,1-1 approx for comparison
    dc_prob = p_draw

    return round(p00*100,2), round(p11*100,2), round(p_draw,2)

st.markdown("### Upload Team Stats Excel")
st.write("Columns needed: HomeTeam, HomeScored, HomeConceded, AwayTeam, AwayScored, AwayConceded")

uploaded = st.file_uploader("Upload CSV/XLSX", type=["csv","xlsx"])

if uploaded:
    if uploaded.name.endswith("xlsx"):
        df = pd.read_excel(uploaded)
    else:
        df = pd.read_csv(uploaded)

    results = []
    for _, r in df.iterrows():
        try:
            lam = (float(r['HomeScored']) + float(r['AwayConceded'])) / 2
            mu = (float(r['AwayScored']) + float(r['HomeConceded'])) / 2
        except:
            lam = float(r.get('lambda', 1.2))
            mu = float(r.get('mu', 1.0))

        p00, p11, dc_total = dixon_cole_adjusted_probs(lam, mu, tau)

        # CAT classification 09--13
        if 0.9 <= lam <= 1.3 and 0.9 <= mu <= 1.3:
            cat = "CAT A 09--13 SURE DRAW HIGH"
        elif 0.8 <= lam <= 1.5 and 0.8 <= mu <= 1.5:
            cat = "CAT B"
        else:
            cat = "OTHER"

        results.append([r['HomeTeam'], r['AwayTeam'], round(lam,2), round(mu,2), p00, p11, dc_total, cat])

    out_df = pd.DataFrame(results, columns=["Home","Away","Lambda","Mu","P(0-0)%","P(1-1)%","DixonCole DRAW%","CATEGORY"])
    out_df = out_df.sort_values("DixonCole DRAW%", ascending=False)
    st.dataframe(out_df, use_container_width=True)
    st.success(f"Processed {len(out_df)} games - Top Draw is {out_df.iloc[0]['Home']} vs {out_df.iloc[0]['Away']} = {out_df.iloc[0]['DixonCole DRAW%']}%")
else:
    st.info("Upload your Omega sheet to calculate Dixon-Cole Draw %")
    st.write("Example row: Man City, 1.8, 0.9, Arsenal, 1.4, 1.1")
