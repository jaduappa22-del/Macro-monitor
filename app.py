import streamlit as st
import yfinance as yf
from datetime import datetime
import json

st.set_page_config(
    page_title="Global Macro Terminal",
    page_icon="⚡",
    layout="wide"
)

def fetch_market_data():
    categories = {
        "🏷️ 원자재 & 에너지 (Commodities & Energy)": {
            "Gold (금)": "GC=F",
            "Silver (은)": "SI=F",
            "Copper (구리)": "HG=F",
            "Crude Oil WTI (WTI 원유)": "CL=F",
            "Crude Oil Brent (브렌트유)": "BZ=F",
            "Natural Gas (천연가스)": "NG=F"
        },
        "🇺🇸 미국 시장 & 국채 (US Markets)": {
            "S&P 500": "^GSPC",
            "NASDAQ": "^IXIC",
            "Dow Jones": "^DJI",
            "US 10Y Treasury (미국 10년물)": "^TNX"
        },
        "🇰🇷 한국 시장 (Korea Markets)": {
            "KOSPI": "^KS11",
            "KOSDAQ": "^KQ11"
        },
        "🪙 크립토 (Crypto)": {
            "Bitcoin (비트코인)": "BTC-USD",
            "Ethereum (이더리움)": "ETH-USD"
        },
        "💱 환율 (Foreign Exchange)": {
            "USD/KRW (원/달러)": "KRW=X",
            "JPY/KRW (원/엔)": "JPYKRW=X",
            "EUR/KRW (원/유로)": "EURKRW=X"
        }
    }
    
    categorized_data = {}
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
            except:
                pass
            
            categorized_data[category][name] = {
                "current": round(cur, 2),
                "change_rate": round(rate, 2),
                "dates": dates,
                "sparkline": [round(p, 2) for p in prices]
            }
    return categorized_data

market_data = fetch_market_data()
update_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S KST")
data_json = json.dumps(market_data)

html_template = f"""
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
</head>
<body class="bg-gray-950 text-gray-100 font-mono antialiased p-6 min-h-screen">
    <header class="flex justify-between items-center border-b border-gray-800 pb-4 mb-8">
        <div>
            <h1 class="text-2xl font-black tracking-wider text-emerald-400">⚡ GLOBAL MACRO TERMINAL</h1>
            <p class="text-xs text-gray-400 mt-1">Institutional Grade Market Intelligence Dashboard</p>
        </div>
        <div class="text-right">
            <span class="px-2.5 py-1 bg-emerald-950 border border-emerald-800 text-emerald-400 text-xs rounded font-bold">LIVE SYSTEM</span>
            <p class="text-xs text-gray-400 mt-1">Refreshed: {update_time}</p>
        </div>
    </header>

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

st.components.v1.html(html_template, height=1400, scrolling=True)
