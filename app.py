from datetime import datetime
import json
import streamlit as st
import yfinance as yf

st.set_page_config(
    page_title="Global Macro Terminal - Advanced Procurement",
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
      "💱 환율 (Foreign Exchange)": {
          "USD/KRW (원/달러)": "KRW=X",
          "JPY/KRW (원/엔)": "JPYKRW=X",
          "EUR/KRW (원/유로)": "EURKRW=X",
          "USD/JPY (엔/달러)": "JPY=X",
      },
  }

  categorized_data = {}
  summary_flat_list = []
  fx_usd_krw = 0.0
  copper_price = 0.0

  for category, tickers in categories.items():
    categorized_data[category] = {}
    for name, ticker in tickers.items():
      dates, prices, cur, rate, avg_3m = [], [], 0.0, 0.0, 0.0
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
            avg_3m = sum(prices) / len(prices) if prices else cur

            if "USD/KRW" in name:
              fx_usd_krw = cur
            elif "Copper" in name:
              copper_price = cur
      except:
        pass

      item_payload = {
          "name": name,
          "category": category,
          "current": round(cur, 2),
          "change_rate": round(rate, 2),
          "avg_3m": round(avg_3m, 2),
          "dates": dates,
          "sparkline": [round(p, 2) for p in prices],
          "avg_line": [round(avg_3m, 2)] * len(prices),
      }

      categorized_data[category][name] = item_payload
      summary_flat_list.append(item_payload)

  return categorized_data, summary_flat_list, fx_usd_krw, copper_price


