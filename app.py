"""CPR Pro Scanner & Backtester v3.2 — © 2026 Buvenesh | Trisea Trader"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from io import BytesIO
import engine as eng

def css():
    st.markdown("""<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800;900&display=swap');
    *{font-family:'Inter',sans-serif!important}
    .main .block-container{padding-top:0.5rem;max-width:1440px}
    .hero{text-align:center;padding:0.6rem 1rem;margin-bottom:0.5rem;
        background:linear-gradient(135deg,#0f172a,#1e293b,#0f172a);
        border:1px solid rgba(0,212,255,.15);border-radius:16px}
    .hero h1{font-size:1.4rem;font-weight:900;margin:0;
        background:linear-gradient(135deg,#00d4ff,#7c3aed,#f472b6);
        -webkit-background-clip:text;-webkit-text-fill-color:transparent}
    .hero p{color:#94a3b8;font-size:.8rem;margin-top:.2rem}
    .mc{background:linear-gradient(145deg,#111827,#1e293b);border-radius:12px;
        padding:.4rem .6rem;border:1px solid rgba(255,255,255,.06)}
    .mc .lb{font-size:.65rem;text-transform:uppercase;letter-spacing:1.2px;color:#64748b;font-weight:600}
    .mc .vl{font-size:1.1rem;font-weight:800}
    .cy .vl{color:#00d4ff}.gn .vl{color:#22c55e}.am .vl{color:#f59e0b}
    .rs .vl{color:#f43f5e}.pp .vl{color:#a78bfa}
    .sh{font-size:0.9rem;font-weight:700;color:#e2e8f0;border-left:3px solid #00d4ff;padding-left:.6rem;margin:0.5rem 0 0.3rem}
    .ib{background:rgba(0,212,255,.06);border:1px solid rgba(0,212,255,.15);border-radius:10px;padding:.4rem .6rem;color:#cbd5e1;font-size:.75rem}
    .stButton>button{border-radius:10px;font-weight:700;background:linear-gradient(135deg,#0ea5e9,#6366f1)!important;color:#fff!important;border:none!important;padding:.2rem 1rem}
    .stTabs [data-baseweb="tab"]{border-radius:8px 8px 0 0;padding:4px 12px;font-weight:600;font-size:.75rem}
    .ft{text-align:center;padding:1.2rem;margin-top:1.5rem;border-top:1px solid rgba(255,255,255,.06);color:#475569;font-size:.7rem}
    .rc{background:linear-gradient(145deg,#111827,#1a2332);border-radius:10px;padding:.8rem 1rem;border:1px solid rgba(255,255,255,.06);margin-bottom:.5rem}
    .rc h4{color:#00d4ff;margin:0 0 .2rem;font-size:.85rem}
    .rc p{color:#94a3b8;margin:0;font-size:.75rem;line-height:1.4}
    div[data-baseweb="select"]{font-size:.78rem!important}
    .stMultiSelect [data-baseweb="tag"]{font-size:.65rem!important;padding:1px 6px!important;margin:1px!important}
    .stMultiSelect{max-height:60px;overflow-y:auto}
    </style>""",unsafe_allow_html=True)

def mc(l,v,c="cy"):
    st.markdown(f'<div class="mc {c}"><div class="lb">{l}</div><div class="vl">{v}</div></div>',unsafe_allow_html=True)

def xl(df):
    b=BytesIO()
    with pd.ExcelWriter(b,engine="openpyxl") as w: df.to_excel(w,index=False,sheet_name="Trades")
    return b.getvalue()

def main():
    st.set_page_config(page_title="CPR Pro v3.2 | Trisea Trader",page_icon="⚡",layout="wide")
    css()
    for k,v in {"rdf":pd.DataFrame(),"raw":pd.DataFrame(),"scan":[],"ran":False}.items():
        if k not in st.session_state: st.session_state[k]=v

    logo_svg = """
    <div style="display: flex; justify-content: center; align-items: center; margin-top: -20px; margin-bottom: 0px;">
        <svg width="210" height="60" viewBox="0 0 300 100" xmlns="http://www.w3.org/2000/svg">
            <defs>
                <linearGradient id="sunGrad" x1="0%" y1="0%" x2="100%" y2="100%">
                    <stop offset="0%" stop-color="#F59E0B" />
                    <stop offset="100%" stop-color="#EA580C" />
                </linearGradient>
                <linearGradient id="waveGrad" x1="0%" y1="0%" x2="100%" y2="0%">
                    <stop offset="0%" stop-color="#0284C7" />
                    <stop offset="100%" stop-color="#3B82F6" />
                </linearGradient>
            </defs>
            <circle cx="45" cy="50" r="28" fill="url(#sunGrad)" opacity="0.15"/>
            <circle cx="45" cy="50" r="18" fill="url(#sunGrad)" opacity="0.4"/>
            <path d="M 5 35 Q 20 20, 35 35 T 65 35 L 85 35" fill="none" stroke="url(#waveGrad)" stroke-width="3" stroke-linecap="round">
                <animate attributeName="d" values="M 5 35 Q 20 20, 35 35 T 65 35 L 85 35; M 5 35 Q 20 50, 35 35 T 65 35 L 85 35; M 5 35 Q 20 20, 35 35 T 65 35 L 85 35" dur="3s" repeatCount="indefinite" />
            </path>
            <path d="M 5 50 Q 20 35, 35 50 T 65 50 L 85 50" fill="none" stroke="url(#waveGrad)" stroke-width="4.5" stroke-linecap="round">
                <animate attributeName="d" values="M 5 50 Q 20 35, 35 50 T 65 50 L 85 50; M 5 50 Q 20 65, 35 50 T 65 50 L 85 50; M 5 50 Q 20 35, 35 50 T 65 50 L 85 50" dur="3s" begin="0.5s" repeatCount="indefinite" />
            </path>
            <path d="M 5 65 Q 20 50, 35 65 T 65 65 L 85 65" fill="none" stroke="url(#waveGrad)" stroke-width="3" stroke-linecap="round">
                <animate attributeName="d" values="M 5 65 Q 20 50, 35 65 T 65 65 L 85 65; M 5 65 Q 20 80, 35 65 T 65 65 L 85 65; M 5 65 Q 20 50, 35 65 T 65 65 L 85 65" dur="3s" begin="1s" repeatCount="indefinite" />
            </path>
            <rect x="70" y="22" width="12" height="38" fill="#10B981" rx="2"/>
            <line x1="76" y1="12" x2="76" y2="22" stroke="#10B981" stroke-width="2.5" stroke-linecap="round"/>
            <line x1="76" y1="60" x2="76" y2="72" stroke="#10B981" stroke-width="2.5" stroke-linecap="round"/>
            <text x="105" y="54" font-family="'Inter', sans-serif" font-weight="800" font-size="34" fill="#F8FAFC" letter-spacing="1.5">TRISEA</text>
            <text x="108" y="74" font-family="'Inter', sans-serif" font-weight="600" font-size="13" fill="#10B981" letter-spacing="5.5">TRADER</text>
        </svg>
    </div>
    """
    st.markdown(logo_svg, unsafe_allow_html=True)
    st.markdown('<div class="hero"><h1>⚡ CPR PRO SCANNER & BACKTESTER v3.2</h1><p>Structure-Based Entry · Spot Signals · Futures Execution · © 2026 Buvenesh</p></div>',unsafe_allow_html=True)
    
    if "idx_scan" not in st.session_state:
        st.session_state.idx_scan = eng.scan_live_batch("Indices Only", 100)
        
    if st.session_state.idx_scan:
        idx_df = pd.DataFrame(st.session_state.idx_scan)
        if not idx_df.empty:
            cdate = idx_df["CPR Date"].iloc[0] if "CPR Date" in idx_df.columns else ""
            d_str = f" for {cdate}" if cdate else ""
            st.markdown(f'<div class="sh">📌 Index CPR & Expected Day{d_str}</div>',unsafe_allow_html=True)
            cols=st.columns(min(len(idx_df), 4))
            for i,(_,r) in enumerate(idx_df.head(4).iterrows()):
                with cols[i]:
                    ed=r.get("Expected Day","—")
                    ct=r.get("CPR Type","—")
                    clr="gn" if "Bull" in str(ed) or "Very" in ct else ("rs" if "Bear" in str(ed) else "am")
                    mc(r["Symbol"],f"{ct} · {r['CPR %ADR']:.1f}%",clr)
                    st.caption(f"📉 {ed}")

    t1,t2,t3,t5,t4=st.tabs(["📡 TOMORROW CPR SCANNER","🎯 STRATEGY LAB","📊 ANALYTICS","⚙️ OPTIMIZER","📘 PLAYBOOK"])

    # ═══ TAB 1: LIVE SCANNER ═══════════════════════
    with t1:
        st.markdown('<div class="sh">Next Day CPR Scanner</div>',unsafe_allow_html=True)
        c1,c2,c3=st.columns([1,1,1])
        with c1: cat=st.selectbox("Category",["Indices Only","Nifty 50","Nifty F&O"],key="scat")
        with c2: adr_l=st.slider("Max CPR %ADR",5,40,15,key="sadr")
        with c3:
            st.write("")
            go_scan=st.button("📡 Scan Now",use_container_width=True)
        if go_scan:
            pb=st.progress(0,"Starting scan...")
            def pcb(p,t): pb.progress(min(p,1.0),t)
            with st.spinner(""):
                st.session_state.scan=eng.scan_live_batch(cat,adr_l,pcb)
            pb.empty()

        if st.session_state.scan:
            sdf=pd.DataFrame(st.session_state.scan)
            narrow=sdf[sdf["CPR %ADR"]<=adr_l].sort_values("CPR %ADR")
            m1,m2,m3=st.columns(3)
            with m1: mc("Total Scanned",len(sdf))
            with m2: mc("Narrow CPR",len(narrow),"gn" if len(narrow) else "rs")
            with m3: mc("Very Narrow (<5%)",len(sdf[sdf["CPR %ADR"]<5]),"pp")

            st.markdown("")
            if not narrow.empty:
                st.dataframe(narrow.style.format({c:"{:.2f}" for c in narrow.select_dtypes(include=[np.number]).columns},na_rep="—"),use_container_width=True,height=400)

    # ═══ TAB 2: STRATEGY LAB ═══════════════════════
    with t2:
        st.markdown('<div class="sh">V3.2 Strategy Lab — Structure-Based Backtest</div>',unsafe_allow_html=True)
        st.markdown('<div class="ib">Entry: 1st/2nd 5-min candle above PDH+R1 (BUY) or below PDL+S1 (SELL). R:R ≥ 1:1 enforced. Targets at next pivot level.</div>',unsafe_allow_html=True)
        c1,c2,c3,c4=st.columns([1.2,1,1,1.5])
        with c1: idx=st.selectbox("Index",list(eng.INDEX_CONFIG.keys()),key="idx")
        with c2: alim=st.slider("Max CPR Width (%ADR)",5,40,15,key="adr")
        with c3:
            cfg=eng.INDEX_CONFIG[idx]
            prem=st.number_input("Futures Premium",value=cfg["prem"],step=5,key="pm")
            f_sl=st.number_input("Fixed SL (₹) [0=Pivot]",value=0,step=500,key="fsl")
            f_tgt=st.number_input("Fixed Target (₹) [0=Pivot]",value=0,step=500,key="ftgt")
        with c4: 
            bfil=st.checkbox("1st Candle Body ≥40%",key="bf")
            pb_val=st.checkbox("Pivot Boss: Value Area Bias", key="pb_val")
            pb_wick=st.checkbox("Pivot Boss: Open-Drive (No Wicks)", key="pb_wick")
            pb_inside=st.checkbox("Pivot Boss: Inside CPR Only", key="pb_in")

        if st.button("🚀 Run Backtest",use_container_width=True,key="run"):
            with st.spinner("Fetching & simulating..."):
                df=eng.fetch_and_prep(cfg["ticker"])
                if not df.empty:
                    st.session_state.raw=df
                    sigs=eng.scan_v3(df,idx,alim,bfil,pb_val,pb_wick,pb_inside,f_sl,f_tgt)
                    res=eng.simulate(df,sigs,idx,prem)
                    st.session_state.rdf=pd.DataFrame(res) if res else pd.DataFrame()
                    st.session_state.ran=True
                else: st.error("No data available.")

        if not st.session_state.rdf.empty:
            rdf=st.session_state.rdf.copy()
            lot=eng.INDEX_CONFIG[idx]["lot"]

            # ── COMPACT FILTERS ──
            st.markdown('<div class="sh">Filters</div>',unsafe_allow_html=True)
            f1,f2,f3,f4=st.columns(4)
            days=["Monday","Tuesday","Wednesday","Thursday","Friday"]
            with f1: sd=st.multiselect("Day",days,default=days,key="fd")
            with f2: st2=st.multiselect("Type",rdf["Type"].unique().tolist(),default=rdf["Type"].unique().tolist(),key="ft")
            with f3: sc=st.multiselect("CPR",rdf["CPR_Type"].unique().tolist(),default=rdf["CPR_Type"].unique().tolist(),key="fc")
            with f4:
                mos=sorted(rdf["Date"].apply(lambda x:x[:7]).unique().tolist())
                sm=st.multiselect("Month",mos,default=mos,key="fm")
            fdf=rdf[rdf["Day"].isin(sd)&rdf["Type"].isin(st2)&rdf["CPR_Type"].isin(sc)&rdf["Date"].apply(lambda x:x[:7]).isin(sm)]

            # ── METRICS ──
            rpt=eng.performance_report(fdf,lot) if not fdf.empty else {}
            m1,m2,m3,m4,m5=st.columns(5)
            with m1: mc("Trades",rpt.get("Total Trades",0))
            with m2: mc("Win Rate",f"{rpt.get('Win Rate %',0)}%","gn" if rpt.get("Win Rate %",0)>=50 else "rs")
            with m3: mc("Profit Factor",rpt.get("Profit Factor","—"),"am")
            with m4: mc("Expectancy",f"{rpt.get('Expectancy',0)} pts","pp")
            with m5: mc("Total P&L",f"₹{rpt.get('Total P&L ₹',0):,.0f}","gn" if rpt.get("Total P&L ₹",0)>=0 else "rs")

            # ── TABLE ──
            dcols=["Date","Day","Time","Type","Scenario","Entry","SL","Target","Target_Lvl","Exit","Exit Time","Exit Reason","MAE ₹","MFE ₹","P&L Pts","P&L ₹","Risk Pts","RR","Fut Entry","Fut Exit","CPR_%","CPR_Type","Body_%","Success"]
            sdf2=fdf[[c for c in dcols if c in fdf.columns]].copy().sort_values(["Date","Time"],ascending=[False,False]).reset_index(drop=True)
            nc=[c for c in sdf2.select_dtypes(include=[np.number]).columns]
            fmt={c:"{:.2f}" for c in nc if c!="Success"}
            st.dataframe(sdf2.style.format(fmt,na_rep="—").map(
                lambda v:"color:#22c55e;font-weight:700" if isinstance(v,(int,float)) and v>0 else("color:#f43f5e;font-weight:700" if isinstance(v,(int,float)) and v<0 else ""),
                subset=[c for c in["P&L Pts","P&L ₹","MFE ₹","MAE ₹"] if c in sdf2.columns]
            ),use_container_width=True,height=300)

            dc1,dc2=st.columns(2)
            with dc1: st.download_button("📥 Excel",xl(sdf2),"trades.xlsx","application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",use_container_width=True)
            with dc2: st.download_button("📥 CSV",sdf2.to_csv(index=False).encode(),"trades.csv","text/csv",use_container_width=True)

            # ── EQUITY CURVE ──
            st.markdown('<div class="sh">Equity Curve (₹)</div>',unsafe_allow_html=True)
            eq=fdf["P&L ₹"].cumsum().reset_index(drop=True)
            feq=go.Figure()
            feq.add_trace(go.Scatter(y=eq,mode="lines",line=dict(color="#00d4ff",width=2.5),fill="tozeroy",fillcolor="rgba(0,212,255,.08)"))
            feq.update_layout(template="plotly_dark",height=250,paper_bgcolor="#0a0e17",plot_bgcolor="#0a0e17",yaxis_title="Cum P&L ₹",xaxis_title="Trade #",font=dict(family="Inter"),margin=dict(l=50,r=20,t=10,b=30))
            st.plotly_chart(feq,use_container_width=True)

            # ── 2-DAY CHART ──
            st.markdown('<div class="sh">Trade Verification Chart</div>',unsafe_allow_html=True)
            dl=sorted(fdf["Date"].unique().tolist(),reverse=True)
            seld=st.selectbox("Trade Date",dl)

            if seld and not st.session_state.raw.empty:
                raw=st.session_state.raw
                ad=sorted(raw["Date"].unique()); ads=[str(d) for d in ad]
                if seld in ads:
                    di=ads.index(seld)
                    pd_=ads[di-1] if di>0 else None
                    cdays=[pd_,seld] if pd_ else [seld]
                    cdf=raw[raw["Date"].astype(str).isin(cdays)]
                else: cdf=raw[raw["Date"].astype(str)==seld]

                if not cdf.empty:
                    cx=cdf.index.tz_localize(None)
                    fig=make_subplots(rows=2,cols=1,shared_xaxes=True,row_heights=[.8,.2],vertical_spacing=.02)
                    fig.add_trace(go.Candlestick(x=cx,open=cdf["Open"],high=cdf["High"],low=cdf["Low"],close=cdf["Close"],name="Price",increasing_line_color="#16a34a",decreasing_line_color="#dc2626",increasing_fillcolor="#16a34a",decreasing_fillcolor="#dc2626"),row=1,col=1)
                    vc=["#16a34a" if c>=o else "#dc2626" for c,o in zip(cdf["Close"],cdf["Open"])]
                    fig.add_trace(go.Bar(x=cx,y=cdf["Volume"],marker_color=vc,opacity=.5,showlegend=False),row=2,col=1)

                    # Previous day levels
                    if pd_:
                        pday=cdf[cdf["Date"].astype(str)==pd_]
                        tday=cdf[cdf["Date"].astype(str)==seld]
                        if not pday.empty:
                            px0,px1=pday.index[0].tz_localize(None),pday.index[-1].tz_localize(None)
                            plv=pday.iloc[0]
                            for col,lbl,clr,d in [("Top_CPR","TC","#60a5fa","dot"),("Pivot","P","#60a5fa","dashdot"),("Bot_CPR","BC","#60a5fa","dot"),("PDH","PDH","#fb923c","dash"),("PDL","PDL","#fb923c","dash")]:
                                if col in plv.index and not pd.isna(plv[col]):
                                    fig.add_shape(type="line",x0=px0,x1=px1,y0=plv[col],y1=plv[col],line=dict(color=clr,width=1,dash=d),row=1,col=1)
                                    fig.add_annotation(x=px0,y=plv[col],text=f"  {lbl}",showarrow=False,font=dict(color=clr,size=9),xanchor="left",row=1,col=1)
                            # Split line
                            if not tday.empty:
                                sp=tday.index[0].tz_localize(None)
                                fig.add_vline(x=sp,line_dash="solid",line_color="#94a3b8",line_width=1.5,opacity=.7,row=1,col=1)

                    # Current day levels
                    td=cdf[cdf["Date"].astype(str)==seld]
                    if not td.empty:
                        tx0,tx1=td.index[0].tz_localize(None),td.index[-1].tz_localize(None)
                        lv=td.iloc[0]
                        for col,lbl,clr,d in [("Top_CPR","TC","#3b82f6","solid"),("Pivot","Pivot","#3b82f6","dot"),("Bot_CPR","BC","#3b82f6","solid"),("PDH","PDH","#f59e0b","dash"),("PDL","PDL","#f59e0b","dash"),("R1","R1","#22c55e","dashdot"),("S1","S1","#ef4444","dashdot"),("R2","R2","#15803d","dot"),("S2","S2","#b91c1c","dot"),("R3","R3","#166534","longdashdot"),("S3","S3","#7f1d1d","longdashdot")]:
                            if col in lv.index and not pd.isna(lv[col]):
                                fig.add_shape(type="line",x0=tx0,x1=tx1,y0=lv[col],y1=lv[col],line=dict(color=clr,width=1.2,dash=d),row=1,col=1)
                                fig.add_annotation(x=tx1,y=lv[col],text=f"{lbl} ",showarrow=False,font=dict(color=clr,size=9),xanchor="right",row=1,col=1)

                    # Trade signals + EXIT markers
                    dt=fdf[fdf["Date"]==seld]
                    for _,t in dt.iterrows():
                        try: tdt=pd.to_datetime(f"{t['Date']} {t['Time']}")
                        except: continue
                        ib=t["Type"]=="BUY"
                        ec="#16a34a" if ib else "#dc2626"
                        # Entry arrow
                        fig.add_trace(go.Scatter(x=[tdt],y=[t["Entry"]],mode="markers+text",marker=dict(symbol="triangle-up" if ib else "triangle-down",size=16,color=ec,line=dict(width=1.5,color="#000")),text=[f"  {t['Type']} ENTRY"],textposition="middle right",textfont=dict(color=ec,size=11,family="Inter"),showlegend=False),row=1,col=1)
                        # SL/Target lines
                        eod=tx1 if not td.empty else tdt
                        for yv,lc,ls in [(t["Target"],"#16a34a","dashdot"),(t["SL"],"#dc2626","dashdot")]:
                            fig.add_shape(type="line",x0=tdt,x1=eod,y0=yv,y1=yv,line=dict(color=lc,width=1.5,dash=ls),row=1,col=1)
                        # EXIT marker
                        try:
                            et_str=t.get("Exit Time",t["Time"])
                            edt=pd.to_datetime(f"{t['Date']} {et_str}")
                        except: edt=eod
                        er=t["Exit Reason"]
                        if er=="Target Hit": em,ecl,etx="star","#16a34a","TARGET HIT ✅"
                        elif er=="SL Hit": em,ecl,etx="x","#dc2626","SL HIT ❌"
                        else: em,ecl,etx="circle","#f59e0b","EOD EXIT ⏰"
                        fig.add_trace(go.Scatter(x=[edt],y=[t["Exit"]],mode="markers+text",marker=dict(symbol=em,size=14,color=ecl,line=dict(width=2,color="#000")),text=[f"  {etx}"],textposition="middle right",textfont=dict(color=ecl,size=10,family="Inter"),showlegend=False),row=1,col=1)

                    # Remove overnight gaps between days
                    fig.update_xaxes(rangebreaks=[
                        dict(bounds=[15.5,9.25],pattern="hour"),  # Hide 15:30 to 09:15
                    ],gridcolor="#f1f5f9")
                    fig.update_layout(template="plotly_white",height=700,paper_bgcolor="#ffffff",plot_bgcolor="#fafbfc",
                        title=dict(text=f"📊 {idx} · {seld}",font=dict(size=14,color="#1e293b")),
                        xaxis_rangeslider_visible=False,font=dict(family="Inter",color="#334155"),
                        legend=dict(orientation="h",y=1.03,x=.5,xanchor="center"),dragmode="pan",
                        margin=dict(l=50,r=50,t=40,b=20))
                    fig.update_yaxes(title_text="Price",gridcolor="#e2e8f0",row=1,col=1)
                    fig.update_yaxes(title_text="Vol",gridcolor="#e2e8f0",row=2,col=1)
                    ccfg={"scrollZoom":True,"displaylogo":False,"toImageButtonOptions":{"format":"png","filename":f"cpr_{seld}","height":900,"width":1600,"scale":2}}
                    st.plotly_chart(fig,use_container_width=True,config=ccfg)
                    st.caption("🖱️ Scroll=Zoom · Drag=Pan · Double-click=Reset · 📷 Camera icon=Download PNG")

        elif st.session_state.ran:
            st.warning("No valid setups found (R:R < 1:1 or target in wrong direction filtered out).")

    # ═══ TAB 3: ANALYTICS ═════════════════════════
    with t3:
        st.markdown('<div class="sh">Performance Analytics</div>',unsafe_allow_html=True)
        if st.session_state.rdf.empty:
            st.info("Run a backtest in **Strategy Lab** first.")
        else:
            rdf=st.session_state.rdf
            lot=eng.INDEX_CONFIG.get(st.session_state.get("idx","NIFTY 50"),{}).get("lot",1)
            rpt=eng.performance_report(rdf,lot)
            c1,c2=st.columns(2)
            with c1:
                st.markdown("#### Summary")
                st.dataframe(pd.DataFrame(rpt.items(),columns=["Metric","Value"]),use_container_width=True,hide_index=True)
            with c2:
                st.markdown("#### P&L Distribution")
                fh=go.Figure()
                fh.add_trace(go.Histogram(x=rdf["P&L Pts"],nbinsx=15,marker_color="#6366f1"))
                fh.add_vline(x=0,line_dash="dash",line_color="#f43f5e",line_width=2)
                fh.update_layout(template="plotly_dark",height=250,paper_bgcolor="#0a0e17",plot_bgcolor="#0a0e17",xaxis_title="P&L Pts",margin=dict(l=40,r=20,t=10,b=30))
                st.plotly_chart(fh,use_container_width=True)
            c3,c4=st.columns(2)
            with c3:
                st.markdown("#### By Trade Type")
                for tp in["BUY","SELL"]:
                    s=rdf[rdf["Type"]==tp]
                    if len(s): mc(f"{tp} ({len(s)})",f"{s['Success'].sum()/len(s)*100:.1f}%","gn" if s['Success'].mean()>=.5 else "rs"); st.markdown("")
            with c4:
                st.markdown("#### By CPR Type")
                for ct in["Very Narrow","Narrow","Mid","Wide"]:
                    s=rdf[rdf["CPR_Type"]==ct]
                    if len(s): mc(f"{ct} ({len(s)})",f"{s['Success'].sum()/len(s)*100:.1f}%","gn" if s['Success'].mean()>=.5 else "am"); st.markdown("")
            st.markdown("#### By Day of Week")
            dw=rdf.groupby("Day").agg(Trades=("Success","count"),Wins=("Success","sum"),PnL=("P&L Pts","sum"))
            dw["Win%"]=(dw["Wins"]/dw["Trades"]*100).round(1); dw["PnL"]=dw["PnL"].round(2)
            st.dataframe(dw,use_container_width=True)

            st.markdown('<div class="sh">Trade Excursion (MAE / MFE)</div>',unsafe_allow_html=True)
            st.write("Tracks how far trades went into profit (MFE) vs how far they went into loss (MAE) before exiting.")
            import plotly.express as px
            rdf_c = rdf.copy()
            rdf_c["Outcome"] = rdf_c["Success"].apply(lambda x: "Winner" if x else "Loser")
            fig = px.scatter(rdf_c, x="MAE ₹", y="MFE ₹", color="Outcome",
                             color_discrete_map={"Winner": "#22c55e", "Loser": "#ef4444"},
                             hover_data=["Date", "Time", "Type", "P&L ₹"],
                             title="Maximum Adverse vs Favorable Excursion")
            fig.update_layout(template="plotly_dark", height=500)
            st.plotly_chart(fig, use_container_width=True)

    # ═══ TAB 5: OPTIMIZER ══════════════════════════
    with t5:
        st.markdown('<div class="sh">Hyperparameter Optimizer</div>',unsafe_allow_html=True)
        st.write("Run a Grid Search to find the mathematically perfect SL and Target for Win Rate.")
        o_idx = st.selectbox("Select Index for Optimization", list(eng.INDEX_CONFIG.keys()), key="opt_idx")
        co1, co2 = st.columns(2)
        with co1:
            o_sl_min = st.number_input("Min SL (₹)", 1000, 5000, 1500, 500)
            o_sl_max = st.number_input("Max SL (₹)", 1000, 10000, 3500, 500)
        with co2:
            o_tgt_min = st.number_input("Min Target (₹)", 2000, 15000, 4000, 1000)
            o_tgt_max = st.number_input("Max Target (₹)", 2000, 20000, 10000, 1000)
            
        if o_sl_max < o_sl_min: o_sl_max = o_sl_min
        if o_tgt_max < o_tgt_min: o_tgt_max = o_tgt_min
        
        if st.button("🚀 Run Grid Search", use_container_width=True, key="opt_run"):
            with st.spinner(f"Fetching data and running grid search for {o_idx}..."):
                cfg = eng.INDEX_CONFIG[o_idx]
                df = eng.fetch_and_prep(cfg["ticker"])
                if not df.empty:
                    alim = 15 # default
                    lot = cfg["lot"]
                    hm_data = []
                    sl_range = list(range(o_sl_min, o_sl_max + 500, 500))
                    tgt_range = list(range(o_tgt_min, o_tgt_max + 1000, 1000))
                    
                    for s in sl_range:
                        for t in tgt_range:
                            sigs = eng.scan_v3(df, o_idx, alim, f_sl_rs=s, f_tgt_rs=t)
                            if not sigs: continue
                            res = eng.simulate(df, sigs, o_idx, 0)
                            if not res: continue
                            tdf = pd.DataFrame(res)
                            wr = tdf["Success"].mean() * 100
                            eod_exits = (tdf["Exit Reason"] == "EOD Exit").sum() if "Exit Reason" in tdf.columns else 0
                            
                            w_mask = tdf["Success"]
                            avg_w = tdf.loc[w_mask, "P&L Pts"].mean() if w_mask.any() else 0
                            avg_l = tdf.loc[~w_mask, "P&L Pts"].mean() if (~w_mask).any() else 0
                            exp_pts = (wr/100 * avg_w) + ((1 - wr/100) * avg_l)
                            if pd.isna(exp_pts): exp_pts = 0
                            pnl_sum = tdf["P&L ₹"].sum()
                            
                            hm_data.append({"SL": s, "Target": t, "WinRate": wr, "Expectancy": exp_pts, "PnL": pnl_sum, "Trades": len(tdf), "EOD_Exits": eod_exits})
                    
                    if hm_data:
                        st.session_state.opt_hm_data = hm_data
                        st.session_state.opt_idx_run = o_idx
                        st.session_state.opt_num_days = df["Date"].nunique()
                    else:
                        st.warning("No trades generated in this grid.")
                else:
                    st.error("Failed to fetch data for the selected index.")
                    
        if "opt_hm_data" in st.session_state:
            hdf = pd.DataFrame(st.session_state.opt_hm_data)
            
            df_norm = hdf.copy()
            for c in ["WinRate", "Expectancy", "PnL"]:
                cmin, cmax = df_norm[c].min(), df_norm[c].max()
                df_norm[c] = (df_norm[c] - cmin) / (cmax - cmin) if cmax > cmin else 1.0
            smin, smax = df_norm["SL"].min(), df_norm["SL"].max()
            df_norm["SL_norm"] = 1.0 - ((df_norm["SL"] - smin) / (smax - smin)) if smax > smin else 1.0
            
            df_norm["Score"] = df_norm["WinRate"] + df_norm["Expectancy"] + df_norm["PnL"] + df_norm["SL_norm"]
            red_idx = df_norm["Score"].idxmax()
            red_sl, red_tgt = hdf.loc[red_idx, "SL"], hdf.loc[red_idx, "Target"]
            red_trades = hdf.loc[red_idx, "Trades"]
            
            blue_idx = hdf.sort_values(by=["WinRate", "SL", "Expectancy"], ascending=[False, True, False]).index[0]
            blue_sl, blue_tgt = hdf.loc[blue_idx, "SL"], hdf.loc[blue_idx, "Target"]
            
            black_idx = hdf.sort_values(by=["EOD_Exits", "WinRate", "SL"], ascending=[True, False, True]).index[0]
            black_sl, black_tgt = hdf.loc[black_idx, "SL"], hdf.loc[black_idx, "Target"]
            black_eod = hdf.loc[black_idx, "EOD_Exits"]
            
            hdf_wr = hdf.pivot(index="SL", columns="Target", values="WinRate").fillna(0)
            hdf_exp = hdf.pivot(index="SL", columns="Target", values="Expectancy").fillna(0)
            hdf_pnl = hdf.pivot(index="SL", columns="Target", values="PnL").fillna(0)
            
            cd_wr = np.stack((hdf_exp.values, hdf_pnl.values), axis=-1)
            cd_exp = np.stack((hdf_wr.values, hdf_pnl.values), axis=-1)
            
            st.markdown("### Optimization Results")
            st.caption(f"Tested over **{st.session_state.get('opt_num_days', 0)} days**. Score Best (Red) executed **{int(red_trades)} trades**. Black Box: Min EOD Exits ({int(black_eod)}).")
            ht1, ht2 = st.tabs(["🎯 Win Rate %", "📈 Expectancy (Pts)"])
            
            def draw_borders(fig):
                fig.add_shape(type="rect", x0=red_tgt-500, x1=red_tgt+500, y0=red_sl-250, y1=red_sl+250,
                              line=dict(color="#ef4444", width=4), fillcolor="rgba(0,0,0,0)")
                fig.add_shape(type="rect", x0=blue_tgt-480, x1=blue_tgt+480, y0=blue_sl-230, y1=blue_sl+230,
                              line=dict(color="#3b82f6", width=4), fillcolor="rgba(0,0,0,0)")
                fig.add_shape(type="rect", x0=black_tgt-460, x1=black_tgt+460, y0=black_sl-210, y1=black_sl+210,
                              line=dict(color="#000000", width=4), fillcolor="rgba(0,0,0,0)")
            
            with ht1:
                fig1 = go.Figure(data=go.Heatmap(
                    z=hdf_wr.values, x=hdf_wr.columns, y=hdf_wr.index,
                    text=hdf_wr.values, texttemplate="%{text:.1f}%", customdata=cd_wr,
                    hovertemplate="Target: ₹%{x}<br>SL: ₹%{y}<br>WinRate: %{z:.1f}%<br>Expectancy: %{customdata[0]:.1f} pts<br>P&L: ₹%{customdata[1]:,.0f}<extra></extra>",
                    colorscale="Greens"
                ))
                draw_borders(fig1)
                fig1.update_layout(template="plotly_dark", height=600, xaxis_title="Target (₹)", yaxis_title="Stop Loss (₹)")
                st.plotly_chart(fig1, use_container_width=True)

            with ht2:
                fig2 = go.Figure(data=go.Heatmap(
                    z=hdf_exp.values, x=hdf_exp.columns, y=hdf_exp.index,
                    text=hdf_exp.values, texttemplate="%{text:.1f}", customdata=cd_exp,
                    hovertemplate="Target: ₹%{x}<br>SL: ₹%{y}<br>Expectancy: %{z:.1f} pts<br>WinRate: %{customdata[0]:.1f}%<br>P&L: ₹%{customdata[1]:,.0f}<extra></extra>",
                    colorscale="RdYlGn", zmid=0
                ))
                draw_borders(fig2)
                fig2.update_layout(template="plotly_dark", height=600, xaxis_title="Target (₹)", yaxis_title="Stop Loss (₹)")
                st.plotly_chart(fig2, use_container_width=True)

            st.info("""
            **Heatmap Highlight Legend:**
            * 🟥 **Red Box (Best Overall):** Balances Win Rate, Expectancy, and Total Profit, while mathematically favoring a tighter Stop Loss to reduce risk.
            * 🟦 **Blue Box (Max Win Rate):** Strict priority on the highest possible win rate. If tied, it chooses the one with the smallest Stop Loss.
            * ⬛ **Black Box (Clean Execution):** Finds setups with the absolute lowest number of End-Of-Day (EOD) exits. Prioritizes setups where trades decisively hit either the Target or the Stop Loss.
            """)

    # ═══ TAB 4: PLAYBOOK ══════════════════════════
    with t4:
        st.markdown('<div class="sh">V3.2 Strategy Playbook</div>',unsafe_allow_html=True)
        for title,body in [
            ("1 · Entry Logic","<b>BUY:</b> 1st/2nd 5-min candle closes above <b>PDH + R1</b><br><b>SELL:</b> closes below <b>PDL + S1</b><br>Only 09:15–09:25 window. Max 1 trade/day.<br><b>Filter:</b> If 1st candle is a doji (body &lt; 40%), skip the entire day."),
            ("2 · Target","BUY above R1 → <b>R2</b>. Above R2 → <b>R3</b><br>SELL below S1 → <b>S2</b>. Below S2 → <b>S3</b><br>Target MUST be in correct direction. R:R ≥ 1:1 enforced."),
            ("3 · Stop-Loss","<b>Scenario A</b> (1st candle): Wider of broken R1/PDH (BUY) or S1/PDL (SELL)<br><b>Scenario B</b> (2nd candle): Below candle low/high<br>Buffer: NIFTY/FINNIFTY=5pts | BNF/SENSEX/BANKEX=10pts"),
            ("4 · Exit","Full 1 lot. Target / SL / EOD 15:15. No partial booking."),
            ("5 · Lots","NIFTY=65 | BANK NIFTY=30 | FINNIFTY=60 | SENSEX=20 | BANKEX=30"),
            ("6 · CPR Types","Very Narrow (&lt;5%) · Narrow (5–15%) · Mid (15–35%) · Wide (&gt;35%)"),
            ("7 · Fixes in v3.2","✅ Scenario A/B labels corrected<br>✅ Structural SL (Wider) fixed<br>✅ Body filter applied to whole day<br>✅ R:R ≥ 1:1 gate & Target direction"),
        ]: st.markdown(f'<div class="rc"><h4>{title}</h4><p>{body}</p></div>',unsafe_allow_html=True)

    st.markdown('<div class="ft">⚡ CPR Pro Scanner & Backtester v3.2<br>© 2026 Buvenesh | Trisea Trader. All Rights Reserved.</div>',unsafe_allow_html=True)

if __name__=="__main__": main()
