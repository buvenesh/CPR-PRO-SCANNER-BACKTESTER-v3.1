"""
CPR Pro Trading Engine v3.1 — © 2026 Buvenesh | Trisea Trader
Fixes: Target direction validation, R:R >= 1:1, Very Narrow CPR,
batch scanner, expected day type, stock categories.
"""
import yfinance as yf
import pandas as pd
import numpy as np
import pytz

IST = pytz.timezone("Asia/Kolkata")

INDEX_CONFIG = {
    "NIFTY 50":   {"ticker":"^NSEI",               "lot":65,"buf":5, "prem":50},
    "BANK NIFTY": {"ticker":"^NSEBANK",             "lot":30,"buf":10,"prem":100},
    "FINNIFTY":   {"ticker":"NIFTY_FIN_SERVICE.NS", "lot":60,"buf":5, "prem":30},
    "SENSEX":     {"ticker":"^BSESN",               "lot":20,"buf":10,"prem":80},
    "BANKEX":     {"ticker":"BSE-BANK.BO",          "lot":30,"buf":10,"prem":80},
}

NIFTY50 = [
    "RELIANCE","TCS","HDFCBANK","INFY","ICICIBANK","HINDUNILVR","ITC","SBIN",
    "BHARTIARTL","KOTAKBANK","LT","HCLTECH","AXISBANK","ASIANPAINT","MARUTI",
    "SUNPHARMA","TITAN","BAJFINANCE","NTPC","TATAMOTORS","POWERGRID","M&M",
    "ULTRACEMCO","WIPRO","NESTLEIND","DRREDDY","TECHM","INDUSINDBK","BAJAJFINSV",
    "CIPLA","GRASIM","ONGC","COALINDIA","BRITANNIA","EICHERMOT","DIVISLAB",
    "TATACONSUM","APOLLOHOSP","HEROMOTOCO","BPCL","ADANIENT","BAJAJ-AUTO",
    "JSWSTEEL","TATASTEEL","HINDALCO","SBILIFE","HDFCLIFE","SHRIRAMFIN","TRENT","BEL"
]

NIFTY_FNO = NIFTY50 + [
    "BANKBARODA","PNB","IDFCFIRSTB","FEDERALBNK","BANDHANBNK","AUBANK",
    "LTIM","MPHASIS","COFORGE","PERSISTENT","ASHOKLEY","TVSMOTOR","BHARATFORG",
    "AUROPHARMA","BIOCON","LUPIN","MANKIND","COLPAL","DABUR","GODREJCP","MARICO",
    "IOC","GAIL","TATAPOWER","ADANIGREEN","VEDL","NMDC","SAIL",
    "ICICIGI","ICICIPRULI","MUTHOOTFIN","CHOLAFIN","PFC","RECLTD",
    "SHREECEM","AMBUJACEM","ACC","ABB","SIEMENS","HAVELLS","HAL","BHEL",
    "IDEA","PIDILITIND","PAGEIND","DMART","ZOMATO","IRCTC","INDIGO",
    "PIIND","SRF","ASTRAL","CUMMINSIND","DIXON","POLYCAB","VOLTAS",
    "ICICIBANK","MCX","NAUKRI","DEEPAKNTR","LICHSGFIN","IPCALAB","ESCORTS",
    "RAMCOCEM","CROMPTON","OBEROIRLTY","DLF","GODREJPROP","PRESTIGE"
]

STOCK_CATS = {"Indices Only": [], "Nifty 50": NIFTY50, "Nifty F&O": NIFTY_FNO}


def fetch_and_prep(ticker, period="60d", interval="5m"):
    try:
        data = yf.download(ticker, period=period, interval=interval, progress=False)
        if data.empty: return pd.DataFrame()
        if isinstance(data.columns, pd.MultiIndex):
            data.columns = data.columns.get_level_values(0)
        data.index = data.index.tz_convert(IST)
        data["Date"] = data.index.date
        daily = data.groupby("Date").agg(
            {"Open":"first","High":"max","Low":"min","Close":"last","Volume":"sum"}
        ).reset_index()
        levels = _daily_levels(daily)
        data["Datetime"] = data.index
        data = data.reset_index(drop=True).merge(levels, on="Date", how="left", suffixes=("","_d"))
        data = data.dropna(subset=["Pivot"]).set_index("Datetime")
        data.index.name = None
        return data
    except Exception as e:
        print(f"[engine] {e}"); return pd.DataFrame()


