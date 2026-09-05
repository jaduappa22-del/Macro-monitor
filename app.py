from datetime import datetime
import json
import streamlit as st
import yfinance as yf

st.set_page_config(
    page_title="Global Macro Intelligence Terminal",
    page_icon="⚡",
    layout="wide",
)

# 세션 상태에 실무 담당자 인사이트 아카이브 초기화
if "procurement_insights" not in st.session_state:
  st.session_state.procurement_insights = [
      {
          "id": 1,
          "author": "김구매 수석",
          "date": "2026-06-01",
          "content": (
              "구리 가격이 3개월 평균선 하단에 위치해 있으나, 하반기 인프라"
              " 수요 회복 가능성을 고려해 주요 전선 부품은 분할 매수 및 장기 계약"
              " 검토 필요."
          ),
      },
      {
          "id": 2,
          "author": "이전략 매니저",
          "date": "2026-06-03",
          "content": (
              "원/달러 환율 1,350원 공방 지속. 수입 대금 결제일 도래 시 분할"
              " 환전 전략 적용하여 리스크 최소화할 것."
          ),
      },
  ]


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
  copper_change = 0.0

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
              copper_change = rate
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

  return (
      categorized_data,
      summary_flat_list,
      fx_usd_krw,
      copper_price,
      copper_change,
  )


market_data, summary_list, fx_val, copper_val, copper_chg = fetch_market_data()
update_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S KST")
data_json = json.dumps(market_data)
summary_json = json.dumps(summary_list)

stress_status = "안정 (STABLE)"
stress_color = "text-emerald-500 bg-emerald-950/60 border-emerald-800"
if fx_val >= 1350 or copper_chg >= 3.0:
  stress_status = "주의 / 원가 압박 (CAUTION)"
  stress_color = "text-amber-500 bg-amber-950/60 border-amber-800"
if fx_val >= 1380 and copper_chg >= 5.0:
  stress_status = "고위기 / 비상 대응 (CRITICAL)"
  stress_color = "text-red-500 bg-red-950/60 border-red-800"

st.markdown("""
    <style>
    .insight-card { background-color: #1e293b; border: 1px solid #334155; padding: 15px; border-radius: 12px; margin-bottom: 10px; color: #f8fafc; }
    </style>
""", unsafe_allow_html=True)

