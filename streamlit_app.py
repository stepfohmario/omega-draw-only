import streamlit as st
import pandas as pd
import math

st.set_page_config(page_title="OMEGA DRAW ONLY PRO", page_icon="👑", layout="wide")

st.markdown("""
<style>
.big-title {font-size:48px; font-weight:900; text-align:center; color:white;}
.sub {text-align:center; color:#00FF88; font-weight:700;}
</style>
<div class='big-title'>👑 OMEGA SOVEREIGN - DRAW ONLY PRO</div>
<div class='sub'>Dixon-Cole 1997 Tau Correction | CAT 09-13 Sure Draw</div>
""", unsafe_allow_html=True)

st.sidebar.header("⚙️ Dixon-Cole Settings")
tau = st.sidebar.slider("Tau (draw dependence)", 0.0, 0.30, 0.10, 0.01)
st.sidebar.caption("Standard 0.10 = England. 0.13 for low-scoring leagues. Dixon & Coles 1997.")
st.sidebar.markdown("---")
st.sidebar.info("CAT A = Lambda & Mu both 0.9 - 1.3 = SURE DRAW ZONE")

def poisson(k, lam):
    return (lam**k * math.exp(-lam)) / math.factorial(k)

def dixon_cole_draw(lam, mu, tau):
    # Dixon-Cole adjusted low scores
    p00 = poisson(0,lam)*poisson(0,mu)*(1 - lam*mu*tau)
    p11 = poisson(1,lam)*poisson(1,mu)*(1 - tau)
    p01 = poisson(0,lam)*poisson(1,mu)*(1 + mu*tau)
    p10 = poisson(1,lam)*poisson(0,mu)*(1 + lam*tau)

    # For Draw we use corrected 0-0 and 1-1 + normal 2-2
    p22 = poisson(2,lam)*poisson(2,mu)
    # Higher draws small
    p33 = poisson(3,lam)*poisson(3,mu)

    total_draw = (p00 + p11 + p22 + p33) * 100
    return max(0, round(p00*100,2)), max(0, round(p11*100,2)), max(0, round(total_draw,2))

st.markdown("### 📤 Upload Team Stats Excel")
st.caption("Required columns: HomeTeam | HomeScored | HomeConceded | AwayTeam | AwayScored | AwayConceded")
st.caption("Example: Man City | 1.8 | 0.9 | Arsenal | 1.4 | 1.1")

uploaded = st.file_uploader("Drag & Drop CSV / XLSX (200MB max)", type=["csv","xlsx","xls"])

if uploaded:
    try:
        if uploaded.name.endswith(".xlsx") or uploaded.name.endswith(".xls"):
            df = pd.read_excel(uploaded)
        else:
            df = pd.read_csv(uploaded)

        # Clean columns
        df.columns = [c.strip() for c in df.columns]

        results = []
        for _, r in df.iterrows():
            try:
                # Calculate Lambda and Mu
                hs = float(r['HomeScored'])
                hc = float(r['HomeConceded'])
                aws = float(r['AwayScored'])
                awc = float(r['AwayConceded'])

                lam = (hs + awc) / 2
                mu = (aws + hc) / 2

                p00, p11, dc_total = dixon_cole_draw(lam, mu, tau)

                # OMEGA CAT SYSTEM 09--13
                if 0.90 <= lam <= 1.30 and 0.90 <= mu <= 1.30:
                    cat = "🔥 CAT A 09--13 SURE DRAW"
                    score = 100
                elif 0.80 <= lam <= 1.50 and 0.80 <= mu <= 1.50:
                    cat = "⚠️ CAT B DRAW LEAN"
                    score = 70
                elif 0.70 <= lam <= 1.70 and 0.70 <= mu <= 1.70:
                    cat = "CAT C"
                    score = 40
                else:
                    cat = "NO DRAW"
                    score = 10

                results.append([
                    str(r['HomeTeam']), str(r['AwayTeam']),
                    round(lam,2), round(mu,2),
                    p00, p11, dc_total,
                    cat, score
                ])
            except Exception as e:
                continue

        out_df = pd.DataFrame(results, columns=["Home","Away","Lambda","Mu","P(0-0)%","P(1-1)%","DixonCole DRAW%","CATEGORY","Rank"])
        out_df = out_df.sort_values(["Rank","DixonCole DRAW%"], ascending=[False, False])

        # BANKER
        if len(out_df) > 0:
            banker = out_df.iloc[0]
            st.success(f"🏦 BANKER OF THE DAY: {banker['Home']} vs {banker['Away']} | DRAW {banker['DixonCole DRAW%']}% | {banker['CATEGORY']} (Lambda {banker['Lambda']} / {banker['Mu']})")

        st.dataframe(out_df, use_container_width=True, height=600)

        # Download
        csv = out_df.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Download Results CSV", csv, "omega_draw_results.csv", "text/csv")

        st.metric("Total Games Analyzed", len(out_df))
        st.metric("CAT A Found", len(out_df[out_df['CATEGORY'].str.contains("CAT A")]))

    except Exception as err:
        st.error(f"Error reading file: {err}")
        st.write("Make sure columns are: HomeTeam, HomeScored, HomeConceded, AwayTeam, AwayScored, AwayConceded")
else:
    st.info("👆 Upload your Omega Excel to calculate Dixon-Cole Draw % - Engine ready at tau=0.10")
    st.markdown("""
    **How it works:**
    - Lambda = (Home Scored + Away Conceded)/2
    - Mu = (Away Scored + Home Conceded)/2
    - Dixon-Cole corrects 0-0 under-estimation by Poisson
    - CAT A 09--13 = Both Lambda & Mu in 0.9-1.3 = Historic Sure Draw
    """)

st.markdown("---")
st.caption("Built for Stephen | Omega Sovereign Engine | Dixon-Cole 1997")
