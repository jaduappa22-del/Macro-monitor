from datetime import datetime
import json
import streamlit as st
import yfinance as yf

st.set_page_config(
    page_title="Global Macro Terminal - Procurement Edition",
    page_icon="⚡",
    layout="wide",
)


def fetch_market_data():
  categories = {
      "🏷️ 원자재 & 에너지 (Commodities & Energy)": {
          "Gold (금)": "GC=F",
          "Silver (은)": "SI=F",
          "Palladium (팔라듐)": "PA=F",
          "Platinum (백금)": "PL=F",
          "Tin (주석)": "SISI=F",
          "Copper (구리)": "HG=F",
          "Crude Oil WTI (WTI 원유)": "CL=F",
          "Crude Oil Brent (브렌트유)": "BZ=F",
          "Dubai Oil (두바이유)": "DUBA=F",
          "Natural Gas (천연가스)": "NG=F",
      },
      "🇺🇸 미국 시장 & 국채 (US Markets)": {
          "S&P 500": "^GSPC",
          "NASDAQ": "^IXIC",
          "Dow Jones": "^DJI",
          "US 10Y Treasury (미국 10년물)": "^TNX",
      },
      "🇰🇷 한국 시장 (Korea Markets)": {
          "KOSPI": "^KS11",
          "KOSDAQ": "^KQ11",
          "Samsung Electronics (삼성전자)": "005930.KS",
          "SK Hynix (SK하이닉스)": "000660.KS",
          "LG Electronics (LG전자)": "066570.KS",
      },
      "🪙 크립토 (Crypto)": {
          "Bitcoin (비트코인)": "BTC-USD",
          "Ethereum (이더리움)": "ETH-USD",
          "Solana (솔라나)": "SOL-USD",
          "Sui (수이)": "SUI20947-USD",
      },
      "💱 환율 (Foreign Exchange)": {
          "USD/KRW (원/달러)": "KRW=X",
          "JPY/KRW (원/엔)": "JPYKRW=X",
          "EUR/KRW (원/유로)": "EURKRW=X",
          "USD/JPY (엔/달러)": "JPY=X",
      },
  }

  categorized_data = {}
  fx_usd_krw = 0.0
  copper_price = 0.0

  for category, tickers in categories.items():
    categorized_data[category] = {}
    for name, ticker in tickers.items():
      dates, prices, cur, rate = [], [], 0.0, 0.0
      try:
        tk = yf.Ticker(ticker)
        df = tk.history(period="3mo")
        if df is not None and not df.empty and "Close" in df:
          series = df["Close"].dropna()
          if not series.empty:
            dates = [d.strftime("%Y-%m-%d") for d in series.index]
            prices = [float(p) for p in series.tolist()]
            cur = prices[-1]
            prev = prices[-2] if len(prices) >= 2 else cur
            rate = ((cur - prev) / prev) * 100 if prev != 0 else 0.0

            # 주요 구매 지표 캐치
            if "USD/KRW" in name:
              fx_usd_krw = cur
            elif "Copper" in name:
              copper_price = cur
      except:
        pass

      categorized_data[category][name] = {
          "current": round(cur, 2),
          "change_rate": round(rate, 2),
          "dates": dates,
          "sparkline": [round(p, 2) for p in prices],
      }

  return categorized_data, fx_usd_krw, copper_price


market_data, fx_val, copper_val = fetch_market_data()
update_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S KST")
data_json = json.dumps(market_data)

# 구매/교섭팀을 위한 실시간 인사이트 로직 생성
procurement_advice = []
if fx_val > 0:
  if fx_val >= 1350:
    procurement_advice.append({
        "type": "danger",
        "title": f"원/달러 환율 경보 ({fx_val:,.2f}원)",
        "desc": (
            " 수입 원가 상승 압박이 큽니다. 외화 결제 건은 네고 타이밍을"
            " 조율하거나 환헤지 전략을 검토하세요."
        ),
    })
  else:
    procurement_advice.append({
        "type": "safe",
        "title": f"원/달러 환율 안정권 ({fx_val:,.2f}원)",
        "desc": (
            " 기준선(1,350원) 아래에서 안정세를 보이고 있어 수입 대금 결제에"
            " 유리한 국면입니다."
        ),
    })

if copper_val > 0:
  procurement_advice.append({
        "type": "info",
        "title": f"닥터 코퍼(구리) 시세 동향 ({copper_val:,.2f})",
        "desc": (
            " 전선·부품 소재 공급사와의 단가 인상/인하 교섭 시 원자재 추이"
            " 근거 자료로 활용하십시오."
        ),
    })

