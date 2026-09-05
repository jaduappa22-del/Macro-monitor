from datetime import datetime
import json
import streamlit as st
import yfinance as yf

st.set_page_config(
    page_title="Global Macro Intelligence Terminal",
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
          "Copper (구리)": "HG=F",
          "Crude Oil WTI (WTI 원유)": "CL=F",
          "Crude Oil Brent (브렌트유)": "BZ=F",
          "Natural Gas (천연가스)": "NG=F",
      },
      "🚢 해운 물류 운임 지수 (Freight Rates)": {
          "Baltic Dry Index (BDI 해운운임)": "^BDI",
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
<html lang="ko" class="dark">
<head>
    <meta charset="UTF-8">
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <script>
        tailwind.config = {{
            darkMode: 'class',
        }}
        function toggleTheme() {{
            const html = document.documentElement;
            if (html.classList.contains('dark')) {{
                html.classList.remove('dark');
                document.getElementById('theme-btn').innerText = '🌙 다크 모드';
            }} else {{
                html.classList.add('dark');
                document.getElementById('theme-btn').innerText = '☀️ 라이트 모드';
            }}
        }}

        function calculateImpact() {{
            const baseBudget = parseFloat(document.getElementById('annual-budget').value) || 100;
            const fxChange = parseFloat(document.getElementById('fx-slider').value) || 0;
            const rawChange = parseFloat(document.getElementById('raw-slider').value) || 0;
            
            document.getElementById('fx-val-text').innerText = fxChange + '%';
            document.getElementById('raw-val-text').innerText = rawChange + '%';

            const totalImpactPct = (fxChange * 0.6) + (rawChange * 0.4);
            const impactedAmount = baseBudget * (totalImpactPct / 100);
            
            let resultText = `예산 변동 폭: 약 <b>${{impactedAmount >= 0 ? '+' : ''}}{{impactedAmount.toFixed(2)}}억 원</b> (${{totalImpactPct.toFixed(1)}}% 영향)`;
            document.getElementById('simulation-result').innerHTML = resultText;
        }}
    </script>
</head>
<body class="bg-slate-100 dark:bg-gray-950 text-slate-900 dark:text-gray-100 font-mono antialiased p-8 min-h-screen transition-colors duration-300 text-sm">
    
    <!-- 상단 헤더 -->
    <header class="flex flex-col md:flex-row justify-between items-start md:items-center border-b border-slate-300 dark:border-gray-800 pb-5 mb-8 gap-4">
        <div>
            <h1 class="text-3xl font-black tracking-wider text-emerald-600 dark:text-emerald-400">⚡ GLOBAL MACRO INTELLIGENCE TERMINAL</h1>
            <p class="text-sm text-slate-600 dark:text-gray-400 mt-1 font-semibold">Advanced Procurement & Negotiation Analytics Desk</p>
        </div>
        <div class="flex items-center gap-4">
            <button id="theme-btn" onclick="toggleTheme()" class="px-4 py-2 bg-slate-200 dark:bg-gray-800 hover:bg-slate-300 dark:hover:bg-gray-700 text-xs font-bold rounded-xl transition shadow-sm">
                ☀️ 라이트 모드
            </button>
            <div class="text-right hidden sm:block">
                <span class="px-3 py-1 bg-emerald-100 dark:bg-emerald-950 border border-emerald-400 dark:border-emerald-800 text-emerald-800 dark:text-emerald-400 text-xs rounded-lg font-extrabold">LIVE SYSTEM</span>
                <p class="text-xs text-slate-500 dark:text-gray-400 mt-1.5">Refreshed: {update_time}</p>
            </div>
        </div>
    </header>

    <!-- [1] 구매 예산 시뮬레이터 -->
    <div class="mb-10 bg-white dark:bg-gray-900 border-2 border-slate-300 dark:border-emerald-500/40 rounded-2xl p-6 shadow-2xl transition-colors">
        <div class="flex items-center justify-between border-b border-slate-200 dark:border-gray-800 pb-3 mb-4">
            <h2 class="text-base font-extrabold text-emerald-600 dark:text-emerald-400 uppercase tracking-wide">🧮 Procurement Cost Impact Simulator</h2>
            <span class="text-xs text-slate-500 dark:text-gray-400 font-bold">환율 및 원자재 변동 예산 예측</span>
        </div>
        <div class="grid grid-cols-1 md:grid-cols-3 gap-6 items-center">
            <div>
                <label class="block text-xs font-bold text-slate-700 dark:text-gray-300 mb-2">연간 총 구매 예산 (억원)</label>
                <input type="number" id="annual-budget" value="100" oninput="calculateImpact()" class="w-full bg-slate-50 dark:bg-gray-950 border border-slate-300 dark:border-gray-700 rounded-xl px-4 py-2.5 text-base font-bold text-slate-900 dark:text-white focus:outline-none focus:border-emerald-500">
            </div>
            <div>
                <label class="block text-xs font-bold text-slate-700 dark:text-gray-300 mb-2">환율(USD/KRW) 변동: <span id="fx-val-text" class="text-emerald-600 dark:text-emerald-400 font-extrabold">0%</span></label>
                <input type="range" id="fx-slider" min="-20" max="20" value="0" step="1" oninput="calculateImpact()" class="w-full accent-emerald-500 cursor-pointer">
            </div>
            <div>
                <label class="block text-xs font-bold text-slate-700 dark:text-gray-300 mb-2">원자재(구리 등) 변동: <span id="raw-val-text" class="text-emerald-600 dark:text-emerald-400 font-extrabold">0%</span></label>
                <input type="range" id="raw-slider" min="-30" max="30" value="0" step="1" oninput="calculateImpact()" class="w-full accent-emerald-500 cursor-pointer">
            </div>
        </div>
        <div class="mt-5 p-4 bg-slate-100 dark:bg-gray-950/80 rounded-xl border border-slate-200 dark:border-gray-800 flex justify-between items-center">
            <span class="text-xs font-bold text-slate-600 dark:text-gray-400">💡 시뮬레이션 결과 예측</span>
            <div id="simulation-result" class="text-sm font-bold text-slate-900 dark:text-white">예산 변동 폭: <b>0.00억 원</b> (0.0% 영향)</div>
        </div>
    </div>

    <!-- [2] AI 교섭 전략 및 자동 인사이트 매트릭스 -->
    <div class="mb-10 bg-white dark:bg-gray-900 border border-slate-300 dark:border-gray-800 rounded-2xl p-6 shadow-xl transition-colors">
        <div class="flex items-center justify-between border-b border-slate-200 dark:border-gray-800 pb-3 mb-4">
            <h2 class="text-base font-extrabold text-emerald-600 dark:text-emerald-400 uppercase tracking-wide">🎯 AI Procurement & Negotiation Insight Engine</h2>
            <span class="text-xs text-slate-500 dark:text-gray-400 font-bold">3개월 평균선 기준 원가 리스크 분석</span>
        </div>
        <div class="grid grid-cols-1 md:grid-cols-3 gap-5">
            <div class="bg-slate-50 dark:bg-gray-950/60 border border-slate-200 dark:border-gray-800 p-4 rounded-xl">
                <span class="text-sm font-extrabold text-amber-600 dark:text-amber-400 block mb-1">💱 환율 리스크 (USD/KRW)</span>
                <p class="text-xs text-slate-700 dark:text-gray-300 leading-relaxed">현재 환율: <b>{fx_val:,.2f}원</b>. { "1,350원 상회로 수입단가 상승 압박. 네고 분산 필요" if fx_val >= 1350 else "1,350원 하회로 안정 국면. 대금 결제 유리" }</p>
            </div>
            <div class="bg-slate-50 dark:bg-gray-950/60 border border-slate-200 dark:border-gray-800 p-4 rounded-xl">
                <span class="text-sm font-extrabold text-sky-600 dark:text-sky-400 block mb-1">🛠️ 원자재 닥터코퍼 (Copper)</span>
                <p class="text-xs text-slate-700 dark:text-gray-300 leading-relaxed">현재가: <b>{copper_val:,.2f}</b>. 제조업 부품 및 전선류 공급사 단가 인상 요구 시 3개월 평균선 비교 방어 논리 제공.</p>
            </div>
            <div class="bg-slate-50 dark:bg-gray-950/60 border border-slate-200 dark:border-gray-800 p-4 rounded-xl">
                <span class="text-sm font-extrabold text-emerald-600 dark:text-emerald-400 block mb-1">📈 차트 보조선 가이드</span>
                <p class="text-xs text-slate-700 dark:text-gray-300 leading-relaxed">모든 자산 카드 내의 <b>점선</b>은 최근 3개월 평균 가격입니다. 현재가가 평균선 위에 있으면 고점 주의, 아래면 저점 기회입니다.</p>
            </div>
        </div>
    </div>

    <!-- [3] 개선된 히트맵 매트릭스 (시인성 대폭 강화) -->
    <div class="mb-10 bg-white dark:bg-gray-900 border border-slate-300 dark:border-gray-800 rounded-2xl p-6 shadow-xl transition-colors">
        <h2 class="text-base font-extrabold text-emerald-600 dark:text-emerald-400 uppercase tracking-wider border-b border-slate-200 dark:border-gray-800 pb-3 mb-5">🔥 Macro Asset Performance Heatmap (3M Change Matrix)</h2>
        <div id="heatmap-container" class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-3"></div>
    </div>

    <!-- [4] 카테고리별 완벽 분리된 구역 덱 -->
    <div class="space-y-12" id="dashboard-container"></div>

    <script>
        const rawData = {data_json};
        const summaryData = {summary_json};
        
        // 히트맵 렌더링 (가독성 및 폰트 크기 업그레이드)
        const heatmapContainer = document.getElementById('heatmap-container');
        summaryData.forEach(item => {{
            let isUp = item.change_rate >= 0;
            let bgHeat = isUp ? 'bg-red-100 dark:bg-red-950/60 border-red-300 dark:border-red-800 text-red-800 dark:text-red-200' : 'bg-blue-100 dark:bg-blue-950/60 border-blue-300 dark:border-blue-800 text-blue-800 dark:text-blue-200';
            let sign = isUp ? '+' : '';
            
            let cell = document.createElement('div');
            cell.className = `p-4 rounded-xl border-2 ${{bgHeat}} flex flex-col justify-between transition-colors shadow-md`;
            cell.innerHTML = `
                <span class="text-xs font-black truncate" title="${{item.name}}">${{item.name}}</span>
                <div class="flex justify-between items-end mt-3">
                    <span class="text-sm font-extrabold">${{item.current.toLocaleString()}}</span>
                    <span class="text-xs font-black px-1.5 py-0.5 rounded bg-black/10 dark:bg-white/10">${{sign}}${{item.change_rate}}%</span>
                </div>
            `;
            heatmapContainer.appendChild(cell);
        }});

        // 카테고리별 완벽 분리 카드 덱 렌더링
        const container = document.getElementById('dashboard-container');
        let catIndex = 0;

        for (const [category, items] of Object.entries(rawData)) {{
            // 카테고리별 독립된 컨테이너 박스 생성
            let sectionCard = document.createElement('div');
            sectionCard.className = "bg-white dark:bg-gray-900 border-2 border-slate-300 dark:border-gray-800 rounded-3xl p-6 shadow-xl transition-colors";
            
            let sectionHeader = document.createElement('div');
            sectionHeader.className = "border-b-2 border-slate-200 dark:border-gray-800 pb-4 mb-6";
            sectionHeader.innerHTML = `<h2 class="text-xl font-black text-emerald-600 dark:text-emerald-300 tracking-wide">${{category}}</h2>`;
            sectionCard.appendChild(sectionHeader);

            let grid = document.createElement('div');
            grid.className = "grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6";
            
            let itemIndex = 0;
            for (const [name, info] of Object.entries(items)) {{
                let canvasId = `chart-${{itemIndex}}-${{catIndex}}`;
                let isUp = info.change_rate >= 0;
                let badgeClass = isUp ? "bg-red-100 dark:bg-red-950 text-red-800 dark:text-red-400 border border-red-300 dark:border-red-900" : "bg-blue-100 dark:bg-blue-950 text-blue-800 dark:text-blue-400 border border-blue-300 dark:border-blue-900";
                let sign = info.change_rate > 0 ? "+" : "";
                
                let vsAvg = info.current >= info.avg_3m ? "⚠️ 평균선 상단" : "✨ 평균선 하단";
                let vsAvgColor = info.current >= info.avg_3m ? "text-amber-600 dark:text-amber-400 font-extrabold" : "text-emerald-600 dark:text-emerald-400 font-extrabold";

                let card = document.createElement('div');
                card.className = "bg-slate-50 dark:bg-gray-950 border border-slate-200 dark:border-gray-800 p-5 rounded-2xl flex flex-col justify-between hover:border-emerald-500 transition shadow-md";
                card.innerHTML = `
                    <div>
                        <div class="flex justify-between items-start">
                            <h3 class="text-xs font-bold text-slate-700 dark:text-gray-300 truncate w-3/4" title="${{name}}">${{name}}</h3>
                            <span class="text-xs px-2 py-0.5 rounded-md font-extrabold ${{badgeClass}}">${{sign}}${{info.change_rate}}%</span>
                        </div>
                        <div class="mt-3 flex items-baseline justify-between">
                            <span class="text-2xl font-black tracking-tight text-slate-900 dark:text-white">${{info.current.toLocaleString()}}</span>
                            <span class="text-xs ${{vsAvgColor}}">${{vsAvg}}</span>
                        </div>
                        <div class="text-xs text-slate-500 dark:text-gray-400 mt-1 font-semibold">3M Avg: ${{info.avg_3m.toLocaleString()}}</div>
                    </div>
                    <div class="mt-4 h-20 w-full relative"><canvas id="${{canvasId}}"></canvas></div>
                    <div class="mt-3 flex justify-between text-xs text-slate-500 dark:text-gray-400 border-t border-slate-200 dark:border-gray-800/80 pt-2 font-medium">
                        <span>Start: ${{info.dates.length > 0 ? info.dates[0] : 'N/A'}}</span>
                        <span>End: ${{info.dates.length > 0 ? info.dates[info.dates.length-1] : 'N/A'}}</span>
                    </div>
                `;
                grid.appendChild(card);
                itemIndex++;
            }}
            sectionCard.appendChild(grid);
            container.appendChild(sectionCard);
            catIndex++;
        }}

        // Chart.js 렌더링
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
                                        borderWidth: 2.5,
                                        pointRadius: 0,
                                        pointHoverRadius: 5,
                                        tension: 0.1,
                                        fill: false
                                    }},
                                    {{
                                        label: '3M Avg',
                                        data: info.avg_line,
                                        borderColor: '#fbbf24',
                                        borderWidth: 2,
                                        borderDash: [5, 5],
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

st.components.v1.html(html_template, height=2200, scrolling=True)