market_data, summary_list, fx_val, copper_val = fetch_market_data()
update_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S KST")
data_json = json.dumps(market_data)
summary_json = json.dumps(summary_list)

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
            <h1 class="text-2xl font-black tracking-wider text-emerald-400">⚡ GLOBAL MACRO INTELLIGENCE TERMINAL</h1>
            <p class="text-xs text-gray-400 mt-1">Advanced Procurement & Negotiation Analytics Desk</p>
        </div>
        <div class="text-right">
            <span class="px-2.5 py-1 bg-emerald-950 border border-emerald-800 text-emerald-400 text-xs rounded font-bold">LIVE SYSTEM</span>
            <p class="text-xs text-gray-400 mt-1">Refreshed: {update_time}</p>
        </div>
    </header>

    <!-- [1] 실무 교섭 전략 및 자동 인사이트 매트릭스 -->
    <div class="mb-8 bg-gray-900 border border-emerald-500/30 rounded-xl p-4 shadow-xl">
        <div class="flex items-center justify-between border-b border-gray-800 pb-2 mb-3">
            <h2 class="text-xs font-bold text-emerald-400 uppercase tracking-wider">🎯 AI Procurement & Negotiation Insight Engine</h2>
            <span class="text-[10px] text-gray-400">3개월 평균선 기준 원가 리스크 자동 분석</span>
        </div>
        <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div class="bg-gray-950/60 border border-gray-800 p-3 rounded-lg">
                <span class="text-xs font-bold text-amber-400">💱 환율 리스크 (USD/KRW)</span>
                <p class="text-xs text-gray-300 mt-1">현재 환율: <b>{fx_val:,.2f}원</b>. { "1,350원 상회로 수입단가 상승 압박. 네고 분산 필요" if fx_val >= 1350 else "1,350원 하회로 안정 국면. 대금 결제 유리" }</p>
            </div>
            <div class="bg-gray-950/60 border border-gray-800 p-3 rounded-lg">
                <span class="text-xs font-bold text-sky-400">🛠️ 원자재 닥터코퍼 (Copper)</span>
                <p class="text-xs text-gray-300 mt-1">현재가: <b>{copper_val:,.2f}</b>. 제조업 부품 및 전선류 공급사 단가 인상 요구 시 3개월 평균선 비교 방어 논리 제공.</p>
            </div>
            <div class="bg-gray-950/60 border border-gray-800 p-3 rounded-lg">
                <span class="text-xs font-bold text-emerald-400">📈 차트 보조선 가이드</span>
                <p class="text-xs text-gray-300 mt-1">모든 자산 카드 내의 <b>주황색 점선</b>은 최근 3개월 평균 가격입니다. 현재가가 평균선 위에 있으면 고점 주의, 아래면 저점 기회입니다.</p>
            </div>
        </div>
    </div>

    <!-- [2] 글로벌 자산 히트맵 매트릭스 (Heatmap Summary) -->
    <div class="mb-10 bg-gray-900 border border-gray-800 rounded-xl p-4 shadow-xl">
        <h2 class="text-xs font-bold text-emerald-400 uppercase tracking-wider border-b border-gray-800 pb-2 mb-4">🔥 Macro Asset Performance Heatmap (3M Change Matrix)</h2>
        <div id="heatmap-container" class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-2"></div>
    </div>

    <!-- [3] 카테고리별 상세 스파크라인 카드 덱 (3개월 평균선 포함) -->
    <div class="space-y-10" id="dashboard-container"></div>

    <script>
        const rawData = {data_json};
        const summaryData = {summary_json};
        
        // 1. 히트맵 렌더링
        const heatmapContainer = document.getElementById('heatmap-container');
        summaryData.forEach(item => {{
            let isUp = item.change_rate >= 0;
            // 히트맵 컬러 클래스 (상승은 붉은계열/초록계열 선택 - 여기선 상승 빨강, 하락 파랑 금융 스타일)
            let bgHeat = isUp ? 'bg-red-950/40 border-red-900/60 text-red-300' : 'bg-blue-950/40 border-blue-900/60 text-blue-300';
            let sign = isUp ? '+' : '';
            
            let cell = document.createElement('div');
            cell.className = `p-2.5 rounded border ${{bgHeat}} flex flex-col justify-between`;
            cell.innerHTML = `
                <span class="text-[11px] font-semibold truncate" title="${{item.name}}">${{item.name}}</span>
                <div class="flex justify-between items-end mt-2">
                    <span class="text-xs font-bold">${{item.current.toLocaleString()}}</span>
                    <span class="text-[10px] font-black">${{sign}}${{item.change_rate}}%</span>
                </div>
            `;
            heatmapContainer.appendChild(cell);
        }});

        // 2. 카테고리별 카드 및 차트 렌더링
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
                
                // 3개월 평균 대비 현재가 상태 판단
                let vsAvg = info.current >= info.avg_3m ? "⚠️ 평균선 상단 (고점 부근)" : "✨ 평균선 하단 (저점 기회)";
                let vsAvgColor = info.current >= info.avg_3m ? "text-amber-400" : "text-emerald-400";

                let card = document.createElement('div');
                card.className = "bg-gray-900 border border-gray-800 p-4 rounded-xl flex flex-col justify-between hover:border-emerald-500/50 transition shadow-lg";
                card.innerHTML = `
                    <div>
                        <div class="flex justify-between items-start">
                            <h3 class="text-xs font-semibold text-gray-400 truncate w-3/4" title="${{name}}">${{name}}</h3>
                            <span class="text-xs px-1.5 py-0.5 rounded font-bold ${{badgeClass}}">${{sign}}${{info.change_rate}}%</span>
                        </div>
                        <div class="mt-2 flex items-baseline justify-between">
                            <span class="text-xl font-black tracking-tight text-white">${{info.current.toLocaleString()}}</span>
                            <span class="text-[10px] ${{vsAvgColor}} font-bold">${{vsAvg}}</span>
                        </div>
                        <div class="text-[10px] text-gray-500 mt-0.5">3M Avg: ${{info.avg_3m.toLocaleString()}}</div>
                    </div>
                    <div class="mt-3 h-16 w-full relative"><canvas id="${{canvasId}}"></canvas></div>
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

        // 3. Chart.js 스파크라인 및 3개월 평균 수평선(점선) 주입
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
                                datasets: [
                                    {{
                                        label: 'Price',
                                        data: info.sparkline,
                                        borderColor: isUp ? '#f87171' : '#60a5fa',
                                        borderWidth: 2,
                                        pointRadius: 0,
                                        pointHoverRadius: 4,
                                        tension: 0.1,
                                        fill: false
                                    }},
                                    {{
                                        label: '3M Avg',
                                        data: info.avg_line,
                                        borderColor: '#fbbf24', // 주황/노란색 점선 (3개월 평균선)
                                        borderWidth: 1.5,
                                        borderDash: [4, 4],
                                        pointRadius: 0,
                                        fill: false
                                    }}
                                ]
                            }},
                            options: {{
                                responsive: true, maintainAspectRatio: false,
                                plugins: {{
                                    legend: {{ display: false }},
                                    tooltip: {{
                                        enabled: true, mode: 'index', intersect: false,
                                        callbacks: {{
                                            title: ctx => ctx[0].label,
                                            label: ctx => ` ${{ctx.dataset.label}}: ${{ctx.raw.toLocaleString()}}`
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

st.components.v1.html(html_template, height=1700, scrolling=True)