html_template = f"""
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
</head>
<body class="bg-gray-950 text-gray-100 font-mono antialiased p-6 min-h-screen">
    <header class="flex justify-between items-center border-b border-gray-800 pb-4 mb-6">
        <div>
            <h1 class="text-2xl font-black tracking-wider text-emerald-400">⚡ GLOBAL MACRO TERMINAL</h1>
            <p class="text-xs text-gray-400 mt-1">Procurement & Economic Intelligence Desk</p>
        </div>
        <div class="text-right">
            <span class="px-2.5 py-1 bg-emerald-950 border border-emerald-800 text-emerald-400 text-xs rounded font-bold">LIVE SYSTEM</span>
            <p class="text-xs text-gray-400 mt-1">Refreshed: {update_time}</p>
        </div>
    </header>

    <!-- [신규 추가] 자재구매팀 교섭 전략 및 원가 리스크 인사이트 패널 -->
    <div class="mb-8 bg-gray-900 border border-emerald-500/30 rounded-xl p-4 shadow-xl">
        <div class="flex items-center justify-between border-b border-gray-800 pb-2 mb-3">
            <h2 class="text-xs font-bold text-emerald-400 uppercase tracking-wider">🎯 Procurement Negotiation & Cost Action Matrix</h2>
            <span class="text-[10px] text-gray-400">구매 교섭 실무 가이드</span>
        </div>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div class="bg-gray-950/60 border border-gray-800 p-3 rounded-lg">
                <span class="text-xs font-bold text-amber-400">💡 환율 기반 결제 전략</span>
                <p class="text-xs text-gray-300 mt-1">현재 환율({fx_val:,.2f}원) 변동성에 따른 수입 부품 및 원자재 발주 시기 분산 검토 필요.</p>
            </div>
            <div class="bg-gray-950/60 border border-gray-800 p-3 rounded-lg">
                <span class="text-xs font-bold text-sky-400">🛡️ 공급사 단가 인상 방어 논리</span>
                <p class="text-xs text-gray-300 mt-1">원자재(금속·에너지) 스파크라인 트렌드를 바탕으로 공급사의 부당한 인상 요구에 대한 객관적 방어선 구축.</p>
            </div>
        </div>
    </div>

    <div class="space-y-10" id="dashboard-container"></div>

    <script>
        const rawData = {data_json};
        const container = document.getElementById('dashboard-container');
        let catIndex = 0;

        for (const [category, items] of Object.entries(rawData)) {{
            let section = document.createElement('section');
            section.innerHTML = `<h2 class="text-sm font-bold text-emerald-300 border-b border-gray-800 pb-2 mb-4 tracking-wide">${{category}}</h2>`;
            let grid = document.createElement('div');
            grid.className = "grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4";
            
            let itemIndex = 0;
            for (const [name, info] of Object.entries(items)) {{
                let canvasId = `chart-${{itemIndex}}-${{catIndex}}`;
                let isUp = info.change_rate >= 0;
                let badgeClass = isUp ? "bg-red-950 text-red-400 border border-red-900" : "bg-blue-950 text-blue-400 border border-blue-900";
                let sign = info.change_rate > 0 ? "+" : "";
                
                let card = document.createElement('div');
                card.className = "bg-gray-900 border border-gray-800 p-4 rounded-xl flex flex-col justify-between hover:border-emerald-500/50 transition shadow-lg";
                card.innerHTML = `
                    <div>
                        <div class="flex justify-between items-start">
                            <h3 class="text-xs font-semibold text-gray-400 truncate w-3/4" title="${{name}}">${{name}}</h3>
                            <span class="text-xs px-1.5 py-0.5 rounded font-bold ${{badgeClass}}">${{sign}}${{info.change_rate}}%</span>
                        </div>
                        <div class="mt-2 text-xl font-black tracking-tight text-white">${{info.current.toLocaleString()}}</div>
                    </div>
                    <div class="mt-4 h-16 w-full relative"><canvas id="${{canvasId}}"></canvas></div>
                    <div class="mt-2 flex justify-between text-[10px] text-gray-500 border-t border-gray-800/60 pt-1">
                        <span>Start: ${{info.dates.length > 0 ? info.dates[0] : 'N/A'}}</span>
                        <span>End: ${{info.dates.length > 0 ? info.dates[info.dates.length-1] : 'N/A'}}</span>
                    </div>
                `;
                grid.appendChild(card);
                itemIndex++;
            }}
            section.appendChild(grid);
            container.appendChild(section);
            catIndex++;
        }}

        setTimeout(() => {{
            let cIdx = 0;
            for (const [category, items] of Object.entries(rawData)) {{
                let iIdx = 0;
                for (const [name, info] of Object.entries(items)) {{
                    let canvasId = `chart-${{iIdx}}-${{cIdx}}`;
                    let ctx = document.getElementById(canvasId);
                    if (ctx && info.sparkline && info.sparkline.length > 0) {{
                        let isUp = info.change_rate >= 0;
                        new Chart(ctx.getContext('2d'), {{
                            type: 'line',
                            data: {{
                                labels: info.dates,
                                datasets: [{{
                                    data: info.sparkline,
                                    borderColor: isUp ? '#f87171' : '#60a5fa',
                                    borderWidth: 2,
                                    pointRadius: 0,
                                    pointHoverRadius: 4,
                                    pointHoverBackgroundColor: isUp ? '#f87171' : '#60a5fa',
                                    tension: 0.1,
                                    fill: false
                                }}]
                            }},
                            options: {{
                                responsive: true, maintainAspectRatio: false,
                                plugins: {{
                                    legend: {{ display: false }},
                                    tooltip: {{
                                        enabled: true, mode: 'index', intersect: false,
                                        callbacks: {{
                                            title: ctx => ctx[0].label,
                                            label: ctx => ` Price: ${{ctx.raw.toLocaleString()}}`
                                        }}
                                    }}
                                }},
                                scales: {{ x: {{ display: false }}, y: {{ display: false }} }},
                                interaction: {{ mode: 'nearest', axis: 'x', intersect: false }}
                            }}
                        }});
                    }}
                    iIdx++;
                }}
                cIdx++;
            }}
        }}, 400);
    </script>
</body>
</html>
"""

st.components.v1.html(html_template, height=1500, scrolling=True)