def _daily_levels(daily):
    lv = pd.DataFrame()
    lv["Date"] = daily["Date"].shift(-1)
    H, L, C = daily["High"], daily["Low"], daily["Close"]
    lv["Pivot"] = (H+L+C)/3
    lv["Bot_CPR"] = (H+L)/2
    lv["Top_CPR"] = 2*lv["Pivot"] - lv["Bot_CPR"]
    tc = np.maximum(lv["Top_CPR"], lv["Bot_CPR"])
    bc = np.minimum(lv["Top_CPR"], lv["Bot_CPR"])
    lv["Top_CPR"], lv["Bot_CPR"] = tc, bc
    lv["CPR_Width"] = tc - bc
    lv["R1"]=2*lv["Pivot"]-L; lv["S1"]=2*lv["Pivot"]-H
    lv["R2"]=lv["Pivot"]+(H-L); lv["S2"]=lv["Pivot"]-(H-L)
    lv["R3"]=H+2*(lv["Pivot"]-L); lv["S3"]=L-2*(H-lv["Pivot"])
    lv["PDH"]=H.values; lv["PDL"]=L.values; lv["PDC"]=C.values
    lv["ADR"]=(H-L).rolling(14,min_periods=1).mean()
    lv=lv.dropna(subset=["Date"])
    lv["Date"]=pd.to_datetime(lv["Date"]).dt.date
    return lv


def cpr_type(pct):
    if pct < 5: return "Very Narrow"
    if pct < 15: return "Narrow"
    if pct <= 35: return "Mid"
    return "Wide"


def expected_day(cpr_pct, pdc, tc, bc):
    inside = bc <= pdc <= tc
    above = pdc > tc
    if cpr_pct < 5:
        return "🚀 Explosive Trend (Bull)" if above else ("📉 Explosive Trend (Bear)" if not inside else "🔄 Explosive Breakout")
    if cpr_pct < 15:
        return "🟢 Trend Day (Bull)" if above else ("🔴 Trend Day (Bear)" if not inside else "🔄 Double Distribution")
    if cpr_pct <= 35:
        return "📊 Typical Day" if not inside else "🔄 Double Distribution"
    return "🔲 Range / Inside Day"


# ── V3.1 SCANNER ─────────────────────────────────────
def scan_v3(df, index_name, adr_pct_limit=40, body_filter=False):
    buf = INDEX_CONFIG[index_name]["buf"]
    signals = []
    for date in df["Date"].unique():
        day = df[df["Date"]==date]
        if len(day) < 4: continue
        r0 = day.iloc[0]
        adr = r0.get("ADR",1)
        if adr == 0: continue
        cpr_pct = r0.get("CPR_Width",0)/adr*100
        if cpr_pct > adr_pct_limit: continue
        cpr_cat = cpr_type(cpr_pct)
        pdh,pdl = r0["PDH"],r0["PDL"]
        r1,r2,r3 = r0["R1"],r0["R2"],r0["R3"]
        s1,s2,s3 = r0["S1"],r0["S2"],r0["S3"]
        pivot = r0["Pivot"]
        c1 = day.iloc[0]
        c2 = day.iloc[1] if len(day)>1 else None
        c1_range = c1["High"]-c1["Low"]
        c1_body = abs(c1["Close"]-c1["Open"])/c1_range*100 if c1_range>0 else 0
        signal = None

        sig_b = _check_trigger(c1,pdh,pdl,r1,r2,r3,s1,s2,s3,buf,"B",date,pivot)
        if sig_b:
            if body_filter and c1_body < 40: sig_b = None
            else: sig_b["Body_%"]=round(c1_body,2); signal=sig_b

        if signal is None and c2 is not None:
            sig_a = _check_trigger(c2,pdh,pdl,r1,r2,r3,s1,s2,s3,buf,"A",date,pivot)
            if sig_a: sig_a["Body_%"]=round(c1_body,2); signal=sig_a

        if signal:
            for k,v in {"CPR_%":cpr_pct,"CPR_Type":cpr_cat,"R1":r1,"R2":r2,"R3":r3,
                         "S1":s1,"S2":s2,"S3":s3,"PDH":pdh,"PDL":pdl,"Pivot":pivot,
                         "Top_CPR":r0["Top_CPR"],"Bot_CPR":r0["Bot_CPR"]}.items():
                signal[k] = round(v,2) if isinstance(v,(int,float)) else v
            signals.append(signal)
    return signals


