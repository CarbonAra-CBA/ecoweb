(function() {
    // 유틸리티 함수
    const getElement = id => document.getElementById(id);
    const encodeUrl = encodeURIComponent(window.location.href);

    // 스타일 정의
    const badgeStyles = `
        <style>
            #eco-badge {
                --primary: #00824c;
                --secondary: #e5f6ef;
                font-size: 15px;
                text-align: center;
                color: var(--primary);
                line-height: 1.15;
                font-family: -apple-system, BlinkMacSystemFont, sans-serif;
            }
            
            #eco-badge .measurement {
                display: inline-flex;
                justify-content: center;
                align-items: center;
                padding: 0.3em 0.5em;
                border: 0.13em solid var(--secondary);
                border-radius: 0.3em 0 0 0.3em;
                background: #fff;
                min-width: 8.2em;
            }
            
            #eco-badge .link {
                display: inline-flex;
                justify-content: center;
                align-items: center;
                padding: 0.3em 0.5em;
                border: 0.13em solid var(--primary);
                border-radius: 0 0.3em 0.3em 0;
                background: var(--primary);
                color: #fff;
                text-decoration: none;
                font-weight: bold;
            }
            
            #eco-badge .percentage {
                display: block;
                margin-top: 0.5em;
                font-size: 0.9em;
            }
        </style>
    `;

    // API 요청 함수
    const fetchData = async (updateUI = true) => {
        try {
            const response = await fetch(`https://your-app.vercel.app/api/badge?url=${encodeUrl}`);
            if (!response.ok) throw new Error('API request failed');
            
            const data = await response.json();
            if (updateUI) renderBadge(data);
            
            // 캐시 저장
            data.timestamp = new Date().getTime();
            localStorage.setItem(`eco-badge_${encodeUrl}`, JSON.stringify(data));
        } catch (error) {
            getElement('eco-measurement').innerHTML = '측정 실패';
            console.error(error);
            localStorage.removeItem(`eco-badge_${encodeUrl}`);
        }
    };

    // UI 렌더링 함수
    const renderBadge = (data) => {
        getElement('eco-measurement').innerHTML = 
            `${data.carbon}g of CO<sub>2</sub>/view`;
        getElement('eco-percentage').innerHTML = 
            `상위 ${data.percentage}% 친환경 웹사이트`;
    };

    // 배지 초기화
    const initBadge = () => {
        // DOM 요소 생성
        const badge = getElement('eco-badge');
        badge.innerHTML = `
            ${badgeStyles}
            <div class="badge-container">
                <span id="eco-measurement" class="measurement">
                    CO<sub>2</sub> 측정중...
                </span>
                <a href="https://your-domain.com" target="_blank" rel="noopener" 
                   class="link">ECO-WEB</a>
            </div>
            <span id="eco-percentage" class="percentage"></span>
        `;

        // 캐시된 데이터 확인
        const cached = localStorage.getItem(`eco-badge_${encodeUrl}`);
        const now = new Date().getTime();

        if (cached) {
            const data = JSON.parse(cached);
            renderBadge(data);
            
            // 24시간마다 갱신
            if (now - data.timestamp > 86400000) {
                fetchData(false);
            }
        } else {
            fetchData();
        }
    };

    // 브라우저 지원 확인 및 초기화
    if ('fetch' in window) {
        initBadge();
    }
})();