html_template = f"""
<!DOCTYPE html>
<html lang="ko" class="dark">
<head>
    <meta charset="UTF-8">
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <!-- 화면 캡쳐를 위한 html2canvas 라이브러리 로드 -->
    <script src="https://cdnjs.cloudflare.com/ajax/libs/html2canvas/1.4.1/html2canvas.min.js"></script>
    <script>
        tailwind.config = {{ darkMode: 'class' }};
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

        // 대시보드 통째로 이미지 캡쳐 및 다운로드 함수
        function captureDashboard() {{
            const captureBtn = document.getElementById('capture-btn');
            captureBtn.innerText = "📸 캡쳐 중...";
            
            // 전체 바디 영역을 캔버스로 변환
            html2canvas(document.body, {{
                scale: 2, // 고해상도 설정
                useCORS: true,
                backgroundColor: document.documentElement.classList.contains('dark') ? '#030712' : '#f1f5f9'
            }}).then(canvas => {{
                const link = document.createElement('a');
                link.download = 'Macro_Intelligence_Terminal_' + new Date().toISOString().slice(0,10) + '.png';
                link.href = canvas.toDataURL('image/png');
                link.click();
                captureBtn.innerText = "📸 대시보드 전체 캡쳐저장";
            }}).catch(err => {{
                console.error("캡쳐 실패:", err);
                alert("화면 캡쳐 중 오류가 발생했습니다.");
                captureBtn.innerText = "📸 대시보드 전체 캡쳐저장";
            }});
        }}
    </script>
</head>
<body class="bg-slate-100 dark:bg-gray-950 text-slate-900 dark:text-gray-100 font-mono antialiased p-4 min-h-screen transition-colors duration-300 text-sm">
    
    <!-- 상단 헤더 및 캡쳐 버튼 -->
    <header class="flex flex-col md:flex-row justify-between items-start md:items-center border-b border-slate-300 dark:border-gray-800 pb-5 mb-6 gap-4">
        <div>
            <h1 class="text-2xl font-black tracking-wider text-emerald-600 dark:text-emerald-400">⚡ GLOBAL MACRO INTELLIGENCE TERMINAL</h1>
            <p class="text-xs text-slate-600 dark:text-gray-400 mt-1 font-semibold">Advanced Procurement & Negotiation Analytics Desk</p>
        </div>
        <div class="flex items-center gap-3">
            <!-- 캡쳐 버튼 추가 -->
            <button id="capture-btn" onclick="captureDashboard()" class="px-3.5 py-1.5 bg-emerald-600 hover:bg-emerald-700 text-white text-xs font-bold rounded-xl transition shadow-sm flex items-center gap-1.5">
                📸 대시보드 전체 캡쳐저장
            </button>
            <button id="theme-btn" onclick="toggleTheme()" class="px-3 py-1.5 bg-slate-200 dark:bg-gray-800 hover:bg-slate-300 dark:hover:bg-gray-700 text-xs font-bold rounded-xl transition shadow-sm">
                ☀️ 라이트 모드
            </button>
            <div class="text-right hidden sm:block">
                <span class="px-2.5 py-0.5 bg-emerald-100 dark:bg-emerald-950 border border-emerald-400 dark:border-emerald-800 text-emerald-800 dark:text-emerald-400 text-xs rounded-lg font-extrabold">LIVE SYSTEM</span>
                <p class="text-[11px] text-slate-500 dark:text-gray-400 mt-1">Refreshed: {update_time}</p>
            </div>
        </div>
    </header>

    <!-- 매크로 체감 지수 & 실무 액션 시그널 -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
        <div class="bg-white dark:bg-gray-900 border-2 border-slate-300 dark:border-gray-800 rounded-xl p-4 shadow-md flex flex-col justify-between">
            <div>
                <span class="text-[11px] font-bold text-slate-500 dark:text-gray-400 uppercase">🚨 AFK Macro Stress Index</span>
                <div class="mt-2 text-base font-black px-3 py-1.5 rounded-lg border text-center {stress_color}">{stress_status}</div>
            </div>
            <p class="text-[11px] text-slate-500 dark:text-gray-400 mt-2">환율 및 구리 변동성을 복합 반영한 전사 구매 원가 리스크 등급</p>
        </div>
        <div class="bg-white dark:bg-gray-900 border-2 border-slate-300 dark:border-gray-800 rounded-xl p-4 shadow-md flex flex-col justify-between">
            <div>
                <span class="text-[11px] font-bold text-slate-500 dark:text-gray-400 uppercase">💡 Procurement Timing Signal</span>
                <div class="mt-2 text-xs font-extrabold text-emerald-600 dark:text-emerald-400 bg-emerald-50 dark:bg-emerald-950/50 border border-emerald-300 dark:border-emerald-800 px-3 py-1.5 rounded-lg text-center">
                    { "✨ [조기 발주 권장] 3M 평균 하단 박스권" if fx_val < 1350 else "⚠️ [보수적 발주] 원가 상승 압박 구간" }
                </div>
            </div>
            <p class="text-[11px] text-slate-500 dark:text-gray-400 mt-2">현물 시세와 3M 평균 비교를 통한 최적의 대금 결제 및 계약 타이밍</p>
        </div>
        <div class="bg-white dark:bg-gray-900 border-2 border-slate-300 dark:border-gray-800 rounded-xl p-4 shadow-md flex flex-col justify-between">
            <div>
                <span class="text-[11px] font-bold text-slate-500 dark:text-gray-400 uppercase">🛡️ Vendor Negotiation Memo</span>
                <div class="mt-2 text-xs font-bold text-slate-800 dark:text-gray-200 bg-slate-100 dark:bg-gray-950 p-2 rounded-lg border border-slate-200 dark:border-gray-800">
                    "현재 환율({fx_val:,.2f}원) 및 구리 변동률({copper_chg:,.2f}%) 감안 시, 공급사의 전면 단가 인상 요구는 <b>객관적 근거 부족</b>으로 방어 가능."
                </div>
            </div>
            <p class="text-[11px] text-slate-500 dark:text-gray-400 mt-2">공급사 미팅 직전 캡처하여 바로 활용하는 원가 방어 핵심 논리</p>
        </div>
    </div>

    <!-- 구매 예산 시뮬레이터 -->
    <div class="mb-6 bg-white dark:bg-gray-900 border-2 border-slate-300 dark:border-emerald-500/40 rounded-xl p-5 shadow-md transition-colors">
        <div class="flex items-center justify-between border-b border-slate-200 dark:border-gray-800 pb-2 mb-3">
            <h2 class="text-sm font-extrabold text-emerald-600 dark:text-emerald-400 uppercase tracking-wide">🧮 Procurement Cost Impact Simulator</h2>
            <span class="text-xs text-slate-500 dark:text-gray-400 font-bold">환율 및 원자재 변동 예산 예측</span>
        </div>
        <div class="grid grid-cols-1 md:grid-cols-3 gap-4 items-center">
            <div>
                <label class="block text-xs font-bold text-slate-700 dark:text-gray-300 mb-1">연간 총 구매 예산 (억원)</label>
                <input type="number" id="annual-budget" value="100" oninput="calculateImpact()" class="w-full bg-slate-50 dark:bg-gray-950 border border-slate-300 dark:border-gray-700 rounded-lg px-3 py-2 text-sm font-bold text-slate-900 dark:text-white focus:outline-none focus:border-emerald-500">
            </div>
            <div>
                <label class="block text-xs font-bold text-slate-700 dark:text-gray-300 mb-1">환율(USD/KRW) 변동: <span id="fx-val-text" class="text-emerald-600 dark:text-emerald-400 font-extrabold">0%</span></label>
                <input type="range" id="fx-slider" min="-20" max="20" value="0" step="1" oninput="calculateImpact()" class="w-full accent-emerald-500 cursor-pointer">
            </div>
            <div>
                <label class="block text-xs font-bold text-slate-700 dark:text-gray-300 mb-1">원자재(구리 등) 변동: <span id="raw-val-text" class="text-emerald-600 dark:text-emerald-400 font-extrabold">0%</span></label>
                <input type="range" id="raw-slider" min="-30" max="30" value="0" step="1" oninput="calculateImpact()" class="w-full accent-emerald-500 cursor-pointer">
            </div>
        </div>
        <div class="mt-4 p-3 bg-slate-100 dark:bg-gray-950/80 rounded-lg border border-slate-200 dark:border-gray-800 flex justify-between items-center text-xs">
            <span class="font-bold text-slate-600 dark:text-gray-400">💡 시뮬레이션 결과 예측</span>
            <div id="simulation-result" class="font-bold text-slate-900 dark:text-white">예산 변동 폭: <b>0.00억 원</b> (0.0% 영향)</div>
        </div>
    </div>

    <!-- AI 교섭 전략 및 자동 인사이트 매트릭스 -->
    <div class="mb-6 bg-white dark:bg-gray-900 border border-slate-300 dark:border-gray-800 rounded-xl p-5 shadow-md transition-colors">
        <div class="flex items-center justify-between border-b border-slate-200 dark:border-gray-800 pb-2 mb-3">
            <h2 class="text-sm font-extrabold text-emerald-600 dark:text-emerald-400 uppercase tracking-wide">🎯 AI Procurement & Negotiation Insight Engine</h2>
            <span class="text-xs text-slate-500 dark:text-gray-400 font-bold">3개월 평균선 기준 원가 리스크 분석</span>
        </div>
        <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div class="bg-slate-50 dark:bg-gray-950/60 border border-slate-200 dark:border-gray-800 p-3 rounded-lg">
                <span class="text-xs font-extrabold text-amber-600 dark:text-amber-400 block mb-1">💱 환율 리스크 (USD/KRW)</span>
                <p class="text-xs text-slate-700 dark:text-gray-300 leading-relaxed">현재 환율: <b>{fx_val:,.2f}원</b>. { "1,350원 상회로 수입단가 상승 압박. 네고 분산 필요" if fx_val >= 1350 else "1,350원 하회로 안정 국면. 대금 결제 유리" }</p>
            </div>
            <div class="bg-slate-50 dark:bg-gray-950/60 border border-slate-200 dark:border-gray-800 p-3 rounded-lg">
                <span class="text-xs font-extrabold text-sky-600 dark:text-sky-400 block mb-1">🛠️ 원자재 닥터코퍼 (Copper)</span>
                <p class="text-xs text-slate-700 dark:text-gray-300 leading-relaxed">현재가: <b>{copper_val:,.2f}</b>. 제조업 부품 및 전선류 공급사 단가 인상 요구 시 3개월 평균선 비교 방어 논리 제공.</p>
            </div>
            <div class="bg-slate-50 dark:bg-gray-950/60 border border-slate-200 dark:border-gray-800 p-3 rounded-lg">
                <span class="text-xs font-extrabold text-emerald-600 dark:text-emerald-400 block mb-1">📈 차트 보조선 가이드</span>
                <p class="text-xs text-slate-700 dark:text-gray-300 leading-relaxed">모든 자산 카드 내의 <b>점선</b>은 최근 3개월 평균 가격입니다. 현재가가 평균선 위에 있으면 고점 주의, 아래면 저점 기회입니다.</p>
            </div>
        </div>
    </div>

    <!-- 히트맵 매트릭스 -->
    <div class="mb-6 bg-white dark:bg-gray-900 border border-slate-300 dark:border-gray-800 rounded-xl p-5 shadow-md transition-colors">
        <h2 class="text-sm font-extrabold text-emerald-600 dark:text-emerald-400 uppercase tracking-wider border-b border-slate-200 dark:border-gray-800 pb-2 mb-4">🔥 Macro Asset Performance Heatmap (3M Change Matrix)</h2>
        <div id="heatmap-container" class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-2.5"></div>
    </div>

    <!-- 카테고리별 매크로 지표 카드 덱 -->
    <div class="space-y-6 mb-6" id="dashboard-container"></div>

    <!-- 최하단: 학습 센터 -->
    <div class="bg-white dark:bg-gray-900 border-2 border-emerald-500/40 rounded-2xl p-6 shadow-md transition-colors">
        <div class="border-b border-slate-200 dark:border-gray-800 pb-3 mb-4">
            <h2 class="text-lg font-black text-emerald-600 dark:text-emerald-300 tracking-wide">📚 MACRO LEARNING CENTER & CORRELATION MAP</h2>
            <p class="text-xs text-slate-500 dark:text-gray-400 mt-0.5 font-bold">자재구매팀 실무 역량 강화를 위한 거시경제 지표 가이드 및 상관관계 분석</p>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mb-6">
            <div class="bg-slate-50 dark:bg-gray-950 border border-slate-200 dark:border-gray-800 p-4 rounded-xl shadow-sm">
                <span class="text-[11px] font-black px-2 py-0.5 rounded bg-amber-100 dark:bg-amber-950 text-amber-800 dark:text-amber-400">🇺🇸 US 10Y Treasury (국채 금리)</span>
                <h3 class="text-xs font-extrabold text-slate-900 dark:text-white mt-2">글로벌 자금 조달 및 할인율의 기준</h3>
                <p class="text-[11px] text-slate-600 dark:text-gray-400 mt-1.5 leading-relaxed">
                    <b>경제 영향</b>: 무위험 수익률 벤치마크로 전 세계 대출·회사채 금리의 기준.<br>
                    <b>물가·공급</b>: 금리 상승 시 기업 투자 위축, 달러 강세로 수입 원가 압박 심화.
                </p>
            </div>
            <div class="bg-slate-50 dark:bg-gray-950 border border-slate-200 dark:border-gray-800 p-4 rounded-xl shadow-sm">
                <span class="text-[11px] font-black px-2 py-0.5 rounded bg-sky-100 dark:bg-sky-950 text-sky-800 dark:text-sky-400">🛠️ Copper (구리 / 닥터 코퍼)</span>
                <h3 class="text-xs font-extrabold text-slate-900 dark:text-white mt-2">실물 경기 및 전선·부품 원가 선행 지표</h3>
                <p class="text-[11px] text-slate-600 dark:text-gray-400 mt-1.5 leading-relaxed">
                    <b>경제 영향</b>: 건설·전기전자·인프라 전반에 쓰여 '경기의 닥터'로 불림.<br>
                    <b>물가·공급</b>: 구리 상승은 곧바로 전기/전자 부품 및 전선류 공급사 단가 인상 직결.
                </p>
            </div>
            <div class="bg-slate-50 dark:bg-gray-950 border border-slate-200 dark:border-gray-800 p-4 rounded-xl shadow-sm">
                <span class="text-[11px] font-black px-2 py-0.5 rounded bg-yellow-100 dark:bg-yellow-950 text-yellow-800 dark:text-yellow-400">✨ Gold (금 / 안전자산)</span>
                <h3 class="text-xs font-extrabold text-slate-900 dark:text-white mt-2">인플레이션 헷지 및 경제 불확실성 척도</h3>
                <p class="text-[11px] text-slate-600 dark:text-gray-400 mt-1.5 leading-relaxed">
                    <b>경제 영향</b>: 화폐 가치 하락 및 지정학적 리스크 고조 시 자금 유입.<br>
                    <b>물가·공급</b>: 인플레이션 헤지 수단이며, 금값 폭등은 원자재 투기적 매수 심리 반영.
                </p>
            </div>
            <div class="bg-slate-50 dark:bg-gray-950 border border-slate-200 dark:border-gray-800 p-4 rounded-xl shadow-sm">
                <span class="text-[11px] font-black px-2 py-0.5 rounded bg-red-100 dark:bg-red-950 text-red-800 dark:text-red-400">🛢️ Crude Oil (유가 - WTI/Brent)</span>
                <h3 class="text-xs font-extrabold text-slate-900 dark:text-white mt-2">글로벌 물류비와 제조 원가의 심장</h3>
                <p class="text-[11px] text-slate-600 dark:text-gray-400 mt-1.5 leading-relaxed">
                    <b>경제 영향</b>: 석유화학 제품 원료 및 전 세계 해상·육상 물류의 핵심 동력.<br>
                    <b>물가·공급</b>: 유가 상승은 즉각적 CPI 상승 및 컨테이너 운임 할증료(BAF) 유발.
                </p>
            </div>
            <div class="bg-slate-50 dark:bg-gray-950 border border-slate-200 dark:border-gray-800 p-4 rounded-xl shadow-sm">
                <span class="text-[11px] font-black px-2 py-0.5 rounded bg-purple-100 dark:bg-purple-950 text-purple-800 dark:text-purple-400">🪙 Platinum & Palladium</span>
                <h3 class="text-xs font-extrabold text-slate-900 dark:text-white mt-2">정밀 화학 및 전장 부품 핵심 촉매</h3>
                <p class="text-[11px] text-slate-600 dark:text-gray-400 mt-1.5 leading-relaxed">
                    <b>경제 영향</b>: 자동차 배기가스 저감 장치 및 반도체·정밀화학 공정 필수 소재.<br>
                    <b>물가·공급</b>: 특정 산유국 수급 이슈에 취약하여 공급망 리스크 관리 필수.
                </p>
            </div>
            <div class="bg-slate-50 dark:bg-gray-950 border border-slate-200 dark:border-gray-800 p-4 rounded-xl shadow-sm">
                <span class="text-[11px] font-black px-2 py-0.5 rounded bg-emerald-100 dark:bg-emerald-950 text-emerald-800 dark:text-emerald-400">💱 USD/KRW (원/달러 환율)</span>
                <h3 class="text-xs font-extrabold text-slate-900 dark:text-white mt-2">수입 원가 및 대금 결제의 명암</h3>
                <p class="text-[11px] text-slate-600 dark:text-gray-400 mt-1.5 leading-relaxed">
                    <b>경제 영향</b>: 국내 모든 수입 원자재 및 부품의 원화 환산 가격을 결정.<br>
                    <b>물가·공급</b>: 환율 상승(원화 약세) 시 수입 물가 직격탄, 구매 예산 조기 소진 주범.
                </p>
            </div>
        </div>

        <div class="bg-slate-50 dark:bg-gray-950 border border-slate-200 dark:border-gray-800 p-4 rounded-xl">
            <h3 class="text-xs font-black text-slate-900 dark:text-white mb-3">🔗 거시경제 지표 간 상관관계 메커니즘 (Macro Correlation Flow)</h3>
            <div class="grid grid-cols-1 md:grid-cols-3 gap-3 text-xs">
                <div class="p-3 rounded-lg bg-white dark:bg-gray-900 border border-slate-200 dark:border-gray-800 shadow-sm">
                    <span class="font-bold text-amber-600 dark:text-amber-400 block mb-1">① 유가 상승 ➔ 물가·물류비 타격</span>
                    <p class="text-[11px] text-slate-600 dark:text-gray-400">원유가 상승 시 에너지 비용 및 해상/육상 운임 동반 상승으로 최종 부품 단가 인상 압박.</p>
                </div>
                <div class="p-3 rounded-lg bg-white dark:bg-gray-900 border border-slate-200 dark:border-gray-800 shadow-sm">
                    <span class="font-bold text-sky-600 dark:text-sky-400 block mb-1">② 미국 국채금리 ➔ 환율·수입단가 상승</span>
                    <p class="text-[11px] text-slate-600 dark:text-gray-400">미국 금리 상승 시 달러 강세(원/달러 환율 상승)로 수입 원재료 구매 비용 가중.</p>
                </div>
                <div class="p-3 rounded-lg bg-white dark:bg-gray-900 border border-slate-200 dark:border-gray-800 shadow-sm">
                    <span class="font-bold text-emerald-600 dark:text-emerald-400 block mb-1">③ 닥터 코퍼(구리) ➔ 선행 원가 경보</span>
                    <p class="text-[11px] text-slate-600 dark:text-gray-400">구리 가격 추세 전환은 1~2달 뒤 실제 제조업 자재 공급사의 단가 조정 요구로 직결.</p>
                </div>
            </div>
        </div>
    </div>

    <script>
        const rawData = {data_json};
        const summaryData = {summary_json};
        
        // 1. 히트맵 렌더링
        const heatmapContainer = document.getElementById('heatmap-container');
        if (heatmapContainer && heatmapContainer.children.length === 0) {{
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
        }}

        // 2. 카테고리별 매크로 지표 카드 덱 렌더링
        const container = document.getElementById('dashboard-container');
        if (container && container.children.length === 0) {{
            let catIndex = 0;
            for (const [category, items] of Object.entries(rawData)) {{
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
        }}

        // 3. Chart.js 스파크라인 및 3개월 평균선 렌더링
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

st.components.v1.html(html_template, height=1850, scrolling=True)

# ── [가장 하단] 실무 담당자 인사이트 관리 섹션 ──
st.markdown("---")
st.markdown(
    "### 📝 실무 담당자 마켓 인사이트 아카이브 (Team Insight & Memo Board)"
)
st.markdown(
    "구매팀 팀원들이 직접 인사이트와 협상 팁을 기록하고 관리하는 공간입니다."
)

with st.form("insight_form", clear_on_submit=True):
  col_in1, col_in2 = st.columns([1, 4])
  with col_in1:
    author_input = st.text_input("작성자명", placeholder="예: 김구매 수석")
  with col_in2:
    content_input = st.text_input(
        "인사이트 및 협상 팁 내용",
        placeholder=(
            "예: 특정 원자재 단가 인상 건 관련 3개월 평균선 기준 방어 논리 공유"
        ),
    )

  submitted = st.form_submit_button("✍️ 인사이트 등록하기")
  if submitted:
    if author_input and content_input:
      new_id = (
          max([item["id"] for item in st.session_state.procurement_insights])
          + 1
          if st.session_state.procurement_insights
          else 1
      )
      current_date = datetime.now().strftime("%Y-%m-%d")
      st.session_state.procurement_insights.append({
          "id": new_id,
          "author": author_input,
          "date": current_date,
          "content": content_input,
      })
      st.success("인사이트가 성공적으로 등록되었습니다!")
      st.rerun()
    else:
      st.warning("작성자와 내용을 모두 입력해 주세요.")

st.markdown("#### 📋 등록된 팀 내 인사이트 목록")

if not st.session_state.procurement_insights:
  st.info("등록된 인사이트가 없습니다. 첫 번째 의견을 남겨주세요!")
else:
  for item in st.session_state.procurement_insights:
    with st.container():
      st.markdown(
          f"""
                <div class="insight-card">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                        <span style="font-weight: bold; color: #38bdf8; font-size: 14px;">👤 {item['author']}</span>
                        <span style="color: #94a3b8; font-size: 12px;">📅 {item['date']}</span>
                    </div>
                    <div style="font-size: 14px; color: #f1f5f9; line-height: 1.5;">{item['content']}</div>
                </div>
                """,
          unsafe_allow_html=True,
      )
      if st.button(f"삭제 (ID: {item['id']})", key=f"del_{item['id']}"):
        st.session_state.procurement_insights = [
            i for i in st.session_state.procurement_insights if i["id"] != item["id"]
        ]
        st.success(f"ID {item['id']} 인사이트가 삭제되었습니다.")
        st.rerun()