def _check_trigger(candle,pdh,pdl,r1,r2,r3,s1,s2,s3,buf,scenario,date,pivot):
    close = candle["Close"]
    ts = candle.name.strftime("%H:%M") if hasattr(candle.name,"strftime") else str(candle.name)

    # ── BUY ──
    if close > pdh and close > r1:
        target = r3 if close > r2 else r2
        tlbl = "R3" if close > r2 else "R2"
        # FIX 1: Target must be ABOVE entry for BUY
        if target <= close: return None
        if scenario == "B":
            sl_o1 = (r2-buf) if close>r2 else (r1-buf)
            sl = min(sl_o1, pdh-buf)
        else:
            sl = candle["Low"]-buf
        risk = close-sl
        reward = target-close
        if risk<=0 or reward<=0: return None
        # FIX 2: R:R >= 1:1
        if reward/risk < 1.0: return None
        return {"Date":str(date),"Time":ts,"Type":"BUY","Scenario":scenario,
                "Entry":round(close,2),"SL":round(sl,2),"Target":round(target,2),
                "Target_Lvl":tlbl,"Risk_Pts":round(risk,2),"Reward_Pts":round(reward,2),
                "RR":round(reward/risk,2)}

    # ── SELL ──
    if close < pdl and close < s1:
        target = s3 if close < s2 else s2
        tlbl = "S3" if close < s2 else "S2"
        # FIX 1: Target must be BELOW entry for SELL
        if target >= close: return None
        if scenario == "B":
            sl_o1 = (s2+buf) if close<s2 else (s1+buf)
            sl = max(sl_o1, pdl+buf)
        else:
            sl = candle["High"]+buf
        risk = sl-close
        reward = close-target
        if risk<=0 or reward<=0: return None
        # FIX 2: R:R >= 1:1
        if reward/risk < 1.0: return None
        return {"Date":str(date),"Time":ts,"Type":"SELL","Scenario":scenario,
                "Entry":round(close,2),"SL":round(sl,2),"Target":round(target,2),
                "Target_Lvl":tlbl,"Risk_Pts":round(risk,2),"Reward_Pts":round(reward,2),
                "RR":round(reward/risk,2)}
    return None


# ── SIMULATOR ────────────────────────────────────────
def simulate(df, signals, index_name, premium=0):
    lot = INDEX_CONFIG[index_name]["lot"]
    results = []
    for sig in signals:
        date,etime = sig["Date"],sig["Time"]
        entry,sl,target = sig["Entry"],sig["SL"],sig["Target"]
        side = sig["Type"]
        day = df[df["Date"].astype(str)==date]
        if day.empty: continue
        try: ts = pd.Timestamp(f"{date} {etime}",tz=IST)
        except: continue
        post = day.loc[day.index>ts]
        if post.empty: continue
        exit_px,exit_rsn,exit_time = entry,"EOD",etime
        for idx_t,bar in post.iterrows():
            h,l = bar["High"],bar["Low"]
            t_str = idx_t.strftime("%H:%M") if hasattr(idx_t,"strftime") else ""
            if side=="BUY":
                if l<=sl: exit_px,exit_rsn,exit_time=sl,"SL Hit",t_str; break
                if h>=target: exit_px,exit_rsn,exit_time=target,"Target Hit",t_str; break
            else:
                if h>=sl: exit_px,exit_rsn,exit_time=sl,"SL Hit",t_str; break
                if l<=target: exit_px,exit_rsn,exit_time=target,"Target Hit",t_str; break
        else:
            eod = post[post.index.hour==15]
            exit_px = eod.iloc[0]["Close"] if not eod.empty else post.iloc[-1]["Close"]
            exit_rsn,exit_time = "EOD Exit",eod.index[0].strftime("%H:%M") if not eod.empty else post.index[-1].strftime("%H:%M")

        pnl_pts = round((exit_px-entry) if side=="BUY" else (entry-exit_px),2)
        try: dow=pd.Timestamp(date).day_name()
        except: dow=""
        results.append({
            "Date":date,"Day":dow,"Time":etime,"Type":side,"Scenario":sig["Scenario"],
            "Entry":round(entry,2),"SL":round(sl,2),"Target":round(target,2),
            "Target_Lvl":sig["Target_Lvl"],"Exit":round(exit_px,2),"Exit Time":exit_time,
            "Exit Reason":exit_rsn,"P&L Pts":pnl_pts,"P&L ₹":round(pnl_pts*lot,2),
            "Risk Pts":sig["Risk_Pts"],"RR":sig["RR"],
            "Fut Entry":round(entry+premium,2),"Fut Exit":round(exit_px+premium,2),
            "CPR_%":sig["CPR_%"],"CPR_Type":sig["CPR_Type"],"Body_%":sig.get("Body_%",0),
            "Success":pnl_pts>0,
        })
    return results


def performance_report(tdf, lot_size=1):
    if tdf.empty: return {}
    n=len(tdf); w=int(tdf["Success"].sum()); l=n-w; wr=w/n*100
    avg_w=tdf.loc[tdf["Success"],"P&L Pts"].mean() if w else 0
    avg_l=tdf.loc[~tdf["Success"],"P&L Pts"].mean() if l else 0
    exp=(wr/100*avg_w)+((1-wr/100)*avg_l)
    ls=tdf.loc[~tdf["Success"],"P&L Pts"].sum()
    pf=abs(tdf.loc[tdf["Success"],"P&L Pts"].sum()/ls) if ls!=0 else float("inf")
    cum=tdf["P&L Pts"].cumsum(); dd=(cum-cum.cummax()).min()
    return {"Total Trades":n,"Winners":w,"Losers":l,"Win Rate %":round(wr,1),
            "Avg Win":round(avg_w,2),"Avg Loss":round(avg_l,2),
            "Expectancy":round(exp,2),
            "Profit Factor":round(pf,2) if pf!=float("inf") else "∞",
            "Total P&L Pts":round(tdf["P&L Pts"].sum(),2),
            "Total P&L ₹":round(tdf["P&L ₹"].sum(),2),
            "Max DD Pts":round(dd,2)}


# ── BATCH LIVE SCANNER ───────────────────────────────
def scan_live_batch(category="Indices Only", adr_limit=15, progress_cb=None):
    results = []
    # Always scan indices
    idx_results = _scan_indices(adr_limit)
    results.extend(idx_results)

    stocks = STOCK_CATS.get(category, [])
    if stocks:
        tickers = [f"{s}.NS" for s in stocks]
        total = len(tickers)
        batch_sz = 20
        for i in range(0, total, batch_sz):
            batch = tickers[i:i+batch_sz]
            if progress_cb: progress_cb((i+len(batch))/total, f"Scanning {i+len(batch)}/{total}...")
            try:
                tkr_str = " ".join(batch)
                data = yf.download(tkr_str, period="5d", interval="1d", progress=False, group_by="ticker")
                if data.empty: continue
                for t in batch:
                    sym = t.replace(".NS","")
                    try:
                        if len(batch)==1:
                            sdf = data.copy()
                        else:
                            sdf = data[t] if t in data.columns.get_level_values(0) else None
                        if sdf is None or sdf.empty: continue
                        if isinstance(sdf.columns, pd.MultiIndex):
                            sdf.columns = sdf.columns.get_level_values(0)
                        sdf = sdf.dropna(subset=["Close"])
                        if len(sdf)<2: continue
                        prev = sdf.iloc[-2]; curr = sdf.iloc[-1]
                        H,L,C = prev["High"],prev["Low"],prev["Close"]
                        pv=(H+L+C)/3; bc_v=(H+L)/2; tc_v=2*pv-bc_v
                        tc_f,bc_f=max(tc_v,bc_v),min(tc_v,bc_v)
                        cw=tc_f-bc_f
                        dr=H-L; adr_v=dr  # single day approx
                        cpct=cw/adr_v*100 if adr_v>0 else 0
                        results.append({
                            "Symbol":sym,"Price":round(curr["Close"],2),
                            "Pivot":round(pv,2),"TC":round(tc_f,2),"BC":round(bc_f,2),
                            "CPR Width":round(cw,2),"CPR %ADR":round(cpct,1),
                            "CPR Type":cpr_type(cpct),
                            "PDH":round(H,2),"PDL":round(L,2),
                            "R1":round(2*pv-L,2),"S1":round(2*pv-H,2),
                        })
                    except: continue
            except: continue
    return results


def _scan_indices(adr_limit):
    results = []
    for name,cfg in INDEX_CONFIG.items():
        try:
            data = yf.download(cfg["ticker"],period="30d",interval="1d",progress=False)
            if data.empty: continue
            if isinstance(data.columns, pd.MultiIndex):
                data.columns = data.columns.get_level_values(0)
            data = data.dropna(subset=["Close"])
            if len(data)<2: continue
            prev=data.iloc[-2]; curr=data.iloc[-1]
            H,L,C=prev["High"],prev["Low"],prev["Close"]
            pv=(H+L+C)/3; bc_v=(H+L)/2; tc_v=2*pv-bc_v
            tc_f,bc_f=max(tc_v,bc_v),min(tc_v,bc_v)
            cw=tc_f-bc_f
            adr_s=data["High"]-data["Low"]; adr_v=adr_s.rolling(14,min_periods=1).mean().iloc[-1]
            cpct=cw/adr_v*100 if adr_v>0 else 0
            pdc=C
            exp_day=expected_day(cpct,pdc,tc_f,bc_f)
            results.append({
                "Symbol":name,"Price":round(curr["Close"],2),
                "Pivot":round(pv,2),"TC":round(tc_f,2),"BC":round(bc_f,2),
                "CPR Width":round(cw,2),"CPR %ADR":round(cpct,1),
                "CPR Type":cpr_type(cpct),"Expected Day":exp_day,
                "PDH":round(H,2),"PDL":round(L,2),
                "R1":round(2*pv-L,2),"S1":round(2*pv-H,2),
            })
        except: continue
    return results
